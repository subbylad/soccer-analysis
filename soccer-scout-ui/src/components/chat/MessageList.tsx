'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatMessage } from '@/types';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: ChatMessage[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-md"
        >
          <div className="text-6xl mb-4">⚽</div>
          <h2 className="text-xl font-semibold text-slate-700 mb-2">
            Welcome to Soccer Scout AI
          </h2>
          <p className="text-slate-500 mb-6">
            Start by asking about players, comparisons, or tactical insights
          </p>
          <div className="grid grid-cols-1 gap-2 text-sm text-slate-400">
            <div className="bg-white/50 rounded-lg p-3 border border-slate-200">
              &ldquo;Compare Haaland vs Mbappé&rdquo;
            </div>
            <div className="bg-white/50 rounded-lg p-3 border border-slate-200">
              &ldquo;Who can play alongside Kobbie Mainoo?&rdquo;
            </div>
            <div className="bg-white/50 rounded-lg p-3 border border-slate-200">
              &ldquo;Find young midfielders under 21&rdquo;
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-4">
      <div className="space-y-4">
        <AnimatePresence mode="popLayout">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};