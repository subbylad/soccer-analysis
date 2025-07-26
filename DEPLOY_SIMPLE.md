# Simple Deployment Guide

After the codebase cleanup, deployment is now straightforward with clean configuration files.

## 🚂 Railway Backend Deployment

1. **Connect Repository**: Link your GitHub repo to Railway
2. **Set Environment Variable**:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. **Deploy**: Railway will automatically use `nixpacks.toml` configuration
4. **Configuration Used**:
   - `nixpacks.toml`: Start command with gunicorn
   - `gunicorn.conf.py`: Production server settings
   - `requirements.txt`: Python dependencies

## 🌍 Vercel Frontend Deployment

1. **Connect Repository**: Link your GitHub repo to Vercel
2. **Root Directory**: Set to `soccer-scout-ui`
3. **Framework**: Next.js (auto-detected)
4. **Environment Variable** (optional):
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
   ```
5. **Deploy**: Vercel will use `vercel.json` configuration

## 🧪 Test Deployment

### Railway Backend Test:
```bash
curl https://your-railway-app.railway.app/api/health
```

### Vercel Frontend Test:
```bash
curl https://your-vercel-app.vercel.app/api/health
```

## 📁 Essential Files

- **Backend**: `api_server.py`, `nixpacks.toml`, `gunicorn.conf.py`, `requirements.txt`
- **Frontend**: `soccer-scout-ui/` directory with `vercel.json`
- **Data**: `data/clean/` contains all player data
- **Config**: Clean, single-purpose configuration files

## 🔧 Local Development

```bash
# Backend
python3 api_server.py --port 5001 --debug

# Frontend  
cd soccer-scout-ui
npm run dev
```

Visit: http://localhost:3000

## 🎯 What's Different After Cleanup

- ✅ Single deployment method per platform (no more multiple scripts)
- ✅ Clean configuration files (no duplicates)
- ✅ All debug/test files removed
- ✅ Core functionality preserved and tested
- ✅ Professional project structure

The Soccer Scout AI is now ready for reliable production deployment! 🚀