# Soccer Scout AI - Production Deployment Guide

## 🎯 Overview

This guide provides comprehensive instructions for deploying the Soccer Scout AI system to production environments. The system consists of:

- **Frontend**: Next.js + React chat interface with TypeScript
- **Backend**: Flask API server with GPT-4 integration
- **Data**: 2,853+ players from Big 5 European leagues (FBref 2024/25)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI    │───▶│   Flask API     │───▶│   OpenAI GPT-4  │
│   (Frontend)    │    │   (Backend)     │    │   (AI Engine)   │
│   Port 3000     │    │   Port 5001     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run the automated deployment script
./deploy-all.sh
```

### Option 2: Platform-Specific Deployment
```bash
# Deploy to Vercel (Frontend) + Railway (Backend)
./deploy-vercel.sh    # Frontend
./deploy-railway.sh   # Backend

# Deploy to Render (Full Stack)
./deploy-render.sh

# Deploy with Docker (Self-hosted)
./deploy-docker.sh production
```

## 📋 Prerequisites

### Required Tools
- **Node.js** 18+ and npm 8+
- **Python** 3.11+ and pip
- **Git** for version control
- **OpenAI API Key** (required for GPT-4 features)

### Platform-Specific Requirements
- **Vercel**: Vercel CLI (`npm install -g vercel`)
- **Railway**: Railway CLI (`npm install -g @railway/cli`)
- **Docker**: Docker Desktop or Docker Engine
- **Render**: GitHub/GitLab repository

## 🔧 Environment Configuration

### 1. Backend Environment (`.env`)
```bash
# Copy and configure backend environment
cp .env.example .env

# Required variables:
OPENAI_API_KEY=sk-your-api-key-here
FLASK_ENV=production
NODE_ENV=production
CORS_ORIGINS=https://your-frontend-domain.com
```

### 2. Frontend Environment (`soccer-scout-ui/.env.local`)
```bash
# Copy and configure frontend environment
cd soccer-scout-ui
cp .env.example .env.local

# Required variables:
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NODE_ENV=production
```

## 🌐 Platform-Specific Deployments

### Vercel + Railway (Recommended)

**Best for**: Production applications with high availability requirements

#### Backend (Railway)
1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy Backend**:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ./deploy-railway.sh
   ```

3. **Note the backend URL** (e.g., `https://your-app.railway.app`)

#### Frontend (Vercel)
1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Update API URL**:
   ```bash
   export NEXT_PUBLIC_API_URL="https://your-backend.railway.app"
   ```

3. **Deploy Frontend**:
   ```bash
   ./deploy-vercel.sh
   ```

**Pros**: Fast global CDN, automatic scaling, excellent performance
**Cons**: Costs scale with usage

---

### Render (Full Stack)

**Best for**: Simple deployment with minimal configuration

1. **Run setup script**:
   ```bash
   ./deploy-render.sh
   ```

2. **Follow the generated guide** in `RENDER_DEPLOYMENT.md`

3. **Manual steps in Render dashboard**:
   - Create Web Service for backend
   - Create Static Site for frontend
   - Set environment variables
   - Deploy both services

**Pros**: Simple setup, integrated monitoring, free tier available
**Cons**: Slower cold starts on free tier

---

### Docker (Self-hosted)

**Best for**: On-premise deployment or full control over infrastructure

#### Development
```bash
./deploy-docker.sh run
```

#### Production
```bash
./deploy-docker.sh production
```

#### Docker Compose
```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Pros**: Full control, consistent environments, easy scaling
**Cons**: Requires infrastructure management

## 🔒 Security Configuration

### Production Security Headers
- **CSP**: Content Security Policy enabled
- **HSTS**: HTTP Strict Transport Security
- **X-Frame-Options**: Clickjacking protection
- **X-Content-Type-Options**: MIME type sniffing protection

### Rate Limiting
- **Development**: 100 requests/minute, 1000/hour
- **Production**: 60 requests/minute, 500/hour

### CORS Configuration
```python
# Production CORS settings
CORS_ORIGINS = [
    "https://your-frontend.vercel.app",
    "https://your-custom-domain.com"
]
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **Frontend**: `https://your-frontend.com/health`
- **Backend**: `https://your-backend.com/api/health`

### Monitoring
```bash
# Check backend health
curl https://your-backend.com/api/health

# Check frontend health  
curl https://your-frontend.com/health

# View backend logs (Railway)
railway logs

# View frontend logs (Vercel)
vercel logs
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. CORS Errors
**Problem**: Frontend can't connect to backend
**Solution**: Update `CORS_ORIGINS` in backend environment

#### 2. OpenAI API Errors
**Problem**: GPT-4 features not working
**Solution**: Verify `OPENAI_API_KEY` is set correctly

#### 3. Build Failures
**Problem**: Deployment fails during build
**Solution**: Check Node.js/Python versions and dependencies

#### 4. Cold Start Issues
**Problem**: Slow initial response times
**Solution**: Use paid plans or implement warming strategies

### Debug Commands
```bash
# Test backend locally
python3 api_server.py --debug

# Test frontend locally
cd soccer-scout-ui && npm run dev

# Test API connection
python3 test_connection.py

# Run integration tests
python3 test_gpt_integration.py
```

## 📈 Performance Optimization

### Backend Optimizations
- **Gunicorn**: Production WSGI server with gevent workers
- **Caching**: In-memory query result caching
- **Rate Limiting**: Prevents API abuse
- **Data Compression**: Gzip compression enabled

### Frontend Optimizations
- **Next.js**: Server-side rendering and static generation
- **Image Optimization**: WebP and AVIF formats
- **Bundle Splitting**: Optimized JavaScript bundles
- **CDN**: Global content delivery via Vercel

## 🔄 CI/CD Pipeline

### GitHub Actions (Example)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

## 📚 Additional Resources

### Documentation
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

### Platform Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)

### Support
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: This guide and inline code comments

## 🎉 Post-Deployment Checklist

- [ ] ✅ Frontend loads and displays chat interface
- [ ] ✅ Backend API responds to health checks
- [ ] ✅ GPT-4 integration works for tactical queries
- [ ] ✅ Player search and comparison functions work
- [ ] ✅ CORS is properly configured
- [ ] ✅ SSL certificates are active
- [ ] ✅ Custom domains are configured (if applicable)
- [ ] ✅ Monitoring and alerting are set up
- [ ] ✅ Backup and disaster recovery plans are in place
- [ ] ✅ Performance metrics are baseline and monitored
- [ ] ✅ User documentation is updated with production URLs

---

## 🏆 Production Readiness

Your Soccer Scout AI system is now production-ready with:

- **Professional UI**: Modern React chat interface
- **AI Intelligence**: GPT-4 enhanced tactical analysis
- **Scalable Architecture**: Cloud-native deployment
- **Security**: Production-grade security headers and rate limiting
- **Performance**: Optimized for speed and reliability
- **Monitoring**: Health checks and logging

**Ready to scout the next football superstar! ⚽**