# Soccer Scout AI - Simple & Reliable

A simplified AI-powered soccer scout that uses GPT-5 models to analyze 2,854 players from Europe's top 5 leagues.

## 🚀 Quick Start

### Local Development
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-gpt-5-api-key"

# Install dependencies
pip install -r requirements.txt

# Run server
python3 simple_scout_api.py

# Test
curl http://localhost:8080/health
```

### Example Queries
```bash
# Find young players
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find creative midfielders in Premier League under 21"}'

# Compare players
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare Haaland vs Mbappé"}'
```

## 🏗️ Architecture

### Two-Stage AI System
1. **GPT-5-nano Parser**: Converts natural language to filter criteria
2. **Database Filter**: Efficient pandas filtering on 2,854 players
3. **GPT-5-mini Analysis**: Generates conversational scout insights

### Key Features
- ✅ No JSON parsing issues
- ✅ Reliable fallback mechanisms
- ✅ Fast response times
- ✅ Frontend compatible
- ✅ Professional scout insights

## 📊 Data Coverage
- **Players**: 2,854 from Big 5 European leagues
- **Season**: 2024/25
- **Leagues**: Premier League, La Liga, Serie A, Bundesliga, Ligue 1
- **Metrics**: 50+ per player including computed metrics

## 🌐 API Endpoints

- `POST /chat` - Main chat endpoint
- `POST /api/query` - Legacy compatibility endpoint
- `GET /health` - Health check
- `GET /` - API information

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway deployment instructions.

## 📁 Project Structure
```
simple_scout_api.py    # Main API server
data/                  # Player database
  comprehensive/
    processed/
      unified_player_data.csv
requirements.txt       # Python dependencies
railway.toml          # Railway config
gunicorn.conf.py      # Production server config
```

## 🔧 Environment Variables
- `OPENAI_API_KEY` - Required for AI features
- `PORT` - Server port (default: 8080)
- `DEBUG` - Enable debug mode (default: false)