#!/bin/bash

echo "🚀 Soccer Scout API - Environment Setup"
echo "======================================"

# Check if .env exists
if [ -f .env ]; then
    echo "✅ .env file found"
    # Check if OPENAI_API_KEY is set in .env
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env; then
        echo "✅ OPENAI_API_KEY is configured in .env"
    else
        echo "⚠️  OPENAI_API_KEY not configured in .env"
        echo ""
        echo "Please add your OpenAI API key to .env:"
        echo "OPENAI_API_KEY=sk-..."
    fi
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your OpenAI API key:"
    echo "    OPENAI_API_KEY=sk-..."
fi

echo ""
echo "To test your setup:"
echo "  export \$(cat .env | xargs)"
echo "  python3 simple_scout_api.py"
echo ""