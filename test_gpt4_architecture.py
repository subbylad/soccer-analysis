#!/usr/bin/env python3
"""
Test script for the new GPT-4 first architecture
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_gpt4_architecture():
    """Test the new GPT-4 first architecture."""
    
    print("🧪 Testing GPT-4 First Architecture for Soccer Analytics")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️  Warning: No OpenAI API key found in environment")
        print("   Set OPENAI_API_KEY to test GPT-4 functionality")
        print("   Testing fallback behavior instead...\n")
    else:
        print("✅ OpenAI API key found - testing full GPT-4 functionality\n")
    
    # Initialize API with GPT-4 support
    try:
        config = APIConfig(
            openai_api_key=openai_key,
            data_dir="data/clean"
        )
        api = SoccerAnalyticsAPI(config)
        print("✅ API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return False
    
    # Test queries - mix of simple and complex
    test_queries = [
        "Compare Haaland vs Mbappé",  # Traditional pattern matching
        "Find young midfielders under 21",  # Should go to GPT-4
        "Who are the best goal scorers in La Liga?",  # Should go to GPT-4
        "Show me defensive midfielders with good passing stats",  # GPT-4
        "What players are similar to Pedri's playing style?",  # Complex GPT-4
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} different query types:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        
        try:
            # Process the query
            result = api.query(query)
            
            # Display results
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   📊 Type: {result.get('type', 'unknown')}")
            print(f"   ⏱️  Time: {result.get('total_execution_time', 0):.2f}s")
            
            if result.get('success'):
                total_found = result.get('total_found', 0)
                print(f"   📈 Results: {total_found} items found")
                
                # Show chat text (first 200 chars)
                chat_text = result.get('chat_text', '')
                if chat_text:
                    preview = chat_text.replace('\n', ' ')[:200]
                    print(f"   💬 Preview: {preview}{'...' if len(chat_text) > 200 else ''}")
                
                # Show if GPT-4 was used
                if result.get('type') == 'gpt4_analysis':
                    print("   🤖 Powered by GPT-4 code generation")
                elif 'generated_code' in result:
                    print("   🤖 GPT-4 enhanced analysis")
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"   ❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
    
    # Test API health
    print(f"\n🏥 API Health Check:")
    print("-" * 30)
    
    try:
        health = api.health_check()
        print(f"   Status: {health.get('status', 'unknown')}")
        
        components = health.get('components', {})
        for component, status in components.items():
            emoji = "✅" if status == "healthy" else "⚠️"
            print(f"   {emoji} {component}: {status}")
            
        data_loaded = health.get('data_loaded', False)
        print(f"   📊 Data loaded: {'✅ Yes' if data_loaded else '❌ No'}")
        
    except Exception as e:
        print(f"   💥 Health check failed: {e}")
    
    # Test data summary
    print(f"\n📊 Data Summary:")
    print("-" * 20)
    
    try:
        summary = api.get_data_summary()
        if 'error' in summary:
            print(f"   ❌ Error: {summary['error']}")
        else:
            total_players = summary.get('total_players', 0)
            leagues = summary.get('leagues', [])
            print(f"   👥 Total players: {total_players}")
            print(f"   🏆 Leagues: {len(leagues)} ({'✅' if leagues else '❌'})")
            if leagues:
                print(f"       {', '.join(leagues[:3])}{'...' if len(leagues) > 3 else ''}")
    except Exception as e:
        print(f"   💥 Data summary failed: {e}")
    
    print(f"\n{'=' * 60}")
    print("🎉 GPT-4 Architecture Test Completed!")
    
    if openai_key:
        print("✅ Full GPT-4 functionality tested")
    else:
        print("⚠️  Fallback behavior tested (set OPENAI_API_KEY for full test)")
    
    print("\n💡 Next steps:")
    print("   1. Set OPENAI_API_KEY environment variable for GPT-4 features")
    print("   2. Test with the frontend chat interface")
    print("   3. Try complex tactical queries like 'Who can play alongside Pedri?'")
    
    return True

if __name__ == "__main__":
    success = test_gpt4_architecture()
    exit(0 if success else 1)