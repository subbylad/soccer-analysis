'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot, Loader2 } from 'lucide-react';
import { ChatMessage } from '@/types';
import { PlayerCard } from '@/components/player/PlayerCard';
import { formatDate } from '@/utils';
import { cn } from '@/utils';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="flex flex-col gap-4 mb-8"
    >
      {/* Message header with world.org minimal design */}
      <div className="flex items-center gap-3">
        <div
          className={cn(
            'w-6 h-6 rounded-full flex items-center justify-center text-xs',
            isUser
              ? 'bg-world-text-primary text-white'
              : 'bg-world-text-secondary text-white'
          )}
        >
          {isUser ? <User size={12} /> : <Bot size={12} />}
        </div>
        <span className="world-text-meta">
          {isUser ? 'You' : 'Soccer Scout AI'}
        </span>
        <span className="world-text-meta text-world-text-muted">
          {formatDate(message.timestamp)}
        </span>
      </div>

      {/* Message content with world.org typography */}
      <div className="ml-9">
        {message.isLoading ? (
          <div className="flex items-center gap-2 text-world-text-secondary">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="world-text-body">Analyzing your query...</span>
          </div>
        ) : (
          <div className="world-text-body whitespace-pre-wrap break-words">
            {message.content}
          </div>
        )}

        {/* Player Cards with world.org styling */}
        {message.players && message.players.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-6 space-y-3"
          >
            {message.players.map((player) => (
              <PlayerCard key={player.id} player={player} />
            ))}
          </motion.div>
        )}

        {/* Tactical Analysis with world.org minimal design */}
        {message.analysis && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6 world-card"
          >
            <div className="flex items-center gap-3 mb-4">
              <h3 className="world-text-body font-semibold">Tactical Analysis</h3>
              {message.analysis.compatibility_score && (
                <span className="bg-world-bg-muted text-world-text-secondary px-2 py-1 rounded text-xs font-medium">
                  {Math.round(message.analysis.compatibility_score * 100)}% Match
                </span>
              )}
            </div>
            
            <p className="world-text-body text-world-text-secondary mb-4">
              {message.analysis.reasoning}
            </p>

            {/* Strengths & Weaknesses */}
            {(message.analysis.strengths || message.analysis.weaknesses) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {message.analysis.strengths && (
                  <div className="border border-world-border-muted rounded p-3">
                    <h4 className="world-text-meta font-medium mb-2">Strengths</h4>
                    <ul className="world-text-meta text-world-text-secondary space-y-1">
                      {message.analysis.strengths.map((strength, i) => (
                        <li key={i}>• {strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {message.analysis.weaknesses && (
                  <div className="border border-world-border-muted rounded p-3">
                    <h4 className="world-text-meta font-medium mb-2">Areas to Consider</h4>
                    <ul className="world-text-meta text-world-text-secondary space-y-1">
                      {message.analysis.weaknesses.map((weakness, i) => (
                        <li key={i}>• {weakness}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* System Fits */}
            <div className="flex flex-wrap gap-2">
              {message.analysis.tactical_fit && (
                <div className="world-text-meta text-world-text-secondary bg-world-bg-muted px-3 py-1 rounded">
                  System: {message.analysis.tactical_fit}
                </div>
              )}
              {message.analysis.formation_fit && (
                <div className="world-text-meta text-world-text-secondary bg-world-bg-muted px-3 py-1 rounded">
                  Formation: {message.analysis.formation_fit}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Comparison Analysis with world.org styling */}
        {message.comparison && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-6 world-card"
          >
            <h3 className="world-text-body font-semibold mb-4">
              Player Comparison
            </h3>
            
            <p className="world-text-body text-world-text-secondary mb-4">
              {message.comparison.comparison_summary}
            </p>

            {/* Advantages */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="border border-world-border-muted rounded p-3">
                <h4 className="world-text-meta font-medium mb-2">
                  {message.comparison.player_1.name} Advantages
                </h4>
                <ul className="world-text-meta text-world-text-secondary space-y-1">
                  {message.comparison.strengths_comparison.player_1_advantages.map((advantage, i) => (
                    <li key={i}>• {advantage}</li>
                  ))}
                </ul>
              </div>
              <div className="border border-world-border-muted rounded p-3">
                <h4 className="world-text-meta font-medium mb-2">
                  {message.comparison.player_2.name} Advantages
                </h4>
                <ul className="world-text-meta text-world-text-secondary space-y-1">
                  {message.comparison.strengths_comparison.player_2_advantages.map((advantage, i) => (
                    <li key={i}>• {advantage}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Winner & Recommendation */}
            <div className="bg-world-bg-muted border border-world-border-muted rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="world-text-meta font-medium">Statistical Winner:</span>
                <span className="bg-world-accent text-white px-2 py-1 rounded text-xs font-medium">
                  {message.comparison.statistical_winner}
                </span>
              </div>
              <p className="world-text-meta text-world-text-secondary">
                {message.comparison.recommendation}
              </p>
            </div>
          </motion.div>
        )}

        {/* Scouting Report with world.org minimal design */}
        {message.scouting_report && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-6 world-card"
          >
            <div className="flex items-center gap-3 mb-4">
              <h3 className="world-text-body font-semibold">Scouting Report</h3>
              <span className="bg-world-bg-muted text-world-text-secondary px-2 py-1 rounded text-xs font-medium">
                {message.scouting_report.tier}
              </span>
            </div>
            
            <p className="world-text-body text-world-text-secondary mb-4">
              {message.scouting_report.potential_summary}
            </p>

            {/* Strengths & Areas for Improvement */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="border border-world-border-muted rounded p-3">
                <h4 className="world-text-meta font-medium mb-2">Key Strengths</h4>
                <ul className="world-text-meta text-world-text-secondary space-y-1">
                  {message.scouting_report.key_strengths.map((strength, i) => (
                    <li key={i}>• {strength}</li>
                  ))}
                </ul>
              </div>
              <div className="border border-world-border-muted rounded p-3">
                <h4 className="world-text-meta font-medium mb-2">Areas for Development</h4>
                <ul className="world-text-meta text-world-text-secondary space-y-1">
                  {message.scouting_report.areas_for_improvement.map((area, i) => (
                    <li key={i}>• {area}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Comparable Players */}
            {message.scouting_report.comparable_players && message.scouting_report.comparable_players.length > 0 && (
              <div className="bg-world-bg-muted border border-world-border-muted rounded p-3 mb-4">
                <h4 className="world-text-meta font-medium mb-2">Similar Players</h4>
                <div className="flex flex-wrap gap-2">
                  {message.scouting_report.comparable_players.map((player, i) => (
                    <span key={i} className="bg-world-bg-card border border-world-border text-world-text-secondary px-2 py-1 rounded text-xs">
                      {player}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            <div className="bg-world-bg-muted border border-world-border-muted rounded p-3">
              <h4 className="world-text-meta font-medium mb-1">Scout Recommendation</h4>
              <p className="world-text-meta text-world-text-secondary">
                {message.scouting_report.recommendation}
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};