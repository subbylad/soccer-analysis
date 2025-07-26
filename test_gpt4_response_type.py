#!/usr/bin/env python3
"""
Test GPT-4 response type specifically
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_gpt4_response_type():
    """Test that GPT-4 queries return the correct response type."""
    
    print("🧪 Testing GPT-4 Response Type")
    print("=" * 35)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ No OpenAI API key found!")
        return False
    
    # Initialize API
    try:
        config = APIConfig(openai_api_key=openai_key, data_dir="data/clean")
        api = SoccerAnalyticsAPI(config)
        print("✅ API initialized")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test a simple GPT-4 query
    query = "Search for players named Messi"
    print(f"\nQuery: \"{query}\"")
    
    try:
        result = api.query(query)
        
        success = result.get('success', False)
        response_type = result.get('type', 'unknown')
        
        print(f"✅ Success: {success}")
        print(f"🤖 Type: {response_type}")
        
        if response_type == 'gpt4_analysis':
            print("🎉 CORRECT: GPT-4 analysis type detected!")
            
            # Check for GPT-4 specific fields
            generated_code = result.get('generated_code', '')
            insights = result.get('insights', [])
            
            if generated_code:
                print("🔧 Generated code present")
                code_preview = generated_code.replace('\n', ' ')[:100]
                print(f"   Preview: {code_preview}...")
            
            if insights:
                print(f"💡 Insights present: {len(insights)} insights")
                
            total_found = result.get('total_found', 0)
            print(f"📊 Results: {total_found} items")
            
            return True
        else:
            print(f"❌ WRONG TYPE: Expected 'gpt4_analysis', got '{response_type}'")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_gpt4_response_type()
    exit(0 if success else 1)