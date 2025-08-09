#!/bin/bash
# Simple start script for Railway

echo "🚀 Starting Soccer Scout API..."
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

# Try to start with gunicorn
gunicorn --bind 0.0.0.0:$PORT --timeout 55 --workers 1 simple_scout_api:app