#!/usr/bin/env python3
"""
Release Creation Tool for KP Dashboard

This script helps create a new release by:
1. Updating the VERSION_FILE_NAME file with new version information
2. Updating the README.md with the new version tag
3. Creating a tag and pushing it to GitHub
4. Triggering GitHub Actions to build the application
5. Updating the GitHub release with release notes (artifacts are handled by GitHub Actions)
"""

import os
import sys
import argparse
import subprocess
import re
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# Constants
VERSION_FILE_NAME = "version.py"
ABORT_MESSAGE = "Aborting release process."
CONTINUE_PROMPT = "Do you want to continue with the release process anyway? (y/n): "
VERSION_CONTINUE_PROMPT = "Do you want to proceed with the release process without updating the version? (y/n): "


def update_version_file(version, version_name):
    """Update the VERSION_FILE_NAME file with new version information"""
    version_file_path = Path(__file__).parent.parent / VERSION_FILE_NAME
    
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
    
    print(f"Updated {VERSION_FILE_NAME} with version {version} ({version_name})")


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


def git_commit_and_push(version):
    """Commit the updated version files and push to GitHub"""
    root_dir = Path(__file__).parent.parent
    
    try:
        # Check if there are changes to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"], 
            cwd=root_dir, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        has_changes = bool(status_result.stdout.strip())
        
        if has_changes:
            # Stage the changes
            subprocess.run(["git", "add", VERSION_FILE_NAME, "README.md"], cwd=root_dir, check=True)
            
            # Commit the changes
            subprocess.run(["git", "commit", "-m", f"Release v{version}"], cwd=root_dir, check=True)
            print(f"Committed changes for version {version}")
        else:
            print("No changes to commit. Proceeding with tag creation.")
        
        # Check if the tag already exists
        tag_name = f"v{version}"
        tag_exists_result = subprocess.run(
            ["git", "tag", "-l", tag_name],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        if tag_name in tag_exists_result.stdout:
            print(f"Tag {tag_name} already exists. Skipping tag creation.")
        else:
            # Create a tag
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], cwd=root_dir, check=True)
            print(f"Created tag {tag_name}")
        
        # Push both the commit and tag in a single operation
        # This prevents triggering two separate GitHub Actions workflows
        push_cmd = ["git", "push", "origin", "master"]
        if tag_name not in tag_exists_result.stdout:
            push_cmd.append(tag_name)
        
        push_result = subprocess.run(
            push_cmd,
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if push_result.returncode != 0:
            print(f"Warning: Failed to push changes.")
            print(f"Error: {push_result.stderr}")
            
            # If it failed because the tag already exists, we should continue
            if not has_changes and "already exists" in push_result.stderr:
                print(f"Tag {tag_name} already exists on remote. Continuing with release process.")
                return True
            return False
        
        print(f"Pushed changes and tag {tag_name} to origin")
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


def wait_for_workflow_completion(version, timeout=6000):
    """Wait for the GitHub Actions workflow to complete"""
    # This requires the GitHub CLI to be installed and authenticated
    root_dir = Path(__file__).parent.parent
    tag_name = f"v{version}"
    
    try:
        repo_info = get_repo_info()
        print(f"Checking GitHub Actions workflow status for tag {tag_name}...")
    except Exception as e:
        print(f"Error getting repository information: {e}")
        print("Skipping workflow check and proceeding with release.")
        proceed = input(CONTINUE_PROMPT)
        if proceed.lower() == 'y':
            return True
        else:
            print(ABORT_MESSAGE)
            return False
    
    # First check if there are any workflows running for this tag
    try:
        # Try to get workflow runs for the tag
        result = subprocess.run(
            ["gh", "run", "list", "--repo", repo_info, "--json", "status,name,headBranch,databaseId,conclusion"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        runs = json.loads(result.stdout)
        
        # Filter runs related to our tag
        tag_runs = [run for run in runs if run.get("headBranch") == tag_name or (run.get("name") == "build" and "tags" in run.get("headBranch", ""))]
        
        if not tag_runs:
            print(f"No workflow runs found for tag {tag_name}. Waiting for workflow to start...")
            # Wait for the workflow to start
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(30)
                result = subprocess.run(
                    ["gh", "run", "list", "--repo", repo_info, "--json", "status,name,headBranch,databaseId,conclusion"],
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                runs = json.loads(result.stdout)
                tag_runs = [run for run in runs if run.get("headBranch") == tag_name or (run.get("name") == "build" and "tags" in run.get("headBranch", ""))]
                
                if tag_runs:
                    print(f"Workflow for tag {tag_name} has started!")
                    break
            
            if not tag_runs:
                print(f"Timeout reached while waiting for workflow to start after {timeout} seconds.")
                proceed = input(CONTINUE_PROMPT)
                if proceed.lower() == 'y':
                    return True
                else:
                    print(ABORT_MESSAGE)
                    return False
        else:
            # Check if any of the runs are already completed successfully
            completed_runs = [run for run in tag_runs if run.get("status") == "completed" and run.get("conclusion") == "success"]
            if completed_runs:
                print(f"Workflow for tag {tag_name} already completed successfully!")
                return True
                
            in_progress_runs = [run for run in tag_runs if run.get("status") in ["in_progress", "queued", "waiting"]]
            if in_progress_runs:
                print(f"Workflow for tag {tag_name} is in progress. Monitoring its status...")
                run_id = in_progress_runs[0].get("databaseId")
                print(f"Run ID: {run_id}")
                
                # Monitor the workflow status until it completes or times out
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Get the current status of the workflow
                    status_result = subprocess.run(
                        ["gh", "run", "view", str(run_id), "--repo", repo_info, "--json", "status,conclusion"],
                        cwd=root_dir,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if status_result.returncode == 0:
                        run_info = json.loads(status_result.stdout)
                        status = run_info.get("status")
                        conclusion = run_info.get("conclusion")
                        
                        print(f"Current status: {status}, Conclusion: {conclusion}")
                        
                        if status == "completed":
                            if conclusion == "success":
                                print(f"Workflow completed successfully!")
                                return True
                            else:
                                print(f"Workflow completed with conclusion: {conclusion}")
                                proceed = input(CONTINUE_PROMPT)
                                if proceed.lower() == 'y':
                                    return True
                                else:
                                    print(ABORT_MESSAGE)
                                    return False
                    
                    print("Continuing to wait...")
                    time.sleep(30)
                
                print(f"Timeout reached after {timeout} seconds.")
                proceed = input(CONTINUE_PROMPT)
                if proceed.lower() == 'y':
                    return True
                else:
                    print(ABORT_MESSAGE)
                    return False
    
    except Exception as e:
        print(f"Error checking workflow status: {e}")
        proceed = input(CONTINUE_PROMPT)
        if proceed.lower() == 'y':
            return True
        else:
            print(ABORT_MESSAGE)
            return False


def update_github_release(version):
    """Update a GitHub release with release notes"""
    
    try:
        repo_info = get_repo_info()
        if not repo_info:
            print("Failed to get repository information")
            return False
        
        print(f"Repository info: {repo_info}")
        
        # Get GitHub token
        gh_token = os.environ.get("GITHUB_TOKEN")
        if not gh_token:
            print("GitHub token not found. Set the GITHUB_TOKEN environment variable.")
            print("Run: export GITHUB_TOKEN=your_token_here")
            return False
        
        # Check if token is valid (just checking length as a basic validation)
        if len(gh_token) < 10:
            print(f"GitHub token appears to be invalid (length: {len(gh_token)})")
            print("Make sure you've set a valid token with: export GITHUB_TOKEN=your_token_here")
            return False
            
        print(f"GitHub token found (length: {len(gh_token)})")
        print(f"Updating GitHub release with release notes...")
        
        # Check if release already exists
        release_tag = f"v{version}"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try multiple times to get the release, as it might take a moment to appear
        max_attempts = 5
        attempt = 0
        release_id = None
        
        while attempt < max_attempts:
            # Get release by tag
            release_url = f"https://api.github.com/repos/{repo_info}/releases/tags/{release_tag}"
            print(f"Checking for release at: {release_url}")
            
            response = requests.get(release_url, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                existing_release = response.json()
                release_id = existing_release["id"]
                print(f"Release {release_tag} found. Release ID: {release_id}")
                break
            else:
                print(f"Response body: {response.text}")
                attempt += 1
                if attempt < max_attempts:
                    print(f"Release {release_tag} not found (attempt {attempt}/{max_attempts}). Waiting for it to be created...")
                    time.sleep(10)  # Wait 10 seconds before trying again
                else:
                    print(f"Release {release_tag} not found after {max_attempts} attempts.")
                    print(f"You can manually update the release notes once the workflow has completed.")
                    return False
        
        if release_id:
            # Get release notes
            release_notes = get_release_notes()
            print(f"Generated release notes ({len(release_notes)} characters)")
            print("First 100 characters of release notes:")
            print(release_notes[:100] + "..." if len(release_notes) > 100 else release_notes)
            
            # Update release with new release notes
            update_data = {
                "body": release_notes
            }
            
            update_url = f"https://api.github.com/repos/{repo_info}/releases/{release_id}"
            print(f"Updating release at: {update_url}")
            
            response = requests.patch(update_url, headers=headers, json=update_data)
            print(f"Update response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✓ Updated release notes for {release_tag}")
                return True
            else:
                print(f"Failed to update release: {response.status_code}")
                print(f"Response body: {response.text}")
                return False
        
        return False
            
    except Exception as e:
        print(f"Error updating GitHub release: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_repo_info():
    """Get the repository owner and name"""
    root_dir = Path(__file__).parent.parent
    
    # Try to get from VERSION_FILE_NAME first
    version_file_path = root_dir / VERSION_FILE_NAME
    repo_owner = None
    repo_name = None
    
    if version_file_path.exists():
        with open(version_file_path, "r") as f:
            for line in f:
                if line.startswith("GITHUB_REPO_OWNER ="):
                    repo_owner = line.split("=")[1].strip().strip('"\'')
                elif line.startswith("GITHUB_REPO_NAME ="):
                    repo_name = line.split("=")[1].strip().strip('"\'')
    
    # If we have both values from VERSION_FILE_NAME, return them
    if repo_owner and repo_name:
        return f"{repo_owner}/{repo_name}"
    
    # Otherwise, try to get from git remote
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        git_url = result.stdout.strip()
        
        # Parse GitHub URL to extract owner and repo
        if "github.com" in git_url:
            # Handle SSH URL format (git@github.com:owner/repo.git)
            if git_url.startswith("git@github.com:"):
                repo_info = git_url.split("git@github.com:")[1].split(".git")[0]
            # Handle HTTPS URL format (https://github.com/owner/repo.git)
            elif git_url.startswith(("https://github.com/", "http://github.com/")):
                repo_info = git_url.split("github.com/")[1].split(".git")[0]
            else:
                raise ValueError(f"Unrecognized GitHub URL format: {git_url}")
            
            return repo_info
    except Exception as e:
        print(f"Error getting repository information from git: {e}")
    
    raise ValueError("Could not determine repository owner and name")


def chmod_plus_x(file_path):
    """Make a file executable"""
    try:
        os.chmod(file_path, 0o755)
        return True
    except Exception as e:
        print(f"Error making file executable: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create a new release of KP Dashboard")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("version_name", help="Version name (e.g., 'Bug Fix Release')")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to GitHub")
    parser.add_argument("--no-wait", action="store_true", help="Skip waiting for GitHub Actions")
    parser.add_argument("--force", action="store_true", help="Force update even if version hasn't changed")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds for waiting for workflow completion (default: 1800)")
    
    args = parser.parse_args()
    
    print(f"Starting release process for KP Astrology Dashboard v{args.version} ({args.version_name})")
    
    # Check if the version is already set to the requested version
    current_version = None
    version_file_path = Path(__file__).parent.parent / VERSION_FILE_NAME
    
    with open(version_file_path, "r") as f:
        for line in f:
            if line.startswith("VERSION ="):
                current_version = line.split("=")[1].strip().strip('"\'')
                break
    
    if current_version == args.version and not args.force:
        print(f"Version is already set to {args.version}. Use --force to update anyway.")
        proceed = input(VERSION_CONTINUE_PROMPT)
        if proceed.lower() != 'y':
            print(ABORT_MESSAGE)
            return
        print("Proceeding with release process without updating version files...")
    else:
        # Update version file
        update_version_file(args.version, args.version_name)
        
        # Update README.md
        update_readme(args.version)
    
    if not args.no_push:
        # Commit and push changes
        print("\nStep 1: Committing and pushing changes to GitHub...")
        push_success = git_commit_and_push(args.version)
        if not push_success:
            print("Warning: There were issues with git operations.")
            proceed = input(CONTINUE_PROMPT)
            if proceed.lower() != 'y':
                print(ABORT_MESSAGE)
                return
        
        if not args.no_wait:
            # Wait for GitHub Actions workflow to complete
            print("\nStep 2: Waiting for GitHub Actions workflow to complete...")
            workflow_success = wait_for_workflow_completion(args.version, args.timeout)
            if not workflow_success:
                print("Aborting release process due to workflow issues.")
                return
        
        # Update GitHub release with release notes
        print("\nStep 3: Updating GitHub release with release notes...")
        release_success = update_github_release(args.version)
        
        if release_success:
            print(f"\n✅ Release v{args.version} process completed successfully!")
            try:
                repo_info = get_repo_info()
                print(f"You can view the release at: https://github.com/{repo_info}/releases/tag/v{args.version}")
            except Exception:
                print("Please check your GitHub repository for the release.")
        else:
            print(f"\n⚠️ Release v{args.version} process completed with warnings.")
            print("Please check the output above for any issues that need to be addressed manually.")
    else:
        print("\nChanges have been made locally but not pushed to GitHub.")
        print("To complete the release process manually:")
        print(f"1. Commit the changes: git commit -m 'Release v{args.version}'")
        print(f"2. Create a tag: git tag -a v{args.version} -m 'Release v{args.version}'")
        print("3. Push the changes: git push origin master")
        print(f"4. Push the tag: git push origin v{args.version}")
        print("5. Wait for GitHub Actions to build the artifacts and create the release")
        print("6. Optionally update the release notes")


if __name__ == "__main__":
    main() 