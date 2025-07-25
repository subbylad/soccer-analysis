"""
Response Formatter - Convert Analysis Results to User-Friendly Format

Takes structured analysis responses and formats them for display
in various UI contexts (chat, dashboard, etc.)
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from .types import *

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats analysis responses for different UI contexts."""
    
    def format_response(self, response: AnalysisResponse) -> Dict[str, Any]:
        """Main entry point for formatting responses."""
        
        # Map response types to formatters
        formatters = {
            ResponseType.PLAYER_LIST: self._format_player_list,
            ResponseType.COMPARISON_TABLE: self._format_comparison,
            ResponseType.ERROR: self._format_error
        }
        
        formatter = formatters.get(response.response_type, self._format_generic)
        return formatter(response)
    
    def _format_player_list(self, response) -> Dict[str, Any]:
        """Format player list responses."""
        
        # Get the data - handle different response types
        data_df = pd.DataFrame()
        summary = "Analysis completed"
        total_found = 0
        
        try:
            # Handle ProspectsResponse
            if hasattr(response, 'prospects') and isinstance(response.prospects, pd.DataFrame):
                data_df = response.prospects
                summary = f"Found {len(data_df)} young prospects"
                total_found = len(data_df)
            
            # Handle PlayerListResponse  
            elif hasattr(response, 'players') and isinstance(response.players, pd.DataFrame):
                data_df = response.players
                summary = getattr(response, 'summary', f"Found {len(data_df)} players")
                total_found = getattr(response, 'total_found', len(data_df))
            
            # Handle empty case
            else:
                summary = "No players found"
                total_found = 0
                
        except Exception as e:
            logger.error(f"Error extracting data from response: {e}")
            summary = "Error processing results"
            total_found = 0
        
        formatted = {
            "type": "player_list",
            "success": response.success,
            "summary": summary,
            "total_found": total_found,
            "execution_time": getattr(response, 'execution_time', 0),
            "players": [],
            "display_data": None
        }
        
        # Process players if we have data
        if not data_df.empty:
            try:
                # Convert to simple records format for display
                formatted["display_data"] = data_df.head(20).to_dict('records')
                
                # Create player cards for chat display
                for idx, row in data_df.head(10).iterrows():
                    try:
                        player_card = {
                            "name": str(row.get('player', f'Player {idx}')),
                            "team": str(row.get('team', 'Unknown')),
                            "league": str(row.get('league', 'Unknown')),
                            "position": str(row.get('position', 'N/A')),
                            "age": int(row.get('age', 0)) if pd.notna(row.get('age')) else 0,
                            "minutes": int(row.get('minutes', 0)) if pd.notna(row.get('minutes')) else 0,
                            "goals": float(row.get('goals', 0)) if pd.notna(row.get('goals')) else 0,
                            "assists": float(row.get('assists', 0)) if pd.notna(row.get('assists')) else 0
                        }
                        formatted["players"].append(player_card)
                    except Exception as e:
                        logger.warning(f"Error processing player {idx}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing player data: {e}")
        
        # Create chat text
        formatted["chat_text"] = self._create_chat_text(formatted)
        
        return formatted
    
    def _format_comparison(self, response) -> Dict[str, Any]:
        """Format comparison responses."""
        formatted = {
            "type": "comparison",
            "success": response.success,
            "summary": f"Comparison of players",
            "execution_time": getattr(response, 'execution_time', 0),
            "comparison_data": None,
            "insights": []
        }
        
        try:
            if hasattr(response, 'comparison_table') and isinstance(response.comparison_table, pd.DataFrame):
                formatted["comparison_data"] = response.comparison_table.to_dict('records')
                formatted["summary"] = f"Comparison of {len(response.comparison_table)} players"
            
            if hasattr(response, 'insights'):
                formatted["insights"] = response.insights
                
        except Exception as e:
            logger.error(f"Error formatting comparison: {e}")
        
        formatted["chat_text"] = self._create_comparison_chat_text(formatted)
        return formatted
    
    def _format_error(self, response) -> Dict[str, Any]:
        """Format error responses."""
        return {
            "type": "error",
            "success": False,
            "error_message": getattr(response, 'error_message', 'Unknown error'),
            "suggestions": getattr(response, 'suggestions', []),
            "execution_time": getattr(response, 'execution_time', 0),
            "chat_text": f"❌ {getattr(response, 'error_message', 'An error occurred')}"
        }
    
    def _format_generic(self, response) -> Dict[str, Any]:
        """Generic formatter for unknown response types."""
        return {
            "type": "generic",
            "success": response.success,
            "summary": "Analysis completed",
            "execution_time": getattr(response, 'execution_time', 0),
            "chat_text": "✅ Analysis completed successfully" if response.success else "❌ Analysis failed"
        }
    
    def _create_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Create chat-friendly text from formatted data."""
        
        if not formatted_data.get('success', False):
            return f"❌ {formatted_data.get('error_message', 'Analysis failed')}"
        
        summary = formatted_data.get('summary', 'Analysis completed')
        players = formatted_data.get('players', [])
        
        if not players:
            return f"✅ {summary}\n\nNo players found matching your criteria."
        
        # Create a nice text summary
        text_parts = [f"✅ {summary}\n"]
        
        # Add top players
        text_parts.append("🌟 **Top Players:**")
        for i, player in enumerate(players[:5], 1):
            name = player.get('name', 'Unknown')
            team = player.get('team', 'Unknown')
            age = player.get('age', 'N/A')
            position = player.get('position', 'N/A')
            
            text_parts.append(f"{i}. **{name}** ({team}) - {position}, Age {age}")
        
        if len(players) > 5:
            text_parts.append(f"\n... and {len(players) - 5} more players")
        
        return "\n".join(text_parts)
    
    def _create_comparison_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Create chat text for comparisons."""
        summary = formatted_data.get('summary', 'Player comparison')
        insights = formatted_data.get('insights', [])
        
        text_parts = [f"✅ {summary}\n"]
        
        if insights:
            text_parts.append("📊 **Key Insights:**")
            for insight in insights[:3]:
                text_parts.append(f"• {insight}")
        
        return "\n".join(text_parts)