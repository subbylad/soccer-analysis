#!/usr/bin/env python3
"""
Debug script to check Railway PORT environment variable
"""

import os
import sys

def main():
    print("🔍 Railway PORT Environment Debug")
    print("=" * 40)
    
    # Check PORT environment variable
    port = os.environ.get('PORT')
    print(f"PORT environment variable: {port}")
    print(f"Type: {type(port)}")
    
    if port:
        try:
            port_int = int(port)
            print(f"✅ PORT is valid integer: {port_int}")
        except ValueError:
            print(f"❌ PORT cannot be converted to integer: '{port}'")
    else:
        print("❌ PORT environment variable not set")
        print("Using default port 8000")
    
    # Check all Railway environment variables
    print("\n🚂 Railway Environment Variables:")
    railway_vars = {k: v for k, v in os.environ.items() if 'RAILWAY' in k}
    for key, value in railway_vars.items():
        print(f"  {key}: {value}")
    
    # Check other common port-related variables
    print("\n🌐 Network-related Environment Variables:")
    network_vars = ['HOST', 'HOSTNAME', 'SERVER_NAME']
    for var in network_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
    
    print("\n" + "=" * 40)
    
    # Final bind address calculation
    port = os.environ.get('PORT', '8000')
    bind_address = f"0.0.0.0:{port}"
    print(f"🚀 Final bind address: {bind_address}")

if __name__ == "__main__":
    main()