"""
Analysis Router - Connect Queries to Analysis Functions

Routes structured requests to the appropriate analysis functions
and handles execution, caching, and error management.
"""

import time
import logging
from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path
import sys
import os

# Add parent directory to path to import analysis modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.clean_player_analyzer import CleanPlayerAnalyzer
from analysis.young_dm_scouting import YoungDMScout
from .types import *

logger = logging.getLogger(__name__)

class AnalysisRouter:
    """Routes analysis requests to appropriate functions."""
    
    def __init__(self, data_dir: str = "data/clean"):
        """Initialize with analysis components."""
        try:
            self.analyzer = CleanPlayerAnalyzer(data_dir=data_dir)
            self.young_scout = YoungDMScout(data_dir=data_dir)
            self.cache = {}  # Simple in-memory cache
            logger.info("Analysis router initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analysis router: {e}")
            raise
    
    def execute_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute analysis based on request type."""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                logger.info(f"Cache hit for {request.query_type}")
                cached_response = self.cache[cache_key]
                cached_response.execution_time = time.time() - start_time
                return cached_response
            
            # Route to appropriate handler
            handler_map = {
                QueryType.PLAYER_SEARCH: self._handle_player_search,
                QueryType.PLAYER_COMPARISON: self._handle_player_comparison,
                QueryType.YOUNG_PROSPECTS: self._handle_young_prospects,
                QueryType.TOP_PERFORMERS: self._handle_top_performers,
                QueryType.CUSTOM_FILTER: self._handle_custom_filter,
                QueryType.TACTICAL_ANALYSIS: self._handle_tactical_analysis,
                QueryType.UNKNOWN: self._handle_unknown
            }
            
            handler = handler_map.get(request.query_type)
            if not handler:
                return self._create_error_response(
                    request, f"No handler for query type: {request.query_type}"
                )
            
            # Execute analysis
            response = handler(request)
            response.execution_time = time.time() - start_time
            
            # Cache successful responses
            if response.success:
                self.cache[cache_key] = response
            
            logger.info(f"Analysis completed in {response.execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            error_response = self._create_error_response(request, str(e))
            error_response.execution_time = time.time() - start_time
            return error_response
    
    def _handle_player_search(self, request: PlayerSearchRequest) -> AnalysisResponse:
        """Handle player search requests."""
        try:
            results = self.analyzer.search_players(
                name_pattern=request.player_name,
                min_minutes=request.min_minutes,
                position=request.position
            )
            
            # Apply league filter if specified
            if request.league and not results.empty:
                league_mask = [idx[0] == request.league for idx in results.index]
                results = results[league_mask]
            
            if results.empty:
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message=f"No players found matching '{request.player_name}'",
                    suggestions=[
                        f"Try reducing minimum minutes (currently {request.min_minutes})",
                        "Check the spelling of the player name",
                        "Try searching for just the last name"
                    ]
                )
            
            summary = f"Found {len(results)} player(s) matching '{request.player_name}'"
            if request.position:
                summary += f" playing as {request.position}"
            if request.league:
                summary += f" in {request.league}"
            
            return PlayerListResponse(
                success=True,
                original_request=request,
                players=results,
                total_found=len(results),
                summary=summary
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Player search failed: {e}")
    
    def _handle_player_comparison(self, request: PlayerComparisonRequest) -> AnalysisResponse:
        """Handle player comparison requests."""
        try:
            # Search for each player
            found_players = []
            for player_name in request.player_names:
                player_results = self.analyzer.search_players(
                    name_pattern=player_name,
                    min_minutes=request.min_minutes
                )
                if not player_results.empty:
                    # Take the first match (most relevant)
                    found_players.append((player_name, player_results.iloc[0]))
                else:
                    logger.warning(f"Player not found: {player_name}")
            
            if len(found_players) < 2:
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message=f"Could not find enough players to compare. Found: {[p[0] for p in found_players]}",
                    suggestions=[
                        "Check player name spellings",
                        "Try using last names only",
                        f"Reduce minimum minutes from {request.min_minutes}"
                    ]
                )
            
            # Create comparison data
            comparison_data = []
            player_cards = []
            
            for player_name, player_data in found_players:
                # Extract player info from MultiIndex
                player_idx = player_data.name
                
                comparison_row = {
                    'Player': player_idx[3],  # player name
                    'Team': player_idx[2],    # team
                    'League': player_idx[0],  # league
                    'Position': player_data.get('position', 'N/A'),
                    'Age': player_data.get('age', 'N/A'),
                    'Minutes': player_data.get('minutes', 0),
                    'Goals': player_data.get('goals', 0),
                    'Assists': player_data.get('assists', 0),
                    'Goals/90': player_data.get('goals_per_90', 0),
                    'Assists/90': player_data.get('assists_per_90', 0),
                }
                
                for stat in request.comparison_stats:
                    if stat in player_data:
                        comparison_row[stat] = player_data[stat]
                
                comparison_data.append(comparison_row)
                
                # Create player card
                player_cards.append({
                    'name': player_idx[3],
                    'team': player_idx[2],
                    'league': player_idx[0],
                    'stats': dict(player_data)
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Generate insights
            insights = self._generate_comparison_insights(comparison_df)
            
            # Create chart data
            chart_data = {
                'players': [row['Player'] for row in comparison_data],
                'goals_per_90': [row['Goals/90'] for row in comparison_data],
                'assists_per_90': [row['Assists/90'] for row in comparison_data],
                'total_goals': [row['Goals'] for row in comparison_data],
                'total_assists': [row['Assists'] for row in comparison_data]
            }
            
            return ComparisonResponse(
                success=True,
                original_request=request,
                comparison_table=comparison_df,
                chart_data=chart_data,
                insights=insights,
                player_cards=player_cards
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Player comparison failed: {e}")
    
    def _handle_young_prospects(self, request: YoungProspectsRequest) -> AnalysisResponse:
        """Handle young prospects requests."""
        try:
            # Use the specialized young DM scout for midfielder analysis
            if request.position and 'midfielder' in request.position.lower():
                prospects_df = self.young_scout.scout_young_defensive_midfielders(
                    max_age=request.max_age,
                    min_minutes=request.min_minutes
                )
            else:
                # Use general young prospects analysis
                prospects_df = self.analyzer.get_young_prospects(
                    max_age=request.max_age,
                    min_minutes=request.min_minutes
                )
                
                # Apply position filter if specified
                if request.position and not prospects_df.empty:
                    position_mask = prospects_df['position'].str.contains(
                        request.position, case=False, na=False
                    )
                    prospects_df = prospects_df[position_mask]
                
                # Apply league filter if specified  
                if request.league and not prospects_df.empty:
                    league_mask = prospects_df['league'] == request.league
                    prospects_df = prospects_df[league_mask]
            
            if prospects_df.empty:
                filters_text = f"under {request.max_age}"
                if request.position:
                    filters_text += f", {request.position}"
                if request.league:
                    filters_text += f", {request.league}"
                
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message=f"No young prospects found ({filters_text})",
                    suggestions=[
                        f"Try increasing max age from {request.max_age}",
                        f"Try reducing minimum minutes from {request.min_minutes}",
                        "Remove position or league filters"
                    ]
                )
            
            # Limit results
            if len(prospects_df) > request.limit:
                prospects_df = prospects_df.head(request.limit)
            
            # Generate age group analysis
            age_groups = self._analyze_age_groups(prospects_df)
            
            # Generate league breakdown
            league_breakdown = prospects_df['league'].value_counts().to_dict()
            
            # Generate top recommendations
            top_recommendations = self._generate_prospect_recommendations(prospects_df.head(5))
            
            return ProspectsResponse(
                success=True,
                original_request=request,
                prospects=prospects_df,
                age_groups=age_groups,
                league_breakdown=league_breakdown,
                top_recommendations=top_recommendations
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Young prospects analysis failed: {e}")
    
    def _handle_top_performers(self, request: TopPerformersRequest) -> AnalysisResponse:
        """Handle top performers requests."""
        try:
            # Get qualified players
            all_players = self.analyzer.standard_data[
                self.analyzer.standard_data['minutes'] >= request.min_minutes
            ].copy()
            
            # Apply position filter
            if request.position:
                position_mask = all_players['position'].str.contains(
                    request.position, case=False, na=False
                )
                all_players = all_players[position_mask]
            
            # Apply league filter
            if request.league:
                league_mask = [idx[0] == request.league for idx in all_players.index]
                all_players = all_players[league_mask]
            
            # Check if stat exists
            if request.stat not in all_players.columns:
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message=f"Stat '{request.stat}' not found in data",
                    suggestions=[
                        "Try: 'goals', 'assists', 'goals_per_90', 'assists_per_90'",
                        "Check the spelling of the statistic"
                    ]
                )
            
            # Get top performers
            top_performers = all_players.nlargest(request.limit, request.stat)
            
            if top_performers.empty:
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message="No players found matching criteria",
                    suggestions=[
                        f"Try reducing minimum minutes from {request.min_minutes}",
                        "Remove position or league filters"
                    ]
                )
            
            # Add player info as columns for easier display
            top_performers = top_performers.reset_index()
            
            summary = f"Top {len(top_performers)} performers in {request.stat}"
            if request.position:
                summary += f" ({request.position})"
            if request.league:
                summary += f" in {request.league}"
            
            return PlayerListResponse(
                success=True,
                original_request=request,
                players=top_performers,
                total_found=len(top_performers),
                summary=summary
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Top performers analysis failed: {e}")
    
    def _handle_custom_filter(self, request: CustomFilterRequest) -> AnalysisResponse:
        """Handle custom filter requests."""
        try:
            # Start with all qualified players
            filtered_players = self.analyzer.standard_data[
                self.analyzer.standard_data['minutes'] >= request.min_minutes
            ].copy()
            
            # Apply position filter
            if request.position:
                position_mask = filtered_players['position'].str.contains(
                    request.position, case=False, na=False
                )
                filtered_players = filtered_players[position_mask]
            
            # Apply league filter
            if request.league:
                league_mask = [idx[0] == request.league for idx in filtered_players.index]
                filtered_players = filtered_players[league_mask]
            
            # Apply age filters
            if request.age_min:
                filtered_players = filtered_players[filtered_players['age'] >= request.age_min]
            if request.age_max:
                filtered_players = filtered_players[filtered_players['age'] <= request.age_max]
            
            # Apply stat filters
            for stat, filters in request.stat_filters.items():
                if stat in filtered_players.columns:
                    if 'min' in filters:
                        filtered_players = filtered_players[filtered_players[stat] >= filters['min']]
                    if 'max' in filters:
                        filtered_players = filtered_players[filtered_players[stat] <= filters['max']]
            
            # Limit results
            if len(filtered_players) > request.limit:
                filtered_players = filtered_players.head(request.limit)
            
            if filtered_players.empty:
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message="No players found matching all criteria",
                    suggestions=[
                        "Try relaxing some filters",
                        f"Reduce minimum minutes from {request.min_minutes}",
                        "Remove age or stat restrictions"
                    ]
                )
            
            # Reset index for easier display
            filtered_players = filtered_players.reset_index()
            
            # Generate summary
            summary = f"Found {len(filtered_players)} players matching custom criteria"
            
            return PlayerListResponse(
                success=True,
                original_request=request,
                players=filtered_players,
                total_found=len(filtered_players),
                summary=summary
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Custom filter analysis failed: {e}")
    
    def _handle_tactical_analysis(self, request: TacticalAnalysisRequest) -> AnalysisResponse:
        """Handle GPT-4 enhanced tactical analysis requests."""
        try:
            # Start with all qualified players
            candidates = self.analyzer.standard_data[
                self.analyzer.standard_data['minutes'] >= request.min_minutes
            ].copy()
            
            # Apply basic filters first
            if request.position:
                position_mask = candidates['position'].str.contains(
                    request.position, case=False, na=False
                )
                candidates = candidates[position_mask]
            
            if request.league:
                league_mask = [idx[0] == request.league for idx in candidates.index]
                candidates = candidates[league_mask]
            
            # Apply age filters
            if request.age_min:
                candidates = candidates[candidates['age'] >= request.age_min]
            if request.age_max:
                candidates = candidates[candidates['age'] <= request.age_max]
            
            # If target_player is specified, exclude them from results
            if request.target_player:
                target_mask = ~candidates.index.get_level_values(3).str.contains(
                    request.target_player, case=False, na=False
                )
                candidates = candidates[target_mask]
            
            if candidates.empty:
                filters_desc = []
                if request.position:
                    filters_desc.append(f"position: {request.position}")
                if request.league:
                    filters_desc.append(f"league: {request.league}")
                if request.age_min or request.age_max:
                    age_range = f"age: {request.age_min or 'any'}-{request.age_max or 'any'}"
                    filters_desc.append(age_range)
                
                return ErrorResponse(
                    success=False,
                    original_request=request,
                    error_message=f"No tactical candidates found with criteria: {', '.join(filters_desc)}",
                    suggestions=[
                        "Try expanding age range or removing position/league filters",
                        f"Reduce minimum minutes from {request.min_minutes}",
                        "Check if the target player name is spelled correctly"
                    ]
                )
            
            # Score candidates based on priority stats if provided
            if request.priority_stats:
                # Calculate composite score from priority stats
                scores = []
                for idx, player in candidates.iterrows():
                    score = 0
                    valid_stats = 0
                    
                    for stat in request.priority_stats:
                        if stat in player and pd.notna(player[stat]):
                            # Normalize stat values (simple min-max scaling)
                            stat_values = candidates[stat].dropna()
                            if len(stat_values) > 1:
                                min_val = stat_values.min()
                                max_val = stat_values.max()
                                if max_val > min_val:
                                    normalized = (player[stat] - min_val) / (max_val - min_val)
                                    score += normalized
                                    valid_stats += 1
                    
                    # Average score across valid stats
                    final_score = score / max(valid_stats, 1)
                    scores.append(final_score)
                
                # Add scores to candidates and sort
                candidates = candidates.copy()
                candidates['tactical_score'] = scores
                candidates = candidates.sort_values('tactical_score', ascending=False)
            
            # Limit results
            if len(candidates) > request.limit:
                candidates = candidates.head(request.limit)
            
            # Reset index for easier display
            candidates_display = candidates.reset_index()
            
            # Generate tactical insights
            tactical_insights = self._generate_tactical_insights(
                candidates, request.target_player, request.tactical_context, request.reasoning
            )
            
            # Create specialized tactical response
            tactical_data = {
                'target_player': request.target_player,
                'tactical_context': request.tactical_context,
                'reasoning': request.reasoning,
                'priority_stats': request.priority_stats,
                'candidates': candidates_display,
                'insights': tactical_insights
            }
            
            summary = f"Found {len(candidates)} tactical candidates"
            if request.target_player:
                summary += f" for {request.target_player}"
            if request.position:
                summary += f" ({request.position})"
            if request.league:
                summary += f" in {request.league}"
            
            # Return as PlayerListResponse with tactical data in summary
            return PlayerListResponse(
                success=True,
                original_request=request,
                players=candidates_display,
                total_found=len(candidates),
                summary=f"{summary}\n\nTactical Analysis:\n{request.reasoning}"
            )
            
        except Exception as e:
            return self._create_error_response(request, f"Tactical analysis failed: {e}")
    
    def _handle_unknown(self, request: UnknownRequest) -> AnalysisResponse:
        """Handle unknown query requests."""
        return ErrorResponse(
            success=False,
            original_request=request,
            error_message="I'm not sure how to analyze that query yet.",
            suggestions=request.suggested_queries,
            help_text="Try rephrasing your question or use one of the suggested formats above."
        )
    
    def _generate_comparison_insights(self, comparison_df: pd.DataFrame) -> List[str]:
        """Generate insights from player comparison."""
        insights = []
        
        if len(comparison_df) >= 2:
            # Goals comparison
            goals_col = 'Goals' if 'Goals' in comparison_df.columns else 'goals'
            if goals_col in comparison_df.columns:
                top_scorer = comparison_df.loc[comparison_df[goals_col].idxmax()]
                insights.append(f"🥅 {top_scorer['Player']} leads in goals with {top_scorer[goals_col]}")
            
            # Assists comparison
            assists_col = 'Assists' if 'Assists' in comparison_df.columns else 'assists'
            if assists_col in comparison_df.columns:
                top_assister = comparison_df.loc[comparison_df[assists_col].idxmax()]
                insights.append(f"🎯 {top_assister['Player']} leads in assists with {top_assister[assists_col]}")
            
            # Age comparison
            if 'Age' in comparison_df.columns:
                youngest = comparison_df.loc[comparison_df['Age'].idxmin()]
                oldest = comparison_df.loc[comparison_df['Age'].idxmax()]
                if youngest['Age'] != oldest['Age']:
                    insights.append(f"👶 {youngest['Player']} is youngest at {youngest['Age']}, {oldest['Player']} is oldest at {oldest['Age']}")
        
        return insights
    
    def _analyze_age_groups(self, prospects_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze prospects by age groups."""
        age_groups = {}
        
        if 'age' in prospects_df.columns:
            teenagers = prospects_df[prospects_df['age'] <= 19]
            early_twenties = prospects_df[(prospects_df['age'] >= 20) & (prospects_df['age'] <= 22)]
            
            if not teenagers.empty:
                age_groups['Teenagers (19 and under)'] = teenagers
            if not early_twenties.empty:
                age_groups['Early Twenties (20-22)'] = early_twenties
        
        return age_groups
    
    def _generate_prospect_recommendations(self, top_prospects: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate detailed recommendations for top prospects."""
        recommendations = []
        
        for idx, prospect in top_prospects.iterrows():
            recommendation = {
                'rank': idx + 1,
                'player': prospect.get('player', 'Unknown'),
                'age': prospect.get('age', 'Unknown'),
                'team': prospect.get('team', 'Unknown'),
                'league': prospect.get('league', 'Unknown'),
                'potential_score': prospect.get('potential_score', 0),
                'reasoning': []
            }
            
            # Generate reasoning based on data
            if 'minutes' in prospect and prospect['minutes'] >= 2000:
                recommendation['reasoning'].append("High playing time shows coach trust")
            
            if 'age' in prospect and prospect['age'] <= 20:
                recommendation['reasoning'].append("Very young with years to develop")
            
            if 'potential_score' in prospect and prospect['potential_score'] >= 140:
                recommendation['reasoning'].append("Elite-tier potential score")
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_tactical_insights(self, candidates: pd.DataFrame, target_player: Optional[str], 
                                   tactical_context: str, reasoning: str) -> List[str]:
        """Generate tactical insights for candidate players."""
        insights = []
        
        if not candidates.empty:
            # Age distribution insight
            if 'age' in candidates.columns:
                avg_age = candidates['age'].mean()
                insights.append(f"📊 Average age of candidates: {avg_age:.1f} years")
                
                young_candidates = len(candidates[candidates['age'] <= 23])
                if young_candidates > 0:
                    insights.append(f"🌟 {young_candidates} young prospects (23 and under) identified")
            
            # League distribution insight
            if len(candidates) > 1:
                league_info = candidates.index.get_level_values(0).value_counts()
                top_league = league_info.index[0]
                count = league_info.iloc[0]
                insights.append(f"🏆 {top_league} has the most candidates ({count})")
            
            # Tactical scoring insight
            if 'tactical_score' in candidates.columns:
                top_candidate = candidates.iloc[0]
                candidate_name = top_candidate.name[3] if hasattr(top_candidate.name, '__getitem__') else "Top candidate"
                insights.append(f"⭐ Highest tactical fit: {candidate_name}")
            
            # Playing time insight
            if 'minutes' in candidates.columns:
                avg_minutes = candidates['minutes'].mean()
                insights.append(f"⏱️ Average playing time: {int(avg_minutes)} minutes")
                
                regular_starters = len(candidates[candidates['minutes'] >= 2000])
                if regular_starters > 0:
                    insights.append(f"🎯 {regular_starters} candidates are regular starters (2000+ minutes)")
        
        # Add GPT-4 reasoning if provided
        if reasoning:
            insights.append(f"🧠 AI Analysis: {reasoning[:150]}{'...' if len(reasoning) > 150 else ''}")
        
        return insights
    
    def _get_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for request."""
        # Simple cache key based on request type and key parameters
        key_parts = [str(request.query_type)]
        
        if hasattr(request, 'player_name'):
            key_parts.append(request.player_name)
        if hasattr(request, 'player_names'):
            key_parts.extend(sorted(request.player_names))
        if hasattr(request, 'target_player') and request.target_player:
            key_parts.append(f"target:{request.target_player}")
        if hasattr(request, 'position') and request.position:
            key_parts.append(request.position)
        if hasattr(request, 'league') and request.league:
            key_parts.append(request.league)
        if hasattr(request, 'stat'):
            key_parts.append(request.stat)
        if hasattr(request, 'tactical_context') and request.tactical_context:
            # Use a hash of tactical context to keep cache key manageable
            import hashlib
            context_hash = hashlib.md5(request.tactical_context.encode()).hexdigest()[:8]
            key_parts.append(f"context:{context_hash}")
        
        return "|".join(key_parts)
    
    def _create_error_response(self, request: AnalysisRequest, error_message: str) -> ErrorResponse:
        """Create standardized error response."""
        return ErrorResponse(
            success=False,
            original_request=request,
            error_message=error_message,
            suggestions=[
                "Try rephrasing your question",
                "Check spelling of player names",
                "Use simpler queries to start"
            ]
        )