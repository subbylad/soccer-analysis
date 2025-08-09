#!/bin/bash

# Super fast log checker - uses API endpoint

echo "⚡ Fast Log Check"

# Check production logs via API
echo -e "\n📊 Recent API logs:"
curl -s https://soccer-scout-api-production.up.railway.app/logs | jq '.logs[-10:]' 2>/dev/null

# Check for errors
echo -e "\n🔍 Recent errors:"
curl -s https://soccer-scout-api-production.up.railway.app/logs | jq '.logs[] | select(.level == "ERROR")' 2>/dev/null

# Quick health check
echo -e "\n❤️  Health status:"
curl -s https://soccer-scout-api-production.up.railway.app/health | jq 2>/dev/null