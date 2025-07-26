#!/usr/bin/env python3
"""
Debug numpy import issue
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np

def test_exec_environment():
    print("🔍 Testing exec environment with numpy")
    
    # Create the same execution environment as our code
    exec_globals = {
        'pd': pd,
        'np': np,
        'pandas': pd,
        'numpy': np,
        'len': len,
        'str': str,
    }
    
    print(f"Available globals: {list(exec_globals.keys())}")
    
    # Test different numpy usage patterns
    test_codes = [
        "result = np.array([1, 2, 3])",
        "result = numpy.array([1, 2, 3])",
        "import numpy as np\nresult = np.array([1, 2, 3])",
        "result = len([1, 2, 3])",
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n{i}. Testing: {code}")
        exec_locals = {}
        
        try:
            exec(code, exec_globals, exec_locals)
            result = exec_locals.get('result', 'NO RESULT')
            print(f"   ✅ Success: {result}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    test_exec_environment()