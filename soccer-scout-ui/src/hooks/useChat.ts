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
        // Log the actual error and throw it instead of falling back to demo
        console.error('API query failed:', error);
        throw error;
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
          content: `❌ **Connection Error**

Sorry, I couldn't process your query "${query}" due to a connection issue.

**Possible causes:**
• Network connectivity problem
• Backend service temporarily unavailable
• API response validation failed

**Please try again in a moment.** If the issue persists, the backend may be temporarily down for maintenance.

**Error details:** ${error instanceof Error ? error.message : 'Unknown error'}`,
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