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

echo "🔧 Pre-deployment checks..."

# Check for potential issues
if grep -q "output.*export" next.config.ts; then
    echo "⚠️  WARNING: Static export detected in next.config.ts"
    echo "   This will disable API routes. Make sure it's conditional."
fi

if [ ! -f "vercel.json" ]; then
    echo "⚠️  WARNING: No vercel.json found. Using default configuration."
else
    echo "✅ vercel.json configuration found"
fi

# Clean build artifacts
echo "🧹 Cleaning previous builds..."
rm -rf .next out

echo "📦 Building and deploying Next.js frontend..."
echo "   Framework: Next.js with App Router"
echo "   API Routes: /api/health, /api/query"

# Build and deploy
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "🧪 Test your deployment:"
    echo "   node test-vercel-deployment.js your-app.vercel.app"
    echo ""
    echo "🔧 To connect to Railway backend:"
    echo "1. Get your Railway deployment URL"
    echo "2. Set environment variable in Vercel dashboard:"
    echo "   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app"
    echo ""
    echo "📊 Features available:"
    echo "• Professional Next.js UI with App Router"
    echo "• Working API routes (/api/health, /api/query)"
    echo "• Mock responses for demonstration"
    echo "• Real-time chat interface"
    echo "• Player cards and visualizations"
else
    echo ""
    echo "❌ Deployment failed!"
    echo ""
    echo "🔍 Common issues to check:"
    echo "1. Make sure no static export is enabled"
    echo "2. Check that API routes are in src/app/api/*/route.ts"
    echo "3. Verify vercel.json configuration"
    echo "4. Check build logs in Vercel dashboard"
fi