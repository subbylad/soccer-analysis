#!/usr/bin/env python3
"""
CORS-enabled Flask API Server for Soccer Analytics

Production-ready Flask server that wraps the existing SoccerAnalyticsAPI
for integration with Next.js/React frontend. Provides RESTful endpoints
with proper CORS, error handling, and logging.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import time
import traceback
from typing import Dict, Any, Optional
import json

# Set up logging first to avoid undefined logger errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our existing API with error handling
try:
    from api.main_api import SoccerAnalyticsAPI, APIConfig
    from api.types import QueryContext
    from api.frontend_adapter import FrontendResponseAdapter
except ImportError as e:
    logger.error(f"Failed to import API modules: {e}")
    # Try absolute imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from api.main_api import SoccerAnalyticsAPI, APIConfig
    from api.types import QueryContext
    from api.frontend_adapter import FrontendResponseAdapter

# Import production middleware
try:
    from production_middleware import apply_production_middleware, create_production_config
    PRODUCTION_MIDDLEWARE_AVAILABLE = True
except ImportError:
    PRODUCTION_MIDDLEWARE_AVAILABLE = False
    logger.warning("Production middleware not available - running without enhanced security")

app = Flask(__name__)

# Configure CORS for React frontend
CORS(app, origins=[
    "http://localhost:3000",  # Next.js default
    "http://localhost:3001",  # Alternative port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    # Add production domains here
], supports_credentials=True)

# Global API instance
soccer_api: Optional[SoccerAnalyticsAPI] = None

def init_api():
    """Initialize the Soccer Analytics API with configuration."""
    global soccer_api
    
    try:
        # Get OpenAI API key from environment
        openai_key = os.getenv('OPENAI_API_KEY')
        
        # Create API configuration
        config = APIConfig(
            data_dir="data/clean",
            cache_enabled=True,
            max_cache_size=100,
            log_level="INFO",
            default_min_minutes=500,
            openai_api_key=openai_key
        )
        
        # Initialize API
        soccer_api = SoccerAnalyticsAPI(config)
        logger.info("✅ Soccer Analytics API initialized successfully")
        
        if openai_key:
            logger.info("🧠 GPT-4 enhanced features enabled")
        else:
            logger.info("⚠️ GPT-4 features disabled (no OPENAI_API_KEY)")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize Soccer Analytics API: {e}")
        raise

def create_error_response(message: str, status_code: int = 500, details: Optional[str] = None) -> tuple:
    """Create standardized error response."""
    error_response = {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": time.time()
        }
    }
    
    if details:
        error_response["error"]["details"] = details
        
    return jsonify(error_response), status_code

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response."""
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "timestamp": time.time()
    })

@app.before_request
def log_request():
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log response status."""
    logger.info(f"Response: {response.status_code}")
    return response

# Simple health check endpoint for Railway
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    try:
        return jsonify({
            "status": "healthy",
            "service": "soccer-scout-api",
            "timestamp": time.time()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": time.time()
        }), 500

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({
        "message": "Soccer Scout AI API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/api/health", "/api/query"]
    })

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {e}")
    logger.error(traceback.format_exc())
    return create_error_response(
        "Internal server error",
        status_code=500,
        details=str(e) if app.debug else None
    )

# === CORE API ENDPOINTS ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        health_status = soccer_api.health_check()
        
        # Add server-specific health info
        health_status.update({
            "server": "flask",
            "version": "1.0.0",
            "uptime": time.time() - start_time,
            "endpoints_available": len([rule.rule for rule in app.url_map.iter_rules()])
        })
        
        return create_success_response(health_status, "API is healthy")
        
    except Exception as e:
        return create_error_response(f"Health check failed: {str(e)}", 503)

@app.route('/api/query', methods=['POST'])
def process_query():
    """Main query processing endpoint."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        # Parse request body
        if not request.is_json:
            return create_error_response("Content-Type must be application/json", 400)
        
        data = request.get_json()
        if not data or 'query' not in data:
            return create_error_response("Missing required field: 'query'", 400)
        
        user_query = data['query'].strip()
        if not user_query:
            return create_error_response("Query cannot be empty", 400)
        
        # Extract optional context
        context_data = data.get('context', {})
        context = QueryContext(
            user_id=context_data.get('user_id'),
            previous_queries=context_data.get('previous_queries', []),
            session_data=context_data.get('session_data', {}),
            preferences=context_data.get('preferences', {})
        )
        
        # Process the query
        result = soccer_api.query(user_query, context)
        
        # Adapt response for frontend
        frontend_result = FrontendResponseAdapter.adapt_query_response(result)
        
        # Add request metadata
        frontend_result.update({
            "request_id": f"req_{int(time.time() * 1000)}",
            "query_length": len(user_query),
            "has_context": bool(context_data)
        })
        
        return create_success_response(frontend_result, "Query processed successfully")
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return create_error_response(f"Query processing failed: {str(e)}")

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get query suggestions for autocomplete."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        # Get partial query parameter
        partial_query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)  # Max 20 suggestions
        
        suggestions = soccer_api.get_suggestions(partial_query)[:limit]
        
        return create_success_response({
            "suggestions": suggestions,
            "partial_query": partial_query,
            "count": len(suggestions)
        }, "Suggestions retrieved successfully")
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return create_error_response(f"Failed to get suggestions: {str(e)}")

@app.route('/api/history', methods=['GET'])
def get_query_history():
    """Get recent query history."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 entries
        
        history = soccer_api.get_query_history(limit)
        
        return create_success_response({
            "history": history,
            "count": len(history),
            "limit": limit
        }, "History retrieved successfully")
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return create_error_response(f"Failed to get history: {str(e)}")

@app.route('/api/data/summary', methods=['GET'])
def get_data_summary():
    """Get summary of loaded data."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        summary = soccer_api.get_data_summary()
        
        return create_success_response(summary, "Data summary retrieved successfully")
        
    except Exception as e:
        logger.error(f"Data summary error: {e}")
        return create_error_response(f"Failed to get data summary: {str(e)}")

# === UTILITY ENDPOINTS ===

@app.route('/api/format/chat', methods=['POST'])
def format_for_chat():
    """Format API response for chat display."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        if not request.is_json:
            return create_error_response("Content-Type must be application/json", 400)
        
        data = request.get_json()
        if not data or 'response' not in data:
            return create_error_response("Missing required field: 'response'", 400)
        
        formatted_text = soccer_api.format_for_chat(data['response'])
        
        return create_success_response({
            "formatted_text": formatted_text,
            "length": len(formatted_text)
        }, "Response formatted for chat")
        
    except Exception as e:
        logger.error(f"Chat formatting error: {e}")
        return create_error_response(f"Failed to format for chat: {str(e)}")

@app.route('/api/format/streamlit', methods=['POST'])
def format_for_streamlit():
    """Format API response for Streamlit display."""
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        if not request.is_json:
            return create_error_response("Content-Type must be application/json", 400)
        
        data = request.get_json()
        if not data or 'response' not in data:
            return create_error_response("Missing required field: 'response'", 400)
        
        formatted_components = soccer_api.format_for_streamlit(data['response'])
        
        return create_success_response(formatted_components, "Response formatted for Streamlit")
        
    except Exception as e:
        logger.error(f"Streamlit formatting error: {e}")
        return create_error_response(f"Failed to format for Streamlit: {str(e)}")

# === DEVELOPMENT/DEBUG ENDPOINTS ===

@app.route('/api/debug/config', methods=['GET'])
def get_config():
    """Get API configuration (debug only)."""
    if not app.debug:
        return create_error_response("Endpoint only available in debug mode", 403)
    
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        config_info = {
            "cache_enabled": soccer_api.config.cache_enabled,
            "max_cache_size": soccer_api.config.max_cache_size,
            "default_min_minutes": soccer_api.config.default_min_minutes,
            "ai_features_enabled": bool(soccer_api.config.openai_api_key),  # Don't expose API key existence
            "query_history_length": len(soccer_api.query_history),
            "version": "1.0.0"  # Add version info instead of sensitive paths
        }
        
        return create_success_response(config_info, "Configuration retrieved")
        
    except Exception as e:
        return create_error_response(f"Failed to get config: {str(e)}")

@app.route('/api/debug/test', methods=['POST'])
def run_test_query():
    """Run a test query (debug only)."""
    if not app.debug:
        return create_error_response("Endpoint only available in debug mode", 403)
    
    try:
        if not soccer_api:
            return create_error_response("API not initialized", 503)
        
        # Test with a simple query
        test_query = "Find young midfielders under 21"
        result = soccer_api.query(test_query)
        
        return create_success_response({
            "test_query": test_query,
            "result": result,
            "test_passed": result.get('success', False)
        }, "Test query completed")
        
    except Exception as e:
        return create_error_response(f"Test query failed: {str(e)}")

# === FRONTEND-COMPATIBLE ENDPOINTS ===

@app.route('/query', methods=['POST'])
def frontend_query():
    """Frontend-compatible query endpoint (matches React TypeScript expectations)."""
    try:
        if not soccer_api:
            return jsonify({
                "response_text": "API not initialized",
                "query_type": "search",
                "error": "Service unavailable"
            }), 503
        
        # Parse request body
        if not request.is_json:
            return jsonify({
                "response_text": "Invalid request format",
                "query_type": "search", 
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "response_text": "Missing query parameter",
                "query_type": "search",
                "error": "Missing required field: 'query'"
            }), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({
                "response_text": "Query cannot be empty",
                "query_type": "search",
                "error": "Empty query"
            }), 400
        
        # Extract optional context
        context_data = data.get('context', {})
        context = QueryContext(
            user_id=context_data.get('user_id'),
            previous_queries=context_data.get('previous_queries', []),
            session_data=context_data.get('session_data', {}),
            preferences=context_data.get('preferences', {})
        )
        
        # Process the query
        result = soccer_api.query(user_query, context)
        
        # Adapt response for frontend (direct format expected by React)
        frontend_result = FrontendResponseAdapter.adapt_query_response(result)
        
        return jsonify(frontend_result)
        
    except Exception as e:
        logger.error(f"Frontend query processing error: {e}")
        return jsonify({
            "response_text": f"Query processing failed: {str(e)}",
            "query_type": "search",
            "error": str(e)
        }), 500

@app.route('/query-stream', methods=['POST'])
def frontend_query_stream():
    """Streaming query endpoint for real-time responses."""
    try:
        if not soccer_api:
            return jsonify({
                "response_text": "API not initialized",
                "query_type": "search",
                "error": "Service unavailable"
            }), 503
        
        # Parse request body
        if not request.is_json:
            return jsonify({
                "response_text": "Invalid request format",
                "query_type": "search",
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "response_text": "Missing query parameter", 
                "query_type": "search",
                "error": "Missing required field: 'query'"
            }), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({
                "response_text": "Query cannot be empty",
                "query_type": "search", 
                "error": "Empty query"
            }), 400
        
        # For now, return the same as non-streaming (can be enhanced later for true streaming)
        context_data = data.get('context', {})
        context = QueryContext(
            user_id=context_data.get('user_id'),
            previous_queries=context_data.get('previous_queries', []),
            session_data=context_data.get('session_data', {}),
            preferences=context_data.get('preferences', {})
        )
        
        # Process the query
        result = soccer_api.query(user_query, context)
        
        # Adapt response for frontend
        frontend_result = FrontendResponseAdapter.adapt_query_response(result)
        
        return jsonify(frontend_result)
        
    except Exception as e:
        logger.error(f"Frontend streaming query error: {e}")
        return jsonify({
            "response_text": f"Streaming query failed: {str(e)}",
            "query_type": "search",
            "error": str(e)
        }), 500

# === ROOT ENDPOINT ===

@app.route('/', methods=['GET'])
def root():
    """API information endpoint."""
    return create_success_response({
        "name": "Soccer Analytics API",
        "version": "1.0.0",
        "description": "AI-powered soccer scout with natural language querying",
        "endpoints": {
            "POST /api/query": "Process natural language queries",
            "GET /api/suggestions": "Get query suggestions",
            "GET /api/history": "Get query history",
            "GET /api/data/summary": "Get data summary",
            "GET /api/health": "Health check",
            "POST /api/format/chat": "Format response for chat",
            "POST /api/format/streamlit": "Format response for Streamlit"
        },
        "features": [
            "Natural language query processing",
            "GPT-4 enhanced tactical analysis",
            "Player comparison and search",
            "Young prospect identification",
            "2,853 players from Big 5 European leagues"
        ]
    }, "Soccer Analytics API is running")

# Initialize API on startup
start_time = time.time()

def create_app(debug=False, enable_production_features=True):
    """Create and configure the Flask app."""
    app.debug = debug
    
    try:
        init_api()
        
        # Apply production middleware if available and enabled
        if PRODUCTION_MIDDLEWARE_AVAILABLE and enable_production_features and not debug:
            config = create_production_config()
            apply_production_middleware(app, config)
            logger.info("🔒 Production middleware enabled")
        elif enable_production_features and not PRODUCTION_MIDDLEWARE_AVAILABLE:
            logger.warning("⚠️ Production middleware requested but not available")
        else:
            logger.info("🔧 Running in development mode - production middleware disabled")
        
        # Set max content length to prevent large payloads
        app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB
        
        logger.info("🚀 Flask API server ready!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Flask app: {e}")
        raise
    
    return app

# Initialize app for production/development
try:
    # Always create the app instance for Gunicorn to find
    logger.info("🚀 Initializing Flask application...")
    
    # Detect if we're in production environment
    is_production = (
        os.getenv('RAILWAY_ENVIRONMENT') is not None or 
        os.getenv('DYNO') is not None or
        os.getenv('RENDER') is not None or
        'gunicorn' in os.environ.get('SERVER_SOFTWARE', '')
    )
    
    if is_production:
        logger.info("🔒 Production environment detected")
        app = create_app(debug=False, enable_production_features=True)
    else:
        logger.info("🔧 Development environment")
        # Create app but don't auto-initialize in development to avoid conflicts
        pass
        
    logger.info("✅ Flask application initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize Flask app: {e}")
    logger.error(f"Error details: {str(e)}")
    
    # Create a minimal error app for Gunicorn to serve
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def error_page():
        return {
            "error": "Application initialization failed",
            "details": str(e),
            "status": "error"
        }, 500
    
    @app.route('/api/health')
    def error_health():
        return {
            "status": "error",
            "error": "Application failed to initialize",
            "details": str(e)
        }, 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Soccer Analytics API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-production-features', action='store_true', 
                       help='Disable production middleware (rate limiting, security headers)')
    
    args = parser.parse_args()
    
    # Initialize the app
    app = create_app(debug=args.debug, enable_production_features=not args.no_production_features)
    
    print("🚀 Starting Soccer Analytics API Server")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔧 Debug mode: {args.debug}")
    print(f"🔒 Production features: {not args.no_production_features}")
    print(f"🧠 GPT-4 enabled: {bool(os.getenv('OPENAI_API_KEY'))}")
    print("=" * 50)
    
    # Run the Flask development server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )