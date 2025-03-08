#!/usr/bin/env python3
"""
Release Creation Tool for KP Dashboard

This script helps create a new release by:
1. Updating the version.py file with new version information
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


def git_commit_and_push(version):
    """Commit changes and push to GitHub"""
    root_dir = Path(__file__).parent.parent
    tag_name = f"v{version}"
    
    try:
        # Check if there are any changes to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        has_changes = bool(status_result.stdout.strip())
        
        if has_changes:
            # Stage the changes
            subprocess.run(["git", "add", "version.py", "README.md"], cwd=root_dir, check=True)
            
            # Commit the changes
            subprocess.run(["git", "commit", "-m", f"Release v{version}"], cwd=root_dir, check=True)
            print(f"Committed changes for version {version}")
        else:
            print("No changes to commit. Proceeding with tag creation.")
        
        # Check if the tag already exists
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


def wait_for_workflow_completion(version, timeout=1800):
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
        return True
    
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
                                proceed = input("Do you want to continue with the release process anyway? (y/n): ")
                                if proceed.lower() == 'y':
                                    return True
                                else:
                                    print("Aborting release process.")
                                    sys.exit(1)
                    
                    print("Continuing to wait...")
                    time.sleep(30)
    
    except Exception as e:
        print(f"Error checking workflow status: {e}")
    
    # Wait for the workflow to complete
    print(f"Timeout reached after {timeout} seconds. Proceeding anyway.")
    return True  # Return True to continue with release process even if timeout


def update_github_release(version):
    """Update a GitHub release with release notes"""
    
    try:
        repo_info = get_repo_info()
        if not repo_info:
            return False
        
        # Get GitHub token
        gh_token = os.environ.get("GITHUB_TOKEN")
        if not gh_token:
            print("GitHub token not found. Set the GITHUB_TOKEN environment variable.")
            return False
        
        print(f"Updating GitHub release with release notes...")
        
        # Check if release already exists
        release_tag = f"v{version}"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get release by tag
        release_url = f"https://api.github.com/repos/{repo_info}/releases/tags/{release_tag}"
        response = requests.get(release_url, headers=headers)
        
        release_id = None
        if response.status_code == 200:
            existing_release = response.json()
            release_id = existing_release["id"]
            print(f"Release {release_tag} already exists. Updating it...")
            
            # Update release with new release notes
            update_data = {
                "body": get_release_notes()
            }
            
            update_url = f"https://api.github.com/repos/{repo_info}/releases/{release_id}"
            response = requests.patch(update_url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                print(f"✓ Updated release notes for {release_tag}")
                return True
            else:
                print(f"Failed to update release: {response.status_code} - {response.text}")
                return False
            
        else:
            print(f"Release {release_tag} not found. It may still be in the process of being created by the workflow.")
            print(f"You can manually update the release notes once the workflow has completed.")
            return False
        
    except Exception as e:
        print(f"Error updating GitHub release: {e}")
        return False


def get_repo_info():
    """Get the repository owner and name"""
    root_dir = Path(__file__).parent.parent
    
    # Try to get from version.py first
    version_file_path = root_dir / "version.py"
    repo_owner = None
    repo_name = None
    
    if version_file_path.exists():
        with open(version_file_path, "r") as f:
            for line in f:
                if line.startswith("GITHUB_REPO_OWNER ="):
                    repo_owner = line.split("=")[1].strip().strip('"\'')
                elif line.startswith("GITHUB_REPO_NAME ="):
                    repo_name = line.split("=")[1].strip().strip('"\'')
    
    # If we have both values from version.py, return them
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
    version_file_path = Path(__file__).parent.parent / "version.py"
    
    with open(version_file_path, "r") as f:
        for line in f:
            if line.startswith("VERSION ="):
                current_version = line.split("=")[1].strip().strip('"\'')
                break
    
    if current_version == args.version and not args.force:
        print(f"Version is already set to {args.version}. Use --force to update anyway.")
        proceed = input("Do you want to proceed with the release process without updating the version? (y/n): ")
        if proceed.lower() != 'y':
            print("Aborting release process.")
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
            proceed = input("Do you want to continue with the release process anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Aborting release process.")
                return
        
        if not args.no_wait:
            # Wait for GitHub Actions workflow to complete
            print("\nStep 2: Waiting for GitHub Actions workflow to complete...")
            wait_for_workflow_completion(args.version, args.timeout)
        
        # Update GitHub release with release notes
        print("\nStep 3: Updating GitHub release with release notes...")
        release_success = update_github_release(args.version)
        
        if release_success:
            print(f"\n✅ Release v{args.version} process completed successfully!")
            try:
                repo_info = get_repo_info()
                print(f"You can view the release at: https://github.com/{repo_info}/releases/tag/v{args.version}")
            except:
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