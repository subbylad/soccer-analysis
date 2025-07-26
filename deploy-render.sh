#!/bin/bash
# Soccer Scout AI - Render Deployment Script
# This script helps set up deployment to Render.com

set -e

echo "🚀 Soccer Scout AI - Render Deployment Guide"
echo "============================================"

echo "🔧 Render doesn't have a CLI, so this script will:"
echo "   1. Create necessary configuration files"
echo "   2. Provide step-by-step deployment instructions"
echo ""

# Create render.yaml for infrastructure as code
cat > render.yaml << 'EOF'
# Soccer Scout AI - Render Configuration
services:
  # Backend API Service
  - type: web
    name: soccer-scout-api
    env: python
    plan: free  # Change to starter/standard for production
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --config gunicorn.conf.py api_server:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_HOST
        value: 0.0.0.0
      - key: LOG_LEVEL
        value: INFO
      - key: ENABLE_RATE_LIMITING
        value: true
      - key: ENABLE_SECURITY_HEADERS
        value: true
      - key: OPENAI_API_KEY
        sync: false  # Set manually in Render dashboard for security
      - key: CORS_ORIGINS
        value: https://your-frontend.onrender.com

  # Frontend Service (Static Site)
  - type: static_site
    name: soccer-scout-ui
    buildCommand: cd soccer-scout-ui && npm install && npm run build:production
    publishPath: soccer-scout-ui/out
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_API_URL
        value: https://soccer-scout-api.onrender.com
EOF

echo "✅ Created render.yaml configuration file"

# Create build script for frontend
cat > soccer-scout-ui/build-render.sh << 'EOF'
#!/bin/bash
# Render build script for Next.js frontend
npm install
npm run build:production
EOF

chmod +x soccer-scout-ui/build-render.sh
echo "✅ Created frontend build script"

# Create deployment checklist
cat > RENDER_DEPLOYMENT.md << 'EOF'
# Render Deployment Guide

## Prerequisites
1. GitHub/GitLab repository with your code
2. Render account (https://render.com)
3. OpenAI API key

## Backend Deployment (Flask API)

### Step 1: Create Web Service
1. Go to Render Dashboard → Create → Web Service
2. Connect your GitHub repository
3. Use these settings:
   - **Name**: soccer-scout-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --config gunicorn.conf.py api_server:app`
   - **Plan**: Free (or Starter for production)

### Step 2: Set Environment Variables
Add these in the Environment section:
- `FLASK_ENV` = `production`
- `FLASK_HOST` = `0.0.0.0`
- `LOG_LEVEL` = `INFO`
- `ENABLE_RATE_LIMITING` = `true`
- `ENABLE_SECURITY_HEADERS` = `true`
- `OPENAI_API_KEY` = `your_openai_api_key_here`
- `CORS_ORIGINS` = `https://your-frontend.onrender.com`

### Step 3: Deploy
Click "Create Web Service" and wait for deployment.

## Frontend Deployment (Next.js)

### Step 1: Create Static Site
1. Go to Render Dashboard → Create → Static Site
2. Connect your GitHub repository
3. Use these settings:
   - **Name**: soccer-scout-ui
   - **Root Directory**: soccer-scout-ui
   - **Build Command**: `npm install && npm run build:production`
   - **Publish Directory**: `.next`

### Step 2: Set Environment Variables
- `NODE_ENV` = `production`
- `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`

### Step 3: Deploy
Click "Create Static Site" and wait for deployment.

## Post-Deployment
1. Update CORS_ORIGINS in backend with actual frontend URL
2. Test both services
3. Set up custom domains if needed
4. Configure monitoring and alerts

## Render URLs
- Backend: https://soccer-scout-api.onrender.com
- Frontend: https://soccer-scout-ui.onrender.com
EOF

echo "✅ Created deployment guide: RENDER_DEPLOYMENT.md"

# Check environment variables
echo ""
echo "🔍 Environment Check:"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set - you'll need to add this in Render dashboard"
else
    echo "✅ OPENAI_API_KEY is set"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub/GitLab"
echo "2. Follow the guide in RENDER_DEPLOYMENT.md"
echo "3. Set up your services on Render.com"
echo "4. Configure environment variables"
echo "5. Deploy and test!"

echo ""
echo "🔗 Useful Links:"
echo "   Render Dashboard: https://dashboard.render.com"
echo "   Documentation: https://render.com/docs"
echo "   Support: https://render.com/support"

echo ""
echo "💡 Tips:"
echo "   - Free tier sleeps after 15 minutes of inactivity"
echo "   - Use Starter plan ($7/month) for production workloads"
echo "   - Set up health checks and monitoring"
echo "   - Consider using Render PostgreSQL for data persistence"