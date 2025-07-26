#!/usr/bin/env python3

import requests
import json

def test_backend():
    """Test if Flask backend is working"""
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            print("✅ Flask backend is working!")
            print(f"Health check: {response.json()}")
            
            # Test a simple query
            query_response = requests.post('http://localhost:5001/api/query', 
                                         json={"query": "Tell me about Haaland"})
            if query_response.status_code == 200:
                result = query_response.json()
                print("✅ Query endpoint working!")
                # Handle both response formats
                if 'data' in result and 'response_text' in result['data']:
                    preview = result['data']['response_text'][:200]
                elif 'response_text' in result:
                    preview = result['response_text'][:200]
                else:
                    preview = str(result)[:200]
                print(f"Response preview: {preview}...")
                return True
        else:
            print(f"❌ Backend not responding: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
    return False

if __name__ == "__main__":
    print("🧪 Testing Soccer Scout AI Backend Connection")
    print("=" * 50)
    
    if test_backend():
        print("\n✅ Backend is fully operational!")
        print("You can now:")
        print("- Visit http://localhost:3000 for the Next.js UI")
        print("- Visit http://localhost:5001 for direct API access")
    else:
        print("\n❌ Backend connection failed")
        print("Try restarting the Flask server")