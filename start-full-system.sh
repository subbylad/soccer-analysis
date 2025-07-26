#!/bin/bash

# Soccer Scout AI - Full System Startup Script
# Launches both Flask backend (with GPT-4) and Next.js frontend

set -e

echo "🚀 Starting Soccer Scout AI - Full System"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OpenAI API key not found. GPT-4 features will be disabled.${NC}"
    echo -e "${YELLOW}   Set OPENAI_API_KEY environment variable to enable GPT-4 integration.${NC}"
    echo ""
else
    echo -e "${GREEN}✅ OpenAI API key found - GPT-4 features enabled${NC}"
    echo ""
fi

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down Soccer Scout AI...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
}
trap cleanup EXIT INT TERM

# Start Flask Backend (Port 5001)
echo -e "${BLUE}🐍 Starting Flask Backend (GPT-4 Enhanced)...${NC}"
cd /Users/subomiladitan/socceranalysis
python3 api_server.py --port 5001 --debug &
FLASK_PID=$!

# Wait for Flask to start
echo "   Waiting for Flask backend to initialize..."
sleep 3

# Test Flask backend
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo -e "${GREEN}✅ Flask backend running on http://localhost:5001${NC}"
else
    echo -e "${RED}❌ Flask backend failed to start${NC}"
    exit 1
fi

# Start Next.js Frontend (Port 3000)
echo -e "${BLUE}⚛️  Starting Next.js Frontend (Professional UI)...${NC}"
cd /Users/subomiladitan/socceranalysis/soccer-scout-ui
npm run dev &
NEXTJS_PID=$!

# Wait for Next.js to start
echo "   Waiting for Next.js frontend to initialize..."
sleep 5

# Test Next.js frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Next.js frontend running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Next.js frontend failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Soccer Scout AI is fully operational!${NC}"
echo "========================================"
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 Backend API:${NC} http://localhost:5001"
echo -e "${BLUE}🧪 Test Page:${NC} http://localhost:3000/test"
echo ""
echo -e "${YELLOW}💡 Try these queries:${NC}"
echo '   • "Compare Haaland vs Mbappé"'
echo '   • "Who can play alongside Kobbie Mainoo in Ligue 1?"'
echo '   • "Find young midfielders under 21"'
echo '   • "What type of player would complement Bellingham in Real Madrid?"'
echo ""
echo -e "${YELLOW}📊 Features Available:${NC}"
echo "   • Professional Next.js UI with world.org aesthetic"
echo "   • GPT-4 enhanced tactical analysis"
echo "   • 2,850+ players from Big 5 European leagues"
echo "   • Real-time query processing"
echo "   • Interactive suggestions and autocomplete"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"

# Keep script running
wait