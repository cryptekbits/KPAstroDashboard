#!/usr/bin/env python3
"""
Release Creation Tool for KP Dashboard

This script helps create a new release by:
1. Updating the version.py file with new version information
2. Updating the README.md with the new version tag
3. Creating a tag and pushing it to GitHub
4. Triggering GitHub Actions to build the application
5. Creating a GitHub release with release notes and artifacts
"""

import os
import sys
import shutil
import zipfile
import argparse
import subprocess
import re
import time
import requests
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


def update_readme(version):
    """Update the README.md file with the new version tag"""
    readme_path = Path(__file__).parent.parent / "README.md"
    
    with open(readme_path, "r") as f:
        content = f.read()
    
    # Update the version badge in the README
    updated_content = re.sub(
        r'!\[version\]\(https://img\.shields\.io/badge/version-[^-]+-[^)]+\)',
        f'![version](https://img.shields.io/badge/version-{version}-green)',
        content
    )
    
    with open(readme_path, "w") as f:
        f.write(updated_content)
    
    print(f"Updated README.md with version {version}")


def create_source_code_zip(version):
    """Create a zip file of the source code for release"""
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent
    
    # Create the zip file
    zip_file_name = f"SourceCode-v{version}.zip"
    zip_file_path = root_dir / zip_file_name
    
    # Define directories and files to exclude
    exclude_dirs = [".git", "venv", "__pycache__", "build", "dist", "temp_release", "logs"]
    exclude_files = [".DS_Store"]
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, arcname)
    
    print(f"Created source code zip file: {zip_file_name}")
    return zip_file_path


def git_commit_and_push(version):
    """Commit changes and push to GitHub"""
    root_dir = Path(__file__).parent.parent
    
    try:
        # Stage the changes
        subprocess.run(["git", "add", "version.py", "README.md"], cwd=root_dir, check=True)
        
        # Commit the changes
        subprocess.run(["git", "commit", "-m", f"Release v{version}"], cwd=root_dir, check=True)
        
        # Create a tag
        tag_name = f"v{version}"
        subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], cwd=root_dir, check=True)
        
        # Push the changes and tag
        subprocess.run(["git", "push", "origin", "master"], cwd=root_dir, check=True)
        subprocess.run(["git", "push", "origin", tag_name], cwd=root_dir, check=True)
        
        print(f"Committed and pushed changes with tag {tag_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        return False


def get_release_notes():
    """Generate release notes by comparing with the previous tag"""
    root_dir = Path(__file__).parent.parent
    
    try:
        # Get the previous tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
            cwd=root_dir, 
            capture_output=True, 
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            # If there's no previous tag, get all commits
            prev_tag = ""
            range_spec = "HEAD"
        else:
            prev_tag = result.stdout.strip()
            range_spec = f"{prev_tag}..HEAD"
        
        # Get commits since the previous tag
        result = subprocess.run(
            ["git", "log", range_spec, "--pretty=format:- %s"],
            cwd=root_dir, 
            capture_output=True, 
            text=True,
            check=True
        )
        
        commits = result.stdout.strip()
        
        if not commits:
            return "No changes since the last release."
        
        if prev_tag:
            header = f"## Changes since {prev_tag}\n\n"
        else:
            header = "## Initial Release\n\n"
        
        return header + commits
    except subprocess.CalledProcessError as e:
        print(f"Error generating release notes: {e}")
        return "Release notes generation failed. Please check the commit history."


def wait_for_workflow_completion(version, timeout=1800):
    """Wait for the GitHub Actions workflow to complete"""
    # This requires the GitHub CLI to be installed and authenticated
    root_dir = Path(__file__).parent.parent
    
    # Get the repository information from version.py
    version_file_path = root_dir / "version.py"
    repo_owner = None
    repo_name = None
    
    with open(version_file_path, "r") as f:
        for line in f:
            if line.startswith("GITHUB_REPO_OWNER"):
                repo_owner = line.split("=")[1].strip().strip('"\'')
            elif line.startswith("GITHUB_REPO_NAME"):
                repo_name = line.split("=")[1].strip().strip('"\'')
    
    if not repo_owner or not repo_name:
        print("Could not determine repository information from version.py")
        return False
    
    print(f"Waiting for GitHub Actions workflow to complete for tag v{version}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check workflow status using GitHub CLI
            result = subprocess.run(
                ["gh", "run", "list", "--repo", f"{repo_owner}/{repo_name}", "--branch", f"v{version}", "--json", "status"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            if "completed" in result.stdout:
                print("Workflow completed successfully!")
                return True
            
            print("Workflow still running. Waiting 30 seconds...")
            time.sleep(30)
        except subprocess.CalledProcessError as e:
            print(f"Error checking workflow status: {e}")
            print("Continuing to wait...")
            time.sleep(30)
    
    print(f"Timeout reached after {timeout} seconds. Proceeding anyway.")
    return False


def create_github_release(version, source_code_zip):
    """Create a GitHub release with the source code zip and release notes"""
    root_dir = Path(__file__).parent.parent
    
    # Generate release notes
    release_notes = get_release_notes()
    
    try:
        # Create a GitHub release using GitHub CLI
        subprocess.run(
            [
                "gh", "release", "create", f"v{version}",
                "--title", f"Release v{version}",
                "--notes", release_notes,
                source_code_zip
            ],
            cwd=root_dir,
            check=True
        )
        
        print(f"Created GitHub release v{version}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating GitHub release: {e}")
        print("Please create the release manually with the following steps:")
        print(f"1. Go to the GitHub repository releases page")
        print(f"2. Create a new release with tag 'v{version}'")
        print(f"3. Add the release notes and upload the source code zip file")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create a new release of KP Dashboard")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("version_name", help="Version name (e.g., 'Bug Fix Release')")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to GitHub")
    parser.add_argument("--no-wait", action="store_true", help="Skip waiting for GitHub Actions")
    
    args = parser.parse_args()
    
    # Update version file
    update_version_file(args.version, args.version_name)
    
    # Update README.md
    update_readme(args.version)
    
    # Create source code zip
    source_code_zip = create_source_code_zip(args.version)
    
    if not args.no_push:
        # Commit and push changes
        if not git_commit_and_push(args.version):
            print("Failed to push changes to GitHub. Aborting.")
            return
        
        if not args.no_wait:
            # Wait for GitHub Actions workflow to complete
            wait_for_workflow_completion(args.version)
        
        # Create GitHub release
        create_github_release(args.version, source_code_zip)
    else:
        print("\nChanges have been made locally but not pushed to GitHub.")
        print("To complete the release process manually:")
        print(f"1. Commit the changes: git commit -m 'Release v{args.version}'")
        print(f"2. Create a tag: git tag -a v{args.version} -m 'Release v{args.version}'")
        print("3. Push the changes: git push origin master")
        print(f"4. Push the tag: git push origin v{args.version}")
        print("5. Create a GitHub release with the source code zip file")


if __name__ == "__main__":
    main() 