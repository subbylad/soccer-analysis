"""
Gunicorn configuration for Railway deployment
"""

import os

# Server socket - Railway provides PORT environment variable
port = os.environ.get('PORT', '8000')
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = 1  # Railway has memory limits, keep this low
worker_class = "sync"
worker_connections = 1000
timeout = 55  # Railway timeout optimization - must be under 60s
keepalive = 2

# Restart workers after this many requests, with some randomness
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "soccer-scout-api"

# Preload app for better memory usage
preload_app = True

# Print configuration for debugging
print(f"🚀 Gunicorn starting on port {port}")
print(f"🔧 Bind address: {bind}")