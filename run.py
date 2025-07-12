#!/usr/bin/env python
"""
Entry point for Manga Uploader Pro
Run this file to start the application
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and run
from main import main

if __name__ == "__main__":
    main()
