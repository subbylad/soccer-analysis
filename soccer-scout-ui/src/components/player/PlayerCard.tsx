'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Calendar } from 'lucide-react';
import { Player } from '@/types';
import { formatNumber, formatAge, formatPosition, getTierLabel } from '@/utils';

interface PlayerCardProps {
  player: Player;
}

export const PlayerCard: React.FC<PlayerCardProps> = ({ player }) => {
  const { stats } = player;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="world-card hover:shadow-world-medium"
    >
      {/* Player header with world.org typography */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h3 className="world-text-body font-semibold mb-2">
            {player.name}
          </h3>
          
          <div className="flex items-center gap-4 world-text-meta text-world-text-secondary">
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {player.club}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {formatAge(player.age)}
            </span>
          </div>
        </div>

        <div className="text-right">
          <div className="bg-world-bg-muted text-world-text-secondary px-3 py-1 rounded font-medium world-text-meta">
            {formatPosition(player.position)}
          </div>
          {stats.potential_score && (
            <div className="world-text-meta text-world-text-muted mt-1">
              {getTierLabel(stats.potential_score)}
            </div>
          )}
        </div>
      </div>

      {/* Minimal stats table with world.org aesthetic */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
          <span className="world-text-meta text-world-text-secondary">Goals</span>
          <span className="world-text-meta font-medium">
            {stats.goals} ({formatNumber(stats.goals_per_90)}/90)
          </span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
          <span className="world-text-meta text-world-text-secondary">Assists</span>
          <span className="world-text-meta font-medium">
            {stats.assists} ({formatNumber(stats.assists_per_90)}/90)
          </span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
          <span className="world-text-meta text-world-text-secondary">Expected Goals</span>
          <span className="world-text-meta font-medium">
            {formatNumber(stats.xg)}
          </span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
          <span className="world-text-meta text-world-text-secondary">Minutes Played</span>
          <span className="world-text-meta font-medium">
            {stats.minutes_played.toLocaleString()} ({stats.matches_played} games)
          </span>
        </div>
      </div>

      {/* Additional stats in minimal world.org style */}
      {stats.xa > 0 && (
        <div className="space-y-2 mb-6">
          <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
            <span className="world-text-meta text-world-text-secondary">Expected Assists</span>
            <span className="world-text-meta font-medium">{formatNumber(stats.xa)}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
            <span className="world-text-meta text-world-text-secondary">Performance vs Expected</span>
            <span className="world-text-meta font-medium">
              {stats.goals + stats.assists > stats.xg + stats.xa ? 'Above' : 'Below'} expected
            </span>
          </div>
        </div>
      )}

      {/* Progressive stats */}
      {(stats.progressive_passes > 0 || stats.progressive_carries > 0) && (
        <div className="space-y-2 mb-6">
          {stats.progressive_passes > 0 && (
            <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
              <span className="world-text-meta text-world-text-secondary">Progressive Passes</span>
              <span className="world-text-meta font-medium">{stats.progressive_passes}</span>
            </div>
          )}
          {stats.progressive_carries > 0 && (
            <div className="flex justify-between items-center py-2 border-b border-world-border-muted">
              <span className="world-text-meta text-world-text-secondary">Progressive Carries</span>
              <span className="world-text-meta font-medium">{stats.progressive_carries}</span>
            </div>
          )}
        </div>
      )}

      {/* Footer with league and nationality */}
      <div className="flex items-center justify-between pt-4 mt-6 border-t border-world-border-muted">
        <span className="world-text-meta text-world-text-secondary">{player.league}</span>
        <span className="world-text-meta text-world-text-muted">{player.nationality}</span>
      </div>
    </motion.div>
  );
};