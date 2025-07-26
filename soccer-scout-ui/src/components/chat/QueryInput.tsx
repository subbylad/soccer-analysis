'use client';

import React, { useState, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import { cn } from '@/utils';

interface QueryInputProps {
  disabled?: boolean;
}

export const QueryInput: React.FC<QueryInputProps> = ({ disabled = false }) => {
  const [query, setQuery] = useState('');
  const { sendMessage, isLoading } = useChat();

  const handleSubmit = () => {
    if (!query.trim() || disabled || isLoading) return;
    
    sendMessage(query);
    setQuery('');
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const suggestedQueries = [
    "Compare Haaland vs Mbappé",
    "Who can play alongside Kobbie Mainoo?",
    "Find young midfielders under 21",
    "Best alternatives to Rodri",
  ];

  return (
    <div className="bg-world-bg-card border-t border-world-border">
      <div className="world-layout-grid py-6">
        {/* Suggested Queries with world.org minimal design */}
        {query === '' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4"
          >
            <div className="flex flex-wrap gap-2">
              {suggestedQueries.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion)}
                  className="world-text-meta text-world-text-secondary bg-world-bg-muted hover:opacity-60 px-3 py-2 rounded border border-world-border-muted transition-opacity duration-300"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Input Area with world.org styling */}
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about players, tactics, comparisons..."
            disabled={disabled}
            rows={1}
            className={cn(
              'world-input w-full resize-none pr-12 min-h-[52px] max-h-32',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
            style={{
              height: 'auto',
              minHeight: '52px',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 128) + 'px';
            }}
          />

          {/* Send Button with world.org minimal design */}
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || disabled || isLoading}
            className={cn(
              'absolute right-3 top-1/2 transform -translate-y-1/2 w-8 h-8 rounded flex items-center justify-center transition-opacity duration-300',
              query.trim() && !disabled && !isLoading
                ? 'bg-world-accent text-white hover:opacity-60'
                : 'bg-world-bg-muted text-world-text-muted cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Status Indicator with world.org typography */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="world-text-meta text-world-text-secondary mt-3 flex items-center gap-2"
          >
            <div className="w-2 h-2 bg-world-text-secondary rounded-full animate-pulse" />
            Processing your query...
          </motion.div>
        )}
      </div>
    </div>
  );
};