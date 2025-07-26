#!/usr/bin/env python3
"""
Frontend Response Adapter for Soccer Analytics API

Adapts the internal API response format to match the React frontend's
expected response structure defined in TypeScript interfaces.
"""

from typing import Dict, Any, List, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class FrontendResponseAdapter:
    """
    Adapts internal API responses to match React frontend TypeScript interfaces.
    
    Expected React frontend format:
    - QueryResponse: { response_text, players?, analysis?, query_type }
    - Player: { id, name, position, age, club, league, nationality, stats }
    - TacticalAnalysis: { summary, reasoning, alternatives, tactical_fit }
    """
    
    @staticmethod
    def adapt_query_response(internal_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt internal API response to React frontend QueryResponse format.
        
        Args:
            internal_response: Response from SoccerAnalyticsAPI.query()
            
        Returns:
            Response formatted for React frontend
        """
        try:
            # Extract basic info
            response_text = internal_response.get('chat_text', '')
            if not response_text:
                response_text = internal_response.get('summary', 'Analysis completed')
            
            # Determine query type
            query_type = FrontendResponseAdapter._map_query_type(
                internal_response.get('type', 'search')
            )
            
            # Build base response
            frontend_response = {
                "response_text": response_text,
                "query_type": query_type
            }
            
            # Add players if available
            players = FrontendResponseAdapter._extract_players(internal_response)
            if players:
                frontend_response["players"] = players
            
            # Add tactical analysis if available
            analysis = FrontendResponseAdapter._extract_tactical_analysis(internal_response)
            if analysis:
                frontend_response["analysis"] = analysis
            
            logger.debug(f"Adapted response: {query_type} with {len(players) if players else 0} players")
            return frontend_response
            
        except Exception as e:
            logger.error(f"Failed to adapt response: {e}")
            return {
                "response_text": "Error processing response",
                "query_type": "search",
                "error": str(e)
            }
    
    @staticmethod
    def _map_query_type(internal_type: str) -> str:
        """Map internal query types to frontend types."""
        type_mapping = {
            'player_comparison': 'comparison',
            'comparison': 'comparison',           # Direct comparison type
            'player_search': 'search', 
            'player_list': 'search',
            'top_performers': 'scouting',         # Top performers are scouting
            'young_prospects': 'scouting',
            'tactical_analysis': 'tactical',
            'position_analysis': 'scouting',
            'error': 'search'
        }
        return type_mapping.get(internal_type, 'search')
    
    @staticmethod
    def _extract_players(internal_response: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Extract and format player data for frontend.""" 
        players_data = []
        
        # For comparison queries, use comparison_data
        if internal_response.get('type') == 'comparison' and 'comparison_data' in internal_response:
            raw_players = internal_response['comparison_data']
        # For player lists, merge players array (has team/league) with display_data (has more stats)
        else:
            display_data = internal_response.get('display_data', [])
            players_array = internal_response.get('players', [])
            
            # Merge data from both sources for complete information
            if display_data and players_array:
                raw_players = []
                for i, display_item in enumerate(display_data):
                    # Start with display data (has more stats)
                    merged_item = display_item.copy()
                    
                    # Merge in team/league info from players array if available
                    if i < len(players_array):
                        player_info = players_array[i]
                        merged_item.update({
                            'name': player_info.get('name', merged_item.get('name')),
                            'team': player_info.get('team', merged_item.get('team', 'Unknown')),
                            'league': player_info.get('league', merged_item.get('league', 'Unknown')),
                            'club': player_info.get('team', merged_item.get('team', 'Unknown')),  # Alias for frontend
                        })
                    
                    raw_players.append(merged_item)
            elif players_array:
                # Use players array if display_data is not available
                raw_players = players_array
            elif display_data:
                # Use display_data if players array is not available
                raw_players = display_data
            else:
                raw_players = []
        
        if not raw_players:
            return None
        
        for i, player in enumerate(raw_players):
            if isinstance(player, dict):
                formatted_player = FrontendResponseAdapter._format_player(player, i)
                if formatted_player:
                    players_data.append(formatted_player)
        
        return players_data if players_data else None
    
    @staticmethod
    def _format_player(player_data: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Format individual player data for frontend."""
        try:
            # Extract basic player info - handle different response formats
            name = (
                player_data.get('Player') or           # Comparison format
                player_data.get('player') or           # Display data format  
                player_data.get('extracted_name') or   # Merged name from players array
                player_data.get('name') or             # Players array format
                f'Player {index + 1}'
            )
            
            # Clean up mangled names
            if name and 'Player (' in name:
                # Extract actual name from format like "Player ('ENG-Premier League', 2425, 'Arsenal', 'Bukayo Saka')"
                import re
                match = re.search(r"'([^']+)'[^']*$", name)
                if match:
                    name = match.group(1)
            
            # Handle age - could be string "N/A" or number  
            age_raw = player_data.get('Age', player_data.get('age', 0))
            try:
                if age_raw == "N/A" or age_raw is None or pd.isna(age_raw):
                    age = 0
                else:
                    age = int(float(age_raw))
            except (ValueError, TypeError):
                age = 0
            
            # Create player object matching React TypeScript interface
            formatted_player = {
                "id": str(player_data.get('id', f'player_{index}')),
                "name": name,
                "position": player_data.get('Position', player_data.get('position', 'Unknown')),
                "age": age,
                "club": player_data.get('Team', player_data.get('team', player_data.get('Squad', player_data.get('club', 'Unknown')))),
                "league": player_data.get('League', player_data.get('league', player_data.get('Comp', 'Unknown'))),
                "nationality": player_data.get('Nation', player_data.get('nationality', 'Unknown')),
                "stats": FrontendResponseAdapter._format_player_stats(player_data)
            }
            
            return formatted_player
            
        except Exception as e:
            logger.warning(f"Failed to format player data: {e}")
            return None
    
    @staticmethod
    def _format_player_stats(player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format player statistics for frontend."""
        
        def safe_float(value, default=0.0):
            """Safely convert value to float."""
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        def safe_int(value, default=0):
            """Safely convert value to int.""" 
            try:
                if value is None or value == '':
                    return default
                return int(float(value))  # Convert through float first for decimal strings
            except (ValueError, TypeError):
                return default
        
        return {
            "goals": safe_int(player_data.get('Goals', player_data.get('goals', player_data.get('Gls', 0)))),
            "assists": safe_int(player_data.get('Assists', player_data.get('assists', player_data.get('Ast', 0)))),
            "matches_played": safe_int(player_data.get('Matches', player_data.get('matches_played', player_data.get('MP', 0)))),
            "minutes_played": safe_int(player_data.get('Minutes', player_data.get('minutes_played', player_data.get('minutes', player_data.get('Min', 0))))),
            "goals_per_90": safe_float(player_data.get('Goals_per_90', player_data.get('goals_per_90', player_data.get('Gls/90', 0)))),
            "assists_per_90": safe_float(player_data.get('Assists_per_90', player_data.get('assists_per_90', player_data.get('Ast/90', 0)))),
            "xg": safe_float(player_data.get('xG', player_data.get('xg', player_data.get('expected_goals', player_data.get('Expected_Goals', 0))))),
            "xa": safe_float(player_data.get('xA', player_data.get('xa', player_data.get('expected_assists', player_data.get('Expected_Assists', 0))))),
            "progressive_passes": safe_int(player_data.get('Progressive_Passes', player_data.get('progressive_passes', player_data.get('PrgP', 0)))),
            "progressive_carries": safe_int(player_data.get('Progressive_Carries', player_data.get('progressive_carries', player_data.get('PrgC', 0)))),
            "potential_score": safe_float(player_data.get('potential_score', player_data.get('Potential_Score')))
        }
    
    @staticmethod
    def _extract_tactical_analysis(internal_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract tactical analysis data for frontend."""
        
        # Check for tactical analysis data
        tactical_data = (
            internal_response.get('tactical_data') or
            internal_response.get('analysis') or
            internal_response.get('scout_report')
        )
        
        if not tactical_data:
            # Create basic analysis from available data
            if internal_response.get('type') == 'tactical_analysis':
                return {
                    "summary": internal_response.get('summary', 'Tactical analysis completed'),
                    "reasoning": internal_response.get('reasoning', 'Analysis based on player statistics and position requirements'),
                    "alternatives": [],
                    "tactical_fit": internal_response.get('tactical_fit', 'Good tactical compatibility')
                }
            return None
        
        return {
            "summary": tactical_data.get('summary', 'Tactical analysis completed'),
            "reasoning": tactical_data.get('reasoning', tactical_data.get('explanation', 'Analysis based on tactical requirements')),
            "alternatives": FrontendResponseAdapter._extract_players(tactical_data) or [],
            "tactical_fit": tactical_data.get('tactical_fit', tactical_data.get('compatibility', 'Good tactical fit'))
        }
    
    @staticmethod
    def adapt_suggestions_response(internal_response: Dict[str, Any]) -> List[str]:
        """Adapt suggestions response for frontend."""
        try:
            suggestions = internal_response.get('suggestions', [])
            if isinstance(suggestions, list):
                return suggestions
            return []
        except Exception as e:
            logger.error(f"Failed to adapt suggestions: {e}")
            return []
    
    @staticmethod
    def adapt_error_response(error_message: str, original_query: str = "") -> Dict[str, Any]:
        """Create error response in frontend format."""
        return {
            "response_text": f"❌ {error_message}",
            "query_type": "search",
            "error": error_message,
            "original_query": original_query
        }

# Convenience function for easy usage
def adapt_for_frontend(internal_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to adapt any internal response for frontend consumption.
    
    Args:
        internal_response: Response from internal API
        
    Returns:
        Response formatted for React frontend
    """
    return FrontendResponseAdapter.adapt_query_response(internal_response)