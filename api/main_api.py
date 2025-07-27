"""
Main Soccer Analytics API

The primary interface that coordinates query processing, analysis execution,
and response formatting. This is the single entry point for all natural
language soccer analysis requests.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .query_processor import QueryProcessor
from .ai_query_processor import AIQueryProcessor  
from .analysis_router import AnalysisRouter
from .ai_analysis_router import AIAnalysisRouter  
from .response_formatter import ResponseFormatter
from .types import QueryContext, AnalysisRequest, AnalysisResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for the Soccer Analytics API."""
    data_dir: str = "data/clean"
    comprehensive_data_dir: str = "data/comprehensive"  # For AI engine
    cache_enabled: bool = True
    max_cache_size: int = 100
    log_level: str = "INFO"
    default_min_minutes: int = 500
    openai_api_key: Optional[str] = None  # For GPT-4 enhanced query processing
    enable_ai_engine: bool = True  # Enable revolutionary AI analysis engine
    ai_first: bool = True  # Use AI-native processing when available

class SoccerAnalyticsAPI:
    """
    Main Soccer Analytics API
    
    Provides natural language querying capabilities over soccer data.
    Coordinates query processing, analysis execution, and response formatting.
    
    Example usage:
        api = SoccerAnalyticsAPI()
        result = api.query("Compare Haaland vs Mbappé")
        formatted = api.format_for_chat(result)
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize the Soccer Analytics API.
        
        Args:
            config: API configuration options
        """
        self.config = config or APIConfig()
        
        # Set up logging
        log_level = getattr(logging, self.config.log_level.upper())
        logging.getLogger().setLevel(log_level)
        
        # Initialize components
        try:
            logger.info("Initializing Revolutionary Soccer Analytics API with AI Engine...")
            openai_key = getattr(self.config, 'openai_api_key', None)
            enable_ai = getattr(self.config, 'enable_ai_engine', True)
            ai_first = getattr(self.config, 'ai_first', True)
            
            # Always use AI-native architecture for better error handling and fallback
            if ai_first and enable_ai:
                logger.info("Initializing AI-first architecture...")
                self.query_processor = AIQueryProcessor(openai_api_key=openai_key, enable_ai=True)
                self.analysis_router = AIAnalysisRouter(
                    data_dir=self.config.data_dir,
                    comprehensive_data_dir=getattr(self.config, 'comprehensive_data_dir', 'data/comprehensive'),
                    openai_api_key=openai_key,
                    enable_ai_engine=True
                )
                self.ai_native = True
                logger.info("AI-native components initialized successfully")
            else:
                logger.info("Initializing traditional components with AI enhancement...")
                self.query_processor = QueryProcessor(openai_api_key=openai_key)
                self.analysis_router = AnalysisRouter(data_dir=self.config.data_dir, openai_api_key=openai_key)
                self.ai_native = False
                logger.info("Traditional components with AI enhancement initialized")
            
            self.response_formatter = ResponseFormatter()
            
            # Simple query history
            self.query_history = []
            
            logger.info("Soccer Analytics API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize API: {e}")
            raise RuntimeError(f"API initialization failed: {e}")
    
    def query(self, user_query: str, context: Optional[QueryContext] = None) -> Dict[str, Any]:
        """
        Main query interface - processes natural language and returns formatted results.
        
        Args:
            user_query: Natural language query about soccer data
            context: Optional context information (user ID, previous queries, etc.)
            
        Returns:
            Formatted response dictionary ready for UI display
            
        Example:
            result = api.query("Who are the best young midfielders?")
            # Returns formatted response with player data, insights, and display components
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: '{user_query}'")
            
            # Step 1: Parse natural language query into structured request
            parsed_request = self.query_processor.process_query(user_query, context)
            logger.info(f"Parsed as: {parsed_request.query_type.value} (confidence: {parsed_request.confidence})")
            
            # Step 2: Execute analysis using existing soccer analytics functions
            analysis_response = self.analysis_router.execute_analysis(parsed_request)
            logger.info(f"Analysis completed: success={analysis_response.success}")
            
            # Step 3: Format response for UI display
            formatted_response = self.response_formatter.format_response(analysis_response)
            
            # Add metadata
            total_time = time.time() - start_time
            formatted_response.update({
                "total_execution_time": total_time,
                "query_confidence": parsed_request.confidence,
                "timestamp": time.time(),
                "original_query": user_query
            })
            
            # Store in history
            self._add_to_history(user_query, formatted_response)
            
            logger.info(f"Query completed in {total_time:.2f}s")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return self._create_error_response(user_query, str(e), time.time() - start_time)
    
    def query_structured(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Advanced interface for pre-structured requests.
        
        Args:
            request: Already parsed AnalysisRequest object
            
        Returns:
            Raw AnalysisResponse object (not formatted for UI)
        """
        try:
            logger.info(f"Executing structured request: {request.query_type.value}")
            return self.analysis_router.execute_analysis(request)
        except Exception as e:
            logger.error(f"Structured query failed: {e}")
            raise
    
    def format_for_chat(self, response: Dict[str, Any]) -> str:
        """
        Format API response specifically for chat interfaces.
        
        Args:
            response: Response from api.query()
            
        Returns:
            Chat-friendly text string
        """
        if "chat_text" in response:
            return response["chat_text"]
        elif response.get("type") == "error":
            return response.get("error_message", "An error occurred")
        else:
            return f"Found {response.get('total_found', 0)} results"
    
    def format_for_streamlit(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format API response specifically for Streamlit interfaces.
        
        Args:
            response: Response from api.query()
            
        Returns:
            Dictionary with Streamlit-specific components
        """
        if "streamlit_components" in response:
            return response["streamlit_components"]
        else:
            # Create basic Streamlit components
            return {
                "success_message": response.get("summary", "Analysis completed"),
                "data": response.get("display_data", []),
                "error": response.get("error_message") if not response.get("success", True) else None
            }
    
    def get_suggestions(self, partial_query: str = "") -> List[str]:
        """
        Get query suggestions for autocomplete or help.
        
        Args:
            partial_query: Optional partial query for context-aware suggestions
            
        Returns:
            List of suggested queries
        """
        # Enhanced suggestions for AI-native system
        if self.ai_native:
            ai_suggestions = [
                "Find a creative midfielder like Pedri but with better defensive work rate",
                "Who can play alongside Kobbie Mainoo in Ligue 1's tactical system?",
                "Compare Haaland vs Mbappé across all performance dimensions",
                "Find young wingers under 21 with pace and creativity for counter-attacking football",
                "Alternative to Rodri for Manchester City's possession-based system",
                "Defenders who can contribute in attacking phases like Timber",
                "Find a box-to-box midfielder similar to Bellingham for Real Madrid",
                "Young prospects in Serie A with high tactical intelligence",
                "Left-backs who can play inverted role in Pep's system",
                "Find strikers with hold-up play for a 4-2-3-1 formation"
            ]
            base_suggestions = ai_suggestions
        else:
            base_suggestions = [
                "Compare Haaland vs Mbappé",
                "Find young midfielders under 21",
                "Top scorers in Premier League", 
                "Best defensive midfielders",
                "Who can play alongside Kobbie Mainoo?",
                "Find players similar to Pedri",
                "Young prospects under 23",
                "Alternative to Rodri in Ligue 1",
                "Top assists in Serie A",
                "Defenders who complement Varane's style"
            ]
        
        # Filter suggestions based on partial query
        if partial_query:
            partial_lower = partial_query.lower()
            filtered = [s for s in base_suggestions if partial_lower in s.lower()]
            return filtered[:5] if filtered else base_suggestions[:5]
        
        return base_suggestions[:5]
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent query history.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of recent queries with metadata
        """
        return self.query_history[-limit:] if self.query_history else []
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the loaded data.
        
        Returns:
            Dictionary with data statistics
        """
        try:
            if self.ai_native:
                # Get AI engine database summary
                summary = self.analysis_router.get_ai_database_summary()
                return {
                    "total_players": summary.get("total_players", 0),
                    "total_metrics": summary.get("total_metrics", 0),
                    "leagues": summary.get("leagues", []),
                    "positions": summary.get("positions", []),
                    "ai_enabled": summary.get("ai_enabled", False),
                    "data_dimensions": summary.get("data_dimensions", {}),
                    "last_updated": "2024/25 season",
                    "system_type": "AI-Native Analysis Engine"
                }
            else:
                # Traditional system summary
                summary = self.analysis_router.traditional_analyzer.data_summary
                return {
                    "total_players": summary.get("total_players", 0),
                    "leagues": summary.get("leagues", []),
                    "age_range": summary.get("age_range", [16, 40]),
                    "data_shape": summary.get("data_shape", [0, 0]),
                    "last_updated": "2024/25 season",
                    "system_type": "Traditional Analysis with AI Enhancement"
                }
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health and component status.
        
        Returns:
            Health status information
        """
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }
        
        try:
            # Check query processor
            test_request = self.query_processor.process_query("test")
            health["components"]["query_processor"] = "healthy"
        except Exception as e:
            health["components"]["query_processor"] = f"error: {e}"
            health["status"] = "degraded"
        
        try:
            # Check analysis router
            data_summary = self.analysis_router.traditional_analyzer.data_summary
            health["components"]["analysis_router"] = "healthy"
            health["data_loaded"] = data_summary.get("total_players", 0) > 0
        except Exception as e:
            health["components"]["analysis_router"] = f"error: {e}"
            health["status"] = "degraded"
        
        try:
            # Check response formatter
            self.response_formatter.format_response
            health["components"]["response_formatter"] = "healthy"
        except Exception as e:
            health["components"]["response_formatter"] = f"error: {e}"
            health["status"] = "degraded"
        
        return health
    
    def get_ai_status(self) -> Dict[str, Any]:
        """
        Get detailed AI system status and capabilities.
        
        Returns:
            Dictionary with AI system information
        """
        ai_status = {
            "ai_native": self.ai_native,
            "timestamp": time.time()
        }
        
        if self.ai_native:
            # Get detailed AI engine status
            try:
                engine_status = self.analysis_router.get_engine_status()
                performance_stats = self.analysis_router.get_performance_stats()
                
                ai_status.update({
                    "system_type": "Revolutionary AI-Native Analysis Engine",
                    "capabilities": [
                        "Multi-dimensional tactical reasoning",
                        "Natural language query understanding", 
                        "GPT-4 powered insights",
                        "Comprehensive player profiling",
                        "Formation and system analysis",
                        "Playing style compatibility"
                    ],
                    "engine_status": engine_status,
                    "performance": performance_stats,
                    "query_processing": "AI-first with GPT-4 understanding"
                })
                
                # Get query processor stats if available
                if hasattr(self.query_processor, 'get_processing_stats'):
                    ai_status["query_stats"] = self.query_processor.get_processing_stats()
                    
            except Exception as e:
                ai_status["error"] = f"Failed to get AI status: {e}"
        else:
            ai_status.update({
                "system_type": "Traditional Analysis with AI Enhancement",
                "capabilities": [
                    "Pattern-based query processing",
                    "Statistical player analysis",
                    "GPT-4 enhanced responses",
                    "Basic tactical analysis"
                ],
                "query_processing": "Pattern matching with AI enhancement"
            })
        
        return ai_status
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """
        Get comprehensive system capabilities based on current configuration.
        
        Returns:
            Dictionary describing system capabilities
        """
        capabilities = {
            "timestamp": time.time(),
            "system_version": "2.0 - Revolutionary AI-Native",
            "ai_native": self.ai_native
        }
        
        if self.ai_native:
            capabilities.update({
                "analysis_types": [
                    "Multi-dimensional player search with tactical context",
                    "Sophisticated player comparison across all metrics",
                    "Formation and system compatibility analysis", 
                    "Playing style and tactical role matching",
                    "Market value and transfer feasibility assessment",
                    "Youth prospect evaluation with potential scoring",
                    "Team composition and partnership analysis"
                ],
                "query_understanding": [
                    "Natural language processing with GPT-4",
                    "Tactical concept recognition",
                    "Entity extraction (players, teams, formations)",
                    "Intent classification with confidence scoring",
                    "Context-aware query enhancement"
                ],
                "data_sources": [
                    "FBref comprehensive stats (200+ metrics)",
                    "Standard performance data",
                    "Advanced tactical metrics",
                    "Possession and defensive data",
                    "Goalkeeper specific metrics",
                    "AI-generated player insights"
                ],
                "intelligence_features": [
                    "GPT-4 powered tactical reasoning",
                    "Multi-dimensional player profiling",
                    "Automated scout report generation",
                    "Playing style analysis",
                    "Formation fit assessment",
                    "Alternative player suggestions"
                ]
            })
        else:
            capabilities.update({
                "analysis_types": [
                    "Player search by position and criteria",
                    "Basic player comparison",
                    "Statistical analysis and ranking",
                    "Young prospect identification"
                ],
                "query_understanding": [
                    "Pattern-based query matching",
                    "Basic entity extraction",
                    "GPT-4 enhanced responses"
                ],
                "data_sources": [
                    "FBref standard data (100+ metrics)",
                    "Basic performance statistics"
                ]
            })
        
        return capabilities
    
    def _add_to_history(self, query: str, response: Dict[str, Any]) -> None:
        """Add query and response to history."""
        history_entry = {
            "query": query,
            "timestamp": time.time(),
            "success": response.get("success", False),
            "execution_time": response.get("total_execution_time", 0),
            "query_type": response.get("type", "unknown")
        }
        
        self.query_history.append(history_entry)
        
        # Keep history manageable
        if len(self.query_history) > self.config.max_cache_size:
            self.query_history = self.query_history[-self.config.max_cache_size:]
    
    def _create_error_response(self, query: str, error_message: str, execution_time: float) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "type": "error",
            "success": False,
            "error_message": error_message,
            "suggestions": self.get_suggestions(),
            "total_execution_time": execution_time,
            "original_query": query,
            "timestamp": time.time(),
            "chat_text": f"❌ {error_message}\\n\\n💡 Try one of these suggestions:\\n" + 
                        "\\n".join(f"• {s}" for s in self.get_suggestions()[:3])
        }

# Convenience functions for easy usage
def create_api(data_dir: str = "data/clean") -> SoccerAnalyticsAPI:
    """
    Create a Soccer Analytics API instance with custom data directory.
    
    Args:
        data_dir: Path to clean data directory
        
    Returns:
        Configured SoccerAnalyticsAPI instance
    """
    config = APIConfig(data_dir=data_dir)
    return SoccerAnalyticsAPI(config)

def quick_query(query: str, data_dir: str = "data/clean") -> str:
    """
    Quick convenience function for single queries.
    
    Args:
        query: Natural language query
        data_dir: Path to data directory
        
    Returns:
        Chat-formatted response string
        
    Example:
        result = quick_query("Find young midfielders")
        print(result)
    """
    api = create_api(data_dir)
    response = api.query(query)
    return api.format_for_chat(response)