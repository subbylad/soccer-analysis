#!/usr/bin/env python3
"""
Simple wrapper to ensure gunicorn can find the app
"""
from simple_scout_api import app

if __name__ == "__main__":
    app.run()