#!/usr/bin/env python3
"""
Test GPT-4 with simple queries to isolate the numpy issue
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_simple_gpt4():
    """Test GPT-4 with simple queries."""
    
    print("🧪 Testing Simple GPT-4 Queries")
    print("=" * 40)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ No OpenAI API key found!")
        return False
    
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
    
    # Simple test queries that shouldn't use complex methods
    simple_queries = [
        "Search for players named Messi",  # Simple search
        "How many players are in the dataset?",  # Simple data info
    ]
    
    print(f"\n🔍 Testing {len(simple_queries)} simple queries:")
    print("-" * 40)
    
    for i, query in enumerate(simple_queries, 1):
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
                if query_type == 'gpt4_analysis':
                    print("   🎉 GPT-4 WORKED!")
                    
                    # Show generated code if available
                    generated_code = result.get('generated_code', '')
                    if generated_code:
                        print(f"   🔧 Generated code:")
                        print(f"      {generated_code[:200]}...")
                        
                    total_found = result.get('total_found', 0)
                    print(f"   📊 Results: {total_found} items")
                    
                elif query_type == 'player_list':
                    print("   ⚠️  Used legacy pattern matching")
                else:
                    print(f"   ❓ Type: {query_type}")
                    
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"   ❌ Error: {error_msg}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            import traceback
            traceback.print_exc()
    
    return True

if __name__ == "__main__":
    success = test_simple_gpt4()
    exit(0 if success else 1)