'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MessageList } from './MessageList';
import { QueryInput } from './QueryInput';
import { useChatStore } from '@/store/chatStore';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading } = useChatStore();

  return (
    <div className="world-chat-container">
      {/* World.org inspired header */}
      <header className="bg-world-bg-card border-b border-world-border py-8">
        <div className="world-layout-grid">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 className="world-text-title mb-2">
              Soccer Scout AI
            </h1>
            <p className="world-text-meta max-w-2xl">
              AI-powered tactical analysis and player insights for professional scouts. 
              Ask about players, formations, tactical compatibility, or scouting reports.
            </p>
          </motion.div>
        </div>
      </header>

      {/* Main chat area with world.org grid layout */}
      <main className="flex-1 py-12">
        <div className="world-layout-grid">
          <div className="flex flex-col gap-8">
            <MessageList messages={messages} />
            <QueryInput disabled={isLoading} />
          </div>
        </div>
      </main>
    </div>
  );
};