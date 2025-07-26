import { create } from 'zustand';
import { ChatMessage, ChatState } from '@/types';

interface ChatStore extends ChatState {
  // Actions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  setLoading: (loading: boolean) => void;
  setCurrentQuery: (query: string) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // State
  messages: [],
  isLoading: false,
  currentQuery: '',

  // Actions
  addMessage: (message) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  updateMessage: (id, updates) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, ...updates } : msg
      ),
    }));
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setCurrentQuery: (query) => {
    set({ currentQuery: query });
  },

  clearMessages: () => {
    set({ messages: [] });
  },
}));