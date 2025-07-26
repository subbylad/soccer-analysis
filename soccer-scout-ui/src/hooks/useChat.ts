import { useMutation } from '@tanstack/react-query';
import { useChatStore } from '@/store/chatStore';
import { api } from '@/services/api';
import { QueryResponse } from '@/types';

// Response validation schema to prevent runtime crashes
const validateQueryResponse = (data: any): data is QueryResponse => {
  return (
    data &&
    typeof data === 'object' &&
    typeof data.response_text === 'string' &&
    typeof data.query_type === 'string' &&
    (data.players === undefined || Array.isArray(data.players)) &&
    (data.analysis === undefined || typeof data.analysis === 'object') &&
    (data.comparison === undefined || typeof data.comparison === 'object') &&
    (data.scouting_report === undefined || typeof data.scouting_report === 'object')
  );
};

export const useChat = () => {
  const { addMessage, updateMessage, setLoading } = useChatStore();

  const queryMutation = useMutation({
    mutationFn: async (query: string): Promise<QueryResponse> => {
      try {
        const data = await api.query(query);
        
        // Validate response structure to prevent runtime errors
        if (!validateQueryResponse(data)) {
          console.error('Invalid API response structure:', data);
          throw new Error('Invalid response format from API');
        }
        
        return data;
      } catch (error) {
        // Fallback response when API is not available (e.g., in Vercel deployment)
        console.warn('API not available, using fallback response:', error);
        return {
          response_text: `Thank you for trying Soccer Scout AI! 

I'm a demonstration of the world.org-inspired minimal design transformation. In a full deployment, I would connect to our Flask backend API to provide:

• Player comparisons and analysis
• Tactical scouting insights  
• GPT-4 enhanced tactical recommendations
• Young player prospect identification

To see the full functionality, run the application locally with both the Next.js frontend and Flask backend servers.

**Sample queries I can handle:**
- "Compare Haaland vs Mbappé"
- "Who can play alongside Kobbie Mainoo in Ligue 1?"
- "Find young midfielders under 21"
- "Best alternatives to Rodri"

The interface you're seeing showcases the new world.org-inspired minimal aesthetic - clean typography, generous whitespace, and professional styling.`,
          query_type: 'demo',
          players: [],
        };
      }
    },
    onMutate: (query) => {
      // Add user message immediately
      addMessage({
        content: query,
        type: 'user',
      });

      // Add loading assistant message
      const loadingId = Date.now().toString() + '_loading';
      addMessage({
        content: '',
        type: 'assistant',
        isLoading: true,
      });

      setLoading(true);
      return { loadingId };
    },
    onSuccess: (data, query, context) => {
      // Find the loading message and update it
      const { messages } = useChatStore.getState();
      const loadingMessage = messages.find(msg => msg.isLoading && msg.type === 'assistant');
      
      if (loadingMessage) {
        // Safe property access with validation
        updateMessage(loadingMessage.id, {
          content: data.response_text || 'No response received',
          isLoading: false,
          players: data.players || [],
          analysis: data.analysis || undefined,
          comparison: data.comparison || undefined,
          scouting_report: data.scouting_report || undefined,
          query_type: data.query_type || 'general',
        });
      }

      setLoading(false);
    },
    onError: (error, query, context) => {
      // Find the loading message and update it with error
      const { messages } = useChatStore.getState();
      const loadingMessage = messages.find(msg => msg.isLoading && msg.type === 'assistant');
      
      if (loadingMessage) {
        updateMessage(loadingMessage.id, {
          content: `I'm sorry, I encountered an error processing your query: ${error instanceof Error ? error.message : 'Unknown error'}`,
          isLoading: false,
        });
      }

      setLoading(false);
    },
  });

  const sendMessage = (query: string) => {
    if (!query.trim()) return;
    queryMutation.mutate(query);
  };

  return {
    sendMessage,
    isLoading: queryMutation.isPending,
    error: queryMutation.error,
  };
};