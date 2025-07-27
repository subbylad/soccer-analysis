"""
AI-Native Query Processor

Revolutionary query processing system that replaces pattern matching with 
genuine AI intelligence for understanding complex tactical soccer queries.

This processor works directly with GPT-4 to understand context, extract entities,
and route to appropriate analysis engines with sophisticated reasoning.
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import openai
from datetime import datetime

from .types import (QueryContext, AnalysisRequest, QueryType, 
                   PlayerSearchRequest, PlayerComparisonRequest, 
                   TacticalAnalysisRequest)

logger = logging.getLogger(__name__)

@dataclass
class QueryUnderstanding:
    """AI understanding of a user query"""
    intent: str
    entities: Dict[str, List[str]]
    tactical_context: Optional[str]
    complexity_score: float
    confidence: float
    reasoning: str
    suggested_analysis_type: str

@dataclass
class AIQueryContext:
    """Extended query context with AI insights"""
    original_query: str
    processed_query: str
    user_intent: str
    tactical_requirements: List[str]
    entity_extraction: Dict[str, Any]
    confidence_score: float
    alternative_interpretations: List[str]

class AIQueryProcessor:
    """
    AI-Native Query Processor
    
    This processor uses GPT-4 to understand natural language soccer queries
    with sophisticated tactical reasoning, replacing traditional pattern matching
    with genuine AI intelligence.
    
    Key capabilities:
    - Natural language understanding with tactical context
    - Entity extraction (players, teams, formations, styles)
    - Intent classification with confidence scoring
    - Complex query decomposition
    - Tactical requirement analysis
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, enable_ai: bool = True):
        """
        Initialize AI Query Processor.
        
        Args:
            openai_api_key: OpenAI API key for GPT-4
            enable_ai: Whether to enable AI features
        """
        self.enable_ai = enable_ai and openai_api_key is not None
        
        if self.enable_ai and openai_api_key:
            openai.api_key = openai_api_key
            logger.info("AI Query Processor initialized with GPT-4")
        else:
            logger.info("AI Query Processor initialized in fallback mode")
        
        # Initialize tactical knowledge base
        self._initialize_tactical_knowledge()
        
        # Query processing statistics
        self.processing_stats = {
            "total_queries": 0,
            "ai_processed": 0,
            "fallback_processed": 0,
            "avg_confidence": 0.0
        }
    
    def _initialize_tactical_knowledge(self) -> None:
        """Initialize tactical knowledge base for query understanding."""
        self.tactical_knowledge = {
            "formations": [
                "4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3", "5-3-2", 
                "4-1-4-1", "3-4-2-1", "4-5-1", "5-4-1"
            ],
            "playing_styles": [
                "tiki-taka", "counter-attack", "high press", "possession-based",
                "direct play", "wing play", "parking the bus", "gegenpress",
                "total football", "catenaccio"
            ],
            "tactical_roles": [
                "false 9", "inverted winger", "wing-back", "anchor man",
                "box-to-box", "playmaker", "destroyer", "sweeper keeper",
                "inside forward", "attacking midfielder", "defensive midfielder"
            ],
            "player_attributes": [
                "pace", "strength", "technique", "vision", "creativity",
                "work rate", "defensive", "attacking", "aerial ability",
                "leadership", "experience", "composure", "finishing"
            ],
            "team_systems": {
                "pep": ["possession", "high press", "inverted fullbacks", "false 9"],
                "klopp": ["gegenpress", "high intensity", "wing play", "counter-press"],
                "mourinho": ["defensive", "counter-attack", "physicality"],
                "guardiola": ["tiki-taka", "possession", "positional play"],
                "conte": ["3-5-2", "wing-backs", "intensity", "direct"]
            }
        }
    
    def process_query(self, query: str, context: Optional[QueryContext] = None) -> AnalysisRequest:
        """
        Main query processing method using AI intelligence.
        
        Args:
            query: Natural language query
            context: Optional query context
            
        Returns:
            Structured AnalysisRequest with AI insights
        """
        self.processing_stats["total_queries"] += 1
        
        try:
            logger.info(f"Processing query with AI: '{query}'")
            
            if self.enable_ai:
                return self._ai_process_query(query, context)
            else:
                return self._fallback_process_query(query, context)
                
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return self._create_error_request(query, str(e))
    
    def _ai_process_query(self, query: str, context: Optional[QueryContext]) -> AnalysisRequest:
        """Process query using GPT-4 intelligence."""
        try:
            # Step 1: Understand the query with AI
            understanding = self._understand_query_with_ai(query, context)
            
            # Step 2: Extract entities and tactical context
            entities = self._extract_entities_with_ai(query, understanding)
            
            # Step 3: Determine analysis type and parameters
            analysis_request = self._create_analysis_request(query, understanding, entities, context)
            
            self.processing_stats["ai_processed"] += 1
            self.processing_stats["avg_confidence"] = (
                (self.processing_stats["avg_confidence"] * (self.processing_stats["ai_processed"] - 1) + 
                 understanding.confidence) / self.processing_stats["ai_processed"]
            )
            
            logger.info(f"AI processing complete: {analysis_request.query_type} (confidence: {understanding.confidence:.2f})")
            return analysis_request
            
        except Exception as e:
            logger.error(f"AI query processing failed: {e}")
            return self._fallback_process_query(query, context)
    
    def _understand_query_with_ai(self, query: str, context: Optional[QueryContext]) -> QueryUnderstanding:
        """Use GPT-4 to understand query intent and context."""
        try:
            # Prepare context for AI
            context_info = ""
            if context:
                context_info = f"\\nContext: {context}"
            
            # Create comprehensive prompt for query understanding
            understanding_prompt = f"""
            Analyze this soccer query and provide deep tactical understanding:
            
            Query: "{query}"{context_info}
            
            Available Analysis Types:
            - player_search: Finding players matching criteria
            - player_comparison: Comparing specific players
            - tactical_analysis: Complex tactical/formation analysis
            - position_analysis: Position-specific insights
            - team_analysis: Team composition analysis
            - prospect_analysis: Young player scouting
            
            Tactical Knowledge Areas:
            - Formations: {', '.join(self.tactical_knowledge['formations'])}
            - Playing Styles: {', '.join(self.tactical_knowledge['playing_styles'])}
            - Tactical Roles: {', '.join(self.tactical_knowledge['tactical_roles'][:10])}
            
            Provide analysis in JSON format:
            {{
                "intent": "what the user wants to achieve",
                "entities": {{
                    "players": ["player names mentioned"],
                    "teams": ["team names mentioned"],
                    "positions": ["positions mentioned"],
                    "leagues": ["leagues mentioned"],
                    "formations": ["formations mentioned"],
                    "tactical_concepts": ["tactical concepts mentioned"],
                    "attributes": ["player attributes mentioned"],
                    "age_criteria": ["age-related criteria"],
                    "style_references": ["playing style references"]
                }},
                "tactical_context": "detailed tactical context and requirements",
                "complexity_score": 0.8,
                "confidence": 0.9,
                "reasoning": "explanation of analysis approach",
                "suggested_analysis_type": "most appropriate analysis type"
            }}
            
            Focus on understanding tactical nuance and context.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": understanding_prompt}],
                max_tokens=600,
                temperature=0.2
            )
            
            ai_understanding = json.loads(response.choices[0].message.content)
            
            return QueryUnderstanding(
                intent=ai_understanding.get("intent", ""),
                entities=ai_understanding.get("entities", {}),
                tactical_context=ai_understanding.get("tactical_context"),
                complexity_score=ai_understanding.get("complexity_score", 0.5),
                confidence=ai_understanding.get("confidence", 0.7),
                reasoning=ai_understanding.get("reasoning", ""),
                suggested_analysis_type=ai_understanding.get("suggested_analysis_type", "player_search")
            )
            
        except Exception as e:
            logger.error(f"AI query understanding failed: {e}")
            return self._fallback_query_understanding(query)
    
    def _extract_entities_with_ai(self, query: str, understanding: QueryUnderstanding) -> Dict[str, Any]:
        """Extract and enhance entities using AI."""
        try:
            # Enhanced entity extraction prompt
            entity_prompt = f"""
            Extract and enhance soccer entities from this query:
            
            Query: "{query}"
            Initial Understanding: {understanding.entities}
            
            Enhance entity extraction with:
            1. Player name variations and nicknames
            2. Team name variations and abbreviations  
            3. League name variations
            4. Tactical concept relationships
            5. Implicit requirements and constraints
            
            Return enhanced entities in JSON:
            {{
                "players": {{
                    "mentioned": ["exact names mentioned"],
                    "variations": ["possible name variations"],
                    "implied": ["players implied by context"]
                }},
                "teams": {{
                    "mentioned": ["team names"],
                    "leagues": ["team leagues if determinable"]
                }},
                "tactical_requirements": {{
                    "explicit": ["explicitly mentioned requirements"],
                    "implicit": ["tactically implied requirements"],
                    "constraints": ["any constraints or filters"]
                }},
                "search_criteria": {{
                    "position": "position filter if any",
                    "age": "age criteria if any",
                    "league": "league filter if any",
                    "style": "playing style if any",
                    "attributes": ["required attributes"]
                }},
                "context_clues": {{
                    "formation": "formation context if any",
                    "system": "tactical system if any",
                    "comparison_basis": "what to compare on if comparison"
                }}
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4", 
                messages=[{"role": "user", "content": entity_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            enhanced_entities = json.loads(response.choices[0].message.content)
            return enhanced_entities
            
        except Exception as e:
            logger.error(f"AI entity extraction failed: {e}")
            return self._basic_entity_extraction(query, understanding)
    
    def _create_analysis_request(self, 
                               query: str, 
                               understanding: QueryUnderstanding,
                               entities: Dict[str, Any],
                               context: Optional[QueryContext]) -> AnalysisRequest:
        """Create structured analysis request based on AI understanding."""
        
        analysis_type = understanding.suggested_analysis_type
        
        # Create base request parameters
        base_params = {
            "query": query,
            "confidence": understanding.confidence,
            "ai_reasoning": understanding.reasoning,
            "tactical_context": understanding.tactical_context,
            "entities": entities
        }
        
        # Route to specific request type based on analysis
        if analysis_type == "player_search":
            return self._create_player_search_request(base_params, entities)
        elif analysis_type == "player_comparison":
            return self._create_player_comparison_request(base_params, entities)
        elif analysis_type == "tactical_analysis":
            return self._create_tactical_analysis_request(base_params, entities)
        elif analysis_type == "position_analysis":
            return self._create_position_analysis_request(base_params, entities)
        else:
            return self._create_general_request(base_params, entities)
    
    def _create_player_search_request(self, base_params: Dict, entities: Dict) -> AnalysisRequest:
        """Create player search request with AI-enhanced criteria."""
        search_criteria = entities.get("search_criteria", {})
        tactical_reqs = entities.get("tactical_requirements", {})
        
        # Extract search parameters
        position = search_criteria.get("position")
        age_criteria = search_criteria.get("age")
        league = search_criteria.get("league")
        style = search_criteria.get("style")
        attributes = search_criteria.get("attributes", [])
        
        # Create player search request
        return PlayerSearchRequest(
            query_type=QueryType.PLAYER_SEARCH,
            position=position,
            league=league,
            min_minutes=500,  # Default minimum
            max_age=self._parse_age_criteria(age_criteria) if age_criteria else None,
            min_goals_per_90=None,
            min_assists_per_90=None,
            confidence=base_params["confidence"],
            ai_enhanced=True,
            tactical_context=base_params.get("tactical_context"),
            style_requirements=style,
            attribute_requirements=attributes,
            explicit_requirements=tactical_reqs.get("explicit", []),
            implicit_requirements=tactical_reqs.get("implicit", [])
        )
    
    def _create_player_comparison_request(self, base_params: Dict, entities: Dict) -> AnalysisRequest:
        """Create player comparison request with AI insights."""
        players = entities.get("players", {})
        mentioned_players = players.get("mentioned", [])
        
        if len(mentioned_players) < 2:
            # Look for implied players or suggest similar analysis
            mentioned_players.extend(players.get("variations", [])[:2])
        
        return PlayerComparisonRequest(
            query_type=QueryType.PLAYER_COMPARISON,
            player_names=mentioned_players,
            comparison_metrics=entities.get("context_clues", {}).get("comparison_basis", "overall"),
            confidence=base_params["confidence"],
            ai_enhanced=True,
            tactical_context=base_params.get("tactical_context"),
            comparison_focus=entities.get("tactical_requirements", {}).get("explicit", [])
        )
    
    def _create_tactical_analysis_request(self, base_params: Dict, entities: Dict) -> AnalysisRequest:
        """Create tactical analysis request with sophisticated reasoning."""
        context_clues = entities.get("context_clues", {})
        tactical_reqs = entities.get("tactical_requirements", {})
        
        return TacticalAnalysisRequest(
            query_type=QueryType.TACTICAL_ANALYSIS,
            tactical_question=base_params["query"],
            formation_context=context_clues.get("formation"),
            system_context=context_clues.get("system"),
            team_context=entities.get("teams", {}).get("mentioned", []),
            position_focus=entities.get("search_criteria", {}).get("position"),
            confidence=base_params["confidence"],
            ai_enhanced=True,
            tactical_requirements=tactical_reqs.get("explicit", []) + tactical_reqs.get("implicit", []),
            analysis_depth="comprehensive"
        )
    
    def _create_position_analysis_request(self, base_params: Dict, entities: Dict) -> AnalysisRequest:
        """Create position-specific analysis request."""
        position = entities.get("search_criteria", {}).get("position", "Midfielder")
        
        return PlayerSearchRequest(
            query_type=QueryType.POSITION_ANALYSIS,
            position=position,
            league=entities.get("search_criteria", {}).get("league"),
            min_minutes=500,
            confidence=base_params["confidence"],
            ai_enhanced=True,
            tactical_context=base_params.get("tactical_context"),
            analysis_focus="position_specific"
        )
    
    def _create_general_request(self, base_params: Dict, entities: Dict) -> AnalysisRequest:
        """Create general analysis request for complex queries."""
        return AnalysisRequest(
            query_type=QueryType.TACTICAL_ANALYSIS,
            confidence=base_params["confidence"],
            ai_enhanced=True,
            raw_query=base_params["query"],
            extracted_entities=entities,
            tactical_context=base_params.get("tactical_context")
        )
    
    def _parse_age_criteria(self, age_str: str) -> Optional[int]:
        """Parse age criteria from text."""
        if not age_str:
            return None
        
        # Look for patterns like "under 21", "below 25", "less than 23"
        patterns = [
            r"under\s+(\d+)",
            r"below\s+(\d+)", 
            r"less\s+than\s+(\d+)",
            r"younger\s+than\s+(\d+)",
            r"<\s*(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, age_str.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _fallback_process_query(self, query: str, context: Optional[QueryContext]) -> AnalysisRequest:
        """Fallback processing when AI is not available."""
        self.processing_stats["fallback_processed"] += 1
        
        try:
            # Basic pattern matching fallback
            query_lower = query.lower()
            
            # Player search patterns
            if any(word in query_lower for word in ["find", "search", "show", "who are"]):
                return self._create_basic_search_request(query, query_lower)
            
            # Comparison patterns  
            elif any(word in query_lower for word in ["compare", "vs", "versus", "against"]):
                return self._create_basic_comparison_request(query, query_lower)
            
            # Tactical patterns
            elif any(word in query_lower for word in ["alongside", "partner", "complement", "system"]):
                return self._create_basic_tactical_request(query, query_lower)
            
            else:
                return self._create_basic_search_request(query, query_lower)
                
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            return self._create_error_request(query, str(e))
    
    def _create_basic_search_request(self, query: str, query_lower: str) -> AnalysisRequest:
        """Create basic search request using pattern matching."""
        # Extract basic criteria
        position = None
        if "midfielder" in query_lower:
            position = "Midfielder"
        elif "forward" in query_lower or "striker" in query_lower:
            position = "Forward"
        elif "defender" in query_lower:
            position = "Defender"
        elif "goalkeeper" in query_lower:
            position = "Goalkeeper"
        
        # Age criteria
        age_match = re.search(r"under\s+(\d+)", query_lower)
        max_age = int(age_match.group(1)) if age_match else None
        
        return PlayerSearchRequest(
            query_type=QueryType.PLAYER_SEARCH,
            position=position,
            max_age=max_age,
            min_minutes=500,
            confidence=0.6,
            ai_enhanced=False
        )
    
    def _create_basic_comparison_request(self, query: str, query_lower: str) -> AnalysisRequest:
        """Create basic comparison request using pattern matching."""
        # Extract player names (simplified)
        # This is a basic implementation - would need more sophisticated name extraction
        player_names = []
        
        # Look for " vs " or " versus " patterns
        if " vs " in query_lower:
            parts = query.split(" vs ")
            if len(parts) == 2:
                player_names = [parts[0].strip().title(), parts[1].strip().title()]
        
        return PlayerComparisonRequest(
            query_type=QueryType.PLAYER_COMPARISON,
            player_names=player_names,
            confidence=0.5,
            ai_enhanced=False
        )
    
    def _create_basic_tactical_request(self, query: str, query_lower: str) -> AnalysisRequest:
        """Create basic tactical request using pattern matching."""
        return TacticalAnalysisRequest(
            query_type=QueryType.TACTICAL_ANALYSIS,
            tactical_question=query,
            confidence=0.4,
            ai_enhanced=False
        )
    
    def _fallback_query_understanding(self, query: str) -> QueryUnderstanding:
        """Fallback query understanding using basic analysis."""
        return QueryUnderstanding(
            intent="Basic query analysis",
            entities={},
            tactical_context=None,
            complexity_score=0.3,
            confidence=0.5,
            reasoning="Fallback analysis - AI not available",
            suggested_analysis_type="player_search"
        )
    
    def _basic_entity_extraction(self, query: str, understanding: QueryUnderstanding) -> Dict[str, Any]:
        """Basic entity extraction fallback."""
        return {
            "players": {"mentioned": [], "variations": [], "implied": []},
            "teams": {"mentioned": [], "leagues": []},
            "tactical_requirements": {"explicit": [], "implicit": [], "constraints": []},
            "search_criteria": {},
            "context_clues": {}
        }
    
    def _create_error_request(self, query: str, error: str) -> AnalysisRequest:
        """Create error request for failed processing."""
        return AnalysisRequest(
            query_type=QueryType.PLAYER_SEARCH,
            confidence=0.0,
            ai_enhanced=False,
            error=error,
            raw_query=query
        )
    
    # Utility methods
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get query processing statistics."""
        return self.processing_stats.copy()
    
    def enhance_query_with_context(self, query: str, previous_queries: List[str]) -> str:
        """Enhance query with context from previous queries."""
        if not self.enable_ai or not previous_queries:
            return query
        
        try:
            context_prompt = f"""
            Enhance this soccer query using context from previous queries:
            
            Current Query: "{query}"
            Previous Queries: {previous_queries[-3:]}  # Last 3 queries
            
            Return an enhanced query that:
            1. Incorporates relevant context from previous queries
            2. Maintains the user's current intent
            3. Improves clarity and specificity
            
            Return just the enhanced query text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": context_prompt}],
                max_tokens=100,
                temperature=0.2
            )
            
            enhanced_query = response.choices[0].message.content.strip()
            logger.info(f"Enhanced query: '{query}' -> '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            logger.debug(f"Query enhancement failed: {e}")
            return query
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest improvements to unclear queries."""
        if not self.enable_ai:
            return [
                "Try being more specific about position or league",
                "Include player names for comparisons",
                "Specify age ranges or playing style preferences"
            ]
        
        try:
            suggestion_prompt = f"""
            Suggest improvements for this soccer query to get better results:
            
            Query: "{query}"
            
            Provide 3-4 specific suggestions that would:
            1. Make the query more precise
            2. Add helpful tactical context
            3. Include relevant search criteria
            
            Return as a JSON array of suggestion strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": suggestion_prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions
            
        except Exception as e:
            logger.debug(f"Query suggestions failed: {e}")
            return [
                "Try being more specific about the type of analysis you want",
                "Include specific player names, positions, or leagues",
                "Add tactical context like formation or playing style"
            ]