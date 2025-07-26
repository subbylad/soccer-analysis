import { useMutation } from '@tanstack/react-query';
import { useChatStore } from '@/store/chatStore';
import { api } from '@/services/api';
import { QueryResponse } from '@/types';

export const useChat = () => {
  const { addMessage, updateMessage, setLoading } = useChatStore();

  const queryMutation = useMutation({
    mutationFn: async (query: string): Promise<QueryResponse> => {
      return api.query(query);
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
        updateMessage(loadingMessage.id, {
          content: data.response_text,
          isLoading: false,
          players: data.players,
          analysis: data.analysis,
          comparison: data.comparison,
          scouting_report: data.scouting_report,
          query_type: data.query_type,
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