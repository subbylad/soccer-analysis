"""
AI Analysis Router

Revolutionary routing system that integrates the AI-native analysis engine
with the existing API architecture while maintaining backward compatibility.

This router intelligently decides between AI-powered analysis and traditional
methods based on query complexity and AI availability.
"""

import logging
import time
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .types import AnalysisRequest, AnalysisResponse, QueryType
try:
    from analysis.ai_analysis_engine import AIAnalysisEngine, AnalysisContext
    from analysis.clean_player_analyzer import CleanPlayerAnalyzer
except ImportError:
    # Handle relative import issues
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from analysis.ai_analysis_engine import AIAnalysisEngine, AnalysisContext
    from analysis.clean_player_analyzer import CleanPlayerAnalyzer

from .analysis_router import AnalysisRouter  # Original router for fallback

logger = logging.getLogger(__name__)

class AIAnalysisRouter:
    """
    AI-Enhanced Analysis Router
    
    This router provides the next generation of soccer analysis by integrating
    the AI-native analysis engine with existing systems. It offers:
    
    - Intelligent routing between AI and traditional analysis
    - Seamless backward compatibility
    - Performance optimization with caching
    - Graceful fallback when AI is unavailable
    """
    
    def __init__(self, 
                 data_dir: str = "data/clean",
                 comprehensive_data_dir: str = "data/comprehensive", 
                 openai_api_key: Optional[str] = None,
                 enable_ai_engine: bool = True):
        """
        Initialize AI Analysis Router.
        
        Args:
            data_dir: Traditional clean data directory
            comprehensive_data_dir: Comprehensive data directory for AI engine
            openai_api_key: OpenAI API key for GPT-4 features
            enable_ai_engine: Whether to enable AI analysis engine
        """
        self.data_dir = Path(data_dir)
        self.comprehensive_data_dir = Path(comprehensive_data_dir)
        self.enable_ai = enable_ai_engine and openai_api_key is not None
        
        # Initialize AI analysis engine
        try:
            if self.enable_ai:
                self.ai_engine = AIAnalysisEngine(
                    comprehensive_data_dir=str(comprehensive_data_dir),
                    openai_api_key=openai_api_key,
                    enable_ai_enhancement=True
                )
                logger.info("AI Analysis Engine initialized successfully")
            else:
                self.ai_engine = None
                logger.info("AI Analysis Engine disabled")
        except Exception as e:
            logger.error(f"Failed to initialize AI engine: {e}")
            self.ai_engine = None
            self.enable_ai = False
        
        # Initialize traditional analyzer for fallback
        try:
            self.traditional_analyzer = CleanPlayerAnalyzer(data_dir=str(data_dir))
            logger.info("Traditional analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize traditional analyzer: {e}")
            self.traditional_analyzer = None
        
        # Initialize original router for complex fallback
        try:
            self.original_router = AnalysisRouter(data_dir=str(data_dir))
            logger.info("Original router initialized for fallback")
        except Exception as e:
            logger.error(f"Failed to initialize original router: {e}")
            self.original_router = None
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "ai_engine_requests": 0,
            "traditional_requests": 0,
            "avg_ai_time": 0.0,
            "avg_traditional_time": 0.0,
            "ai_success_rate": 0.0,
            "traditional_success_rate": 0.0
        }
        
        # Query result cache
        self.result_cache = {}
        self.cache_size_limit = 100
    
    def execute_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Main analysis execution method with intelligent routing.
        
        Args:
            request: Analysis request object
            
        Returns:
            Analysis response with results and insights
        """
        start_time = time.time()
        self.performance_stats["total_requests"] += 1
        
        try:
            logger.info(f"Executing analysis: {request.query_type.value}")
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.result_cache:
                logger.info("Returning cached result")
                return self.result_cache[cache_key]
            
            # Decide on analysis engine
            use_ai_engine = self._should_use_ai_engine(request)
            
            if use_ai_engine and self.ai_engine:
                response = self._execute_ai_analysis(request, start_time)
            else:
                response = self._execute_traditional_analysis(request, start_time)
            
            # Cache successful results
            if response.success:
                self._cache_result(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            return self._create_error_response(request, str(e), time.time() - start_time)
    
    def _should_use_ai_engine(self, request: AnalysisRequest) -> bool:
        """Decide whether to use AI engine based on request characteristics."""
        if not self.enable_ai or not self.ai_engine:
            return False
        
        # Use AI for enhanced requests
        if hasattr(request, 'ai_enhanced') and request.ai_enhanced:
            return True
        
        # Use AI for tactical analysis
        if request.query_type == QueryType.TACTICAL_ANALYSIS:
            return True
        
        # Use AI for complex searches with high confidence
        if (request.query_type == QueryType.PLAYER_SEARCH and 
            hasattr(request, 'confidence') and request.confidence > 0.7):
            return True
        
        # Use AI if traditional analyzer is not available
        if not self.traditional_analyzer:
            return True
        
        return False
    
    def _execute_ai_analysis(self, request: AnalysisRequest, start_time: float) -> AnalysisResponse:
        """Execute analysis using AI engine."""
        try:
            logger.info("Using AI analysis engine")
            self.performance_stats["ai_engine_requests"] += 1
            
            # Convert request to AI engine format
            ai_context = self._convert_to_ai_context(request)
            
            # Execute AI analysis
            if hasattr(request, 'raw_query'):
                ai_result = self.ai_engine.analyze_query(request.raw_query, ai_context)
            else:
                ai_result = self.ai_engine.analyze_query(str(request.query_type.value), ai_context)
            
            # Convert AI result to standard response format
            response = self._convert_ai_result_to_response(request, ai_result, start_time)
            
            # Update performance stats
            execution_time = time.time() - start_time
            self._update_ai_performance_stats(execution_time, response.success)
            
            return response
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to traditional analysis
            return self._execute_traditional_analysis(request, start_time)
    
    def _execute_traditional_analysis(self, request: AnalysisRequest, start_time: float) -> AnalysisResponse:
        """Execute analysis using traditional methods."""
        try:
            logger.info("Using traditional analysis")
            self.performance_stats["traditional_requests"] += 1
            
            # Use original router if available, otherwise direct analyzer
            if self.original_router:
                response = self.original_router.execute_analysis(request)
            else:
                response = self._execute_direct_traditional_analysis(request)
            
            # Update performance stats
            execution_time = time.time() - start_time
            self._update_traditional_performance_stats(execution_time, response.success)
            
            return response
            
        except Exception as e:
            logger.error(f"Traditional analysis failed: {e}")
            return self._create_error_response(request, str(e), time.time() - start_time)
    
    def _execute_direct_traditional_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute analysis directly using traditional analyzer."""
        if not self.traditional_analyzer:
            raise ValueError("No analysis engines available")
        
        # Convert request to traditional format and execute
        if request.query_type == QueryType.PLAYER_SEARCH:
            return self._execute_traditional_player_search(request)
        elif request.query_type == QueryType.PLAYER_COMPARISON:
            return self._execute_traditional_comparison(request)
        else:
            # Basic fallback
            return AnalysisResponse(
                success=True,
                data=[],
                summary="Analysis completed using traditional methods",
                total_found=0,
                analysis_type=request.query_type.value
            )
    
    def _execute_traditional_player_search(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute player search using traditional analyzer."""
        try:
            # Extract search criteria from request
            position = getattr(request, 'position', None)
            min_minutes = getattr(request, 'min_minutes', 500)
            
            if position:
                results = self.traditional_analyzer.get_players_by_position(position, min_minutes)
            else:
                # Get young prospects as default
                results = self.traditional_analyzer.get_young_prospects()
            
            # Convert to standard format
            players_data = []
            for idx, player in results.iterrows():
                if hasattr(idx, '__len__') and len(idx) >= 4:
                    # Multi-index format
                    player_data = {
                        "name": idx[3],
                        "team": idx[2],
                        "league": idx[0],
                        "position": player.get('position', 'Unknown'),
                        "goals": player.get('goals', 0),
                        "assists": player.get('assists', 0),
                        "minutes": player.get('minutes', 0)
                    }
                else:
                    # DataFrame format
                    player_data = {
                        "name": getattr(player, 'player', 'Unknown'),
                        "position": player.get('position', 'Unknown'),
                        "goals": player.get('goals', 0),
                        "assists": player.get('assists', 0),
                        "minutes": player.get('minutes', 0)
                    }
                
                players_data.append(player_data)
            
            return AnalysisResponse(
                success=True,
                data=players_data,
                summary=f"Found {len(players_data)} players using traditional analysis",
                total_found=len(players_data),
                analysis_type="player_search"
            )
            
        except Exception as e:
            logger.error(f"Traditional player search failed: {e}")
            raise
    
    def _execute_traditional_comparison(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute player comparison using traditional analyzer."""
        try:
            player_names = getattr(request, 'player_names', [])
            
            if len(player_names) < 2:
                return AnalysisResponse(
                    success=False,
                    error="Need at least 2 players for comparison",
                    analysis_type="comparison"
                )
            
            comparison_df = self.traditional_analyzer.compare_players(player_names)
            
            # Convert to standard format
            comparison_data = comparison_df.to_dict('records')
            
            return AnalysisResponse(
                success=True,
                data=comparison_data,
                summary=f"Compared {len(comparison_data)} players",
                total_found=len(comparison_data),
                analysis_type="comparison"
            )
            
        except Exception as e:
            logger.error(f"Traditional comparison failed: {e}")
            raise
    
    def _convert_to_ai_context(self, request: AnalysisRequest) -> Optional[AnalysisContext]:
        """Convert analysis request to AI context."""
        try:
            # Extract requirements from request
            requirements = {}
            
            if hasattr(request, 'position') and request.position:
                requirements['position'] = request.position
            
            if hasattr(request, 'league') and request.league:
                requirements['league'] = request.league
            
            if hasattr(request, 'max_age') and request.max_age:
                requirements['max_age'] = request.max_age
            
            # Create AI context
            return AnalysisContext(
                query_type=request.query_type.value,
                specific_requirements=requirements,
                tactical_context=getattr(request, 'tactical_context', None),
                formation=getattr(request, 'formation_context', None),
                team_context=getattr(request, 'team_context', None)
            )
            
        except Exception as e:
            logger.debug(f"Failed to convert to AI context: {e}")
            return None
    
    def _convert_ai_result_to_response(self, 
                                     request: AnalysisRequest, 
                                     ai_result: Dict[str, Any], 
                                     start_time: float) -> AnalysisResponse:
        """Convert AI engine result to standard response format."""
        try:
            success = ai_result.get("success", True)
            
            if not success:
                return AnalysisResponse(
                    success=False,
                    error=ai_result.get("error", "AI analysis failed"),
                    analysis_type=request.query_type.value,
                    execution_time=time.time() - start_time
                )
            
            # Extract data
            players_data = ai_result.get("players", [])
            total_found = ai_result.get("total_found", len(players_data))
            summary = ai_result.get("ai_summary", ai_result.get("summary", "AI analysis completed"))
            
            return AnalysisResponse(
                success=True,
                data=players_data,
                summary=summary,
                total_found=total_found,
                analysis_type=ai_result.get("type", request.query_type.value),
                execution_time=time.time() - start_time,
                ai_enhanced=True,
                confidence=ai_result.get("confidence", 0.8),
                ai_insights=ai_result.get("ai_summary", "")
            )
            
        except Exception as e:
            logger.error(f"Failed to convert AI result: {e}")
            return self._create_error_response(request, str(e), time.time() - start_time)
    
    def _generate_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for request."""
        try:
            # Create cache key from request attributes
            key_parts = [
                request.query_type.value,
                str(getattr(request, 'position', '')),
                str(getattr(request, 'league', '')),
                str(getattr(request, 'max_age', '')),
                str(getattr(request, 'player_names', []))
            ]
            
            return "_".join(filter(None, key_parts))
            
        except Exception:
            return f"request_{id(request)}"
    
    def _cache_result(self, cache_key: str, response: AnalysisResponse) -> None:
        """Cache analysis result."""
        try:
            # Implement LRU-style cache
            if len(self.result_cache) >= self.cache_size_limit:
                # Remove oldest entry
                oldest_key = next(iter(self.result_cache))
                del self.result_cache[oldest_key]
            
            self.result_cache[cache_key] = response
            
        except Exception as e:
            logger.debug(f"Failed to cache result: {e}")
    
    def _update_ai_performance_stats(self, execution_time: float, success: bool) -> None:
        """Update AI engine performance statistics."""
        ai_requests = self.performance_stats["ai_engine_requests"]
        
        # Update average time
        current_avg = self.performance_stats["avg_ai_time"]
        self.performance_stats["avg_ai_time"] = (
            (current_avg * (ai_requests - 1) + execution_time) / ai_requests
        )
        
        # Update success rate
        if ai_requests == 1:
            self.performance_stats["ai_success_rate"] = 1.0 if success else 0.0
        else:
            current_rate = self.performance_stats["ai_success_rate"]
            self.performance_stats["ai_success_rate"] = (
                (current_rate * (ai_requests - 1) + (1.0 if success else 0.0)) / ai_requests
            )
    
    def _update_traditional_performance_stats(self, execution_time: float, success: bool) -> None:
        """Update traditional analysis performance statistics."""
        trad_requests = self.performance_stats["traditional_requests"]
        
        # Update average time
        current_avg = self.performance_stats["avg_traditional_time"]
        self.performance_stats["avg_traditional_time"] = (
            (current_avg * (trad_requests - 1) + execution_time) / trad_requests
        )
        
        # Update success rate
        if trad_requests == 1:
            self.performance_stats["traditional_success_rate"] = 1.0 if success else 0.0
        else:
            current_rate = self.performance_stats["traditional_success_rate"]
            self.performance_stats["traditional_success_rate"] = (
                (current_rate * (trad_requests - 1) + (1.0 if success else 0.0)) / trad_requests
            )
    
    def _create_error_response(self, 
                             request: AnalysisRequest, 
                             error_message: str, 
                             execution_time: float) -> AnalysisResponse:
        """Create standardized error response."""
        return AnalysisResponse(
            success=False,
            error=error_message,
            analysis_type=request.query_type.value,
            execution_time=execution_time,
            data=[],
            total_found=0
        )
    
    # Public utility methods
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for both engines."""
        return self.performance_stats.copy()
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all analysis engines."""
        return {
            "ai_engine_available": self.ai_engine is not None,
            "ai_enabled": self.enable_ai,
            "traditional_analyzer_available": self.traditional_analyzer is not None,
            "original_router_available": self.original_router is not None,
            "cache_size": len(self.result_cache),
            "cache_limit": self.cache_size_limit
        }
    
    def clear_cache(self) -> None:
        """Clear the result cache."""
        self.result_cache.clear()
        logger.info("Analysis result cache cleared")
    
    def get_ai_database_summary(self) -> Dict[str, Any]:
        """Get summary of AI engine database."""
        if self.ai_engine:
            return self.ai_engine.get_database_summary()
        else:
            return {"status": "AI engine not available"}
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all components."""
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }
        
        # Check AI engine
        if self.ai_engine:
            try:
                ai_summary = self.ai_engine.get_database_summary()
                health["components"]["ai_engine"] = {
                    "status": "healthy",
                    "players_loaded": ai_summary.get("total_players", 0),
                    "ai_enabled": ai_summary.get("ai_enabled", False)
                }
            except Exception as e:
                health["components"]["ai_engine"] = {"status": f"error: {e}"}
                health["status"] = "degraded"
        else:
            health["components"]["ai_engine"] = {"status": "not_available"}
        
        # Check traditional analyzer
        if self.traditional_analyzer:
            try:
                trad_summary = self.traditional_analyzer.data_summary
                health["components"]["traditional_analyzer"] = {
                    "status": "healthy",
                    "players_loaded": trad_summary.get("total_players", 0)
                }
            except Exception as e:
                health["components"]["traditional_analyzer"] = {"status": f"error: {e}"}
                health["status"] = "degraded"
        else:
            health["components"]["traditional_analyzer"] = {"status": "not_available"}
        
        # Check if we have at least one working engine
        if (not self.ai_engine and not self.traditional_analyzer):
            health["status"] = "critical"
            health["error"] = "No analysis engines available"
        
        return health

# Backward compatibility - alias for existing imports
AnalysisRouter = AIAnalysisRouter