#!/usr/bin/env python3
"""
Build script for KP Astrology Dashboard - Windows version

This script packages the application into a standalone Windows executable using py2exe.

Usage examples:
  # Build the executable
  python build_win.py
  
  # Clean build directories before building
  python build_win.py --clean
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from distutils.core import setup
import py2exe

# Import version information
from version import VERSION

APP_NAME = f"KPAstrologyDashboard-v{VERSION}-win"

def collect_data_files():
    """Collect all data files needed for the build"""
    data_files = [
        ("", ["config.json"]),
        ("resources", [os.path.join("resources", f) for f in os.listdir("resources")]),
        ("astro_engine/data", [os.path.join("astro_engine/data", f) for f in os.listdir("astro_engine/data")]),
        ("data_generators", ["data_generators/locations.json"]),
    ]
    
    # Add flatlib if it exists in the root directory
    if os.path.exists('flatlib') and os.path.isdir('flatlib'):
        # Recursively add all files from flatlib directory
        for root, dirs, files in os.walk('flatlib'):
            if files:
                rel_dir = os.path.relpath(root, '.')
                file_paths = [os.path.join(root, file) for file in files]
                data_files.append((rel_dir, file_paths))
        print("Added local flatlib directory to the build")
    
    # Look for additional data files that might be needed
    print("Scanning for additional data files...")
    for root, dirs, files in os.walk("."):
        if ".git" in root or "venv" in root or "__pycache__" in root or "build" in root or "dist" in root:
            continue
            
        # Include all JSON files that might contain configuration or data
        json_files = [os.path.join(root, file) for file in files if file.endswith(".json") and 
                      not any(p in file for p in ["package", "tsconfig"]) and
                      not (root == "." and file == "config.json") and  # Skip already added files
                      not (root == "data_generators" and file == "locations.json")]
        
        if json_files:
            rel_dir = os.path.relpath(root, ".")
            data_files.append((rel_dir, json_files))
            print(f"Added JSON files from {rel_dir}")
                    
        # Include all data directories
        if "data" in dirs:
            data_dir = os.path.join(root, "data")
            if data_dir != "astro_engine/data":  # Skip already added directories
                rel_dir = os.path.relpath(data_dir, ".")
                data_files.append((rel_dir, [os.path.join(data_dir, f) for f in os.listdir(data_dir)]))
                print(f"Added data directory: {rel_dir}")
    
    return data_files

def main():
    """Main entry point"""
    # Check for --clean flag directly in sys.argv to handle argument parsing issues
    should_clean = False
    if "--clean" in sys.argv:
        should_clean = True
        sys.argv.remove("--clean")
    
    # Clean build directories if requested
    if should_clean:
        print("Cleaning build directories...")
        for dir_to_clean in ['build', 'dist']:
            if os.path.exists(dir_to_clean):
                shutil.rmtree(dir_to_clean, ignore_errors=True)
                print(f"Removed {dir_to_clean} directory")
    
    # Prepare arguments for setup
    data_files = collect_data_files()
    
    # Add py2exe to sys.argv to trigger the build
    if 'py2exe' not in sys.argv:
        sys.argv.append('py2exe')
    
    # Configure py2exe options
    py2exe_options = {
        'bundle_files': 1,
        'compressed': True,
        'optimize': 2,
        'includes': [
            'pandas', 
            'numpy', 
            'PyQt5', 
            'requests', 
            'packaging', 
            'geopy', 
            'polars', 
            'flatlib', 
            'flatlib.const',
            'flatlib.chart',
            'flatlib.geopos',
            'flatlib.datetime',
            'flatlib.object',
            'flatlib.aspects',
            'tabulate', 
            'psutil', 
            'ephem', 
            'dateutil'
        ],
        'excludes': ['tkinter', 'matplotlib', 'scipy'],
        'dll_excludes': ['w9xpopen.exe', 'MSVCP90.dll'],
        'dist_dir': 'dist',
    }
    
    # Run setup
    setup(
        name=APP_NAME,
        version=VERSION,
        description="KP Astrology Dashboard",
        author="KP Astrology",
        windows=[{
            'script': 'main.py',
            'icon_resources': [(1, 'resources/favicon.ico')],
            'dest_base': APP_NAME
        }],
        options={'py2exe': py2exe_options},
        data_files=data_files,
    )
    
    print(f"Build completed successfully. Output in dist/{APP_NAME}.exe")
    
    # Move the executable to the release_artifacts directory if it exists
    release_artifacts_dir = "release_artifacts"
    if not os.path.exists(release_artifacts_dir):
        os.makedirs(release_artifacts_dir)
    
    executable_path = f"dist/{APP_NAME}.exe"
    if os.path.exists(executable_path):
        dest_path = os.path.join(release_artifacts_dir, f"{APP_NAME}.exe")
        shutil.copy2(executable_path, dest_path)
        print(f"Copied executable to {dest_path}")

if __name__ == "__main__":
    main() 