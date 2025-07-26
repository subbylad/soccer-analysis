#!/bin/bash

echo "🚀 Deploying Soccer Scout AI to Railway"
echo "======================================"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://railway.app/cli"
    exit 1
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔑 Please login to Railway first:"
    echo "   railway login"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found in environment"
    echo "   Export it: export OPENAI_API_KEY='sk-your-key-here'"
    echo "   Or set it in Railway after deployment"
fi

echo "📦 Deploying from current directory..."
echo "   Make sure you've committed your latest changes to git"

# Debug port configuration
echo ""
echo "🔍 Checking PORT configuration..."
echo "   Gunicorn will read PORT from environment variable"
echo "   Railway automatically sets PORT for deployed services"

# Deploy
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "🔧 Next steps:"
echo "1. Set your OpenAI API key:"
echo "   railway variables set OPENAI_API_KEY='sk-your-key-here'"
echo ""
echo "2. Check deployment status:"
echo "   railway status"
echo ""
echo "3. View logs:"
echo "   railway logs"
echo ""
echo "4. Open your app:"
echo "   railway open"