#!/usr/bin/env python3
"""
Test script specifically for GPT-4 first architecture
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_gpt4_first():
    """Test GPT-4 first processing with various query types."""
    
    print("🤖 Testing GPT-4 FIRST Architecture")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ No OpenAI API key found!")
        print("   Set OPENAI_API_KEY environment variable to test GPT-4 first architecture")
        return False
    
    print("✅ OpenAI API key found - testing GPT-4 first processing\n")
    
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
    
    # Test queries that should go to GPT-4
    gpt4_queries = [
        "Find the best young midfielders under 22",
        "Who are the top goal scorers in Serie A this season?",
        "Show me creative midfielders with good passing stats",
        "Which defenders have the most progressive passes?",
        "Find players similar to Pedri's playing style",
        "Who would be a good partner for Declan Rice in midfield?",
    ]
    
    print(f"\n🧠 Testing {len(gpt4_queries)} GPT-4 queries:")
    print("-" * 40)
    
    for i, query in enumerate(gpt4_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        
        try:
            # Process the query
            result = api.query(query)
            
            # Display results
            success = result.get('success', False)
            query_type = result.get('type', 'unknown')
            execution_time = result.get('total_execution_time', 0)
            
            print(f"   ✅ Success: {success}")
            print(f"   🤖 Type: {query_type}")
            print(f"   ⏱️  Time: {execution_time:.2f}s")
            
            if success:
                total_found = result.get('total_found', 0)
                print(f"   📊 Results: {total_found} items")
                
                # Show if GPT-4 was actually used
                if query_type == 'gpt4_analysis':
                    print("   🎉 GPT-4 ANALYSIS USED!")
                    
                    # Show generated code if available
                    generated_code = result.get('generated_code', '')
                    if generated_code:
                        code_preview = generated_code.replace('\n', ' ')[:100]
                        print(f"   🔧 Code: {code_preview}...")
                    
                    # Show insights
                    insights = result.get('insights', [])
                    if insights:
                        print(f"   💡 Insights: {len(insights)} generated")
                        
                elif query_type == 'player_list':
                    print("   ⚠️  Used legacy pattern matching")
                else:
                    print(f"   ❓ Unexpected type: {query_type}")
                
                # Show a preview of results
                chat_text = result.get('chat_text', '')
                if chat_text:
                    preview = chat_text.replace('\n', ' ')[:150]
                    print(f"   💬 Preview: {preview}...")
                    
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"   ❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Test one comparison (should still use pattern matching)
    print(f"\n🔄 Testing comparison (should use pattern matching):")
    print("-" * 50)
    
    comparison_query = "Compare Haaland vs Mbappé"
    print(f"Query: \"{comparison_query}\"")
    
    try:
        result = api.query(comparison_query)
        query_type = result.get('type', 'unknown')
        success = result.get('success', False)
        
        print(f"   ✅ Success: {success}")
        print(f"   📊 Type: {query_type}")
        
        if query_type == 'comparison':
            print("   ✅ Correctly used pattern matching for comparison")
        elif query_type == 'gpt4_analysis':
            print("   ⚠️  Used GPT-4 instead of pattern matching")
        else:
            print(f"   ❓ Unexpected type: {query_type}")
            
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    print(f"\n{'=' * 50}")
    print("🎉 GPT-4 First Architecture Test Completed!")
    print("\n🔍 Summary:")
    print("   - GPT-4 should be used for all complex queries")
    print("   - Simple comparisons should still use pattern matching")
    print("   - Generated code should be visible in results")
    print("   - AI insights should be provided")
    
    return True

if __name__ == "__main__":
    success = test_gpt4_first()
    exit(0 if success else 1)