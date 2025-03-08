#!/usr/bin/env python3
"""
Windows Executable Build Script for KP Astrology Dashboard

This script builds a Windows executable using PyInstaller.
It's designed to be run from GitHub Actions or locally.

Usage:
  python tools/build_windows_exe.py [--onefile] [--debug]
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

# Add parent directory to path so we can import version
sys.path.append(str(Path(__file__).parent.parent))
from version import VERSION

def main():
    """Main entry point for the build script"""
    parser = argparse.ArgumentParser(description="Build Windows executable for KP Astrology Dashboard")
    parser.add_argument("--onefile", action="store_true", help="Create a single executable file")
    parser.add_argument("--debug", action="store_true", help="Build with debug information")
    args = parser.parse_args()
    
    # Set up paths
    root_dir = Path(__file__).parent.parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Clean build directories if they exist
    if dist_dir.exists():
        print(f"Cleaning {dist_dir}...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print(f"Cleaning {build_dir}...")
        shutil.rmtree(build_dir)
    
    # Create output directories
    dist_dir.mkdir(exist_ok=True)
    
    # Determine PyInstaller options
    pyinstaller_args = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        f"--name=KPAstrologyDashboard-{VERSION}",
        "--add-data=resources;resources",
        "--add-data=flatlib;flatlib",
        "--add-data=yogas;yogas",
        "--add-data=astro_engine/data;astro_engine/data",
        "--add-data=config.json;.",
    ]
    
    # Check if the icon file exists, if not use the favicon.ico
    icon_path = "resources/icons/app_icon.ico"
    fallback_icon_path = "resources/favicon.ico"
    
    if os.path.exists(os.path.join(root_dir, icon_path)):
        pyinstaller_args.append(f"--icon={icon_path}")
    elif os.path.exists(os.path.join(root_dir, fallback_icon_path)):
        print(f"Warning: {icon_path} not found, using {fallback_icon_path} instead")
        pyinstaller_args.append(f"--icon={fallback_icon_path}")
    else:
        print(f"Warning: No icon files found at {icon_path} or {fallback_icon_path}")
    
    pyinstaller_args.append("--hidden-import=PIL._tkinter_finder")
    
    # Add debug flag if requested
    if args.debug:
        pyinstaller_args.append("--debug=all")
    
    # Determine if we're building a single file or a directory
    if args.onefile:
        pyinstaller_args.append("--onefile")
    else:
        pyinstaller_args.append("--onedir")
    
    # Add the main script
    pyinstaller_args.append("main.py")
    
    # Run PyInstaller
    print(f"Building Windows executable with PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_args)}")
    
    try:
        subprocess.run(pyinstaller_args, cwd=root_dir, check=True)
        print(f"Successfully built Windows executable!")
        
        # Create a ZIP archive of the executable
        if not args.onefile:
            # For onedir builds, zip the entire directory
            exe_dir = dist_dir / f"KPAstrologyDashboard-{VERSION}"
            if exe_dir.exists():
                zip_path = dist_dir / f"KPAstrologyDashboard-{VERSION}-Windows.zip"
                print(f"Creating ZIP archive: {zip_path}")
                
                # Create a zip file
                shutil.make_archive(
                    str(zip_path).replace(".zip", ""),
                    "zip",
                    root_dir=dist_dir,
                    base_dir=f"KPAstrologyDashboard-{VERSION}"
                )
                print(f"ZIP archive created: {zip_path}")
        else:
            # For onefile builds, zip just the executable
            exe_path = dist_dir / f"KPAstrologyDashboard-{VERSION}.exe"
            if exe_path.exists():
                zip_path = dist_dir / f"KPAstrologyDashboard-{VERSION}-Windows.zip"
                print(f"Creating ZIP archive: {zip_path}")
                
                # Create a zip file
                shutil.make_archive(
                    str(zip_path).replace(".zip", ""),
                    "zip",
                    root_dir=dist_dir,
                    base_dir=f"KPAstrologyDashboard-{VERSION}.exe"
                )
                print(f"ZIP archive created: {zip_path}")
        
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error building Windows executable: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 