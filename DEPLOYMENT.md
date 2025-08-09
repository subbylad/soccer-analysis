# Deployment Guide - Simple Scout API

## Railway Deployment (Recommended)

### 1. Prerequisites
- Railway account
- GitHub repository connected
- OpenAI API key

### 2. Environment Variables
Set these in Railway dashboard:
```
OPENAI_API_KEY=your-gpt-5-api-key-here
PORT=8080
```

### 3. Deploy
1. Connect your GitHub repo to Railway
2. Railway will auto-deploy using `railway.toml`
3. Wait for build to complete
4. Access at: `https://your-app.up.railway.app`

### 4. Verify Deployment
```bash
# Health check
curl https://your-app.up.railway.app/health

# Test query
curl -X POST https://your-app.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find young midfielders in Premier League"}'
```

## Local Development

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run server
python3 simple_scout_api.py

# Test
curl http://localhost:8080/health
```

## Architecture
- **API**: `simple_scout_api.py` - Two-stage AI architecture
- **Models**: GPT-5-nano (parser) + GPT-5-mini (analysis)
- **Data**: 2,854 players from Big 5 leagues
- **Endpoints**: `/chat`, `/api/query`, `/health`

## Troubleshooting
- If health check shows "unhealthy", check OPENAI_API_KEY
- If timeouts occur, queries may be too complex
- Check Railway logs for detailed errors