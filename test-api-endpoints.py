#!/usr/bin/env python3
"""
Simple test script to validate API endpoints locally
"""

import requests
import json
import sys

def test_endpoint(url, method='GET', data=None):
    """Test an API endpoint"""
    try:
        print(f"🧪 Testing {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"   ✅ Valid JSON response")
                if 'status' in json_data:
                    print(f"   Status: {json_data['status']}")
                return True
            except:
                print(f"   ✅ Response received (not JSON)")
                return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
    
    print(f"🚀 Testing API endpoints at: {base_url}")
    print("=" * 50)
    
    tests = [
        # Basic endpoints
        (f"{base_url}/", "GET"),
        (f"{base_url}/health", "GET"),
        (f"{base_url}/api/health", "GET"),
        
        # API endpoints
        (f"{base_url}/api/query", "POST", {"query": "Tell me about Haaland"}),
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if len(test) == 3:
            url, method, data = test
        else:
            url, method = test
            data = None
            
        if test_endpoint(url, method, data):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())