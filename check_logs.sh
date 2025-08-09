#!/bin/bash

# Fast Railway log checker

echo "🚀 Fetching Railway logs..."

# Method 1: Get latest deployment logs with timeout
timeout 5 railway logs --deployment 2>/dev/null | tail -50

if [ $? -eq 124 ]; then
    echo "⚠️  Logs taking too long, trying build logs..."
    timeout 5 railway logs --build 2>/dev/null | tail -30
fi

# Show most recent errors/warnings
echo -e "\n📍 Recent errors/warnings:"
timeout 3 railway logs 2>/dev/null | grep -E "ERROR|error|WARNING|warning|failed|Failed" | tail -10 || echo "No recent errors found"