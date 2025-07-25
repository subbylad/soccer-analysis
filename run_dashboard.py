#!/usr/bin/env python3
"""
Dashboard Launcher Script

Simple script to launch the Streamlit web dashboard with proper configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit dashboard."""
    print("🚀 Starting Soccer Analysis Web Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Launch Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "dashboards/web_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.serverAddress", "localhost"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped successfully!")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Streamlit is installed: pip3 install streamlit plotly")
        print("2. Ensure data files exist in data/clean/ directory")
        print("3. Check that all dependencies are installed")

if __name__ == "__main__":
    main()