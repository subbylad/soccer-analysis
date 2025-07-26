// Core types for the Soccer Scout AI interface

export interface Player {
  id: string;
  name: string;
  position: string;
  age: number;
  club: string;
  league: string;
  nationality: string;
  stats: PlayerStats;
  // Additional fields that might come from the backend
  season?: string;
  team_id?: string;
  player_id?: string;
}

export interface PlayerStats {
  // Basic stats
  goals: number;
  assists: number;
  matches_played: number;
  minutes_played: number;
  
  // Per 90 stats
  goals_per_90: number;
  assists_per_90: number;
  
  // Expected stats
  xg: number;
  xa: number;
  xg_per_90?: number;
  xa_per_90?: number;
  
  // Progressive stats
  progressive_passes: number;
  progressive_carries: number;
  progressive_passes_per_90?: number;
  progressive_carries_per_90?: number;
  
  // Defensive stats (for full compatibility)
  tackles?: number;
  interceptions?: number;
  blocks?: number;
  clearances?: number;
  
  // Passing stats
  passes_completed?: number;
  passes_attempted?: number;
  pass_completion_percentage?: number;
  
  // Additional stats
  cards_yellow?: number;
  cards_red?: number;
  fouls?: number;
  fouled?: number;
  
  // Scouting metrics
  potential_score?: number;
  scout_rating?: number;
  
  // Market value (if available)
  market_value?: number;
  market_value_currency?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
  players?: Player[];
  analysis?: TacticalAnalysis;
  comparison?: ComparisonAnalysis;
  scouting_report?: ScoutingReport;
  query_type?: 'comparison' | 'search' | 'tactical' | 'scouting' | 'general' | 'demo';
}

export interface TacticalAnalysis {
  summary: string;
  reasoning: string;
  alternatives?: Player[];
  tactical_fit?: string;
  formation_fit?: string;
  strengths?: string[];
  weaknesses?: string[];
  compatibility_score?: number;
  system_analysis?: string;
}

export interface ComparisonAnalysis {
  player_1: Player;
  player_2: Player;
  comparison_summary: string;
  strengths_comparison: {
    player_1_advantages: string[];
    player_2_advantages: string[];
  };
  statistical_winner: string;
  recommendation: string;
}

export interface ScoutingReport {
  player: Player;
  tier: 'Elite' | 'High' | 'Good' | 'Developing';
  tier_emoji: string;
  potential_summary: string;
  key_strengths: string[];
  areas_for_improvement: string[];
  comparable_players?: string[];
  recommendation: string;
}

export interface QueryResponse {
  response_text: string;
  players?: Player[];
  analysis?: TacticalAnalysis;
  comparison?: ComparisonAnalysis;
  scouting_report?: ScoutingReport;
  query_type: 'comparison' | 'search' | 'tactical' | 'scouting' | 'general' | 'demo';
  processing_time?: number;
  data_source?: string;
  suggestions?: string[];
}

export interface APIConfig {
  baseUrl: string;
  timeout: number;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  currentQuery: string;
}

// Backend API request/response types for better type safety
export interface QueryRequest {
  query: string;
  include_analysis?: boolean;
  max_players?: number;
  filters?: {
    position?: string;
    league?: string;
    age_min?: number;
    age_max?: number;
    min_minutes?: number;
  };
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  version?: string;
  uptime?: number;
  database_status?: 'connected' | 'disconnected';
  api_features?: string[];
}

// Error types for better error handling
export interface APIErrorResponse {
  detail: string;
  code?: string;
  type?: 'validation_error' | 'not_found' | 'server_error';
  context?: Record<string, any>;
}

// UI-specific types
export interface LoadingState {
  isLoading: boolean;
  loadingMessage?: string;
  progress?: number;
}

export interface NotificationState {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  id: string;
}