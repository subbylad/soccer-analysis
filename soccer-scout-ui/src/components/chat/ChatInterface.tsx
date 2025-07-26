'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MessageList } from './MessageList';
import { QueryInput } from './QueryInput';
import { useChatStore } from '@/store/chatStore';
import ErrorBoundary from '@/components/ErrorBoundary';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading } = useChatStore();

  return (
    <div className="chat-container">
      {/* Professional Header */}
      <header className="chat-header">
        <div className="chat-header-content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <div className="mb-4">
              <h1 className="text-display-md font-bold gradient-text-primary mb-3">
                Soccer Scout AI
              </h1>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto text-balance">
                AI-powered tactical analysis and player insights for professional scouts. 
                Ask about players, formations, tactical compatibility, or scouting reports.
              </p>
            </div>
            
            {/* Feature highlights */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex flex-wrap justify-center gap-2 mt-6"
            >
              {[
                'Player Comparisons',
                'Tactical Analysis',
                'GPT-4 Enhanced',
                '2,850+ Players',
                'Big 5 Leagues'
              ].map((feature, index) => (
                <span
                  key={feature}
                  className="badge-primary"
                >
                  {feature}
                </span>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="chat-main">
        <div className="chat-messages">
          <div className="chat-messages-content">
            <ErrorBoundary>
              <MessageList messages={messages} />
            </ErrorBoundary>
          </div>
        </div>
        
        {/* Input Container */}
        <div className="chat-input-container">
          <div className="chat-input-content">
            <ErrorBoundary>
              <QueryInput disabled={isLoading} />
            </ErrorBoundary>
          </div>
        </div>
      </main>
    </div>
  );
};