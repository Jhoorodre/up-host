"""
Build script for Manga Uploader Pro
Creates standalone executable using PyInstaller
"""

import PyInstaller.__main__
import shutil
from pathlib import Path
import sys

def build():
    # Clean previous builds
    for folder in ['build', 'dist']:
        if Path(folder).exists():
            shutil.rmtree(folder)
    
    # PyInstaller arguments
    args = [
        'src/main.py',
        '--name=MangaUploaderPro',
        '--onefile',
        '--windowed',
        '--icon=assets/icon.ico',
        '--add-data=src/ui/qml;ui/qml',
        '--hidden-import=PySide6.QtQml',
        '--hidden-import=qasync',
        '--hidden-import=httpx',
        '--hidden-import=loguru',
        '--collect-all=PySide6',
    ]
    
    # Platform specific
    if sys.platform == 'win32':
        args.extend([
            '--version-file=version.txt',
            '--uac-admin',
        ])
    
    print("Building Manga Uploader Pro...")
    PyInstaller.__main__.run(args)
    
    print("Build complete! Check dist/ folder")

if __name__ == "__main__":
    build()