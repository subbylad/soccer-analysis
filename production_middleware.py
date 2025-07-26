#!/usr/bin/env python3
"""
Production Middleware for Soccer Analytics API

Additional middleware for production deployment including rate limiting,
request validation, security headers, and enhanced logging.
"""

import time
import logging
import functools
from collections import defaultdict, deque
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify, g
import threading

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 100, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.clients = defaultdict(lambda: {
            'minute': deque(),
            'hour': deque()
        })
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """Check if client is allowed to make request."""
        current_time = time.time()
        
        with self.lock:
            client_data = self.clients[client_id]
            
            # Clean old entries
            self._clean_old_entries(client_data['minute'], current_time - 60)
            self._clean_old_entries(client_data['hour'], current_time - 3600)
            
            # Check limits
            minute_count = len(client_data['minute'])
            hour_count = len(client_data['hour'])
            
            if minute_count >= self.requests_per_minute:
                return False, {
                    'error': 'Rate limit exceeded (per minute)',
                    'retry_after': 60,
                    'limit': self.requests_per_minute,
                    'current': minute_count
                }
            
            if hour_count >= self.requests_per_hour:
                return False, {
                    'error': 'Rate limit exceeded (per hour)',
                    'retry_after': 3600,
                    'limit': self.requests_per_hour,
                    'current': hour_count
                }
            
            # Add current request
            client_data['minute'].append(current_time)
            client_data['hour'].append(current_time)
            
            return True, {
                'remaining_minute': self.requests_per_minute - minute_count - 1,
                'remaining_hour': self.requests_per_hour - hour_count - 1
            }
    
    def _clean_old_entries(self, queue: deque, cutoff_time: float):
        """Remove entries older than cutoff time."""
        while queue and queue[0] < cutoff_time:
            queue.popleft()

class RequestValidator:
    """Validate incoming requests."""
    
    @staticmethod
    def validate_query_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate query request data."""
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"
        
        if 'query' not in data:
            return False, "Missing required field: 'query'"
        
        query = data['query']
        if not isinstance(query, str):
            return False, "Field 'query' must be a string"
        
        query = query.strip()
        if not query:
            return False, "Query cannot be empty"
        
        if len(query) > 500:
            return False, "Query too long (max 500 characters)"
        
        # Optional context validation
        if 'context' in data:
            context = data['context']
            if not isinstance(context, dict):
                return False, "Field 'context' must be an object"
        
        return True, None
    
    @staticmethod
    def validate_format_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate format request data."""
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"
        
        if 'response' not in data:
            return False, "Missing required field: 'response'"
        
        if not isinstance(data['response'], dict):
            return False, "Field 'response' must be an object"
        
        return True, None

class SecurityHeaders:
    """Add security headers to responses."""
    
    @staticmethod
    def apply_headers(response):
        """Apply security headers to response."""
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self' https:; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), screen-wake-lock=()"
        )
        
        return response

class RequestLogger:
    """Enhanced request logging."""
    
    @staticmethod
    def log_request():
        """Log incoming request with details."""
        g.start_time = time.time()
        
        # Log request details
        logger.info(f"REQUEST: {request.method} {request.path}")
        logger.info(f"  Client: {request.remote_addr}")
        logger.info(f"  User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        if request.is_json and hasattr(request, 'json') and request.json:
            # Log query but not full data for privacy
            if 'query' in request.json:
                query = request.json['query'][:100]  # First 100 chars
                logger.info(f"  Query: {query}{'...' if len(request.json['query']) > 100 else ''}")
    
    @staticmethod
    def log_response(response):
        """Log response with timing."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(f"RESPONSE: {response.status_code} ({duration:.3f}s)")
        else:
            logger.info(f"RESPONSE: {response.status_code}")
        
        return response

def apply_production_middleware(app, config: Optional[Dict[str, Any]] = None):
    """Apply all production middleware to Flask app."""
    
    if config is None:
        config = {}
    
    # Initialize rate limiter
    rate_limiter = RateLimiter(
        requests_per_minute=config.get('rate_limit_per_minute', 100),
        requests_per_hour=config.get('rate_limit_per_hour', 1000)
    )
    
    # Rate limiting middleware
    @app.before_request
    def check_rate_limit():
        """Check rate limits before processing request."""
        
        # Skip rate limiting for health checks
        if request.path == '/api/health':
            return None
        
        client_id = request.remote_addr
        allowed, info = rate_limiter.is_allowed(client_id)
        
        if not allowed:
            response = jsonify({
                'success': False,
                'error': {
                    'message': info['error'],
                    'status_code': 429,
                    'retry_after': info['retry_after'],
                    'limit': info['limit'],
                    'current': info['current']
                }
            })
            response.status_code = 429
            response.headers['Retry-After'] = str(info['retry_after'])
            return response
        
        # Add rate limit headers to successful requests
        g.rate_limit_info = info
    
    # Request validation middleware
    @app.before_request
    def validate_request():
        """Validate request format and content."""
        
        # Skip validation for GET requests and health checks
        if request.method == 'GET' or request.path == '/api/health':
            return None
        
        # Check content type for POST requests
        if request.method == 'POST':
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': {
                        'message': 'Content-Type must be application/json',
                        'status_code': 400
                    }
                }), 400
            
            try:
                data = request.get_json()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': {
                        'message': f'Invalid JSON: {str(e)}',
                        'status_code': 400
                    }
                }), 400
            
            # Validate specific endpoints
            if request.path == '/api/query':
                valid, error_msg = RequestValidator.validate_query_request(data)
                if not valid:
                    return jsonify({
                        'success': False,
                        'error': {
                            'message': error_msg,
                            'status_code': 400
                        }
                    }), 400
            
            elif request.path in ['/api/format/chat', '/api/format/streamlit']:
                valid, error_msg = RequestValidator.validate_format_request(data)
                if not valid:
                    return jsonify({
                        'success': False,
                        'error': {
                            'message': error_msg,
                            'status_code': 400
                        }
                    }), 400
    
    # Request logging
    app.before_request(RequestLogger.log_request)
    
    # Response middleware
    @app.after_request
    def enhance_response(response):
        """Add security headers and rate limit info to response."""
        
        # Add security headers (except in debug mode for easier development)
        if not app.debug:
            response = SecurityHeaders.apply_headers(response)
        
        # Add rate limit headers
        if hasattr(g, 'rate_limit_info'):
            info = g.rate_limit_info
            response.headers['X-RateLimit-Remaining-Minute'] = str(info['remaining_minute'])
            response.headers['X-RateLimit-Remaining-Hour'] = str(info['remaining_hour'])
        
        # Log response
        response = RequestLogger.log_response(response)
        
        return response
    
    # Global error handler
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': {
                'message': 'Endpoint not found',
                'status_code': 404,
                'available_endpoints': [
                    'GET /api/health',
                    'POST /api/query',
                    'GET /api/suggestions',
                    'GET /api/history',
                    'GET /api/data/summary',
                    'POST /api/format/chat',
                    'POST /api/format/streamlit'
                ]
            }
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle method not allowed errors."""
        return jsonify({
            'success': False,
            'error': {
                'message': f'Method {request.method} not allowed for {request.path}',
                'status_code': 405,
                'allowed_methods': list(e.valid_methods) if hasattr(e, 'valid_methods') else []
            }
        }), 405
    
    @app.errorhandler(413)
    def request_too_large(e):
        """Handle request too large errors."""
        return jsonify({
            'success': False,
            'error': {
                'message': 'Request too large',
                'status_code': 413,
                'max_size': '1MB'
            }
        }), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Handle rate limit exceeded (this should be handled by middleware, but just in case)."""
        return jsonify({
            'success': False,
            'error': {
                'message': 'Rate limit exceeded',
                'status_code': 429,
                'retry_after': 60
            }
        }), 429
    
    logger.info("✅ Production middleware applied successfully")
    logger.info(f"   Rate limiting: {config.get('rate_limit_per_minute', 100)}/min, {config.get('rate_limit_per_hour', 1000)}/hour")
    logger.info("   Security headers enabled")
    logger.info("   Request validation enabled")
    logger.info("   Enhanced logging enabled")

def create_production_config() -> Dict[str, Any]:
    """Create production configuration for middleware."""
    return {
        'rate_limit_per_minute': 100,  # Requests per minute per IP
        'rate_limit_per_hour': 1000,   # Requests per hour per IP
        'enable_security_headers': True,
        'enable_request_validation': True,
        'enable_detailed_logging': True
    }