#!/usr/bin/env python3
"""
Rent Manager GUI Launcher
Run this script to start the Flet GUI application.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Check dependencies
try:
    import flet
    print("✓ Flet is installed")
except ImportError:
    print("✗ Flet is not installed. Install it with: pip install flet")
    sys.exit(1)

try:
    import sqlite3
    print("✓ SQLite3 is available")
except ImportError:
    print("✗ SQLite3 is not available")
    sys.exit(1)

# Import and run the app
try:
    from app import main
    print("\n" + "="*60)
    print("Rent Manager GUI")
    print("="*60)
    print("\nStarting application...")
    print("The GUI window will open in a new window.")
    print("\nDocumentation: See GUI_README.md for detailed information.")
    print("="*60 + "\n")
    
    import flet as ft
    ft.app(target=main)
except Exception as e:
    print(f"✗ Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
