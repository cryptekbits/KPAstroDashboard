#!/usr/bin/env python3
"""
Release Creation Tool for KP Dashboard

This script helps create a new release by:
1. Updating the version.py file with new version information
2. Creating a zip file of the application
3. Providing instructions for creating a GitHub release
"""

import os
import sys
import shutil
import zipfile
import argparse
from datetime import datetime
from pathlib import Path


def update_version_file(version, version_name):
    """Update the version.py file with new version information"""
    version_file_path = Path(__file__).parent.parent / "version.py"
    
    with open(version_file_path, "r") as f:
        lines = f.readlines()
    
    with open(version_file_path, "w") as f:
        for line in lines:
            if line.startswith("VERSION ="):
                f.write(f'VERSION = "{version}"\n')
            elif line.startswith("VERSION_NAME ="):
                f.write(f'VERSION_NAME = "{version_name}"\n')
            elif line.startswith("BUILD_DATE ="):
                f.write(f'BUILD_DATE = "{datetime.now().strftime("%Y-%m-%d")}"\n')
            else:
                f.write(line)
    
    print(f"Updated version.py with version {version} ({version_name})")


def create_release_zip(version):
    """Create a zip file of the application for release"""
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent
    
    # Create a temporary directory for the release
    temp_dir = root_dir / "temp_release"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Define directories and files to include
    dirs_to_include = [
        "ui", "astro_engine", "calculations", "data_generators", 
        "exporters", "yogas"
    ]
    
    files_to_include = [
        "main.py", "version.py", "config.json", "requirements.txt", 
        "README.md"
    ]
    
    # Copy directories
    for dir_name in dirs_to_include:
        src_dir = root_dir / dir_name
        dst_dir = temp_dir / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir)
    
    # Copy files
    for file_name in files_to_include:
        src_file = root_dir / file_name
        dst_file = temp_dir / file_name
        if src_file.exists():
            shutil.copy2(src_file, dst_file)
    
    # Create the zip file
    zip_file_name = f"kp_dashboard_v{version}.zip"
    zip_file_path = root_dir / zip_file_name
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    print(f"Created release zip file: {zip_file_name}")
    return zip_file_path


def main():
    parser = argparse.ArgumentParser(description="Create a new release of KP Dashboard")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("version_name", help="Version name (e.g., 'Bug Fix Release')")
    
    args = parser.parse_args()
    
    # Update version file
    update_version_file(args.version, args.version_name)
    
    # Create release zip
    zip_file_path = create_release_zip(args.version)
    
    # Print instructions
    print("\nRelease preparation complete!")
    print("\nTo create a GitHub release:")
    print("1. Commit and push the version changes to GitHub")
    print(f"2. Create a new release on GitHub with tag 'v{args.version}'")
    print(f"3. Upload the zip file: {zip_file_path}")
    print("4. Add release notes describing the changes")


if __name__ == "__main__":
    main() 