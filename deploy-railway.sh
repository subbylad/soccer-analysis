#!/bin/bash
# Soccer Scout AI - Railway Deployment Script (Backend)
# This script deploys the Flask API backend to Railway

set -e

echo "🚀 Soccer Scout AI - Railway Deployment Script"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable is required!"
    echo "   Please set it: export OPENAI_API_KEY='your_api_key_here'"
    exit 1
fi

# Create or link Railway project
echo "🏗️  Setting up Railway project..."
if [ ! -f "railway.json" ]; then
    echo "Creating new Railway project..."
    railway create soccer-scout-api
else
    echo "Using existing Railway project..."
fi

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
railway variables set FLASK_ENV=production
railway variables set NODE_ENV=production
railway variables set FLASK_HOST=0.0.0.0
railway variables set LOG_LEVEL=INFO
railway variables set ENABLE_RATE_LIMITING=true
railway variables set ENABLE_SECURITY_HEADERS=true

# Update CORS origins (will be updated after deployment with actual URL)
railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up --detach

# Wait for deployment to complete
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Get deployment URL
DEPLOYMENT_URL=$(railway domain)
if [ -z "$DEPLOYMENT_URL" ]; then
    # Generate a Railway domain if not exists
    railway domain
    DEPLOYMENT_URL=$(railway domain)
fi

echo "✅ Deployment successful!"
echo "🌐 Backend API URL: https://$DEPLOYMENT_URL"

# Test the deployment
echo "🧪 Testing deployment..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DEPLOYMENT_URL/api/health" || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed (HTTP $HTTP_CODE). Check logs with: railway logs"
fi

echo ""
echo "📝 Post-deployment checklist:"
echo "1. Update frontend NEXT_PUBLIC_API_URL with: https://$DEPLOYMENT_URL"
echo "2. Test API endpoints: https://$DEPLOYMENT_URL/api/health"
echo "3. Check logs: railway logs"
echo "4. Monitor performance: railway status"
echo "5. Set up custom domain if needed: railway domain add your-domain.com"

# Show useful commands
echo ""
echo "🛠️  Useful Railway commands:"
echo "   railway logs          - View application logs"
echo "   railway status        - Check deployment status"
echo "   railway restart       - Restart the application"
echo "   railway variables     - View/edit environment variables"
echo "   railway domain        - Manage custom domains"