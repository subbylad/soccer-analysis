#!/usr/bin/env python3
"""
Revolutionary AI-Native Flask Server for Soccer Scout

Streamlined server that serves the pure AI-first soccer intelligence platform.
Completely replaces pattern-based systems with GPT-4 powered analysis.

Features:
- 3-step AI pipeline: Parser → Analysis → Reasoning
- Professional scout-level tactical intelligence
- Beautiful frontend integration
- Comprehensive error handling
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from api.ai_native_api import create_revolutionary_api
import os
import logging
import time
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS for frontend integration
CORS(app, origins=[
    "http://localhost:3000",           # Local development
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    # Production frontends
    "https://soccer-scout-ui.vercel.app",
    "https://soccer-scout-frontend.vercel.app", 
    "https://*.vercel.app"             # All Vercel deployments
], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Global API instance
revolutionary_api = None

def initialize_revolutionary_api():
    """Initialize the revolutionary AI-native API"""
    global revolutionary_api
    
    logger.info("🚀 Initializing Revolutionary AI-Native Soccer Scout")
    
    try:
        # Get OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            logger.warning("⚠️ No OpenAI API key found - AI features will be unavailable")
            logger.warning("   Set OPENAI_API_KEY environment variable to enable revolutionary features")
            return False
        
        # Initialize revolutionary API
        revolutionary_api = create_revolutionary_api(openai_key)
        logger.info("✅ Revolutionary AI-Native Soccer Scout Ready")
        logger.info(f"   🧠 GPT-4 Analysis Engine: Active")
        logger.info(f"   📊 Comprehensive Data: {revolutionary_api.get_system_status()['data_status']['total_players']} players")
        logger.info(f"   🎯 Tactical Intelligence: Professional Grade")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Revolutionary API: {e}")
        logger.error(f"   Details: {traceback.format_exc()}")
        return False

# Initialize on startup
api_initialized = initialize_revolutionary_api()

@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"🌐 {request.method} {request.path} - {request.remote_addr}")

@app.after_request 
def log_response(response):
    """Log response status"""
    logger.info(f"📤 Response: {response.status_code}")
    return response

# === CORE ENDPOINTS ===

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check for Railway and monitoring"""
    if not revolutionary_api:
        return jsonify({
            "status": "error",
            "service": "revolutionary-ai-soccer-scout",
            "error": "AI engine not initialized - OpenAI API key required",
            "timestamp": datetime.now().isoformat()
        }), 503
    
    try:
        health_status = revolutionary_api.health_check()
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "service": "revolutionary-ai-soccer-scout",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def detailed_health():
    """Detailed health check with system status"""
    if not revolutionary_api:
        return jsonify({
            "success": False,
            "error": "Revolutionary AI engine not initialized",
            "details": "OpenAI API key required for AI-native features"
        }), 503
    
    try:
        status = revolutionary_api.get_system_status()
        return jsonify({
            "success": True,
            "message": "Revolutionary AI-Native System Operational",
            "data": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"System status check failed: {str(e)}"
        }), 500

@app.route('/api/query', methods=['POST'])
def process_revolutionary_query():
    """
    Revolutionary AI-native query processing endpoint
    
    Processes natural language soccer queries using the 3-step AI pipeline:
    1. GPT-4 parses natural language into structured parameters
    2. Python performs high-performance analysis across comprehensive data
    3. GPT-4 generates professional scout-level tactical intelligence
    """
    
    if not revolutionary_api:
        return jsonify({
            "success": False,
            "error": "Revolutionary AI analysis unavailable",
            "error_type": "configuration_error",
            "details": "OpenAI API key required for AI-native features",
            "suggestions": [
                "Contact administrator to configure OpenAI API key",
                "This system requires GPT-4 for professional-grade analysis"
            ]
        }), 503
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json",
                "error_type": "request_format"
            }), 400
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'query' parameter in request body",
                "error_type": "missing_parameter",
                "example": {"query": "Who can play alongside Kobbie Mainoo in Ligue 1?"}
            }), 400
        
        query_text = data['query'].strip()
        if not query_text:
            return jsonify({
                "success": False,
                "error": "Query cannot be empty",
                "error_type": "empty_query",
                "suggestions": [
                    "Try: 'Find creative midfielders like Pedri'",
                    "Try: 'Best young forwards under 21'",
                    "Try: 'Who can replace Rodri for Manchester City?'"
                ]
            }), 400
        
        logger.info(f"🧠 Processing Revolutionary Query: '{query_text}'")
        
        # Execute revolutionary AI analysis with timeout handling
        start_time = time.time()
        MAX_REQUEST_TIME = 50  # Railway timeout protection (60s total - 10s buffer)
        
        try:
            # Pre-check: If we're already close to timeout, return quick error
            if time.time() - start_time > MAX_REQUEST_TIME:
                logger.warning("⚠️ Request timeout detected before processing")
                return jsonify({
                    "success": False,
                    "error": "Request processing timeout - try a simpler query",
                    "error_type": "request_timeout",
                    "execution_time": time.time() - start_time,
                    "response_text": "Processing took too long. Please try a simpler query.",
                    "recommendations": [],
                    "summary": "",
                    "suggestions": [
                        "Try a more specific query",
                        "Reduce the complexity of your request",
                        "Ask about fewer players or attributes"
                    ]
                }), 408  # Request Timeout status
            
            result = revolutionary_api.query(query_text)
            execution_time = time.time() - start_time
            
            # Post-processing timeout check
            if execution_time > MAX_REQUEST_TIME:
                logger.warning(f"⚠️ Query exceeded time limit: {execution_time:.1f}s")
                return jsonify({
                    "success": False,
                    "error": f"Query processing took too long ({execution_time:.1f}s)",
                    "error_type": "processing_timeout",
                    "execution_time": execution_time,
                    "response_text": "Query processing exceeded time limits. Please try a simpler request.",
                    "recommendations": [],
                    "summary": "",
                    "suggestions": [
                        "Try breaking down your query into smaller parts",
                        "Be more specific about player names or positions",
                        "Reduce the scope of your search"
                    ]
                }), 408
            
            # Ensure response_text field exists for frontend compatibility
            if result.get("success") and "response_text" not in result:
                result["response_text"] = result.get("summary", "Analysis completed successfully.")
            
        except Exception as query_exception:
            execution_time = time.time() - start_time
            logger.error(f"❌ Query execution failed after {execution_time:.1f}s: {query_exception}")
            
            # Handle specific timeout-related exceptions
            error_message = str(query_exception)
            if "timeout" in error_message.lower() or execution_time > MAX_REQUEST_TIME:
                return jsonify({
                    "success": False,
                    "error": f"Query processing timeout after {execution_time:.1f}s",
                    "error_type": "timeout_error",
                    "execution_time": execution_time,
                    "response_text": "The query took too long to process. Please try a simpler request.",
                    "recommendations": [],
                    "summary": "",
                    "suggestions": [
                        "Try a more specific query with fewer parameters",
                        "Break complex queries into smaller parts",
                        "Reduce the scope of your player search"
                    ]
                }), 408
            
            # Return structured error response with frontend compatibility
            return jsonify({
                "success": False,
                "error": f"Analysis system error: {error_message}", 
                "error_type": "query_execution_error",
                "execution_time": execution_time,
                "response_text": "Analysis could not be completed due to a system error. Please try again.",
                "recommendations": [],
                "summary": "",
                "suggestions": [
                    "Try rephrasing your query",
                    "Check if the system is temporarily overloaded",
                    "Contact support if the issue persists"
                ]
            }), 500
        
        # Return results
        if result.get("success"):
            logger.info(f"✅ Revolutionary analysis completed in {result.get('execution_time', execution_time):.1f}s")
            return jsonify(result)
        else:
            logger.warning(f"⚠️ Analysis failed: {result.get('error', 'Unknown error')}")
            # Ensure error responses have frontend compatibility fields
            if "response_text" not in result:
                result["response_text"] = result.get("error", "Analysis failed")
            if "recommendations" not in result:
                result["recommendations"] = []
            if "summary" not in result:
                result["summary"] = ""
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"❌ Revolutionary query processing failed: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error during revolutionary analysis: {str(e)}",
            "error_type": "server_error"
        }), 500

@app.route('/api/capabilities', methods=['GET'])
def get_system_capabilities():
    """Get comprehensive system capabilities and example queries"""
    if not revolutionary_api:
        return jsonify({
            "system_type": "revolutionary_ai_native",
            "status": "unavailable",
            "error": "AI engine not initialized - OpenAI API key required"
        }), 503
    
    try:
        capabilities = revolutionary_api.get_capabilities()
        return jsonify({
            "success": True,
            "message": "Revolutionary AI-Native Soccer Scout Capabilities",
            "data": capabilities,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get capabilities: {str(e)}"
        }), 500

# === LEGACY COMPATIBILITY ENDPOINTS ===

@app.route('/query', methods=['POST'])
def legacy_query_endpoint():
    """Legacy endpoint for frontend compatibility"""
    logger.info("📱 Legacy endpoint called - redirecting to revolutionary analysis")
    return process_revolutionary_query()

@app.route('/query-stream', methods=['POST']) 
def legacy_stream_endpoint():
    """Legacy streaming endpoint - returns immediate results for now"""
    logger.info("📱 Legacy stream endpoint called - using revolutionary analysis")
    return process_revolutionary_query()

# === INFORMATION ENDPOINTS ===

@app.route('/', methods=['GET'])
def api_information():
    """API information and documentation"""
    return jsonify({
        "name": "Revolutionary AI-Native Soccer Scout",
        "version": "2.0.2-revolutionary-deployment-fix",
        "description": "Professional-grade soccer intelligence powered by GPT-4",
        "architecture": "3-step AI pipeline: Parser → Analysis → Reasoning",
        
        "features": [
            "🧠 GPT-4 natural language understanding",
            "📊 Multi-dimensional player analysis (50+ metrics)",
            "🎯 Professional scout-level tactical intelligence", 
            "⚽ Formation and system compatibility analysis",
            "🤝 Partnership and playing style assessment",
            "💰 Market intelligence and development potential",
            "🔢 Confidence scoring for all recommendations"
        ],
        
        "endpoints": {
            "POST /api/query": "Revolutionary AI-native query processing",
            "GET /api/capabilities": "System capabilities and examples",
            "GET /api/health": "Detailed system health and status",
            "GET /health": "Simple health check for monitoring"
        },
        
        "example_queries": [
            "Who can play alongside Kobbie Mainoo in Ligue 1?",
            "Find a creative midfielder like Pedri but with better defensive work rate",
            "Alternative to Rodri for Manchester City's pressing system", 
            "Best young wingers under 21 for counter-attacking football",
            "Find a false 9 for Barcelona's possession style"
        ],
        
        "data_coverage": {
            "leagues": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"],
            "season": "2024/25",
            "players": "2,854 with comprehensive metrics",
            "ai_enhanced": True
        },
        
        "system_status": "revolutionary_ai_native" if api_initialized else "initialization_failed"
    })

@app.route('/api/examples', methods=['GET'])
def get_query_examples():
    """Get example queries for different use cases"""
    return jsonify({
        "query_examples": {
            "player_search": [
                "Find creative midfielders in Premier League",
                "Best young defenders under 23",
                "Top goalkeepers in Serie A"
            ],
            "tactical_analysis": [
                "Who can play alongside Kobbie Mainoo in Ligue 1?",
                "Find a partner for Bellingham in Real Madrid's midfield",
                "Who complements Haaland's playing style?"
            ],
            "alternatives": [
                "Alternative to Rodri for Manchester City",
                "Find a replacement for Benzema",
                "Who can replace Casemiro's role?"
            ],
            "style_matching": [
                "Find players similar to Pedri's style",
                "Creative midfielder like De Bruyne but younger",
                "Defensive midfielder with Kante's work rate"
            ],
            "formation_specific": [
                "Find a false 9 for Barcelona's system",
                "Best wing-backs for a 3-5-2 formation",
                "Central midfielder for Pep's 4-3-3"
            ]
        },
        "advanced_queries": [
            "Find a creative midfielder like Pedri but with better defensive work rate for a 4-3-3 formation",
            "Who are the most undervalued strikers in Ligue 1 under 25?",
            "Find a left-footed center-back who can play out from the back like Stones"
        ]
    })

# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "error_type": "not_found",
        "available_endpoints": [
            "POST /api/query - Revolutionary AI analysis",
            "GET /api/capabilities - System capabilities", 
            "GET /api/health - System status",
            "GET / - API information"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "error_type": "server_error",
        "suggestion": "Try again in a moment or contact support"
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {e}")
    logger.error(f"   Traceback: {traceback.format_exc()}")
    
    return jsonify({
        "success": False,
        "error": "Unexpected server error",
        "error_type": "unhandled_exception",
        "details": str(e) if app.debug else "Contact support for assistance"
    }), 500

# === MAIN APPLICATION ===

def create_app(debug=False):
    """Create and configure the Flask app"""
    app.debug = debug
    
    # Set security headers for production
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY' 
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app

# Configure app for production deployment (Railway/gunicorn)
app = create_app(debug=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Revolutionary AI-Native Soccer Scout API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5001)), help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Configure app for local development
    app.debug = args.debug
    
    print("🚀 Starting Revolutionary AI-Native Soccer Scout API")
    print("=" * 60)
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔧 Debug mode: {args.debug}")
    print(f"🧠 AI Engine: {'✅ Active' if api_initialized else '❌ Not Available'}")
    print(f"📊 Architecture: 3-Step AI Pipeline (Parser → Analysis → Reasoning)")
    
    if api_initialized:
        status = revolutionary_api.get_system_status()
        print(f"👥 Players: {status['data_status']['total_players']}")
        print(f"📈 Metrics: {status['data_status']['total_metrics']} per player")
        print(f"🎯 Intelligence: Professional Scout Grade")
    else:
        print("⚠️  Set OPENAI_API_KEY environment variable to enable AI features")
    
    print("=" * 60)
    
    # Run the server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )