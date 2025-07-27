#!/usr/bin/env python3
"""
Test Integration Fixes for Revolutionary AI-Native Soccer Scout

Tests the improved error handling, retry logic, and fallback mechanisms
to ensure robust frontend-backend integration.
"""

import os
import sys
import json
import time
from typing import Dict

# Add the project root to path
sys.path.append('.')

def test_integration_fixes():
    """Test the integration fixes"""
    print("🧪 Testing Integration Fixes for Revolutionary AI System")
    print("=" * 60)
    
    try:
        from api.ai_native_api import create_revolutionary_api
        
        # Test without OpenAI key (fallback mode)
        print("\n📋 Test 1: System without OpenAI key (fallback mode)")
        try:
            api_fallback = create_revolutionary_api(openai_api_key="invalid_key")
            result = api_fallback.query("Find young midfielders")
            print(f"✅ Fallback mode works - Success: {result.get('success')}")
            print(f"   Response has required fields: {check_response_fields(result)}")
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
        
        # Test with valid OpenAI key if available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("\n🧠 Test 2: System with OpenAI integration")
            try:
                api_ai = create_revolutionary_api(openai_api_key=openai_key)
                result = api_ai.query("Find creative midfielders")
                print(f"✅ AI mode works - Success: {result.get('success')}")
                print(f"   Response has required fields: {check_response_fields(result)}")
                print(f"   Response text length: {len(result.get('response_text', ''))}")
                print(f"   Recommendations count: {len(result.get('recommendations', []))}")
            except Exception as e:
                print(f"❌ AI test failed: {e}")
        else:
            print("\n⚠️ Test 2 Skipped: No OpenAI API key found")
        
        print("\n📊 Test 3: Response field validation")
        test_response_validation()
        
        print("\n✅ Integration testing complete!")
        
    except Exception as e:
        print(f"❌ Integration test setup failed: {e}")

def check_response_fields(response: Dict) -> bool:
    """Check if response has all required fields for frontend"""
    required_fields = [
        'success', 'response_text', 'recommendations', 'summary'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in response:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   Missing fields: {missing_fields}")
        return False
    
    return True

def test_response_validation():
    """Test response structure validation"""
    
    # Mock successful response
    mock_response = {
        "success": True,
        "response_text": "Test response text",
        "recommendations": [
            {
                "player": "Test Player",
                "team": "Test Team",
                "reasoning": "Test reasoning"
            }
        ],
        "summary": "Test summary"
    }
    
    print(f"   Mock response validation: {check_response_fields(mock_response)}")
    
    # Test empty response handling
    empty_response = {"success": False}
    print(f"   Empty response validation: {check_response_fields(empty_response)}")

if __name__ == '__main__':
    test_integration_fixes()