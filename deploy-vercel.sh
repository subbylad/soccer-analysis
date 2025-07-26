#!/bin/bash
# Soccer Scout AI - Vercel Deployment Script (Frontend)
# This script deploys the Next.js frontend to Vercel

set -e

echo "🚀 Soccer Scout AI - Vercel Deployment Script"
echo "============================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Navigate to frontend directory
cd soccer-scout-ui

# Check if we have the required environment variables
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo "⚠️  NEXT_PUBLIC_API_URL not set. Using default..."
    export NEXT_PUBLIC_API_URL="https://your-backend.railway.app"
fi

# Set production environment
export NODE_ENV=production

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Run build to check for errors
echo "🔨 Building application..."
npm run build:production

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod --yes

# Get deployment URL
DEPLOYMENT_URL=$(vercel ls --limit=1 | grep -o 'https://[^ ]*' | head -1)
echo "✅ Deployment successful!"
echo "🌐 Frontend URL: $DEPLOYMENT_URL"
echo "🔗 Backend URL: $NEXT_PUBLIC_API_URL"

echo ""
echo "📝 Post-deployment checklist:"
echo "1. Update CORS_ORIGINS in your backend with: $DEPLOYMENT_URL"
echo "2. Test the deployment: $DEPLOYMENT_URL"
echo "3. Update DNS records if using custom domain"
echo "4. Set up monitoring and analytics"

# Optional: Set up custom domain
read -p "🌐 Do you want to add a custom domain? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain name: " DOMAIN
    vercel domains add $DOMAIN
    echo "🌐 Domain $DOMAIN added. Configure your DNS to point to Vercel."
fi