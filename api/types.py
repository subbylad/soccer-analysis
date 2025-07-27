"""
Data types for the Soccer Analytics API

Defines request and response types for structured communication
between query processing and analysis execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import pandas as pd

class QueryType(Enum):
    """Types of queries the system can handle."""
    PLAYER_SEARCH = "player_search"
    PLAYER_COMPARISON = "player_comparison"
    YOUNG_PROSPECTS = "young_prospects"
    TOP_PERFORMERS = "top_performers"
    POSITION_ANALYSIS = "position_analysis"
    TEAM_ANALYSIS = "team_analysis"
    SIMILAR_PLAYERS = "similar_players"
    CUSTOM_FILTER = "custom_filter"
    TACTICAL_ANALYSIS = "tactical_analysis"  # GPT-4 enhanced tactical analysis
    GPT4_ANALYSIS = "gpt4_analysis"  # Direct GPT-4 code generation and execution
    UNKNOWN = "unknown"

class ResponseType(Enum):
    """Types of responses the system can generate."""
    PLAYER_LIST = "player_list"
    COMPARISON_TABLE = "comparison_table"
    CHART_DATA = "chart_data"
    SUMMARY_STATS = "summary_stats"
    ERROR = "error"
    SUGGESTION = "suggestion"

# Base Request Types
@dataclass
class AnalysisRequest:
    """Base class for all analysis requests."""
    query_type: QueryType = QueryType.UNKNOWN
    original_query: str = ""
    confidence: float = 1.0  # How confident we are in the interpretation
    ai_enhanced: bool = False  # Support for AI-enhanced analysis
    error: Optional[str] = None  # Support for error messages in requests
    raw_query: Optional[str] = None  # Support for original raw query text
    
@dataclass
class PlayerSearchRequest(AnalysisRequest):
    """Request to search for specific players."""
    player_name: str = ""
    min_minutes: int = 500
    position: Optional[str] = None
    league: Optional[str] = None
    
    def __post_init__(self):
        self.query_type = QueryType.PLAYER_SEARCH

@dataclass
class PlayerComparisonRequest(AnalysisRequest):
    """Request to compare multiple players."""
    player_names: List[str] = field(default_factory=list)
    comparison_stats: List[str] = field(default_factory=lambda: ['goals', 'assists', 'goals_per_90', 'assists_per_90'])
    min_minutes: int = 500
    
    def __post_init__(self):
        self.query_type = QueryType.PLAYER_COMPARISON

@dataclass
class YoungProspectsRequest(AnalysisRequest):
    """Request to find young player prospects."""
    max_age: int = 23
    min_minutes: int = 1000
    position: Optional[str] = None
    league: Optional[str] = None
    limit: int = 10
    
    def __post_init__(self):
        self.query_type = QueryType.YOUNG_PROSPECTS

@dataclass
class TopPerformersRequest(AnalysisRequest):
    """Request to find top performers in a specific stat."""
    stat: str = "goals"
    position: Optional[str] = None
    league: Optional[str] = None
    min_minutes: int = 500
    limit: int = 10
    
    def __post_init__(self):
        self.query_type = QueryType.TOP_PERFORMERS

@dataclass
class CustomFilterRequest(AnalysisRequest):
    """Request with custom filtering criteria."""
    position: Optional[str] = None
    league: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    min_minutes: int = 500
    stat_filters: Dict[str, Dict[str, float]] = field(default_factory=dict)  # {'goals': {'min': 10, 'max': 50}}
    limit: int = 20
    
    def __post_init__(self):
        self.query_type = QueryType.CUSTOM_FILTER

@dataclass
class TacticalAnalysisRequest(AnalysisRequest):
    """Request for GPT-4 enhanced tactical analysis (e.g., finding tactical partners)."""
    target_player: Optional[str] = None  # Player to find partners/alternatives for
    position: Optional[str] = None
    league: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    min_minutes: int = 500
    tactical_context: str = ""  # GPT-4 generated context
    priority_stats: List[str] = field(default_factory=list)  # Key stats for analysis
    reasoning: str = ""  # GPT-4 reasoning for the request
    limit: int = 10
    
    def __post_init__(self):
        self.query_type = QueryType.TACTICAL_ANALYSIS

@dataclass
class GPT4AnalysisRequest(AnalysisRequest):
    """Request for direct GPT-4 code generation and execution."""
    
    def __post_init__(self):
        self.query_type = QueryType.GPT4_ANALYSIS

@dataclass
class UnknownRequest(AnalysisRequest):
    """Request that couldn't be parsed into a known pattern."""
    suggested_queries: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.query_type = QueryType.UNKNOWN

# Response Types
@dataclass
class AnalysisResponse:
    """Base class for all analysis responses."""
    success: bool = False
    response_type: ResponseType = ResponseType.PLAYER_LIST
    original_request: Optional[AnalysisRequest] = None
    execution_time: float = 0.0
    error: Optional[str] = None  # Support for error messages
    analysis_type: Optional[str] = None  # Support for analysis type classification
    data: Any = None  # Support for general data payload
    summary: str = ""  # Support for summary text
    total_found: int = 0  # Support for result count
    ai_enhanced: bool = False  # Support for AI-enhanced analysis flag
    confidence: float = 0.0  # Support for confidence scoring
    ai_insights: str = ""  # Support for AI-generated insights
    
@dataclass
class PlayerListResponse(AnalysisResponse):
    """Response containing a list of players."""
    players: pd.DataFrame = field(default_factory=pd.DataFrame)
    total_found: int = 0
    summary: str = ""
    
    def __post_init__(self):
        self.response_type = ResponseType.PLAYER_LIST

@dataclass
class ComparisonResponse(AnalysisResponse):
    """Response containing player comparison data."""
    comparison_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    chart_data: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    player_cards: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.response_type = ResponseType.COMPARISON_TABLE

@dataclass
class ProspectsResponse(AnalysisResponse):
    """Response containing young prospects analysis."""
    prospects: pd.DataFrame = field(default_factory=pd.DataFrame)
    age_groups: Dict[str, pd.DataFrame] = field(default_factory=dict)
    league_breakdown: Dict[str, int] = field(default_factory=dict)
    top_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.response_type = ResponseType.PLAYER_LIST

@dataclass
class GPT4AnalysisResponse(AnalysisResponse):
    """Response from GPT-4 code generation and execution."""
    result: Any = None
    data: Any = None
    summary: str = ""
    insights: List[str] = field(default_factory=list)
    generated_code: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        self.response_type = ResponseType.PLAYER_LIST  # Default to player list for UI compatibility

@dataclass
class ErrorResponse(AnalysisResponse):
    """Response for errors or unknown queries."""
    error_message: str = ""
    suggestions: List[str] = field(default_factory=list)
    help_text: str = ""
    
    def __post_init__(self):
        self.response_type = ResponseType.ERROR
        self.success = False

# Utility types
@dataclass
class EntityExtraction:
    """Results of entity extraction from natural language query."""
    players: List[str] = field(default_factory=list)
    positions: List[str] = field(default_factory=list)
    leagues: List[str] = field(default_factory=list)
    stats: List[str] = field(default_factory=list)
    age_references: List[str] = field(default_factory=list)
    comparison_indicators: List[str] = field(default_factory=list)
    superlatives: List[str] = field(default_factory=list)  # "best", "top", "worst"
    
@dataclass
class QueryContext:
    """Context information for query processing."""
    user_id: Optional[str] = None
    previous_queries: List[str] = field(default_factory=list)
    session_data: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)