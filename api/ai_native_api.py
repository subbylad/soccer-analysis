"""
Revolutionary AI-Native Soccer Analytics API

Complete replacement for traditional pattern-based approach.
Pure AI-first architecture using GPT-4 for all intelligence.

This API provides professional scout-level tactical analysis using the
3-step AI pipeline: Parser → Analysis → Reasoning
"""

from analysis.ai_native_engine import AIScoutEngine, AIAnalysisConfig
from typing import Dict, Optional, Any
import os
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class RevolutionaryAIAPI:
    """
    AI-Native Soccer Analytics API
    
    Complete replacement for pattern-based systems.
    Provides professional-grade tactical intelligence using GPT-4.
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize the revolutionary AI-native API"""
        
        logger.info("🚀 Initializing Revolutionary AI-Native Soccer Scout API")
        
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for AI-native analysis")
        
        # Configure AI analysis engine
        config = AIAnalysisConfig(
            openai_api_key=openai_api_key,
            model="gpt-4",
            max_candidates=50,
            confidence_threshold=0.7,
            enable_caching=True,
            data_dir="data/comprehensive/processed"
        )
        
        try:
            # Initialize the revolutionary AI scout engine
            self.ai_scout = AIScoutEngine(config)
            self.initialization_time = datetime.now()
            self.query_count = 0
            self.successful_queries = 0
            
            logger.info("✅ Revolutionary AI-Native API initialized successfully")
            logger.info(f"   🧠 Model: {config.model}")
            logger.info(f"   📊 Data: {self.ai_scout.get_system_status()['total_players']} players")
            logger.info(f"   🎯 Metrics: {self.ai_scout.get_system_status()['total_metrics']} metrics per player")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI-native API: {e}")
            raise Exception(f"Revolutionary API initialization failed: {e}")
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Main entry point for AI-native soccer analysis
        
        Processes natural language queries using the revolutionary 3-step pipeline:
        1. GPT-4 parses natural language into structured parameters
        2. Python performs high-performance data analysis 
        3. GPT-4 generates professional scout-level insights
        
        Args:
            query_text: Natural language soccer query
            
        Returns:
            Comprehensive analysis with tactical intelligence
        """
        
        self.query_count += 1
        logger.info(f"🎯 Processing Query #{self.query_count}: '{query_text}'")
        
        # Input validation
        if not query_text or len(query_text.strip()) < 3:
            return {
                "success": False,
                "error": "Query too short - please provide a more detailed question",
                "error_type": "input_validation",
                "suggestions": [
                    "Try: 'Who can play alongside Kobbie Mainoo in Ligue 1?'",
                    "Try: 'Find creative midfielders like Pedri but more defensive'",
                    "Try: 'Best young forwards under 21 for counter-attacking'"
                ]
            }
        
        try:
            # Execute revolutionary AI-native analysis
            result = self.ai_scout.analyze_query(query_text)
            
            if result.get("success"):
                self.successful_queries += 1
                # Format for beautiful frontend consumption
                return self._format_for_frontend(result)
            else:
                # Handle analysis failures gracefully
                return self._handle_analysis_failure(result, query_text)
                
        except Exception as e:
            logger.error(f"❌ Revolutionary analysis failed for query '{query_text}': {e}")
            return {
                "success": False,
                "error": f"AI analysis system error: {str(e)}",
                "error_type": "system_error",
                "query": query_text,
                "suggestions": [
                    "Try rephrasing your question",
                    "Check if player names are spelled correctly",
                    "Try a simpler query to start"
                ]
            }
    
    def _format_for_frontend(self, ai_result: Dict) -> Dict:
        """
        Format AI results for beautiful frontend display
        
        Transforms the comprehensive AI analysis into a structure
        optimized for the React frontend components.
        """
        
        tactical_intel = ai_result.get("tactical_intelligence", {})
        metadata = ai_result.get("metadata", {})
        
        # Extract recommendations with rich formatting
        recommendations = []
        for rec in tactical_intel.get("top_recommendations", []):
            formatted_rec = {
                "player": rec.get("player_name", "Unknown"),
                "team": rec.get("current_team", "Unknown"),
                "league": rec.get("league", "Unknown"),
                "reasoning": rec.get("tactical_reasoning", ""),
                "confidence": rec.get("confidence_score", 0.0),
                "strengths": rec.get("key_strengths", []),
                "role": rec.get("tactical_role", ""),
                "concerns": rec.get("potential_concerns", ""),
                "metrics": rec.get("supporting_metrics", {}),
                "ai_generated": True
            }
            recommendations.append(formatted_rec)
        
        # Extract alternatives
        alternatives = []
        for alt in tactical_intel.get("alternative_considerations", []):
            alternatives.append({
                "player": alt.get("player_name", "Unknown"),
                "reasoning": alt.get("reasoning", "")
            })
        
        # Create response_text for frontend compatibility
        executive_summary = tactical_intel.get("executive_summary", "")
        scout_rec = tactical_intel.get("scout_recommendation", "")
        
        # Enhanced response text with fallback handling
        if scout_rec:
            response_text = f"{executive_summary}\n\n{scout_rec}"
        else:
            response_text = executive_summary or "Analysis completed successfully. Please see detailed recommendations below."
        
        # Ensure response_text is never empty
        if not response_text.strip():
            response_text = f"Found {len(recommendations)} player recommendations matching your query."
        
        return {
            "success": True,
            "type": "ai_native_revolutionary",
            "query": ai_result.get("query", ""),
            "execution_time": ai_result.get("execution_time", 0),
            
            # Frontend compatibility
            "response_text": response_text,
            
            # Main content
            "summary": tactical_intel.get("executive_summary", ""),
            "recommendations": recommendations,
            
            # Tactical analysis
            "tactical_analysis": tactical_intel.get("tactical_analysis", {}),
            "alternatives": alternatives,
            "professional_insights": tactical_intel.get("professional_insights", {}),
            "scout_recommendation": tactical_intel.get("scout_recommendation", ""),
            
            # Metadata for frontend
            "metadata": {
                "analysis_type": ai_result.get("analysis_type", ""),
                "candidates_analyzed": metadata.get("candidates_found", 0),
                "ai_steps_completed": metadata.get("ai_steps_completed", 3),
                "comprehensive_data_used": metadata.get("comprehensive_data_used", True),
                "query_parameters": metadata.get("parsed_parameters", {}),
                "model_used": "gpt-4",
                "confidence_level": "professional_grade"
            },
            
            # For advanced users
            "raw_data": ai_result.get("raw_candidate_data", [])[:10],  # Top 10 candidates
            
            # Response formatting
            "display_format": "tactical_intelligence",
            "ui_components": ["recommendations", "tactical_analysis", "alternatives", "insights"]
        }
    
    def _handle_analysis_failure(self, failed_result: Dict, query: str) -> Dict:
        """Handle analysis failures gracefully with helpful feedback"""
        
        step_failed = failed_result.get("step_failed", "unknown")
        error_message = failed_result.get("error", "Analysis failed")
        
        # Provide specific guidance based on failure point
        if step_failed == "parsing":
            suggestions = [
                "Try rephrasing your question more clearly",
                "Be specific about leagues, positions, or player attributes",
                "Example: 'Find creative midfielders in Premier League'"
            ]
        elif step_failed == "filtering":
            suggestions = failed_result.get("suggestions", [
                "Try broader search criteria",
                "Reduce minimum minutes requirement", 
                "Expand to more leagues or positions"
            ])
        elif step_failed == "reasoning":
            suggestions = [
                "The data analysis completed but AI reasoning failed",
                "Try a simpler query or contact support",
                "This may be a temporary issue with the AI service"
            ]
        else:
            suggestions = [
                "Try a different query",
                "Check if player names are spelled correctly",
                "Contact support if the issue persists"
            ]
        
        return {
            "success": False,
            "error": error_message,
            "error_type": f"analysis_failure_{step_failed}",
            "query": query,
            "suggestions": suggestions,
            "step_failed": step_failed,
            "ai_native": True
        }
    
    def get_capabilities(self) -> Dict:
        """Return comprehensive system capabilities"""
        return {
            "system_type": "ai_native_revolutionary",
            "ai_model": "gpt-4",
            "capabilities": [
                "Natural language query understanding with GPT-4",
                "Multi-dimensional player analysis across 50+ metrics",
                "Professional scout-level tactical intelligence", 
                "Formation and system compatibility analysis",
                "Playing style and partnership assessment",
                "Market intelligence and development potential",
                "Confidence scoring for all recommendations"
            ],
            "supported_queries": [
                "Player search with tactical requirements",
                "Partnership and compatibility analysis", 
                "Alternative player identification",
                "Formation-specific recommendations",
                "Playing style similarity analysis",
                "Market value and potential assessment"
            ],
            "example_queries": [
                "Who can play alongside Kobbie Mainoo in Ligue 1?",
                "Find a creative midfielder like Pedri but with better defensive work rate",
                "Alternative to Rodri for Manchester City's pressing system",
                "Best young wingers under 21 for counter-attacking football",
                "Find a false 9 for Barcelona's possession style",
                "Who are the most undervalued strikers in Serie A?"
            ],
            "data_coverage": {
                "total_players": self.ai_scout.get_system_status()["total_players"],
                "metrics_per_player": self.ai_scout.get_system_status()["total_metrics"],
                "leagues": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"],
                "seasons": ["2024/25"],
                "comprehensive_data": True
            }
        }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status for monitoring"""
        ai_status = self.ai_scout.get_system_status()
        
        return {
            "status": "revolutionary_ai_native",
            "healthy": ai_status["ready_for_analysis"],
            "initialization_time": self.initialization_time.isoformat(),
            "uptime": str(datetime.now() - self.initialization_time),
            
            # Query statistics
            "query_stats": {
                "total_queries": self.query_count,
                "successful_queries": self.successful_queries,
                "success_rate": (self.successful_queries / max(self.query_count, 1)) * 100
            },
            
            # AI engine status
            "ai_engine": {
                "model": "gpt-4",
                "status": "operational",
                **ai_status
            },
            
            # Data status
            "data_status": {
                "comprehensive_data_loaded": ai_status["data_loaded"],
                "total_players": ai_status["total_players"],
                "total_metrics": ai_status["total_metrics"],
                "player_profiles_ready": ai_status["player_profiles_generated"]
            },
            
            # System capabilities
            "capabilities_active": [
                "natural_language_understanding",
                "tactical_intelligence_generation", 
                "professional_scout_analysis",
                "multi_dimensional_player_assessment"
            ]
        }
    
    def health_check(self) -> Dict:
        """Simple health check for monitoring systems"""
        try:
            status = self.get_system_status()
            return {
                "status": "healthy" if status["healthy"] else "degraded",
                "service": "ai_native_soccer_scout",
                "ai_enabled": True,
                "data_ready": status["data_status"]["comprehensive_data_loaded"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "ai_native_soccer_scout", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Factory function for easy initialization
def create_revolutionary_api(openai_api_key: Optional[str] = None) -> RevolutionaryAIAPI:
    """
    Factory function to create the revolutionary AI-native API
    
    Args:
        openai_api_key: OpenAI API key (if None, will try environment variable)
        
    Returns:
        Initialized RevolutionaryAIAPI instance
    """
    
    # Try to get API key from parameter or environment
    api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "OpenAI API key is required for the revolutionary AI-native system. "
            "Provide it as a parameter or set OPENAI_API_KEY environment variable."
        )
    
    return RevolutionaryAIAPI(api_key)