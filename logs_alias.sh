#!/bin/bash

# Add this alias to your shell for instant log checking
# Run: source logs_alias.sh

# Instant log check
alias logs='curl -s https://soccer-scout-api-production.up.railway.app/logs | jq ".logs[-10:]"'

# Check errors only
alias logerrors='curl -s https://soccer-scout-api-production.up.railway.app/logs | jq ".logs[] | select(.level == \"ERROR\")"'

# Full Railway logs (with timeout)
alias rlogs='railway logs | tail -50'

echo "✅ Log aliases added!"
echo "Commands:"
echo "  logs      - Show last 10 API logs instantly"
echo "  logerrors - Show only errors"
echo "  rlogs     - Show Railway logs (may be slow)"