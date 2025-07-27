"""
Revolutionary AI-Native Soccer Analysis Engine

Completely replaces traditional pattern-matching with a pure AI-first architecture.
Implements the 3-step pipeline: AI Parser → Python Analysis → AI Reasoning

This engine provides professional scout-level tactical intelligence using GPT-4
and comprehensive player data across 2,854 players with 50+ metrics each.
"""

import pandas as pd
import numpy as np
from openai import OpenAI
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisConfig:
    """Configuration for AI-native analysis"""
    openai_api_key: str
    model: str = "gpt-4"
    max_candidates: int = 50
    confidence_threshold: float = 0.7
    enable_caching: bool = True
    data_dir: str = "data/comprehensive/processed"

class AIScoutEngine:
    """
    Revolutionary AI-native soccer analysis engine
    
    Architecture:
    1. AI Parser (GPT-4): Natural language → Structured parameters
    2. Python Analysis: High-performance data filtering and computation
    3. AI Reasoning (GPT-4): Professional scout insights and tactical analysis
    """
    
    def __init__(self, config: AIAnalysisConfig):
        self.config = config
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.comprehensive_data = None
        self.player_profiles = {}
        self.query_cache = {}
        self._initialize_data_engine()
    
    def _initialize_data_engine(self):
        """Initialize comprehensive data engine with full player database"""
        logger.info("🚀 Initializing AI-Native Data Engine...")
        
        data_path = Path(self.config.data_dir)
        
        try:
            # Load unified comprehensive database
            unified_file = data_path / "unified_player_data.csv"
            if unified_file.exists():
                self.comprehensive_data = pd.read_csv(unified_file)
                logger.info(f"✅ Loaded {len(self.comprehensive_data)} players with {len(self.comprehensive_data.columns)} metrics")
            else:
                raise FileNotFoundError(f"Unified data file not found: {unified_file}")
            
            # Pre-compute enhanced metrics for AI optimization
            self._enhance_player_data()
            
            # Generate AI-optimized player profiles
            self._generate_ai_player_profiles()
            
            logger.info("🧠 AI-Native Data Engine ready for professional analysis")
            
        except Exception as e:
            logger.error(f"❌ Error loading comprehensive data: {e}")
            raise Exception(f"Cannot initialize AI engine: {e}")
    
    def _enhance_player_data(self):
        """Add computed metrics for AI analysis"""
        logger.info("📊 Computing enhanced metrics for AI analysis...")
        
        # Defensive work rate indicator
        self.comprehensive_data['defensive_work_rate'] = (
            self.comprehensive_data.get('tackles', 0) + 
            self.comprehensive_data.get('tackles_won', 0) * 2 +
            self.comprehensive_data.get('interceptions', 0)
        ) / self.comprehensive_data.get('nineties', 1).replace(0, 1)
        
        # Creative ability indicator
        self.comprehensive_data['creativity_score'] = (
            self.comprehensive_data.get('assists_per_90', 0) * 3 +
            self.comprehensive_data.get('expected_assists_per_90', 0) * 2 +
            self.comprehensive_data.get('progressive_passes', 0) / self.comprehensive_data.get('nineties', 1).replace(0, 1)
        )
        
        # Attacking threat indicator
        self.comprehensive_data['attacking_threat'] = (
            self.comprehensive_data.get('goals_per_90', 0) * 4 +
            self.comprehensive_data.get('expected_goals_per_90', 0) * 3 +
            self.comprehensive_data.get('progressive_carries', 0) / self.comprehensive_data.get('nineties', 1).replace(0, 1)
        )
        
        # Overall performance indicator
        self.comprehensive_data['performance_rating'] = (
            self.comprehensive_data['creativity_score'] +
            self.comprehensive_data['attacking_threat'] +
            self.comprehensive_data['defensive_work_rate']
        ) / 3
        
        logger.info("✅ Enhanced metrics computed for AI analysis")
    
    def _generate_ai_player_profiles(self):
        """Pre-generate AI-optimized player profiles for efficient querying"""
        logger.info("🧠 Generating AI-optimized player profiles...")
        
        for _, player in self.comprehensive_data.iterrows():
            profile = {
                # Basic info
                "name": player.get("player", "Unknown"),
                "position": player.get("position", "Unknown"),
                "team": player.get("team", "Unknown"),
                "league": player.get("league", "Unknown"),
                "age": player.get("age", 0),
                "nationality": player.get("nationality", "Unknown"),
                
                # Performance metrics
                "goals_per_90": player.get("goals_per_90", 0),
                "assists_per_90": player.get("assists_per_90", 0),
                "minutes_played": player.get("minutes", 0),
                "matches_played": player.get("matches_played", 0),
                
                # AI-computed attributes
                "defensive_work_rate": player.get("defensive_work_rate", 0),
                "creativity_score": player.get("creativity_score", 0),
                "attacking_threat": player.get("attacking_threat", 0),
                "performance_rating": player.get("performance_rating", 0),
                
                # Advanced metrics
                "expected_goals": player.get("expected_goals_per_90", 0),
                "expected_assists": player.get("expected_assists_per_90", 0),
                "progressive_actions": (player.get("progressive_carries", 0) + player.get("progressive_passes", 0)),
                
                # Full stats for comprehensive analysis
                "complete_stats": player.to_dict()
            }
            
            player_id = f"{player.get('player', 'unknown')}_{player.get('team', 'unknown')}".replace(" ", "_").lower()
            self.player_profiles[player_id] = profile
        
        logger.info(f"✅ Generated {len(self.player_profiles)} AI-optimized player profiles")
    
    # STEP 1: AI PARSER - GPT-4 converts natural language to structured parameters
    def parse_natural_language_query(self, query: str) -> Dict:
        """
        STEP 1: Revolutionary AI query parsing
        Converts natural language into precise database parameters using GPT-4
        """
        
        logger.info("🧠 STEP 1: AI Natural Language Parsing")
        
        parsing_prompt = f"""
        You are an elite soccer query parser with deep tactical knowledge. Convert this natural language query into structured database parameters.
        
        Query: "{query}"
        
        Parse and extract into PRECISE JSON format:
        {{
            "analysis_type": "player_search|comparison|tactical_partnership|replacement_analysis|formation_analysis|position_analysis",
            "reference_players": ["exact names of players mentioned"],
            "leagues": ["ENG-Premier League", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"],
            "positions": ["Goalkeeper", "Defender", "Midfielder", "Forward", "Forward/Midfielder", "Midfielder/Defender"],
            "age_constraints": {{"min": 16, "max": 45}},
            "tactical_requirements": {{
                "playing_style": "possession|counter_attack|pressing|creative|defensive|box_to_box",
                "key_attributes": ["pace", "creativity", "defensive_work_rate", "finishing", "aerial_ability"],
                "formation_context": "4-3-3|4-2-3-1|3-5-2|4-4-2|custom",
                "team_style": "barcelona|manchester_city|liverpool|atletico_madrid|custom"
            }},
            "performance_requirements": {{
                "minimum_minutes": 500,
                "goals_importance": "high|medium|low",
                "assists_importance": "high|medium|low",
                "defensive_importance": "high|medium|low"
            }},
            "search_intent": "find_partners|find_alternatives|compare_players|analyze_position|general_search"
        }}
        
        Guidelines:
        - Only include fields that are explicitly mentioned or strongly implied
        - Use exact league names as shown above
        - Be precise with player names (use full names)
        - Infer tactical context from query language
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a precise soccer query parser. Return only valid JSON with exact field names as specified."},
                    {"role": "user", "content": parsing_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            parsed_params = json.loads(response.choices[0].message.content)
            logger.info(f"✅ AI Parser Result: {parsed_params}")
            return parsed_params
            
        except Exception as e:
            logger.error(f"❌ AI parsing failed: {e}")
            return {"error": "Failed to parse query", "fallback": True}
    
    # STEP 2: PYTHON ANALYSIS - High-performance database operations
    def execute_database_analysis(self, parsed_params: Dict) -> pd.DataFrame:
        """
        STEP 2: High-performance Python data analysis
        Filters and computes using AI-parsed parameters across comprehensive dataset
        """
        
        logger.info("⚡ STEP 2: Python Database Analysis")
        filtered_data = self.comprehensive_data.copy()
        
        # Apply league filters
        if "leagues" in parsed_params and parsed_params["leagues"]:
            filtered_data = filtered_data[filtered_data['league'].isin(parsed_params["leagues"])]
            logger.info(f"   📍 League filter: {len(filtered_data)} players")
        
        # Apply position filters
        if "positions" in parsed_params and parsed_params["positions"]:
            position_mask = filtered_data['position'].str.contains(
                '|'.join(parsed_params["positions"]), case=False, na=False
            )
            filtered_data = filtered_data[position_mask]
            logger.info(f"   🎯 Position filter: {len(filtered_data)} players")
        
        # Apply age constraints
        if "age_constraints" in parsed_params:
            age_limits = parsed_params["age_constraints"]
            if "min" in age_limits:
                filtered_data = filtered_data[filtered_data['age'] >= age_limits["min"]]
            if "max" in age_limits:
                filtered_data = filtered_data[filtered_data['age'] <= age_limits["max"]]
            logger.info(f"   👶 Age filter: {len(filtered_data)} players")
        
        # Apply minimum minutes filter
        perf_req = parsed_params.get("performance_requirements", {})
        min_minutes = perf_req.get("minimum_minutes", 500)
        filtered_data = filtered_data[filtered_data['minutes'] >= min_minutes]
        logger.info(f"   ⏱️ Minutes filter: {len(filtered_data)} players")
        
        # Special analysis for reference players (partnerships/alternatives)
        if "reference_players" in parsed_params and parsed_params["reference_players"]:
            filtered_data = self._analyze_player_relationships(
                filtered_data, parsed_params["reference_players"], parsed_params
            )
        
        # Apply tactical requirements
        if "tactical_requirements" in parsed_params:
            filtered_data = self._apply_tactical_filters(filtered_data, parsed_params["tactical_requirements"])
        
        # Rank by relevance and limit for AI processing
        filtered_data = self._rank_by_relevance(filtered_data, parsed_params)
        top_candidates = filtered_data.head(self.config.max_candidates)
        
        logger.info(f"✅ Analysis complete: {len(top_candidates)} top candidates")
        return top_candidates
    
    def _analyze_player_relationships(self, data: pd.DataFrame, reference_players: List[str], params: Dict) -> pd.DataFrame:
        """Analyze partnerships or alternatives for reference players"""
        search_intent = params.get("search_intent", "general_search")
        
        if search_intent == "find_partners":
            # Find complementary players
            return self._find_tactical_partners(data, reference_players)
        elif search_intent == "find_alternatives":
            # Find similar players
            return self._find_similar_players(data, reference_players)
        else:
            # General search - exclude reference players
            for ref_player in reference_players:
                data = data[~data['player'].str.contains(ref_player, case=False, na=False)]
            return data
    
    def _find_tactical_partners(self, data: pd.DataFrame, reference_players: List[str]) -> pd.DataFrame:
        """Find players who would complement the reference player tactically"""
        # This is a simplified implementation - in production this would be much more sophisticated
        # For now, we'll look for players with complementary skills
        
        # Find reference player in our data
        ref_data = self.comprehensive_data[
            self.comprehensive_data['player'].str.contains('|'.join(reference_players), case=False, na=False)
        ]
        
        if ref_data.empty:
            return data
        
        ref_player = ref_data.iloc[0]
        
        # Look for complementary attributes
        # If reference player is creative, find defensive players
        # If reference player is defensive, find creative players
        
        ref_creativity = ref_player.get('creativity_score', 0)
        ref_defensive = ref_player.get('defensive_work_rate', 0)
        
        if ref_creativity > ref_defensive:
            # Reference is creative, find defensive partners
            data['compatibility_score'] = data['defensive_work_rate'] * 2 + data['creativity_score']
        else:
            # Reference is defensive, find creative partners
            data['compatibility_score'] = data['creativity_score'] * 2 + data['defensive_work_rate']
        
        return data.sort_values('compatibility_score', ascending=False)
    
    def _find_similar_players(self, data: pd.DataFrame, reference_players: List[str]) -> pd.DataFrame:
        """Find players with similar playing style to reference players"""
        # Find reference player metrics
        ref_data = self.comprehensive_data[
            self.comprehensive_data['player'].str.contains('|'.join(reference_players), case=False, na=False)
        ]
        
        if ref_data.empty:
            return data
        
        ref_player = ref_data.iloc[0]
        
        # Calculate similarity based on key metrics
        metrics = ['goals_per_90', 'assists_per_90', 'creativity_score', 'defensive_work_rate', 'attacking_threat']
        
        similarity_scores = []
        for _, player in data.iterrows():
            similarity = 0
            for metric in metrics:
                ref_val = ref_player.get(metric, 0)
                player_val = player.get(metric, 0)
                # Calculate normalized difference (lower is more similar)
                if ref_val + player_val > 0:
                    similarity += 1 - abs(ref_val - player_val) / max(ref_val, player_val, 1)
            similarity_scores.append(similarity / len(metrics))
        
        data['similarity_score'] = similarity_scores
        return data.sort_values('similarity_score', ascending=False)
    
    def _apply_tactical_filters(self, data: pd.DataFrame, tactical_req: Dict) -> pd.DataFrame:
        """Apply tactical requirement filters"""
        
        playing_style = tactical_req.get("playing_style")
        key_attributes = tactical_req.get("key_attributes", [])
        
        if playing_style == "creative":
            data = data[data['creativity_score'] > data['creativity_score'].median()]
        elif playing_style == "defensive":
            data = data[data['defensive_work_rate'] > data['defensive_work_rate'].median()]
        elif playing_style == "box_to_box":
            # Balance of offensive and defensive
            data = data[
                (data['creativity_score'] > data['creativity_score'].quantile(0.3)) &
                (data['defensive_work_rate'] > data['defensive_work_rate'].quantile(0.3))
            ]
        
        # Apply key attribute filters
        for attribute in key_attributes:
            if attribute == "creativity" and "creativity_score" in data.columns:
                data = data[data['creativity_score'] > data['creativity_score'].quantile(0.6)]
            elif attribute == "defensive_work_rate" and "defensive_work_rate" in data.columns:
                data = data[data['defensive_work_rate'] > data['defensive_work_rate'].quantile(0.6)]
        
        return data
    
    def _rank_by_relevance(self, data: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """Rank players by relevance to the query"""
        
        # Default ranking by performance rating
        if 'performance_rating' in data.columns:
            data = data.sort_values('performance_rating', ascending=False)
        else:
            # Fallback ranking
            data = data.sort_values(['goals_per_90', 'assists_per_90'], ascending=False)
        
        return data
    
    # STEP 3: AI REASONING - GPT-4 provides professional scout analysis
    def generate_tactical_intelligence(self, query: str, candidates: pd.DataFrame, parsed_params: Dict) -> Dict:
        """
        STEP 3: Revolutionary AI tactical reasoning
        Professional scout-level analysis and tactical insights using GPT-4
        """
        
        logger.info("🧠 STEP 3: AI Tactical Intelligence Generation")
        
        # Prepare comprehensive data summary for AI analysis
        top_candidates = candidates.head(10)
        
        player_summaries = []
        for _, player in top_candidates.iterrows():
            summary = {
                "name": player.get("player", "Unknown"),
                "team": player.get("team", "Unknown"),
                "league": player.get("league", "Unknown"),
                "position": player.get("position", "Unknown"),
                "age": player.get("age", 0),
                "minutes": player.get("minutes", 0),
                "goals_per_90": round(player.get("goals_per_90", 0), 2),
                "assists_per_90": round(player.get("assists_per_90", 0), 2),
                "creativity_score": round(player.get("creativity_score", 0), 2),
                "defensive_work_rate": round(player.get("defensive_work_rate", 0), 2),
                "attacking_threat": round(player.get("attacking_threat", 0), 2),
                "performance_rating": round(player.get("performance_rating", 0), 2)
            }
            player_summaries.append(summary)
        
        tactical_prompt = f"""
        You are an elite soccer scout with deep tactical knowledge. Provide professional analysis based on comprehensive player data.
        
        ORIGINAL QUERY: "{query}"
        
        ANALYSIS CONTEXT:
        - Query Type: {parsed_params.get('analysis_type', 'general')}
        - Total Candidates Found: {len(candidates)}
        - Search Intent: {parsed_params.get('search_intent', 'general_search')}
        - Tactical Context: {parsed_params.get('tactical_requirements', {})}
        
        TOP 10 CANDIDATES DATA:
        {json.dumps(player_summaries, indent=2)}
        
        Provide comprehensive professional scout analysis in JSON format:
        {{
            "executive_summary": "Direct answer to the query with key tactical insights",
            "top_recommendations": [
                {{
                    "player_name": "Full Player Name",
                    "current_team": "Team Name",
                    "league": "League Name",
                    "tactical_reasoning": "Detailed explanation of why this player fits the requirements",
                    "key_strengths": ["strength1", "strength2", "strength3"],
                    "tactical_role": "Specific tactical role they would play",
                    "confidence_score": 0.85,
                    "supporting_metrics": {{"goals_per_90": 0.3, "creativity": "high"}},
                    "potential_concerns": "Any limitations or areas for improvement"
                }}
            ],
            "tactical_analysis": {{
                "formation_compatibility": "How they fit in different formations",
                "playing_style_match": "Compatibility with requested playing style",
                "partnership_dynamics": "How they work with existing players or each other"
            }},
            "alternative_considerations": [
                {{
                    "player_name": "Alternative Player",
                    "reasoning": "Why they are worth considering as an alternative"
                }}
            ],
            "professional_insights": {{
                "market_context": "Assessment of availability and value",
                "development_potential": "Long-term potential and trajectory",
                "tactical_versatility": "Ability to play multiple roles or systems"
            }},
            "scout_recommendation": "Final professional recommendation with confidence level"
        }}
        
        Focus on:
        1. Tactical intelligence and system fit
        2. Playing style compatibility 
        3. Professional insights that scouts would provide
        4. Specific metrics that support your analysis
        5. Realistic assessment of strengths and limitations
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an elite soccer scout providing professional tactical analysis. Focus on actionable insights with supporting data."},
                    {"role": "user", "content": tactical_prompt}
                ],
                temperature=0.3,  # Balance creativity with consistency
                max_tokens=2000
            )
            
            tactical_analysis = json.loads(response.choices[0].message.content)
            logger.info("✅ Professional tactical intelligence generated")
            return tactical_analysis
            
        except Exception as e:
            logger.error(f"❌ Tactical analysis failed: {e}")
            return {"error": "Failed to generate tactical analysis", "details": str(e)}
    
    # MAIN ANALYSIS METHOD - Revolutionary 3-step pipeline
    def analyze_query(self, query: str) -> Dict:
        """
        Revolutionary 3-step AI-native analysis pipeline
        
        This is the main entry point that orchestrates the complete AI-native analysis:
        1. AI Parser: Natural language → Structured parameters
        2. Python Analysis: High-performance data processing
        3. AI Reasoning: Professional scout insights
        """
        
        logger.info(f"\n🚀 STARTING REVOLUTIONARY AI-NATIVE ANALYSIS")
        logger.info(f"Query: '{query}'")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # STEP 1: AI Natural Language Parsing
            logger.info("STEP 1: AI NATURAL LANGUAGE PARSING")
            parsed_params = self.parse_natural_language_query(query)
            
            if parsed_params.get("error"):
                return {
                    "success": False,
                    "error": parsed_params["error"],
                    "step_failed": "parsing"
                }
            
            # STEP 2: Python Database Analysis  
            logger.info("\nSTEP 2: PYTHON DATABASE ANALYSIS")
            candidates = self.execute_database_analysis(parsed_params)
            
            if len(candidates) == 0:
                return {
                    "success": False,
                    "error": "No players found matching the specified criteria",
                    "suggestions": [
                        "Try broader search parameters",
                        "Reduce minimum minutes requirement",
                        "Expand league or position filters"
                    ],
                    "step_failed": "filtering"
                }
            
            # STEP 3: AI Tactical Intelligence Generation
            logger.info("\nSTEP 3: AI TACTICAL INTELLIGENCE GENERATION")
            tactical_analysis = self.generate_tactical_intelligence(query, candidates, parsed_params)
            
            if tactical_analysis.get("error"):
                return {
                    "success": False,
                    "error": tactical_analysis["error"],
                    "step_failed": "reasoning"
                }
            
            # Combine results into comprehensive response
            execution_time = time.time() - start_time
            
            final_result = {
                "success": True,
                "query": query,
                "analysis_type": "ai_native_revolutionary",
                "execution_time": round(execution_time, 2),
                "metadata": {
                    "parsed_parameters": parsed_params,
                    "candidates_found": len(candidates),
                    "top_candidates_analyzed": min(len(candidates), 10),
                    "comprehensive_data_used": True,
                    "ai_steps_completed": 3
                },
                "tactical_intelligence": tactical_analysis,
                "raw_candidate_data": candidates.head(20).to_dict('records')  # Top 20 for reference
            }
            
            logger.info(f"\n✅ AI-NATIVE ANALYSIS COMPLETE in {execution_time:.2f}s")
            logger.info(f"   🎯 Found {len(candidates)} candidates")
            logger.info(f"   🧠 Generated professional tactical intelligence")
            logger.info("=" * 80)
            
            return final_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"\n❌ AI-NATIVE ANALYSIS FAILED after {execution_time:.2f}s: {e}")
            return {
                "success": False,
                "error": f"Revolutionary analysis failed: {str(e)}",
                "execution_time": round(execution_time, 2),
                "step_failed": "system_error"
            }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status for monitoring"""
        return {
            "engine_status": "ai_native_revolutionary",
            "data_loaded": self.comprehensive_data is not None,
            "total_players": len(self.comprehensive_data) if self.comprehensive_data is not None else 0,
            "total_metrics": len(self.comprehensive_data.columns) if self.comprehensive_data is not None else 0,
            "player_profiles_generated": len(self.player_profiles),
            "ai_model": self.config.model,
            "cache_enabled": self.config.enable_caching,
            "ready_for_analysis": True
        }