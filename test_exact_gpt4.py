#!/usr/bin/env python3
"""
Test the exact GPT-4 code execution environment
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from api.query_processor import GPT4CodeExecutor
from analysis.clean_player_analyzer import CleanPlayerAnalyzer

def test_exact_execution():
    """Test the exact GPT-4 execution environment."""
    
    print("🧪 Testing Exact GPT-4 Code Execution")
    print("=" * 40)
    
    # Initialize analyzer
    try:
        analyzer = CleanPlayerAnalyzer(data_dir="data/clean")
        print("✅ Analyzer initialized")
    except Exception as e:
        print(f"❌ Analyzer failed: {e}")
        return False
    
    # Initialize the executor
    try:
        executor = GPT4CodeExecutor(analyzer)
        print("✅ Executor initialized")
    except Exception as e:
        print(f"❌ Executor failed: {e}")
        return False
    
    # Test the exact code that GPT-4 generated
    test_codes = [
        'result = analyzer.search_players("Messi")\nsummary = f"Found {len(result)} players named Messi"',
        'all_players = analyzer.search_players("")\nresult = len(all_players)',
        'result = "Hello World"',  # Simple test
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n{i}. Testing code:")
        print(f"   {code}")
        
        result = executor.execute_code(code)
        
        if result['success']:
            print(f"   ✅ Success!")
            print(f"   📊 Result: {result['result']}")
            if 'summary' in result:
                print(f"   📝 Summary: {result['summary']}")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    return True

if __name__ == "__main__":
    success = test_exact_execution()
    exit(0 if success else 1)