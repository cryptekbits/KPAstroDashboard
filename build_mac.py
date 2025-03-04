#!/usr/bin/env python3
"""
Build script for KP Astrology Dashboard - macOS version

This script packages the application into a standalone macOS app bundle using py2app.

Usage examples:
  # Build the app bundle
  python build_mac.py py2app
  
  # Clean build directories before building
  python build_mac.py clean py2app
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from setuptools import setup

# Import version information
from version import VERSION

APP_NAME = f"KPAstrologyDashboard-v{VERSION}-mac"
APP = ['main.py']
DATA_FILES = [
    'config.json',
    ('resources', ['resources/favicon.ico']),
    ('astro_engine/data', os.listdir('astro_engine/data')),
    ('data_generators', ['data_generators/locations.json']),
]

# Add flatlib if it exists in the root directory
if os.path.exists('flatlib') and os.path.isdir('flatlib'):
    # Recursively add all files from flatlib directory
    for root, dirs, files in os.walk('flatlib'):
        if files:
            rel_dir = os.path.relpath(root, '.')
            file_paths = [os.path.join(root, file) for file in files]
            DATA_FILES.append((rel_dir, file_paths))
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
        DATA_FILES.append((rel_dir, json_files))
        print(f"Added JSON files from {rel_dir}")
                
    # Include all data directories
    if "data" in dirs:
        data_dir = os.path.join(root, "data")
        if data_dir != "astro_engine/data":  # Skip already added directories
            rel_dir = os.path.relpath(data_dir, ".")
            data_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]
            DATA_FILES.append((rel_dir, data_files))
            print(f"Added data directory: {rel_dir}")

# Define py2app options
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.kpastrology.dashboard',
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHumanReadableCopyright': 'Copyright © 2023',
    },
    'iconfile': 'resources/favicon.ico',  # Will be converted to icns if PIL is installed
    'packages': [
        'pandas', 
        'numpy', 
        'PyQt5', 
        'requests', 
        'packaging', 
        'geopy', 
        'polars', 
        'flatlib', 
        'tabulate', 
        'psutil', 
        'ephem', 
        'dateutil'
    ],
    'excludes': ['tkinter', 'matplotlib', 'scipy'],
    'includes': [
        'flatlib',
        'flatlib.const',
        'flatlib.chart',
        'flatlib.geopos',
        'flatlib.datetime',
        'flatlib.object',
        'flatlib.aspects',
    ],
}

if __name__ == '__main__':
    # Add clean option for setup.py
    if 'clean' in sys.argv:
        sys.argv.remove('clean')
        
        print("Cleaning build directories...")
        for dir_to_clean in ['build', 'dist']:
            if os.path.exists(dir_to_clean):
                shutil.rmtree(dir_to_clean, ignore_errors=True)
                print(f"Removed {dir_to_clean} directory")
        
        # Clean the egg info directory
        egg_info = f"{APP_NAME}.egg-info"
        if os.path.exists(egg_info):
            shutil.rmtree(egg_info, ignore_errors=True)
            print(f"Removed {egg_info} directory")
    
    setup(
        name=APP_NAME,
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    
    print(f"Build completed successfully. Output in dist/{APP_NAME}.app")
    
    # Move the app to the release_artifacts directory if it exists
    release_artifacts_dir = "release_artifacts"
    if not os.path.exists(release_artifacts_dir):
        os.makedirs(release_artifacts_dir)
    
    app_bundle_path = f"dist/{APP_NAME}.app"
    if os.path.exists(app_bundle_path):
        dest_path = os.path.join(release_artifacts_dir, f"{APP_NAME}.app")
        # Remove existing app bundle if it exists
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        shutil.copytree(app_bundle_path, dest_path)
        print(f"Copied app bundle to {dest_path}") 