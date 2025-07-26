/**
 * Comprehensive test queries for Soccer Scout AI
 * Used for testing API functionality and demonstrating capabilities
 */

export interface TestQuery {
  id: string;
  query: string;
  description: string;
  expectedType: string;
  category: 'comparison' | 'tactical' | 'prospect' | 'search' | 'demo';
}

export const TEST_QUERIES: TestQuery[] = [
  // Player Comparisons
  {
    id: 'compare-haaland-mbappe',
    query: 'Compare Haaland vs Mbappé',
    description: 'Classic striker comparison with statistical analysis',
    expectedType: 'comparison',
    category: 'comparison'
  },
  {
    id: 'compare-midfielders',
    query: 'Compare Bellingham vs Pedri',
    description: 'Midfield creativity comparison',
    expectedType: 'comparison', 
    category: 'comparison'
  },

  // Tactical Analysis
  {
    id: 'tactical-mainoo',
    query: 'Who can play alongside Kobbie Mainoo in Ligue 1?',
    description: 'GPT-4 enhanced tactical partner analysis',
    expectedType: 'tactical_analysis',
    category: 'tactical'
  },
  {
    id: 'tactical-rodri-alternative',
    query: 'Find an alternative to Rodri for Manchester City',
    description: 'System-specific player replacement analysis',
    expectedType: 'tactical_analysis',
    category: 'tactical'
  },
  {
    id: 'tactical-formation',
    query: 'Who would complement Bellingham in Real Madrid\'s midfield?',
    description: 'Formation-specific tactical analysis',
    expectedType: 'tactical_analysis',
    category: 'tactical'
  },

  // Young Prospects
  {
    id: 'young-midfielders',
    query: 'Find young midfielders under 21',
    description: 'Age-filtered prospect identification',
    expectedType: 'prospect_search',
    category: 'prospect'
  },
  {
    id: 'young-defenders-ligue1',
    query: 'Young defenders under 23 in Ligue 1',
    description: 'League and position specific prospect search',
    expectedType: 'prospect_search',
    category: 'prospect'
  },

  // Player Search
  {
    id: 'search-pedri',
    query: 'Tell me about Pedri',
    description: 'Individual player analysis and profile',
    expectedType: 'search',
    category: 'search'
  },
  {
    id: 'search-similar-style',
    query: 'Show me players similar to Pedri\'s style',
    description: 'Style-based player matching',
    expectedType: 'search',
    category: 'search'
  },

  // Demo/Fallback Queries
  {
    id: 'demo-general',
    query: 'What can you do?',
    description: 'General capabilities demonstration',
    expectedType: 'demo',
    category: 'demo'
  },
  {
    id: 'demo-random',
    query: 'Random soccer question',
    description: 'Fallback response testing',
    expectedType: 'demo',
    category: 'demo'
  }
];

// Quick test functions
export const getRandomTestQuery = (): TestQuery => {
  return TEST_QUERIES[Math.floor(Math.random() * TEST_QUERIES.length)];
};

export const getTestQueriesByCategory = (category: TestQuery['category']): TestQuery[] => {
  return TEST_QUERIES.filter(q => q.category === category);
};

export const getComparisonQueries = () => getTestQueriesByCategory('comparison');
export const getTacticalQueries = () => getTestQueriesByCategory('tactical');
export const getProspectQueries = () => getTestQueriesByCategory('prospect');

// Test query suggestions for autocomplete
export const QUICK_SUGGESTIONS = [
  'Compare Haaland vs Mbappé',
  'Who can play alongside Kobbie Mainoo?',
  'Find young midfielders under 21',
  'Tell me about Pedri',
  'Best alternatives to Rodri'
];