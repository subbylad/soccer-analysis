#!/bin/bash

echo "🚀 Deploying Soccer Scout UI to Vercel"
echo "====================================="

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install it first:"
    echo "   npm install -g vercel"
    exit 1
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔑 Please login to Vercel first:"
    echo "   vercel login"
    exit 1
fi

echo "📦 Building and deploying Next.js frontend..."
echo "   This deployment uses mock API responses"
echo "   Connect to Railway backend by setting NEXT_PUBLIC_API_URL"

# Build and deploy
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔧 To connect to Railway backend:"
echo "1. Get your Railway deployment URL"
echo "2. Set environment variable in Vercel dashboard:"
echo "   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app"
echo ""
echo "📊 Features available:"
echo "• Professional Next.js UI"
echo "• Mock responses for demonstration"
echo "• Real-time chat interface"
echo "• Player cards and visualizations"