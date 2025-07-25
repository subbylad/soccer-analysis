"""
Response Formatter - Convert Analysis Results to User-Friendly Format

Takes structured analysis responses and formats them for display
in various UI contexts (chat, dashboard, etc.)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from .types import *

class ResponseFormatter:
    """Formats analysis responses for different UI contexts."""
    
    def __init__(self):
        self.ui_context = "chat"  # Default context
    
    def format_response(self, response: AnalysisResponse, context: str = "chat") -> Dict[str, Any]:
        """Format response based on UI context."""
        self.ui_context = context
        
        formatter_map = {
            ResponseType.PLAYER_LIST: self._format_player_list,
            ResponseType.COMPARISON_TABLE: self._format_comparison,
            ResponseType.ERROR: self._format_error
        }
        
        formatter = formatter_map.get(response.response_type)
        if not formatter:
            return self._format_generic(response)
        
        return formatter(response)
    
    def _format_player_list(self, response: PlayerListResponse) -> Dict[str, Any]:
        """Format player list responses."""
        formatted = {
            "type": "player_list",
            "success": response.success,
            "summary": response.summary,
            "total_found": response.total_found,
            "execution_time": response.execution_time,
            "players": [],
            "display_data": None
        }
        
        # Format individual players
        for idx, (player_idx, player) in enumerate(response.players.iterrows()):
            if hasattr(player, 'name') and len(player.name) >= 4:
                # MultiIndex case
                player_name = player.name[3]
                team_name = player.name[2] 
                league_name = player.name[0]
            elif 'player' in response.players.columns:
                # Regular DataFrame case
                player_name = player.get('player', 'Unknown')
                team_name = player.get('team', 'Unknown')
                league_name = player.get('league', 'Unknown')
            else:
                # Fallback
                player_name = f"Player {idx + 1}"
                team_name = "Unknown Team"
                league_name = "Unknown League"
            
            player_card = {
                "name": player_name,
                "team": team_name,
                "league": league_name,
                "position": player.get('position', 'N/A'),
                "age": player.get('age', 'N/A'),
                "minutes": player.get('minutes', 0),
                "goals": player.get('goals', 0),
                "assists": player.get('assists', 0),
                "goals_per_90": player.get('goals_per_90', 0),
                "assists_per_90": player.get('assists_per_90', 0),
                "nationality": player.get('nationality', 'N/A'),
                "expected_goals": player.get('expected_goals', 0),
                "expected_assists": player.get('expected_assists', 0)
            }
            
            formatted["players"].append(player_card)
        
        # Create display table for UI
        if not response.players.empty:
            display_columns = ['player', 'team', 'league', 'position', 'age', 'goals', 'assists', 'minutes']
            available_columns = [col for col in display_columns if col in response.players.columns]
            
            if available_columns:
                formatted["display_data"] = response.players[available_columns].to_dict('records')
            else:
                # Create display data from player cards
                formatted["display_data"] = [
                    {
                        'Player': p['name'],
                        'Team': p['team'],
                        'League': p['league'],
                        'Position': p['position'],
                        'Age': p['age'],
                        'Goals': p['goals'],
                        'Assists': p['assists'],
                        'Minutes': p['minutes']
                    }
                    for p in formatted["players"]
                ]
        
        # Generate chat-friendly text
        if self.ui_context == "chat":
            formatted["chat_text"] = self._generate_player_list_chat_text(formatted)
        
        return formatted
    
    def _format_comparison(self, response: ComparisonResponse) -> Dict[str, Any]:
        """Format player comparison responses."""
        formatted = {
            "type": "comparison",
            "success": response.success,
            "execution_time": response.execution_time,
            "comparison_table": response.comparison_table.to_dict('records'),
            "chart_data": response.chart_data,
            "insights": response.insights,
            "player_cards": response.player_cards,
            "summary": f"Comparison of {len(response.player_cards)} players"
        }
        
        # Generate chat-friendly text
        if self.ui_context == "chat":
            formatted["chat_text"] = self._generate_comparison_chat_text(formatted)
        
        return formatted
    
    def _format_error(self, response: ErrorResponse) -> Dict[str, Any]:
        """Format error responses."""
        formatted = {
            "type": "error",
            "success": False,
            "error_message": response.error_message,
            "suggestions": response.suggestions,
            "help_text": response.help_text,
            "execution_time": response.execution_time
        }
        
        # Generate chat-friendly text
        if self.ui_context == "chat":
            formatted["chat_text"] = self._generate_error_chat_text(formatted)
        
        return formatted
    
    def _format_generic(self, response: AnalysisResponse) -> Dict[str, Any]:
        """Generic formatter for unspecified response types."""
        return {
            "type": "generic",
            "success": response.success,
            "response_type": response.response_type.value,
            "execution_time": response.execution_time,
            "raw_response": str(response)
        }
    
    def _generate_player_list_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Generate chat-friendly text for player lists."""
        text_parts = []
        
        # Summary
        text_parts.append(f"✅ {formatted_data['summary']}")
        text_parts.append("")
        
        # Player cards
        for i, player in enumerate(formatted_data['players'][:5], 1):  # Show max 5 in chat
            total_ga = player['goals'] + player['assists']
            
            text_parts.append(f"**{i}. {player['name']}** - {player['team']} ({player['league']})")
            text_parts.append(f"   📍 {player['position']} | Age {player['age']} | {player['nationality']}")
            text_parts.append(f"   ⚽ {player['goals']} goals ({player['goals_per_90']:.2f}/90) | 🎯 {player['assists']} assists ({player['assists_per_90']:.2f}/90)")
            text_parts.append(f"   🏃 {player['minutes']:,} minutes | G+A: {total_ga}")
            text_parts.append("")
        
        # Show remaining count if applicable
        if len(formatted_data['players']) > 5:
            remaining = len(formatted_data['players']) - 5
            text_parts.append(f"... and {remaining} more players")
        
        return "\\n".join(text_parts)
    
    def _generate_comparison_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Generate chat-friendly text for comparisons."""
        text_parts = []
        
        # Summary
        text_parts.append(f"📊 **{formatted_data['summary']}**")
        text_parts.append("")
        
        # Quick comparison
        if formatted_data['comparison_table']:
            for player_data in formatted_data['comparison_table']:
                text_parts.append(f"**{player_data['Player']}** ({player_data['Team']})")
                text_parts.append(f"   ⚽ {player_data['Goals']} goals | 🎯 {player_data['Assists']} assists")
                text_parts.append(f"   📊 {player_data['Goals/90']:.2f} G/90 | {player_data['Assists/90']:.2f} A/90")
                text_parts.append("")
        
        # Insights
        if formatted_data['insights']:
            text_parts.append("**🔍 Key Insights:**")
            for insight in formatted_data['insights']:
                text_parts.append(f"• {insight}")
        
        return "\\n".join(text_parts)
    
    def _generate_error_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Generate chat-friendly text for errors."""
        text_parts = []
        
        text_parts.append(f"❌ {formatted_data['error_message']}")
        text_parts.append("")
        
        if formatted_data['suggestions']:
            text_parts.append("💡 **Try these instead:**")
            for suggestion in formatted_data['suggestions']:
                text_parts.append(f"• {suggestion}")
        
        if formatted_data['help_text']:
            text_parts.append("")
            text_parts.append(formatted_data['help_text'])
        
        return "\\n".join(text_parts)
    
    def format_for_streamlit(self, response: AnalysisResponse) -> Dict[str, Any]:
        """Format specifically for Streamlit display."""
        formatted = self.format_response(response, context="streamlit")
        
        # Add Streamlit-specific formatting
        if response.response_type == ResponseType.PLAYER_LIST:
            formatted["streamlit_components"] = self._create_streamlit_player_components(formatted)
        elif response.response_type == ResponseType.COMPARISON_TABLE:
            formatted["streamlit_components"] = self._create_streamlit_comparison_components(formatted)
        
        return formatted
    
    def _create_streamlit_player_components(self, formatted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Streamlit-specific components for player lists."""
        components = {
            "success_message": formatted_data['summary'],
            "player_cards": [],
            "dataframe": formatted_data.get('display_data', []),
            "metrics": {
                "total_players": formatted_data['total_found'],
                "execution_time": f"{formatted_data['execution_time']:.2f}s"
            }
        }
        
        # Format player cards for Streamlit
        for player in formatted_data['players']:
            card_html = f"""
            <div style="border: 2px solid #1f77b4; border-radius: 10px; padding: 15px; margin: 10px 0; background: linear-gradient(135deg, #f8f9fa, #e3f2fd);">
                <h4 style="color: #1f77b4; margin-bottom: 5px;">⚽ {player['name']}</h4>
                <p><strong>Team:</strong> {player['team']} ({player['league']})</p>
                <p><strong>Position:</strong> {player['position']} | <strong>Age:</strong> {player['age']} | <strong>Nationality:</strong> {player['nationality']}</p>
                <p><strong>Goals:</strong> {player['goals']} ({player['goals_per_90']:.2f}/90) | <strong>Assists:</strong> {player['assists']} ({player['assists_per_90']:.2f}/90)</p>
                <p><strong>Minutes:</strong> {player['minutes']:,} | <strong>xG:</strong> {player['expected_goals']:.1f} | <strong>xA:</strong> {player['expected_assists']:.1f}</p>
            </div>
            """
            components["player_cards"].append(card_html)
        
        return components
    
    def _create_streamlit_comparison_components(self, formatted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Streamlit-specific components for comparisons."""
        components = {
            "summary": formatted_data['summary'],
            "comparison_dataframe": formatted_data['comparison_table'],
            "chart_data": formatted_data['chart_data'],
            "insights": formatted_data['insights'],
            "player_cards": formatted_data['player_cards']
        }
        
        return components
    
    def create_chart_config(self, chart_data: Dict[str, Any], chart_type: str = "scatter") -> Dict[str, Any]:
        """Create chart configuration for visualization libraries."""
        if chart_type == "scatter":
            return {
                "type": "scatter",
                "data": {
                    "x": chart_data.get('goals_per_90', []),
                    "y": chart_data.get('assists_per_90', []),
                    "labels": chart_data.get('players', []),
                    "hover_data": {
                        "Goals": chart_data.get('total_goals', []),
                        "Assists": chart_data.get('total_assists', [])
                    }
                },
                "layout": {
                    "title": "Goals vs Assists per 90 minutes",
                    "xaxis_title": "Goals per 90 min",
                    "yaxis_title": "Assists per 90 min",
                    "height": 500
                }
            }
        
        return {"type": "unknown", "data": chart_data}
    
    def create_summary_stats(self, response: AnalysisResponse) -> Dict[str, Any]:
        """Create summary statistics for any response."""
        stats = {
            "execution_time": f"{response.execution_time:.2f}s",
            "success": response.success,
            "query_type": response.original_request.query_type.value
        }
        
        if hasattr(response, 'total_found'):
            stats["total_results"] = response.total_found
        
        if hasattr(response, 'players') and not response.players.empty:
            stats["data_points"] = len(response.players)
        
        return stats