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
                
                # Check if artifacts are available
                run_id = completed_runs[0].get("databaseId")
                artifacts_result = subprocess.run(
                    ["gh", "run", "view", str(run_id), "--repo", repo_info, "--json", "jobs"],
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if artifacts_result.returncode == 0:
                    jobs_data = json.loads(artifacts_result.stdout)
                    if "jobs" in jobs_data and any(job.get("name", "").startswith("create-") for job in jobs_data["jobs"]):
                        print("Build jobs completed. Artifacts should be available.")
                        return True
                    else:
                        print("Workflow completed but build jobs may not have run. Continuing anyway.")
                        return True
                else:
                    print("Could not check for build jobs. Continuing anyway.")
                    return True
                
            in_progress_runs = [run for run in tag_runs if run.get("status") in ["in_progress", "queued", "waiting"]]
            if in_progress_runs:
                print(f"Workflow for tag {tag_name} is in progress. Waiting for completion...")
            else:
                failed_runs = [run for run in tag_runs if run.get("status") == "completed" and run.get("conclusion") != "success"]
                if failed_runs:
                    print(f"Warning: Workflow for tag {tag_name} has failed!")
                    print("Proceeding with release process, but artifacts may not be available.")
                    return True
    except Exception as e:
        print(f"Error checking workflow status: {e}")
        print("Skipping initial check and continuing with wait...")
    
    # Wait for the workflow to complete
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
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
            
            if tag_runs:
                # Check if any of the runs are completed
                completed_runs = [run for run in tag_runs if run.get("status") == "completed"]
                if completed_runs:
                    successful_runs = [run for run in completed_runs if run.get("conclusion") == "success"]
                    if successful_runs:
                        print(f"Workflow for tag {tag_name} completed successfully!")
                        return True
                    else:
                        print(f"Warning: Workflow for tag {tag_name} has failed or been cancelled.")
                        print("Proceeding with release process, but artifacts may not be available.")
                        return True
                else:
                    print(f"Workflow for tag {tag_name} is still in progress. Waiting...")
            else:
                print(f"No workflow runs found for tag {tag_name} yet. Waiting...")
            
            # Wait for 30 seconds before checking again
            time.sleep(30)
        except Exception as e:
            print(f"Error checking workflow status: {e}")
            print("Continuing to wait...")
            time.sleep(30)
    
    print(f"Timeout reached after {timeout} seconds. Proceeding anyway.")
    return True  # Return True to continue with release process even if timeout


def download_workflow_artifacts(version, repo_info, root_dir):
    """Download artifacts from the GitHub Actions workflow"""
    tag_name = f"v{version}"
    artifacts_dir = root_dir / "release_artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    print(f"Downloading artifacts for version {version}...")
    
    try:
        # Get the workflow runs for this tag
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
            print(f"No workflow runs found for tag {tag_name}.")
            return False
        
        # Find the most recent completed run
        completed_runs = [run for run in tag_runs if run.get("status") == "completed" and run.get("conclusion") == "success"]
        if not completed_runs:
            print(f"No completed workflow runs found for tag {tag_name}.")
            return False
        
        # Sort by ID (higher is more recent)
        completed_runs.sort(key=lambda x: x.get("databaseId", 0), reverse=True)
        run_id = completed_runs[0].get("databaseId")
        
        print(f"Found completed workflow run: {run_id}")
        
        # Download artifacts
        artifacts_result = subprocess.run(
            ["gh", "run", "download", str(run_id), "--repo", repo_info, "--dir", str(artifacts_dir)],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if artifacts_result.returncode != 0:
            print(f"Error downloading artifacts: {artifacts_result.stderr}")
            return False
        
        print(f"Downloaded artifacts to {artifacts_dir}")
        
        # Check what we've downloaded
        artifacts = list(artifacts_dir.glob("**/*"))
        if not artifacts:
            print("No artifacts were downloaded.")
            return False
        
        print(f"Downloaded {len(artifacts)} artifacts:")
        for artifact in artifacts:
            print(f"  - {artifact.relative_to(artifacts_dir)}")
        
        # Search for specific file types
        print("\nSearching for specific file types:")
        print("EXE files:")
        for exe_file in artifacts_dir.glob("**/*.exe"):
            print(f"  - {exe_file.relative_to(artifacts_dir)}")
        
        print("ZIP files:")
        for zip_file in artifacts_dir.glob("**/*.zip"):
            print(f"  - {zip_file.relative_to(artifacts_dir)}")
        
        print("BAT files:")
        for bat_file in artifacts_dir.glob("**/*.bat"):
            print(f"  - {bat_file.relative_to(artifacts_dir)}")
        
        print("SH files:")
        for sh_file in artifacts_dir.glob("**/*.sh"):
            print(f"  - {sh_file.relative_to(artifacts_dir)}")
        
        # Prepare the artifacts for release
        release_dir = root_dir / "release"
        release_dir.mkdir(exist_ok=True)
        
        # Source code ZIP
        source_code_zips = list(artifacts_dir.glob("**/source-code/*.zip"))
        if source_code_zips:
            source_zip = source_code_zips[0]
            target_path = release_dir / f"KPAstrologyDashboard-{version}.zip"
            shutil.copy(source_zip, target_path)
            print(f"Prepared source code ZIP: {target_path}")
        
        # Windows installer
        windows_installers = list(artifacts_dir.glob("**/windows-installer/*.bat"))
        if not windows_installers:
            # Try a more flexible search pattern
            windows_installers = list(artifacts_dir.glob("**/*.bat"))
            print(f"Using flexible search pattern for Windows installer, found {len(windows_installers)} files")
        
        if windows_installers:
            win_installer = windows_installers[0]
            target_path = release_dir / "KPAstrologyDashboard-Windows-Installer.bat"
            shutil.copy(win_installer, target_path)
            print(f"Prepared Windows installer: {target_path}")
        else:
            print("WARNING: No Windows installer (.bat) found!")
        
        # macOS installer (sh)
        macos_installers = list(artifacts_dir.glob("**/macos-installer/*.sh"))
        if not macos_installers:
            # Try a more flexible search pattern
            macos_installers = list(artifacts_dir.glob("**/*.sh"))
            print(f"Using flexible search pattern for macOS installer, found {len(macos_installers)} files")
            
        if macos_installers:
            macos_installer = macos_installers[0]
            target_path = release_dir / "KPAstrologyDashboard-macOS-Installer.sh"
            shutil.copy(macos_installer, target_path)
            chmod_plus_x(target_path)
            print(f"Prepared macOS installer: {target_path}")
            
            # Also create a .command file (which is double-clickable on macOS)
            command_path = release_dir / "KPAstrologyDashboard-macOS-Installer.command"
            shutil.copy(macos_installer, command_path)
            chmod_plus_x(command_path)
            print(f"Prepared macOS command: {command_path}")
        else:
            print("WARNING: No macOS installer (.sh) found!")
            
        # Verify all the expected files are present
        expected_files = [
            f"KPAstrologyDashboard-{version}.zip",
            "KPAstrologyDashboard-Windows-Installer.bat",
            "KPAstrologyDashboard-macOS-Installer.sh",
            "KPAstrologyDashboard-macOS-Installer.command"
        ]
        
        print("\nVerifying release artifacts:")
        missing_files = []
        for file_name in expected_files:
            file_path = release_dir / file_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✓ {file_name} ({file_size} bytes)")
                if file_size == 0:
                    print(f"  WARNING: {file_name} is empty!")
            else:
                print(f"✗ {file_name} is missing!")
                missing_files.append(file_name)
        
        if missing_files:
            print(f"\nWARNING: {len(missing_files)} expected files are missing from the release!")
            print("Missing files: " + ", ".join(missing_files))
            print("This might cause the GitHub release to have incomplete artifacts.")
            
        # Windows executable build is disabled; skipping copying Windows artifacts.
        print("Skipping Windows executable and ZIP artifact copy as Windows build has been removed.")
        
        return True
    except Exception as e:
        print(f"Error downloading artifacts: {e}")
        return False


def create_github_release(version):
    """Create a GitHub release with the artifacts"""
    
    try:
        release_dir = Path.cwd() / "release"
        if not release_dir.exists():
            print("Release directory not found. Run download_workflow_artifacts first.")
            return False
        
        repo_info = get_repo_info()
        if not repo_info:
            return False
        
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        # Get GitHub token
        gh_token = os.environ.get("GITHUB_TOKEN")
        if not gh_token:
            print("GitHub token not found. Set the GITHUB_TOKEN environment variable.")
            return False
        
        print(f"Step 3: Creating GitHub release with artifacts...")
        
        # Check if release already exists
        release_tag = f"v{version}"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get release by tag
        release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{release_tag}"
        response = requests.get(release_url, headers=headers)
        
        release_id = None
        if response.status_code == 200:
            existing_release = response.json()
            release_id = existing_release["id"]
            print(f"Release {release_tag} already exists. Updating it...")
            
            print(f"Updating assets for release {release_tag} (ID: {release_id})...")
            
            # Delete existing assets
            assets = existing_release.get("assets", [])
            for asset in assets:
                asset_id = asset["id"]
                asset_name = asset["name"]
                print(f"Deleting asset: {asset_name}")
                delete_url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 204:
                    print(f"✓ Deleted asset: {asset_name}")
                else:
                    print(f"⚠ Failed to delete asset {asset_name}: {delete_response.status_code}")
            
            # Wait briefly to ensure GitHub API has processed the asset deletions
            time.sleep(1)
        
        # Create a new release if it doesn't exist
        if release_id is None:
            create_data = {
                "tag_name": release_tag,
                "name": f"KP Astrology Dashboard {version}",
                "body": get_release_notes(),
                "draft": False,
                "prerelease": False
            }
            
            create_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            response = requests.post(create_url, headers=headers, json=create_data)
            
            if response.status_code != 201:
                print(f"Failed to create release: {response.status_code} - {response.text}")
                return False
            
            release = response.json()
            release_id = release["id"]
            print(f"✓ Created release: {release['name']}")
        
        # Ensure we have a valid upload URL with the correct release ID
        upload_url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"
        
        # Upload assets to release
        artifacts = list(release_dir.glob("*"))
        
        for artifact in artifacts:
            if artifact.is_file():
                artifact_name = artifact.name
                
                # Check if file exists and is not empty
                if artifact.stat().st_size == 0:
                    print(f"⚠ Skipping empty file: {artifact_name}")
                    continue
                
                # Set proper content type based on file extension
                content_type = "application/octet-stream"
                if artifact.suffix == ".zip":
                    content_type = "application/zip"
                elif artifact.suffix == ".exe":
                    content_type = "application/vnd.microsoft.portable-executable"
                elif artifact.suffix in [".bat", ".sh", ".command"]:
                    content_type = "text/plain"
                
                # Upload asset
                asset_url = f"{upload_url}?name={artifact_name}"
                upload_headers = headers.copy()
                upload_headers["Content-Type"] = content_type
                
                with open(artifact, "rb") as f:
                    response = requests.post(
                        asset_url,
                        headers=upload_headers,
                        data=f
                    )
                
                if response.status_code == 201:
                    print(f"✓ Uploaded {artifact_name}")
                else:
                    print(f"Failed to upload {artifact_name}: {response.status_code} - {response.text}")
        
        print(f"✓ Release {release_tag} is ready: https://github.com/{owner}/{repo}/releases/tag/{release_tag}")
        return True
    
    except Exception as e:
        print(f"Error creating GitHub release: {e}")
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
        
        # Download artifacts from GitHub Actions workflow
        print("\nStep 3: Downloading artifacts from GitHub Actions workflow...")
        repo_info = get_repo_info()
        if repo_info:
            artifacts_success = download_workflow_artifacts(args.version, f"{repo_info['owner']}/{repo_info['repo']}", Path.cwd())
            if not artifacts_success:
                print("Warning: There were issues downloading artifacts.")
                proceed = input("Do you want to continue with the release process anyway? (y/n): ")
                if proceed.lower() != 'y':
                    print("Aborting release process.")
                    return
        
        # Create GitHub release
        print("\nStep 4: Creating GitHub release with artifacts...")
        release_success = create_github_release(args.version)
        
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
        print("5. Wait for GitHub Actions to build the artifacts")
        print("6. Create a GitHub release with the artifacts")


if __name__ == "__main__":
    main() 