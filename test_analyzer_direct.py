#!/usr/bin/env python3
"""
Test CleanPlayerAnalyzer directly to find numpy issue
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np

def test_analyzer_direct():
    """Test CleanPlayerAnalyzer directly."""
    
    print("🔍 Testing CleanPlayerAnalyzer directly")
    print("=" * 40)
    
    try:
        from analysis.clean_player_analyzer import CleanPlayerAnalyzer
        print("✅ Imported CleanPlayerAnalyzer")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    try:
        analyzer = CleanPlayerAnalyzer(data_dir="data/clean")
        print("✅ Analyzer initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test basic search
    try:
        result = analyzer.search_players("Messi")
        print(f"✅ Search worked: found {len(result)} results")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test the actual code execution environment with analyzer
    print("\n🧪 Testing exec environment with analyzer")
    
    exec_globals = {
        'analyzer': analyzer,
        'pd': pd,
        'np': np,
        'pandas': pd,
        'numpy': np,
        'len': len,
        'str': str,
    }
    
    test_code = '''
result = analyzer.search_players("Messi")
summary = f"Found {len(result)} players"
'''
    
    exec_locals = {}
    
    try:
        exec(test_code, exec_globals, exec_locals)
        result = exec_locals.get('result')
        summary = exec_locals.get('summary')
        print(f"✅ Exec worked: {summary}")
        print(f"   Result type: {type(result)}")
        print(f"   Result shape: {result.shape if hasattr(result, 'shape') else 'No shape'}")
    except Exception as e:
        print(f"❌ Exec failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_analyzer_direct()
    exit(0 if success else 1)