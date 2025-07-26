import { create } from 'zustand';
import { ChatMessage, ChatState } from '@/types';

// Counter for unique IDs as fallback for crypto.randomUUID()
let messageIdCounter = 0;

// Helper function to generate unique message IDs
const generateMessageId = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID()
  return `msg_${Date.now()}_${++messageIdCounter}`;
};

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
      id: generateMessageId(), // Fix race condition with unique IDs
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