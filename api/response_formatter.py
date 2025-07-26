"""
Response Formatter - Convert Analysis Results to User-Friendly Format

Takes structured analysis responses and formats them for display
in various UI contexts (chat, dashboard, etc.)
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from .types import *
import textwrap

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
        
        # Handle GPT4AnalysisResponse specifically
        if isinstance(response, GPT4AnalysisResponse):
            return self._format_gpt4_analysis(response)
        
        formatter = formatters.get(response.response_type, self._format_generic)
        return formatter(response)
    
    def _format_player_list(self, response) -> Dict[str, Any]:
        """Format player list responses."""
        
        # Check if this is a tactical analysis response
        if (hasattr(response, 'original_request') and 
            response.original_request and 
            hasattr(response.original_request, 'query_type') and
            response.original_request.query_type == QueryType.TACTICAL_ANALYSIS):
            return self._format_tactical_analysis(response)
        
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
                        # Extract team and league from index if available
                        team = str(row.get('team', 'Unknown'))
                        league = str(row.get('league', 'Unknown'))
                        player_name = str(row.get('player', f'Player {idx}'))
                        
                        # If data comes from MultiIndex DataFrame, extract from index
                        if hasattr(idx, '__getitem__') and len(idx) >= 4:
                            league = str(idx[0]) if idx[0] else league
                            team = str(idx[2]) if idx[2] else team
                            player_name = str(idx[3]) if idx[3] else player_name
                        elif isinstance(idx, tuple) and len(idx) >= 4:
                            league = str(idx[0]) if idx[0] else league
                            team = str(idx[2]) if idx[2] else team
                            player_name = str(idx[3]) if idx[3] else player_name
                        
                        player_card = {
                            "name": player_name,
                            "team": team,
                            "league": league,
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
    
    def _format_gpt4_analysis(self, response: GPT4AnalysisResponse) -> Dict[str, Any]:
        """Format GPT-4 analysis responses."""
        formatted = {
            "type": "gpt4_analysis",
            "success": response.success,
            "summary": response.summary or "GPT-4 Analysis completed",
            "execution_time": getattr(response, 'execution_time', 0),
            "generated_code": response.generated_code,
            "insights": response.insights,
            "result": None,
            "display_data": None,
            "players": []
        }
        
        # Handle different result types
        result = response.result
        if isinstance(result, pd.DataFrame):
            # Convert DataFrame to display format
            try:
                # Reset index if it's a MultiIndex
                if isinstance(result.index, pd.MultiIndex):
                    display_df = result.reset_index()
                else:
                    display_df = result
                
                formatted["display_data"] = display_df.head(20).to_dict('records')
                formatted["total_found"] = len(display_df)
                
                # Create player cards for chat display if it's player data
                if 'player' in display_df.columns or any('player' in str(col).lower() for col in display_df.columns):
                    for idx, row in display_df.head(10).iterrows():
                        try:
                            player_card = {
                                "name": str(row.get('player', row.get('Player', f'Player {idx}'))),
                                "team": str(row.get('team', row.get('Team', 'Unknown'))),
                                "league": str(row.get('league', row.get('League', 'Unknown'))),
                                "position": str(row.get('position', row.get('Position', 'N/A'))),
                                "age": int(row.get('age', row.get('Age', 0))) if pd.notna(row.get('age', row.get('Age', 0))) else 0,
                                "minutes": int(row.get('minutes', row.get('Minutes', 0))) if pd.notna(row.get('minutes', row.get('Minutes', 0))) else 0,
                                "goals": float(row.get('goals', row.get('Goals', 0))) if pd.notna(row.get('goals', row.get('Goals', 0))) else 0,
                                "assists": float(row.get('assists', row.get('Assists', 0))) if pd.notna(row.get('assists', row.get('Assists', 0))) else 0
                            }
                            formatted["players"].append(player_card)
                        except Exception as e:
                            logger.warning(f"Error processing player {idx}: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error processing DataFrame result: {e}")
                formatted["result"] = str(result)
        else:
            # For non-DataFrame results
            formatted["result"] = result
            formatted["total_found"] = 1 if result else 0
        
        # Create chat text
        formatted["chat_text"] = self._create_gpt4_chat_text(formatted)
        
        return formatted
    
    def _create_gpt4_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Create chat text for GPT-4 analysis results."""
        if not formatted_data.get('success', False):
            return f"❌ GPT-4 Analysis failed: {formatted_data.get('error_message', 'Unknown error')}"
        
        summary = formatted_data.get('summary', 'GPT-4 Analysis completed')
        insights = formatted_data.get('insights', [])
        players = formatted_data.get('players', [])
        
        text_parts = [f"🤖 **GPT-4 Analysis:** {summary}\n"]
        
        # Add insights if available
        if insights:
            text_parts.append("🧠 **AI Insights:**")
            for insight in insights[:3]:  # Limit to top 3 insights
                text_parts.append(f"• {insight}")
            text_parts.append("")
        
        # Add player results if available
        if players:
            text_parts.append("🌟 **Top Results:**")
            for i, player in enumerate(players[:5], 1):
                name = player.get('name', 'Unknown')
                team = player.get('team', 'Unknown')
                age = player.get('age', 'N/A')
                position = player.get('position', 'N/A')
                text_parts.append(f"{i}. **{name}** ({team}) - {position}, Age {age}")
            
            if len(players) > 5:
                text_parts.append(f"\n... and {len(players) - 5} more results")
        
        # Add code info
        if formatted_data.get('generated_code'):
            text_parts.append(f"\n🔧 *Powered by AI-generated Python analysis*")
        
        return "\n".join(text_parts)
    
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
    
    def _format_tactical_analysis(self, response) -> Dict[str, Any]:
        """Format tactical analysis responses with rich scout-style presentation."""
        
        # Get the tactical request for context
        request = response.original_request
        data_df = response.players if hasattr(response, 'players') else pd.DataFrame()
        
        formatted = {
            "type": "tactical_analysis",
            "success": response.success,
            "summary": getattr(response, 'summary', 'Tactical analysis completed'),
            "total_found": getattr(response, 'total_found', len(data_df)),
            "execution_time": getattr(response, 'execution_time', 0),
            "tactical_data": {
                "target_player": getattr(request, 'target_player', None),
                "tactical_context": getattr(request, 'tactical_context', ''),
                "reasoning": getattr(request, 'reasoning', ''),
                "priority_stats": getattr(request, 'priority_stats', []),
                "position": getattr(request, 'position', None),
                "league": getattr(request, 'league', None)
            },
            "scout_report": {},
            "candidates": [],
            "display_data": None
        }
        
        # Process tactical candidates if we have data
        if not data_df.empty:
            try:
                # Convert to display format
                formatted["display_data"] = data_df.head(20).to_dict('records')
                
                # Create detailed candidate analysis
                for idx, row in data_df.head(10).iterrows():
                    try:
                        candidate = {
                            "rank": idx + 1,
                            "name": str(row.get('player', f'Player {idx}')),
                            "team": str(row.get('team', 'Unknown')),
                            "league": str(row.get('league', 'Unknown')),
                            "position": str(row.get('position', 'N/A')),
                            "age": int(row.get('age', 0)) if pd.notna(row.get('age')) else 0,
                            "minutes": int(row.get('minutes', 0)) if pd.notna(row.get('minutes')) else 0,
                            "tactical_score": float(row.get('tactical_score', 0)) if pd.notna(row.get('tactical_score')) else None,
                            "key_stats": self._extract_key_stats(row, request.priority_stats),
                            "scout_notes": self._generate_scout_notes(row, request)
                        }
                        formatted["candidates"].append(candidate)
                    except Exception as e:
                        logger.warning(f"Error processing candidate {idx}: {e}")
                        continue
                
                # Generate comprehensive scout report
                formatted["scout_report"] = self._generate_scout_report(
                    data_df, request, formatted["candidates"]
                )
                        
            except Exception as e:
                logger.error(f"Error processing tactical analysis data: {e}")
        
        # Create rich tactical chat text
        formatted["chat_text"] = self._create_tactical_chat_text(formatted)
        
        return formatted
    
    def _extract_key_stats(self, player_row, priority_stats: List[str]) -> Dict[str, Any]:
        """Extract key statistics for tactical analysis display."""
        key_stats = {}
        
        # Always include basic stats
        basic_stats = ['goals', 'assists', 'goals_per_90', 'assists_per_90', 'minutes']
        for stat in basic_stats:
            if stat in player_row and pd.notna(player_row[stat]):
                key_stats[stat] = float(player_row[stat]) if isinstance(player_row[stat], (int, float)) else player_row[stat]
        
        # Add priority stats if they exist
        for stat in priority_stats:
            if stat in player_row and pd.notna(player_row[stat]):
                key_stats[stat] = float(player_row[stat]) if isinstance(player_row[stat], (int, float)) else player_row[stat]
        
        return key_stats
    
    def _generate_scout_notes(self, player_row, request: TacticalAnalysisRequest) -> List[str]:
        """Generate tactical scout notes for individual players."""
        notes = []
        
        # Age assessment
        age = player_row.get('age')
        if pd.notna(age) and age:
            if age <= 21:
                notes.append(f"🌟 Young prospect at {int(age)} - high development potential")
            elif age <= 25:
                notes.append(f"💪 Prime development age ({int(age)}) - entering peak years")
            elif age <= 29:
                notes.append(f"⭐ Experienced player ({int(age)}) - proven at top level")
            else:
                notes.append(f"🧠 Veteran presence ({int(age)}) - leadership qualities")
        
        # Playing time assessment
        minutes = player_row.get('minutes', 0)
        if minutes >= 2500:
            notes.append("🎯 Key player - regular starter with high minutes")
        elif minutes >= 1800:
            notes.append("📋 Important squad member - consistent playing time")
        elif minutes >= 1000:
            notes.append("🔄 Rotation player - valuable squad depth")
        else:
            notes.append("⚠️ Limited playing time - requires further assessment")
        
        # Performance indicators based on priority stats
        if request.priority_stats:
            strong_areas = []
            for stat in request.priority_stats[:3]:  # Check top 3 priority stats
                if stat in player_row and pd.notna(player_row[stat]):
                    value = player_row[stat]
                    if isinstance(value, (int, float)) and value > 0:
                        if 'per_90' in stat:
                            if value >= 0.5:  # Strong per 90 performance
                                strong_areas.append(stat.replace('_per_90', '').replace('_', ' ').title())
                        elif stat in ['goals', 'assists']:
                            if value >= 5:  # Good total output
                                strong_areas.append(stat.replace('_', ' ').title())
            
            if strong_areas:
                notes.append(f"⚡ Strong in: {', '.join(strong_areas)}")
        
        # Tactical score insight
        tactical_score = player_row.get('tactical_score')
        if pd.notna(tactical_score) and tactical_score:
            if tactical_score >= 0.8:
                notes.append("🏆 Excellent tactical fit - top recommendation")
            elif tactical_score >= 0.6:
                notes.append("✅ Good tactical match - strong candidate")
            elif tactical_score >= 0.4:
                notes.append("🤔 Moderate fit - requires deeper analysis")
            else:
                notes.append("📊 Lower tactical score - consider alternatives")
        
        return notes[:4]  # Limit to 4 most important notes
    
    def _generate_scout_report(self, candidates_df: pd.DataFrame, 
                              request: TacticalAnalysisRequest, 
                              processed_candidates: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive scout report with tactical insights."""
        
        scout_report = {
            "executive_summary": "",
            "target_analysis": "",
            "top_recommendations": [],
            "market_overview": {},
            "tactical_insights": [],
            "risk_assessment": {}
        }
        
        # Executive Summary
        target_player = request.target_player or "the specified role"
        position = request.position or "the target position"
        league = request.league or "available leagues"
        
        summary_parts = [
            f"📋 **SCOUT REPORT: Tactical Analysis for {target_player}**",
            f"**Position Focus:** {position}",
            f"**Market:** {league}",
            f"**Candidates Identified:** {len(candidates_df)}"
        ]
        
        if request.reasoning:
            summary_parts.append(f"**AI Analysis:** {request.reasoning[:200]}{'...' if len(request.reasoning) > 200 else ''}")
        
        scout_report["executive_summary"] = "\n".join(summary_parts)
        
        # Target Analysis (based on tactical context)
        if request.tactical_context:
            scout_report["target_analysis"] = textwrap.fill(request.tactical_context, width=80)
        else:
            scout_report["target_analysis"] = f"Seeking players who can complement {target_player} in {position}."
        
        # Top Recommendations (top 3 candidates)
        for i, candidate in enumerate(processed_candidates[:3], 1):
            recommendation = {
                "rank": i,
                "player": candidate["name"],
                "team": candidate["team"],
                "league": candidate["league"],
                "age": candidate["age"],
                "assessment": self._create_player_assessment(candidate),
                "tactical_fit": candidate.get("tactical_score", 0)
            }
            scout_report["top_recommendations"].append(recommendation)
        
        # Market Overview
        if not candidates_df.empty:
            scout_report["market_overview"] = {
                "total_candidates": len(candidates_df),
                "age_distribution": self._analyze_age_distribution(candidates_df),
                "league_breakdown": self._analyze_league_distribution(candidates_df),
                "experience_levels": self._analyze_experience_levels(candidates_df)
            }
        
        # Tactical Insights
        insights = []
        
        if request.priority_stats:
            insights.append(f"🎯 **Key Metrics:** Evaluation focused on {', '.join(request.priority_stats[:3])}")
        
        if not candidates_df.empty:
            # Age insights
            if 'age' in candidates_df.columns:
                avg_age = candidates_df['age'].mean()
                young_count = len(candidates_df[candidates_df['age'] <= 23])
                insights.append(f"📊 **Age Profile:** Average {avg_age:.1f} years, {young_count} prospects under 24")
            
            # Experience insights
            if 'minutes' in candidates_df.columns:
                avg_minutes = candidates_df['minutes'].mean()
                starters = len(candidates_df[candidates_df['minutes'] >= 2000])
                insights.append(f"⏱️ **Experience:** {starters} regular starters (avg {int(avg_minutes)} minutes)")
        
        scout_report["tactical_insights"] = insights
        
        # Risk Assessment
        risk_factors = []
        opportunities = []
        
        if not candidates_df.empty:
            # Age risk assessment
            if 'age' in candidates_df.columns:
                young_prospects = len(candidates_df[candidates_df['age'] <= 21])
                if young_prospects > 0:
                    opportunities.append(f"{young_prospects} young prospects with high potential")
                
                older_players = len(candidates_df[candidates_df['age'] >= 30])
                if older_players > 0:
                    risk_factors.append(f"{older_players} players over 30 - age concerns")
            
            # Playing time assessment
            if 'minutes' in candidates_df.columns:
                limited_minutes = len(candidates_df[candidates_df['minutes'] < 1000])
                if limited_minutes > 0:
                    risk_factors.append(f"{limited_minutes} players with limited playing time")
        
        scout_report["risk_assessment"] = {
            "risk_factors": risk_factors,
            "opportunities": opportunities
        }
        
        return scout_report
    
    def _create_player_assessment(self, candidate: Dict) -> str:
        """Create detailed assessment for individual candidate."""
        assessment_parts = []
        
        # Basic profile
        age = candidate.get('age', 0)
        minutes = candidate.get('minutes', 0)
        tactical_score = candidate.get('tactical_score')
        
        # Age-based assessment
        if age <= 21:
            assessment_parts.append("Young talent with high ceiling")
        elif age <= 25:
            assessment_parts.append("Prime development phase")
        elif age <= 29:
            assessment_parts.append("Experienced performer")
        else:
            assessment_parts.append("Veteran presence")
        
        # Performance assessment
        if tactical_score and tactical_score >= 0.7:
            assessment_parts.append("excellent tactical match")
        elif tactical_score and tactical_score >= 0.5:
            assessment_parts.append("strong tactical fit")
        
        # Playing time assessment
        if minutes >= 2000:
            assessment_parts.append("proven regular starter")
        elif minutes >= 1500:
            assessment_parts.append("important squad player")
        
        # Scout notes integration
        scout_notes = candidate.get('scout_notes', [])
        if scout_notes:
            # Extract key strengths from scout notes
            for note in scout_notes[:2]:  # Take first 2 notes
                if 'Strong in:' in note:
                    strengths = note.replace('⚡ Strong in: ', '')
                    assessment_parts.append(f"excels in {strengths.lower()}")
        
        return ", ".join(assessment_parts).capitalize() + "."
    
    def _analyze_age_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze age distribution of candidates."""
        if 'age' not in df.columns:
            return {}
        
        return {
            "Under 21": len(df[df['age'] <= 21]),
            "21-25": len(df[(df['age'] > 21) & (df['age'] <= 25)]),
            "26-29": len(df[(df['age'] > 25) & (df['age'] <= 29)]),
            "30+": len(df[df['age'] > 29])
        }
    
    def _analyze_league_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze league distribution of candidates."""
        if df.empty or not hasattr(df.index, 'get_level_values'):
            return {}
        
        try:
            league_counts = df.index.get_level_values(0).value_counts()
            return dict(league_counts.head(5))  # Top 5 leagues
        except:
            return {}
    
    def _analyze_experience_levels(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze experience levels based on playing time."""
        if 'minutes' not in df.columns:
            return {}
        
        return {
            "Regular Starters (2000+ min)": len(df[df['minutes'] >= 2000]),
            "Squad Players (1000-2000 min)": len(df[(df['minutes'] >= 1000) & (df['minutes'] < 2000)]),
            "Limited Game Time (<1000 min)": len(df[df['minutes'] < 1000])
        }
    
    def _create_tactical_chat_text(self, formatted_data: Dict[str, Any]) -> str:
        """Create rich tactical analysis chat text."""
        
        if not formatted_data.get('success', False):
            return f"❌ {formatted_data.get('error_message', 'Tactical analysis failed')}"
        
        tactical_data = formatted_data.get('tactical_data', {})
        scout_report = formatted_data.get('scout_report', {})
        candidates = formatted_data.get('candidates', [])
        
        text_parts = []
        
        # Header with tactical context
        target_player = tactical_data.get('target_player', 'the target role')
        position = tactical_data.get('position', 'specified position')
        league_filter = tactical_data.get('league', '')
        
        header = f"🎯 **TACTICAL SCOUT REPORT: {target_player}**"
        if league_filter:
            header += f" (Focus: {league_filter})"
        text_parts.append(header)
        text_parts.append("")
        
        # Executive summary
        exec_summary = scout_report.get('executive_summary', '')
        if exec_summary:
            text_parts.append(exec_summary)
            text_parts.append("")
        
        # AI reasoning if available
        reasoning = tactical_data.get('reasoning', '')
        if reasoning:
            text_parts.append("🧠 **AI TACTICAL ANALYSIS:**")
            text_parts.append(f"{reasoning[:300]}{'...' if len(reasoning) > 300 else ''}")
            text_parts.append("")
        
        # Top recommendations
        if candidates:
            text_parts.append("⭐ **TOP TACTICAL MATCHES:**")
            text_parts.append("")
            
            for i, candidate in enumerate(candidates[:5], 1):
                name = candidate.get('name', 'Unknown')
                team = candidate.get('team', 'Unknown')
                age = candidate.get('age', 'N/A')
                league = candidate.get('league', 'Unknown')
                tactical_score = candidate.get('tactical_score')
                
                # Candidate header
                candidate_line = f"**{i}. {name}** ({team}, {league}) - Age {age}"
                if tactical_score:
                    fit_percentage = int(tactical_score * 100)
                    candidate_line += f" | Tactical Fit: {fit_percentage}%"
                text_parts.append(candidate_line)
                
                # Key stats
                key_stats = candidate.get('key_stats', {})
                if key_stats:
                    stats_line = "   📊 "
                    stat_displays = []
                    
                    if 'goals' in key_stats:
                        stat_displays.append(f"Goals: {key_stats['goals']}")
                    if 'assists' in key_stats:
                        stat_displays.append(f"Assists: {key_stats['assists']}")
                    if 'goals_per_90' in key_stats:
                        stat_displays.append(f"G/90: {key_stats['goals_per_90']:.2f}")
                    if 'assists_per_90' in key_stats:
                        stat_displays.append(f"A/90: {key_stats['assists_per_90']:.2f}")
                    
                    if stat_displays:
                        stats_line += " | ".join(stat_displays)
                        text_parts.append(stats_line)
                
                # Scout notes (top 2)
                scout_notes = candidate.get('scout_notes', [])
                for note in scout_notes[:2]:
                    text_parts.append(f"   {note}")
                
                text_parts.append("")  # Spacing between candidates
        
        # Market insights
        market_overview = scout_report.get('market_overview', {})
        if market_overview:
            text_parts.append("📈 **MARKET OVERVIEW:**")
            
            total_candidates = market_overview.get('total_candidates', 0)
            text_parts.append(f"• Total candidates analyzed: {total_candidates}")
            
            age_dist = market_overview.get('age_distribution', {})
            if age_dist:
                young_prospects = age_dist.get('Under 21', 0) + age_dist.get('21-25', 0)
                if young_prospects > 0:
                    text_parts.append(f"• {young_prospects} prospects under 26 identified")
            
            exp_levels = market_overview.get('experience_levels', {})
            starters = exp_levels.get('Regular Starters (2000+ min)', 0)
            if starters > 0:
                text_parts.append(f"• {starters} proven regular starters available")
            
            text_parts.append("")
        
        # Tactical insights
        tactical_insights = scout_report.get('tactical_insights', [])
        if tactical_insights:
            text_parts.append("🎯 **KEY INSIGHTS:**")
            for insight in tactical_insights:
                text_parts.append(f"• {insight}")
            text_parts.append("")
        
        # Risk assessment
        risk_assessment = scout_report.get('risk_assessment', {})
        opportunities = risk_assessment.get('opportunities', [])
        if opportunities:
            text_parts.append("✅ **OPPORTUNITIES:**")
            for opp in opportunities:
                text_parts.append(f"• {opp}")
        
        risk_factors = risk_assessment.get('risk_factors', [])
        if risk_factors:
            text_parts.append("⚠️ **CONSIDERATIONS:**")
            for risk in risk_factors:
                text_parts.append(f"• {risk}")
        
        # Footer
        if tactical_data.get('priority_stats'):
            priority_stats = tactical_data['priority_stats']
            text_parts.append(f"\n📊 *Analysis based on: {', '.join(priority_stats)}*")
        
        return "\n".join(text_parts)