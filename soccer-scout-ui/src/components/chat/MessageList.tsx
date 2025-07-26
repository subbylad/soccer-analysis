'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessage } from '@/types';
import { MessageBubble } from './MessageBubble';
import { QUICK_SUGGESTIONS } from '@/utils/test-queries';
import { useChat } from '@/hooks/useChat';

interface MessageListProps {
  messages: ChatMessage[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { sendMessage } = useChat();

  const scrollToBottom = () => {
    // Clear any existing timeout to avoid multiple scroll operations
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    // Debounce scroll operations to prevent excessive DOM updates
    scrollTimeoutRef.current = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  useEffect(() => {
    // Only scroll if messages array actually changed (not just re-renders)
    scrollToBottom();
    
    // Cleanup timeout on unmount
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [messages.length]); // Only depend on length to avoid unnecessary scrolls

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="empty-state max-w-2xl"
        >
          {/* Welcome Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="text-8xl mb-8"
          >
            ⚽
          </motion.div>
          
          {/* Welcome Text */}
          <h2 className="empty-state-title text-2xl mb-4">
            Welcome to Soccer Scout AI
          </h2>
          <p className="empty-state-description text-lg mb-8">
            Get started by asking about players, tactical insights, or comparisons. 
            I can analyze 2,850+ players from Europe's top 5 leagues.
          </p>

          {/* Quick Suggestions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="space-y-3 w-full max-w-md"
          >
            <h3 className="text-sm font-medium text-gray-700 mb-4">
              Try these examples:
            </h3>
            {QUICK_SUGGESTIONS.map((suggestion, index) => (
              <motion.button
                key={suggestion}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1, duration: 0.3 }}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full p-4 text-left bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all duration-200 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 group-hover:text-primary-700 transition-colors">
                    "{suggestion}"
                  </span>
                  <svg 
                    className="w-4 h-4 text-gray-400 group-hover:text-primary-500 transition-colors" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M13 7l5 5m0 0l-5 5m5-5H6" 
                    />
                  </svg>
                </div>
              </motion.button>
            ))}
          </motion.div>

          {/* Feature Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 w-full max-w-2xl"
          >
            {[
              {
                icon: '🔍',
                title: 'Player Analysis',
                description: 'Deep dive into individual player statistics and performance'
              },
              {
                icon: '⚡',
                title: 'Tactical Insights',
                description: 'GPT-4 enhanced tactical analysis and formation compatibility'
              },
              {
                icon: '📊',
                title: 'Smart Comparisons',
                description: 'Side-by-side player comparisons with detailed breakdowns'
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + index * 0.1, duration: 0.3 }}
                className="card text-center p-4"
              >
                <div className="text-2xl mb-2">{feature.icon}</div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  {feature.title}
                </h4>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <AnimatePresence mode="popLayout">
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="message"
          >
            <MessageBubble message={message} />
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={messagesEndRef} className="h-4" />
    </div>
  );
};