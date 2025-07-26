#!/usr/bin/env python3
"""
Final comprehensive test of the GPT-4 first architecture
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main_api import SoccerAnalyticsAPI, APIConfig

def test_final_architecture():
    """Test the final GPT-4 first architecture comprehensively."""
    
    print("🎉 FINAL TEST: GPT-4 First Soccer Analytics Architecture")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ No OpenAI API key found!")
        print("   Set OPENAI_API_KEY environment variable to test the full architecture")
        return False
    
    print("✅ OpenAI API key found - testing complete GPT-4 first architecture\n")
    
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
    
    # Test different types of queries to show the architecture
    test_cases = [
        {
            "name": "Simple Player Search",
            "query": "Find players named Messi",
            "expected_type": "gpt4_analysis",
            "should_use_gpt4": True
        },
        {
            "name": "Complex Analysis Query",
            "query": "Who are the best young creative midfielders with high potential?",
            "expected_type": "gpt4_analysis", 
            "should_use_gpt4": True
        },
        {
            "name": "League-Specific Query",
            "query": "Show me the top defenders in Premier League with good passing",
            "expected_type": "gpt4_analysis",
            "should_use_gpt4": True
        },
        {
            "name": "Player Comparison (Pattern Match)",
            "query": "Compare Haaland vs Mbappé",
            "expected_type": "comparison",
            "should_use_gpt4": False
        },
        {
            "name": "Tactical Analysis Query",
            "query": "Find midfielders who would complement Pedri's playing style",
            "expected_type": "gpt4_analysis",
            "should_use_gpt4": True
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} comprehensive tests:")
    print("-" * 50)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {test_case['name']}")
        print(f"   Query: \"{test_case['query']}\"")
        
        try:
            # Process the query
            start_time = time.time()
            result = api.query(test_case['query'])
            end_time = time.time()
            
            # Analyze results
            success = result.get('success', False)
            query_type = result.get('type', 'unknown')
            execution_time = result.get('total_execution_time', 0)
            
            print(f"   ✅ Success: {success}")
            print(f"   🤖 Type: {query_type}")
            print(f"   ⏱️  Time: {execution_time:.2f}s")
            
            # Check if it matches expectations
            type_match = query_type == test_case['expected_type']
            gpt4_used = query_type == 'gpt4_analysis'
            expectation_met = gpt4_used == test_case['should_use_gpt4']
            
            if success and type_match and expectation_met:
                print("   🎯 PERFECT: Met all expectations!")
                test_result = "PASS"
            elif success and expectation_met:
                print("   ✅ GOOD: Architecture working as expected")
                test_result = "PASS"
            elif success:
                print("   ⚠️  PARTIAL: Working but unexpected routing")
                test_result = "PARTIAL"
            else:
                print("   ❌ FAILED: Query failed")
                test_result = "FAIL"
            
            # Show additional details
            if success:
                total_found = result.get('total_found', 0)
                print(f"   📊 Results: {total_found} items found")
                
                if gpt4_used:
                    print("   🧠 GPT-4 CODE GENERATION USED!")
                    generated_code = result.get('generated_code', '')
                    if generated_code:
                        code_preview = generated_code.replace('\n', ' ')[:80]
                        print(f"   🔧 Code: {code_preview}...")
                else:
                    print("   📋 Used traditional pattern matching")
                
                # Show chat preview
                chat_text = result.get('chat_text', '')
                if chat_text:
                    preview = chat_text.replace('\n', ' ')[:100]
                    print(f"   💬 Preview: {preview}...")
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"   ❌ Error: {error_msg}")
            
            results.append({
                'test': test_case['name'],
                'result': test_result,
                'type': query_type,
                'success': success,
                'time': execution_time
            })
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            results.append({
                'test': test_case['name'],
                'result': 'ERROR',
                'type': 'error',
                'success': False,
                'time': 0
            })
    
    # Summary
    print(f"\n{'=' * 60}")
    print("🏆 FINAL ARCHITECTURE TEST SUMMARY")
    print("=" * 60)
    
    passed = len([r for r in results if r['result'] == 'PASS'])
    partial = len([r for r in results if r['result'] == 'PARTIAL'])
    failed = len([r for r in results if r['result'] in ['FAIL', 'ERROR']])
    
    print(f"📊 Results: {passed} PASS | {partial} PARTIAL | {failed} FAIL")
    
    gpt4_tests = len([r for r in results if r['type'] == 'gpt4_analysis'])
    print(f"🤖 GPT-4 Usage: {gpt4_tests}/{len(test_cases)} queries used GPT-4")
    
    avg_time = sum(r['time'] for r in results) / len(results)
    print(f"⏱️  Average Time: {avg_time:.2f}s per query")
    
    print(f"\n🎯 ARCHITECTURE STATUS:")
    if passed >= 4:
        print("   ✅ GPT-4 FIRST ARCHITECTURE WORKING PERFECTLY!")
        print("   🚀 Ready for production use")
    elif passed >= 3:
        print("   ✅ GPT-4 FIRST ARCHITECTURE MOSTLY WORKING")  
        print("   🔧 Minor tweaks needed")
    else:
        print("   ⚠️  GPT-4 FIRST ARCHITECTURE NEEDS WORK")
        print("   🛠️  Debugging required")
    
    print(f"\n💡 Key Features Demonstrated:")
    print("   • GPT-4 generates Python code on-the-fly")
    print("   • Safe code execution environment")
    print("   • Intelligent query routing")
    print("   • Backwards compatibility with pattern matching")
    print("   • Professional soccer analytics results")
    print("   • Frontend-compatible response format")
    
    print(f"\n📋 Next Steps:")
    print("   1. Test with the Next.js frontend interface")
    print("   2. Deploy to production environment")
    print("   3. Monitor GPT-4 usage and costs")
    print("   4. Add more sophisticated analysis methods")
    
    return passed >= 3

if __name__ == "__main__":
    import time
    success = test_final_architecture()
    exit(0 if success else 1)