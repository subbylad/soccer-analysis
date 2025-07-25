#!/usr/bin/env python3
"""
Test script for the Soccer Analytics API
Tests the main API coordinator with sample queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main_api import SoccerAnalyticsAPI, quick_query
import json

def test_api_initialization():
    """Test that the API initializes correctly."""
    print("🔧 Testing API initialization...")
    try:
        api = SoccerAnalyticsAPI()
        print("✅ API initialized successfully")
        return api
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return None

def test_health_check(api):
    """Test the API health check."""
    print("\n🏥 Testing health check...")
    try:
        health = api.health_check()
        print(f"Status: {health['status']}")
        for component, status in health.get('components', {}).items():
            print(f"  - {component}: {status}")
        print("✅ Health check completed")
        return health['status'] == 'healthy'
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_data_summary(api):
    """Test getting data summary."""
    print("\n📊 Testing data summary...")
    try:
        summary = api.get_data_summary()
        print(f"Total players: {summary.get('total_players', 'Unknown')}")
        print(f"Data shape: {summary.get('data_shape', 'Unknown')}")
        print(f"Leagues: {summary.get('leagues', [])[:3]}..." if summary.get('leagues') else "Leagues: Unknown")
        print("✅ Data summary retrieved")
        return True
    except Exception as e:
        print(f"❌ Data summary failed: {e}")
        return False

def test_suggestions(api):
    """Test getting query suggestions."""
    print("\n💡 Testing query suggestions...")
    try:
        suggestions = api.get_suggestions()
        print("Sample suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"  {i}. {suggestion}")
        print("✅ Suggestions retrieved")
        return True
    except Exception as e:
        print(f"❌ Suggestions failed: {e}")
        return False

def test_sample_queries(api):
    """Test the API with sample queries."""
    print("\n🔍 Testing sample queries...")
    
    test_queries = [
        "Find young midfielders under 23",
        "Compare Haaland vs Mbappé", 
        "Top scorers in Premier League",
        "Best defensive midfielders"
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}/4: '{query}' ---")
        try:
            # Test the main query method
            response = api.query(query)
            
            # Check response structure
            if response.get('success', False):
                print(f"✅ Query successful")
                print(f"   Type: {response.get('type', 'unknown')}")
                print(f"   Time: {response.get('total_execution_time', 0):.2f}s")
                print(f"   Confidence: {response.get('query_confidence', 0):.2f}")
                
                # Test chat formatting
                chat_text = api.format_for_chat(response)
                print(f"   Chat preview: {chat_text[:100]}...")
                
                successful_queries += 1
            else:
                print(f"❌ Query failed: {response.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Query exception: {e}")
    
    print(f"\n📈 Query Results: {successful_queries}/{len(test_queries)} successful")
    return successful_queries > 0

def test_quick_query_function():
    """Test the convenience quick_query function."""
    print("\n⚡ Testing quick_query function...")
    try:
        result = quick_query("Find young prospects under 21")
        print(f"Quick query result: {result[:150]}...")
        print("✅ Quick query successful")
        return True
    except Exception as e:
        print(f"❌ Quick query failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Starting Soccer Analytics API Tests\n")
    
    # Test 1: Initialize API
    api = test_api_initialization()
    if not api:
        print("\n💥 Cannot continue - API initialization failed")
        return False
    
    # Test 2: Health check
    healthy = test_health_check(api)
    
    # Test 3: Data summary
    data_ok = test_data_summary(api)
    
    # Test 4: Suggestions
    suggestions_ok = test_suggestions(api)
    
    # Test 5: Sample queries
    queries_ok = test_sample_queries(api)
    
    # Test 6: Quick query function
    quick_ok = test_quick_query_function()
    
    # Summary
    print(f"\n" + "="*50)
    print("🎯 TEST SUMMARY")
    print("="*50)
    print(f"✅ API Initialization: {'PASS' if api else 'FAIL'}")
    print(f"✅ Health Check: {'PASS' if healthy else 'FAIL'}")
    print(f"✅ Data Summary: {'PASS' if data_ok else 'FAIL'}")
    print(f"✅ Suggestions: {'PASS' if suggestions_ok else 'FAIL'}")
    print(f"✅ Sample Queries: {'PASS' if queries_ok else 'FAIL'}")
    print(f"✅ Quick Query: {'PASS' if quick_ok else 'FAIL'}")
    
    all_passed = all([api, healthy, data_ok, suggestions_ok, queries_ok, quick_ok])
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED! The API is ready to use.")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)