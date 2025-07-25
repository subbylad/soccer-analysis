"""
Query Processor - Natural Language to Structured Requests

Implements a 4-tier approach:
1. Pattern matching for common queries
2. Dynamic combination for flexible queries  
3. GPT-4 enhanced parsing for complex tactical queries
4. LLM fallback for novel requests
"""

import re
import os
import json
from typing import List, Dict, Optional, Union
import logging
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .types import *

logger = logging.getLogger(__name__)

class PatternMatcher:
    """Tier 1: Pattern matching for common queries."""
    
    def __init__(self):
        self.patterns = {
            # Player search patterns
            r"(?:find|search|show|get)\s+(.+?)(?:\s|$)": self._create_player_search,
            r"(?:who is|tell me about)\s+(.+?)(?:\s|$)": self._create_player_search,
            
            # Comparison patterns  
            r"compare\s+(.+?)\s+(?:vs|versus|against|and)\s+(.+?)(?:\s|$)": self._create_comparison,
            r"(.+?)\s+(?:vs|versus|against)\s+(.+?)(?:\s|$)": self._create_comparison,
            
            # Young prospects patterns
            r"(?:best|top|good)\s+young\s+(.+?)(?:\s|$)": self._create_young_prospects,
            r"young\s+(?:prospects|talents|players)\s*(?:in\s+(.+?))?(?:\s|$)": self._create_young_prospects,
            r"(?:prospects|talents)\s+under\s+(\d+)": self._create_young_prospects_age,
            
            # Top performers patterns
            r"(?:best|top|leading)\s+(.+?)\s+(?:scorers|goalscorers)": self._create_top_scorers,
            r"(?:best|top|leading)\s+(.+?)\s+(?:assists|assist providers)": self._create_top_assisters,
            r"(?:best|top|leading)\s+(.+?)(?:\s+in\s+(.+?))?(?:\s|$)": self._create_top_performers,
            
            # Position-specific patterns
            r"(?:show|find|get)\s+(.+?)\s+(midfielders|defenders|forwards|goalkeepers)": self._create_position_search,
            r"(midfielders|defenders|forwards|goalkeepers)\s+(?:in\s+(.+?))?(?:\s|$)": self._create_position_search,
        }
        
        # Common entity mappings
        self.position_aliases = {
            'striker': 'Forward', 'strikers': 'Forward',
            'forward': 'Forward', 'forwards': 'Forward', 
            'midfielder': 'Midfielder', 'midfielders': 'Midfielder',
            'mid': 'Midfielder', 'mids': 'Midfielder',
            'defender': 'Defender', 'defenders': 'Defender',
            'cb': 'Defender', 'fullback': 'Defender',
            'goalkeeper': 'Goalkeeper', 'goalkeepers': 'Goalkeeper',
            'keeper': 'Goalkeeper', 'gk': 'Goalkeeper'
        }
        
        self.league_aliases = {
            'premier league': 'ENG-Premier League', 'epl': 'ENG-Premier League',
            'la liga': 'ESP-La Liga', 'laliga': 'ESP-La Liga',
            'serie a': 'ITA-Serie A', 'seriea': 'ITA-Serie A',
            'bundesliga': 'GER-Bundesliga', 'german': 'GER-Bundesliga',
            'ligue 1': 'FRA-Ligue 1', 'ligue1': 'FRA-Ligue 1', 'french': 'FRA-Ligue 1'
        }
    
    def match(self, query: str) -> Optional[AnalysisRequest]:
        """Try to match query against known patterns."""
        query = query.lower().strip()
        
        for pattern, handler in self.patterns.items():
            if match := re.search(pattern, query, re.IGNORECASE):
                try:
                    request = handler(match, query)
                    if request:
                        request.confidence = 0.9  # High confidence for pattern matches
                        logger.info(f"Pattern matched: {pattern} -> {request.query_type}")
                        return request
                except Exception as e:
                    logger.warning(f"Pattern handler failed: {e}")
                    continue
        
        return None
    
    def _create_player_search(self, match, full_query: str) -> Optional[PlayerSearchRequest]:
        """Create player search request from pattern match."""
        player_name = match.group(1).strip()
        
        # Extract additional filters from full query
        position = self._extract_position(full_query)
        league = self._extract_league(full_query)
        min_minutes = self._extract_minutes(full_query)
        
        return PlayerSearchRequest(
            original_query=full_query,
            player_name=player_name,
            position=position,
            league=league,
            min_minutes=min_minutes
        )
    
    def _create_comparison(self, match, full_query: str) -> Optional[PlayerComparisonRequest]:
        """Create comparison request from pattern match."""
        player1 = match.group(1).strip()
        player2 = match.group(2).strip()
        
        return PlayerComparisonRequest(
            original_query=full_query,
            player_names=[player1, player2]
        )
    
    def _create_young_prospects(self, match, full_query: str) -> Optional[YoungProspectsRequest]:
        """Create young prospects request from pattern match."""
        position_text = match.group(1) if match.groups() else None
        position = self._extract_position(position_text or full_query)
        league = self._extract_league(full_query)
        
        # Look for age references
        age_match = re.search(r'under\s+(\d+)', full_query)
        max_age = int(age_match.group(1)) if age_match else 23
        
        return YoungProspectsRequest(
            original_query=full_query,
            position=position,
            league=league,
            max_age=max_age
        )
    
    def _create_young_prospects_age(self, match, full_query: str) -> Optional[YoungProspectsRequest]:
        """Create young prospects request with specific age."""
        max_age = int(match.group(1))
        position = self._extract_position(full_query)
        league = self._extract_league(full_query)
        
        return YoungProspectsRequest(
            original_query=full_query,
            position=position,
            league=league,
            max_age=max_age
        )
    
    def _create_top_scorers(self, match, full_query: str) -> Optional[TopPerformersRequest]:
        """Create top scorers request."""
        context = match.group(1) if match.groups() else ""
        position = self._extract_position(full_query)
        league = self._extract_league(full_query)
        
        return TopPerformersRequest(
            original_query=full_query,
            stat='goals',
            position=position,
            league=league
        )
    
    def _create_top_assisters(self, match, full_query: str) -> Optional[TopPerformersRequest]:
        """Create top assist providers request."""
        context = match.group(1) if match.groups() else ""
        position = self._extract_position(full_query)
        league = self._extract_league(full_query)
        
        return TopPerformersRequest(
            original_query=full_query,
            stat='assists',
            position=position,
            league=league
        )
    
    def _create_top_performers(self, match, full_query: str) -> Optional[TopPerformersRequest]:
        """Create general top performers request."""
        stat_context = match.group(1).strip()
        league_context = match.group(2) if len(match.groups()) > 1 else None
        
        # Try to extract stat from context
        stat = self._extract_stat(stat_context)
        position = self._extract_position(full_query)
        league = self._extract_league(league_context or full_query)
        
        return TopPerformersRequest(
            original_query=full_query,
            stat=stat or 'goals',  # Default to goals
            position=position,
            league=league
        )
    
    def _create_position_search(self, match, full_query: str) -> Optional[CustomFilterRequest]:
        """Create position-based search request."""
        if len(match.groups()) >= 2:
            context = match.group(1)
            position_text = match.group(2)
        else:
            position_text = match.group(1)
            context = ""
        
        position = self._normalize_position(position_text)
        league = self._extract_league(full_query)
        
        return CustomFilterRequest(
            original_query=full_query,
            position=position,
            league=league
        )
    
    def _extract_position(self, text: str) -> Optional[str]:
        """Extract position from text."""
        if not text:
            return None
            
        text = text.lower()
        for alias, position in self.position_aliases.items():
            if alias in text:
                return position
        return None
    
    def _extract_league(self, text: str) -> Optional[str]:
        """Extract league from text."""
        if not text:
            return None
            
        text = text.lower()
        for alias, league in self.league_aliases.items():
            if alias in text:
                return league
        return None
    
    def _extract_stat(self, text: str) -> Optional[str]:
        """Extract stat from text."""
        stat_mapping = {
            'scorer': 'goals', 'goal': 'goals', 'goals': 'goals',
            'assist': 'assists', 'assists': 'assists', 
            'passer': 'progressive_passes', 'passing': 'progressive_passes',
            'tackler': 'tackles', 'tackles': 'tackles',
            'defender': 'defensive_actions'
        }
        
        text = text.lower()
        for keyword, stat in stat_mapping.items():
            if keyword in text:
                return stat
        return None
    
    def _extract_minutes(self, text: str) -> int:
        """Extract minimum minutes from text."""
        # Look for patterns like "500+ minutes", "more than 1000 minutes"
        minutes_match = re.search(r'(\d+)\+?\s*minutes?', text)
        if minutes_match:
            return int(minutes_match.group(1))
        
        # Default based on context
        if any(word in text for word in ['young', 'prospect']):
            return 1000
        return 500
    
    def _normalize_position(self, position_text: str) -> Optional[str]:
        """Normalize position text to standard format."""
        return self._extract_position(position_text)


class DynamicQueryBuilder:
    """Tier 2: Dynamic combination for flexible queries."""
    
    def __init__(self):
        self.entity_extractor = EntityExtractor()
    
    def build(self, query: str) -> Optional[AnalysisRequest]:
        """Try to build request from extracted entities."""
        entities = self.entity_extractor.extract(query)
        
        if self._can_build_custom_filter(entities):
            return self._build_custom_filter(query, entities)
        
        return None
    
    def _can_build_custom_filter(self, entities: EntityExtraction) -> bool:
        """Check if we can build a custom filter from entities."""
        # Need at least one meaningful entity
        return bool(entities.positions or entities.leagues or entities.stats or entities.age_references)
    
    def _build_custom_filter(self, query: str, entities: EntityExtraction) -> CustomFilterRequest:
        """Build custom filter request from entities."""
        request = CustomFilterRequest(original_query=query)
        request.confidence = 0.7  # Medium confidence for dynamic building
        
        # Set basic filters
        if entities.positions:
            request.position = entities.positions[0]  # Take first position
        
        if entities.leagues:
            request.league = entities.leagues[0]  # Take first league
        
        # Handle age references
        for age_ref in entities.age_references:
            age_match = re.search(r'(\d+)', age_ref)
            if age_match:
                age_value = int(age_match.group(1))
                if 'under' in age_ref or 'younger' in age_ref:
                    request.age_max = age_value
                elif 'over' in age_ref or 'older' in age_ref:
                    request.age_min = age_value
        
        # Handle stat filters (basic implementation)
        if entities.stats:
            # For now, just note them - more sophisticated filtering would go here
            pass
        
        return request


class EntityExtractor:
    """Extract entities from natural language queries."""
    
    def __init__(self):
        self.position_patterns = [
            r'\b(midfielder|midfielders|mid|mids)\b',
            r'\b(defender|defenders|defence|defense)\b', 
            r'\b(forward|forwards|striker|strikers|attacker)\b',
            r'\b(goalkeeper|goalkeepers|keeper|gk)\b'
        ]
        
        self.league_patterns = [
            r'\b(premier league|epl)\b',
            r'\b(la liga|laliga)\b',
            r'\b(serie a|seriea)\b', 
            r'\b(bundesliga|german)\b',
            r'\b(ligue 1|ligue1|french)\b'
        ]
        
        self.stat_patterns = [
            r'\b(goals?|scoring|scorer)\b',
            r'\b(assists?|assisting|provider)\b',
            r'\b(passing|passes)\b',
            r'\b(tackles?|tackling)\b',
            r'\b(interceptions?)\b'
        ]
        
        self.age_patterns = [
            r'\b(under|younger than|below)\s+(\d+)\b',
            r'\b(over|older than|above)\s+(\d+)\b',
            r'\b(\d+)\s*(?:years?\s*)?(?:old|age)\b'
        ]
        
        self.comparison_patterns = [
            r'\b(vs|versus|against|compared to)\b',
            r'\b(and|&)\b'
        ]
        
        self.superlative_patterns = [
            r'\b(best|top|greatest|leading|highest)\b',
            r'\b(worst|bottom|lowest)\b'
        ]
    
    def extract(self, query: str) -> EntityExtraction:
        """Extract all entities from query."""
        query = query.lower()
        
        return EntityExtraction(
            positions=self._extract_by_patterns(query, self.position_patterns),
            leagues=self._extract_by_patterns(query, self.league_patterns),
            stats=self._extract_by_patterns(query, self.stat_patterns),
            age_references=self._extract_by_patterns(query, self.age_patterns),
            comparison_indicators=self._extract_by_patterns(query, self.comparison_patterns),
            superlatives=self._extract_by_patterns(query, self.superlative_patterns)
        )
    
    def _extract_by_patterns(self, query: str, patterns: List[str]) -> List[str]:
        """Extract matches for given patterns."""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, query, re.IGNORECASE)
            matches.extend(found)
        return list(set(matches))  # Remove duplicates


class GPTEnhancedQueryProcessor:
    """Tier 3: GPT-4 enhanced parsing for complex tactical queries."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.client = None
        
        if OpenAI is None:
            logger.warning("OpenAI not installed. GPT-4 parsing disabled.")
            return
            
        # Try to get API key from parameter, environment, or disable
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("GPT-4 enhanced query processing enabled")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("No OpenAI API key provided. GPT-4 parsing disabled.")
    
    def can_enhance(self, query: str) -> bool:
        """Check if this query would benefit from GPT-4 enhancement."""
        if not self.client:
            return False
            
        # Keywords that indicate complex tactical analysis
        tactical_keywords = [
            'alongside', 'partner', 'complement', 'fit', 'system', 'style',
            'replace', 'similar to', 'like', 'alternative', 'backup',
            'formation', 'tactical', 'playing style', 'characteristics',
            'profile', 'attributes', 'skillset', 'ability'
        ]
        
        # Complex query patterns that need reasoning
        complex_patterns = [
            r'who (?:can|could|would) .+alongside',
            r'(?:find|show|get) .+ who (?:can|could) .+ with',
            r'(?:alternative|replacement|backup) (?:for|to)',
            r'similar (?:to|like|as)',
            r'complement .+ in .+ system',
            r'fit .+ playing style'
        ]
        
        query_lower = query.lower()
        
        # Check for tactical keywords
        if any(keyword in query_lower for keyword in tactical_keywords):
            return True
            
        # Check for complex patterns
        if any(re.search(pattern, query_lower) for pattern in complex_patterns):
            return True
            
        return False
    
    def enhance_query(self, query: str) -> Optional[AnalysisRequest]:
        """Use GPT-4 to parse complex tactical queries."""
        if not self.client or not self.can_enhance(query):
            return None
            
        try:
            system_prompt = """You are a soccer analytics expert. Parse natural language queries into structured analysis requests.

Focus on extracting:
1. Player names mentioned
2. Position requirements (midfielder, defender, forward, etc.)
3. League preferences (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
4. Age constraints (young prospects, experienced, etc.)
5. Tactical requirements (playing style, formation fit, partner compatibility)
6. Statistical priorities (goals, assists, passing, defensive actions)

Return a JSON object with these fields:
{
    "query_type": "player_search|comparison|young_prospects|tactical_analysis",
    "players_mentioned": ["player1", "player2"],
    "position": "Midfielder|Defender|Forward|Goalkeeper",
    "league": "ENG-Premier League|ESP-La Liga|ITA-Serie A|GER-Bundesliga|FRA-Ligue 1",
    "age_constraints": {"min": 18, "max": 35},
    "tactical_context": "Description of tactical requirements",
    "priority_stats": ["goals", "assists", "progressive_passes"],
    "reasoning": "Explanation of what the user is looking for"
}

If the query asks for players to complement/partner with someone, use "tactical_analysis" type."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this soccer query: {query}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the GPT-4 response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                parsed = json.loads(content)
                return self._create_request_from_gpt_response(query, parsed)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse GPT-4 JSON response: {content}")
                return None
                
        except Exception as e:
            logger.error(f"GPT-4 query enhancement failed: {e}")
            return None
    
    def _create_request_from_gpt_response(self, original_query: str, parsed: Dict) -> AnalysisRequest:
        """Create appropriate request object from GPT-4 parsed data."""
        query_type = parsed.get('query_type', 'player_search')
        
        # Create base request data
        base_data = {
            'original_query': original_query,
            'confidence': 0.8  # High confidence for GPT-4 parsing
        }
        
        if query_type == 'tactical_analysis':
            # Create a custom tactical analysis request
            return TacticalAnalysisRequest(
                **base_data,
                target_player=parsed.get('players_mentioned', [None])[0],
                position=parsed.get('position'),
                league=parsed.get('league'),
                tactical_context=parsed.get('tactical_context', ''),
                priority_stats=parsed.get('priority_stats', []),
                reasoning=parsed.get('reasoning', ''),
                age_min=parsed.get('age_constraints', {}).get('min'),
                age_max=parsed.get('age_constraints', {}).get('max')
            )
        elif query_type == 'comparison':
            return PlayerComparisonRequest(
                **base_data,
                player_names=parsed.get('players_mentioned', [])
            )
        elif query_type == 'young_prospects':
            return YoungProspectsRequest(
                **base_data,
                position=parsed.get('position'),
                league=parsed.get('league'),
                max_age=parsed.get('age_constraints', {}).get('max', 23)
            )
        else:  # Default to player_search
            return PlayerSearchRequest(
                **base_data,
                player_name=parsed.get('players_mentioned', [None])[0] or '',
                position=parsed.get('position'),
                league=parsed.get('league')
            )


class QueryProcessor:
    """Main query processor coordinating all tiers."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.pattern_matcher = PatternMatcher()
        self.dynamic_builder = DynamicQueryBuilder()
        self.gpt_processor = GPTEnhancedQueryProcessor(api_key=openai_api_key)
        self.fallback_suggestions = [
            "Try: 'Compare [player1] vs [player2]'",
            "Try: 'Find young midfielders'",
            "Try: 'Top scorers in Premier League'",
            "Try: 'Show me defenders under 25'",
            "Try: 'Who can play alongside [player name]?'"
        ]
    
    def process_query(self, query: str, context: Optional[QueryContext] = None) -> AnalysisRequest:
        """Process natural language query into structured request."""
        logger.info(f"Processing query: {query}")
        
        # Tier 1: Pattern matching
        if request := self.pattern_matcher.match(query):
            logger.info(f"Matched pattern: {request.query_type}")
            return request
        
        # Tier 2: Dynamic building
        if request := self.dynamic_builder.build(query):
            logger.info(f"Built dynamic request: {request.query_type}")
            return request
        
        # Tier 3: GPT-4 enhanced parsing
        if request := self.gpt_processor.enhance_query(query):
            logger.info(f"GPT-4 enhanced request: {request.query_type}")
            return request
        
        # Tier 4: Unknown query fallback
        logger.info("Could not parse query, returning unknown request")
        return UnknownRequest(
            original_query=query,
            suggested_queries=self.fallback_suggestions,
            confidence=0.0
        )