#!/usr/bin/env python3
"""
Test script for GPT-4 enhanced tactical query processing.

This script demonstrates the new AI-powered soccer scout capabilities
with complex tactical analysis queries.
"""

import os
import sys
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_tactical_queries():
    """Test the GPT-4 enhanced tactical query processing."""
    
    print("🤖 Testing GPT-4 Enhanced Soccer Scout AI")
    print("=" * 50)
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found in environment.")
        print("   GPT-4 features will be disabled.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        print()
    else:
        print("✅ OpenAI API key found - GPT-4 enhanced parsing enabled")
        print()

    # Initialize API with OpenAI support
    config = APIConfig(openai_api_key=api_key)
    
    try:
        api = SoccerAnalyticsAPI(config)
        print("✅ Soccer Analytics API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return False
    
    # Test queries - from simple to complex
    test_queries = [
        # Traditional queries (should work with pattern matching)
        "Find young midfielders under 21",
        "Compare Haaland vs Mbappé",
        
        # Tactical queries (require GPT-4 enhancement)
        "Who can play alongside Kobbie Mainoo in Ligue 1?",
        "Find an alternative to Rodri for Manchester City",
        "Show me players similar to Pedri's style",
        "Who would complement Bellingham in Real Madrid's midfield?",
        "Find defensive midfielders who can replace Casemiro"
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}/{len(test_queries)}: '{query}'")
        print("-" * 60)
        
        try:
            # Process the query
            result = api.query(query)
            
            # Check if successful
            if result.get('success', False):
                print(f"✅ Query successful!")
                print(f"   Type: {result.get('type', 'unknown')}")
                print(f"   Confidence: {result.get('query_confidence', 0):.2f}")
                print(f"   Time: {result.get('total_execution_time', 0):.2f}s")
                
                # Show chat preview
                chat_text = result.get('chat_text', '')
                if chat_text:
                    preview = chat_text.replace('\n', ' ')[:150]
                    print(f"   Preview: {preview}...")
                
                successful_queries += 1
                
            else:
                print(f"❌ Query failed: {result.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Query exception: {e}")
    
    # Summary
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"📈 Success rate: {(successful_queries/len(test_queries)*100):.1f}%")
    
    if api_key and successful_queries > 0:
        print(f"🧠 GPT-4 enhanced tactical analysis is working!")
        print(f"   The system can now handle complex queries like:")
        print(f"   - 'Who can play alongside [player]?'")
        print(f"   - 'Find alternatives to [player] for [team]'")
        print(f"   - 'Show players similar to [player]'s style'")
    
    return successful_queries == len(test_queries)

def demo_gpt_parsing():
    """Demonstrate the GPT-4 query parsing process."""
    
    print("\n🧠 GPT-4 Query Parsing Demo")
    print("=" * 50)
    
    from api.query_processor import GPTEnhancedQueryProcessor
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key required for this demo")
        return
    
    gpt_processor = GPTEnhancedQueryProcessor(api_key=api_key)
    
    test_query = "Who can play alongside Kobbie Mainoo in Ligue 1?"
    
    print(f"Query: '{test_query}'")
    print()
    
    # Check if GPT-4 would enhance this query
    if gpt_processor.can_enhance(test_query):
        print("✅ Query identified as suitable for GPT-4 enhancement")
        
        try:
            enhanced_request = gpt_processor.enhance_query(test_query)
            if enhanced_request:
                print(f"🎯 Parsed as: {enhanced_request.query_type.value}")
                print(f"📍 Target player: {getattr(enhanced_request, 'target_player', 'N/A')}")
                print(f"🌍 League: {getattr(enhanced_request, 'league', 'N/A')}")
                print(f"📊 Tactical context: {getattr(enhanced_request, 'tactical_context', 'N/A')}")
                print(f"🧠 Reasoning: {getattr(enhanced_request, 'reasoning', 'N/A')}")
            else:
                print("❌ GPT-4 parsing failed")
        except Exception as e:
            print(f"💥 GPT-4 parsing error: {e}")
    else:
        print("ℹ️  Query would use traditional pattern matching")

if __name__ == "__main__":
    print("🚀 Starting GPT-4 Enhanced Soccer Scout Tests\n")
    
    # Run main tests
    success = test_tactical_queries()
    
    # Demo GPT parsing if API key available
    if os.getenv('OPENAI_API_KEY'):
        demo_gpt_parsing()
    
    # Final status
    if success:
        print("\n🎉 All tests passed! GPT-4 enhanced soccer scout is ready!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Next steps:")
    print("   1. Set OPENAI_API_KEY for full GPT-4 features") 
    print("   2. Test complex tactical queries in the chat interface")
    print("   3. Integrate with modern React/Vue chat UI")