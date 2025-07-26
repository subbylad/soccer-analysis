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

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

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
            players_mentioned = parsed.get('players_mentioned', [])
            target_player = players_mentioned[0] if players_mentioned else None
            
            age_constraints = parsed.get('age_constraints', {})
            
            return TacticalAnalysisRequest(
                **base_data,
                target_player=target_player,
                position=parsed.get('position'),
                league=parsed.get('league'),
                tactical_context=parsed.get('tactical_context', ''),
                priority_stats=parsed.get('priority_stats', []),
                reasoning=parsed.get('reasoning', ''),
                age_min=age_constraints.get('min') if age_constraints else None,
                age_max=age_constraints.get('max') if age_constraints else None
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
            players_mentioned = parsed.get('players_mentioned', [])
            player_name = players_mentioned[0] if players_mentioned else ''
            
            return PlayerSearchRequest(
                **base_data,
                player_name=player_name,
                position=parsed.get('position'),
                league=parsed.get('league')
            )


class GPT4CodeExecutor:
    """Safe execution environment for GPT-4 generated Python code."""
    
    def __init__(self, analyzer):
        """Initialize with CleanPlayerAnalyzer instance."""
        self.analyzer = analyzer
        self.allowed_modules = {
            'pandas': pd,
            'numpy': np,
            'logging': logging
        }
        
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Safely execute GPT-4 generated Python code.
        
        Args:
            code: Python code string generated by GPT-4
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Create restricted execution environment
            exec_globals = {
                'analyzer': self.analyzer,
                'pd': pd,
                'np': np,
                'pandas': pd,
                'numpy': np,
                # Add safe utility functions
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sum': sum,
                'range': range,
                'enumerate': enumerate,
            }
            
            exec_locals = {}
            
            # Execute the code in restricted environment
            exec(code, exec_globals, exec_locals)
            
            # Return the result - GPT-4 should assign result to 'result' variable
            if 'result' in exec_locals:
                return {
                    'success': True,
                    'result': exec_locals['result'],
                    'data': exec_locals.get('data'),
                    'summary': exec_locals.get('summary', ''),
                    'insights': exec_locals.get('insights', [])
                }
            else:
                return {
                    'success': False,
                    'error': 'Code executed but no result variable found'
                }
                
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            # Also log the locals to see what was available
            logger.error(f"Available globals: {list(exec_globals.keys())}")
            logger.error(f"Code that failed: {code}")
            return {
                'success': False,
                'error': str(e)
            }


class GPT4FirstQueryProcessor:
    """GPT-4 first query processor that generates and executes Python code."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.client = None
        
        if OpenAI is None:
            logger.warning("OpenAI not installed. GPT-4 processing disabled.")
            return
            
        # Try to get API key from parameter, environment, or disable
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("GPT-4 first query processing enabled")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("No OpenAI API key provided. GPT-4 processing disabled.")
    
    def process_query(self, query: str, analyzer, context: Optional[QueryContext] = None) -> Dict[str, Any]:
        """
        Process query using GPT-4 to generate and execute Python code.
        
        Args:
            query: Natural language query
            analyzer: CleanPlayerAnalyzer instance
            context: Optional query context
            
        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            return {
                'success': False,
                'error': 'GPT-4 not available. Please provide OpenAI API key.',
                'suggestions': [
                    "Set OPENAI_API_KEY environment variable",
                    "Initialize API with openai_api_key parameter"
                ]
            }
        
        try:
            # Create comprehensive context about available methods
            analyzer_context = self._create_analyzer_context()
            
            # Build GPT-4 prompt
            system_prompt = f"""You are a soccer analytics expert that generates Python code to analyze player data.

You have access to a CleanPlayerAnalyzer instance called 'analyzer' with these methods and data:

{analyzer_context}

AVAILABLE IMPORTS AND VARIABLES:
- analyzer: CleanPlayerAnalyzer instance
- pd: pandas library
- np: numpy library  
- Standard Python functions: len, str, int, float, list, dict, max, min, abs, round, sum, range, enumerate

IMPORTANT INSTRUCTIONS:
1. Generate Python code that uses the analyzer methods to answer the user's query
2. Always assign your final result to a variable called 'result'
3. If returning player data, ensure it's a pandas DataFrame or Python list/dict
4. You can also set these optional variables:
   - 'data': Additional data for visualization (DataFrame or dict)
   - 'summary': A brief text summary of findings
   - 'insights': A list of key insights or observations
5. Only use the methods available on the analyzer object and the imported libraries
6. Handle potential errors gracefully using try/except if needed
7. For comparisons, use analyzer.compare_players() 
8. For searches, use analyzer.search_players()
9. For young prospects, use analyzer.get_young_prospects()
10. For position analysis, use analyzer.get_players_by_position() and analyzer.get_position_leaders()
11. For filtering by league, use: df[df.index.get_level_values('league') == 'LEAGUE_NAME']
12. Common league names: 'ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 'GER-Bundesliga', 'FRA-Ligue 1'

Example code structure:
```python
# Your analysis code here using analyzer methods
players = analyzer.search_players("Haaland")
result = players
summary = f"Found {{len(players)}} players"
insights = ["Key insight 1", "Key insight 2"]
```"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate Python code to analyze this query: {query}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extract code from response
            generated_code = response.choices[0].message.content.strip()
            
            # Clean up code - remove markdown formatting if present
            if "```python" in generated_code:
                generated_code = generated_code.split("```python")[1].split("```")[0].strip()
            elif "```" in generated_code:
                generated_code = generated_code.split("```")[1].split("```")[0].strip()
            
            logger.info(f"Generated code: {generated_code}")
            
            # Execute the generated code
            executor = GPT4CodeExecutor(analyzer)
            execution_result = executor.execute_code(generated_code)
            
            if execution_result['success']:
                return {
                    'success': True,
                    'result': execution_result['result'],
                    'data': execution_result.get('data'),
                    'summary': execution_result.get('summary', ''),
                    'insights': execution_result.get('insights', []),
                    'generated_code': generated_code,
                    'query_type': 'gpt4_analysis',
                    'original_query': query
                }
            else:
                return {
                    'success': False,
                    'error': execution_result['error'],
                    'generated_code': generated_code,
                    'original_query': query
                }
                
        except Exception as e:
            logger.error(f"GPT-4 query processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_query': query
            }
    
    def _create_analyzer_context(self) -> str:
        """Create comprehensive documentation of analyzer methods for GPT-4."""
        return """
CLEANPLAYERANALYZER METHODS:

1. search_players(name_pattern, min_minutes=300, position=None)
   - Search for players by name
   - Returns: DataFrame with player data and key stats
   - Example: analyzer.search_players("Haaland", min_minutes=500)

2. compare_players(player_names)
   - Compare multiple players across key metrics
   - Args: List of player names 
   - Returns: DataFrame with comparison data
   - Example: analyzer.compare_players(["Haaland", "Mbappé"])

3. get_players_by_position(position, min_minutes=500)
   - Get all players by position
   - Args: position name (Midfielder, Forward, Defender, Goalkeeper)
   - Returns: DataFrame with players in position
   - Example: analyzer.get_players_by_position("Midfielder")

4. get_position_leaders(position, stat, top_n=10, min_minutes=500)
   - Get top performers by position and stat
   - Args: position, stat name, number to return
   - Returns: DataFrame with top performers
   - Example: analyzer.get_position_leaders("Forward", "goals", 10)

5. find_similar_midfielders(target_player, league_filter=None, top_n=10, min_minutes=500, attacking=False, defensive=False)
   - Find midfielders similar to target player
   - Returns: DataFrame with similar players and similarity scores
   - Example: analyzer.find_similar_midfielders("Pedri", league_filter="FRA-Ligue 1")

6. get_young_prospects(max_age=23, min_minutes=500)
   - Get young players with high potential
   - Returns: DataFrame with prospects and potential_score column
   - Example: analyzer.get_young_prospects(max_age=21)
   - Note: Use 'potential_score' column, not 'potential'

DATA STRUCTURE:
- All data has MultiIndex: (league, season, team, player)
- Available leagues: ENG-Premier League, ESP-La Liga, ITA-Serie A, GER-Bundesliga, FRA-Ligue 1
- Common columns: position, age, minutes, goals, assists, goals_per_90, assists_per_90, expected_goals, expected_assists, progressive_carries, progressive_passes

FILTERING EXAMPLES:
- Filter by league: df[df.index.get_level_values('league') == 'ENG-Premier League']
- Filter by position: df[df['position'].str.contains('Midfielder', case=False)]
- Filter by age: df[df['age'] <= 23]
- Filter by minutes: df[df['minutes'] >= 1000]

Remember to always assign your final result to the 'result' variable!
"""


class QueryProcessor:
    """Main query processor - now GPT-4 first with fallback."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.gpt4_processor = GPT4FirstQueryProcessor(api_key=openai_api_key)
        # Keep legacy processors for fallback
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
        
        # NEW ARCHITECTURE: GPT-4 FIRST APPROACH
        # Only use pattern matching for very simple, exact matches
        # Send everything else to GPT-4 for intelligent processing
        
        # Check for exact comparison patterns only (most reliable)
        if " vs " in query.lower() or " versus " in query.lower():
            if request := self.pattern_matcher.match(query):
                logger.info(f"Simple comparison pattern matched: {request.query_type}")
                return request
        
        # For all other queries, go to GPT-4 first
        if self.gpt4_processor.client:  # Only if GPT-4 is available
            logger.info("Routing to GPT-4 first processing")
            return GPT4AnalysisRequest(
                original_query=query,
                confidence=0.9  # High confidence for GPT-4 processing
            )
        
        # Fallback to legacy system if GPT-4 is not available
        logger.info("GPT-4 not available, using legacy processing")
        
        # Try GPT-4 enhanced parsing (might work without full GPT-4)
        if self.gpt_processor.can_enhance(query):
            if request := self.gpt_processor.enhance_query(query):
                logger.info(f"GPT-4 enhanced request: {request.query_type}")
                return request
        
        # Pattern matching fallback
        if request := self.pattern_matcher.match(query):
            logger.info(f"Fallback pattern matched: {request.query_type}")
            return request
        
        # Dynamic building fallback
        if request := self.dynamic_builder.build(query):
            logger.info(f"Dynamic request built: {request.query_type}")
            return request
        
        # Unknown query
        logger.info("Creating unknown request")
        return UnknownRequest(
            original_query=query,
            suggested_queries=self.fallback_suggestions,
            confidence=0.0
        )