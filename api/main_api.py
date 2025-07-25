"""
Main Soccer Analytics API

The primary interface that coordinates query processing, analysis execution,
and response formatting. This is the single entry point for all natural
language soccer analysis requests.
"""

import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .query_processor import QueryProcessor
from .analysis_router import AnalysisRouter  
from .response_formatter import ResponseFormatter
from .types import QueryContext, AnalysisRequest, AnalysisResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for the Soccer Analytics API."""
    data_dir: str = "data/clean"
    cache_enabled: bool = True
    max_cache_size: int = 100
    log_level: str = "INFO"
    default_min_minutes: int = 500

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
            logger.info("Initializing Soccer Analytics API...")
            self.query_processor = QueryProcessor()
            self.analysis_router = AnalysisRouter(data_dir=self.config.data_dir)
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
        base_suggestions = [
            "Compare Haaland vs Mbappé",
            "Find young midfielders under 21",
            "Top scorers in Premier League", 
            "Best defensive midfielders",
            "Show me forwards in La Liga",
            "Young prospects under 23",
            "Compare Silva vs De Bruyne",
            "Find players like Pedri",
            "Top assists in Serie A",
            "Defenders with high passing"
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
            summary = self.analysis_router.analyzer.data_summary
            return {
                "total_players": summary.get("total_players", 0),
                "leagues": summary.get("leagues", []),
                "age_range": summary.get("age_range", [16, 40]),
                "data_shape": summary.get("data_shape", [0, 0]),
                "last_updated": "2024/25 season"
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
            data_summary = self.analysis_router.analyzer.data_summary
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