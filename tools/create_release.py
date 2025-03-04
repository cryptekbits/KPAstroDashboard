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
        
        # Push the changes if there were any
        if has_changes:
            push_result = subprocess.run(
                ["git", "push", "origin", "master"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if push_result.returncode != 0:
                print("Warning: Failed to push commits, but continuing with tag push.")
                print(f"Error: {push_result.stderr}")
        
        # Push the tag
        tag_push_result = subprocess.run(
            ["git", "push", "origin", tag_name],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if tag_push_result.returncode != 0:
            print(f"Warning: Failed to push tag {tag_name}.")
            print(f"Error: {tag_push_result.stderr}")
            
            # Check if it's because the tag already exists remotely
            if "already exists" in tag_push_result.stderr:
                print(f"Tag {tag_name} already exists on remote. Continuing with release process.")
                return True
            return False
        
        print(f"Pushed tag {tag_name}")
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
        
        import json
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
                    if "jobs" in jobs_data and any(job.get("name", "").startswith("build-") for job in jobs_data["jobs"]):
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
                run_id = in_progress_runs[0].get("databaseId")
                print(f"Workflow for tag {tag_name} is already in progress (Run ID: {run_id}). Waiting for completion...")
    except Exception as e:
        print(f"Error checking initial workflow status: {e}")
        print("Continuing with standard wait procedure...")
    
    start_time = time.time()
    last_status_time = start_time
    while time.time() - start_time < timeout:
        try:
            # Check workflow status using GitHub CLI
            result = subprocess.run(
                ["gh", "run", "list", "--repo", repo_info, "--json", "status,conclusion,headBranch,databaseId,name"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            runs = json.loads(result.stdout)
            tag_runs = [run for run in runs if run.get("headBranch") == tag_name or (run.get("headBranch", "").startswith("refs/tags/") and version in run.get("headBranch", ""))]
            
            current_time = time.time()
            if current_time - last_status_time >= 60:  # Print status update every minute
                print(f"Waiting for workflow completion... Elapsed time: {int((current_time - start_time) / 60)} minutes")
                last_status_time = current_time
            
            if tag_runs:
                for run in tag_runs:
                    if run.get("status") == "completed":
                        if run.get("conclusion") == "success":
                            print(f"Workflow completed successfully! (Run ID: {run.get('databaseId')})")
                            
                            # Wait a bit more to ensure artifacts are fully processed
                            print("Waiting 30 seconds for artifacts to be fully processed...")
                            time.sleep(30)
                            
                            return True
                        else:
                            print(f"Workflow completed with status: {run.get('conclusion')} (Run ID: {run.get('databaseId')})")
                            print("Continuing with release process anyway...")
                            return True
                
                # If we get here, there are runs but none are completed
                print(f"Workflow still running. Status: {tag_runs[0].get('status')}. Waiting...")
            else:
                print(f"No workflow runs found for tag {tag_name} yet. Waiting...")
            
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
    
    # Create artifacts directory if it doesn't exist
    if not artifacts_dir.exists():
        artifacts_dir.mkdir()
    else:
        # Clean up any existing files
        for item in artifacts_dir.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    
    print(f"Downloading build artifacts for release {tag_name}...")
    
    try:
        # List workflow runs to find the one for our tag
        result = subprocess.run(
            ["gh", "run", "list", "--repo", repo_info, "--json", "databaseId,headBranch,status,conclusion"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        runs = json.loads(result.stdout)
        
        # Filter runs related to our tag that have completed successfully
        tag_runs = [
            run for run in runs 
            if (run.get("headBranch") == tag_name or 
                (run.get("headBranch", "").startswith("refs/tags/") and version in run.get("headBranch", "")))
            and run.get("status") == "completed"
            and run.get("conclusion") == "success"
        ]
        
        if not tag_runs:
            print(f"No completed workflow runs found for tag {tag_name}. Skipping artifact download.")
            return []
        
        # Get the run ID of the most recent successful run
        run_id = tag_runs[0]["databaseId"]
        
        # List artifacts for this run
        artifacts_result = subprocess.run(
            ["gh", "run", "download", str(run_id), "--repo", repo_info, "--dir", str(artifacts_dir)],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if artifacts_result.returncode != 0:
            print(f"Error downloading artifacts: {artifacts_result.stderr}")
            return []
        
        print(f"Downloaded artifacts to {artifacts_dir}")
        
        # List downloaded artifacts
        artifact_files = []
        for root, dirs, files in os.walk(artifacts_dir):
            for file in files:
                artifact_files.append(Path(os.path.join(root, file)))
        
        print(f"Found {len(artifact_files)} artifact files")
        
        # Expected artifact patterns
        windows_exe_pattern = "*.exe"
        windows_zip_pattern = "*Windows*.zip"
        macos_zip_pattern = "*macOS*.zip"
        source_zip_pattern = "SourceCode*.zip"
        
        # Find and rename artifacts to match expected naming convention
        renamed_artifacts = []
        
        # Windows executable
        windows_exes = list(artifacts_dir.glob("**/" + windows_exe_pattern))
        if windows_exes:
            windows_exe = windows_exes[0]
            new_name = artifacts_dir / f"{APP_NAME}-{version}.exe"
            shutil.copy(windows_exe, new_name)
            renamed_artifacts.append(new_name)
            print(f"Prepared Windows executable: {new_name.name}")
        else:
            print("No Windows executable found")
        
        # Windows ZIP
        windows_zips = list(artifacts_dir.glob("**/" + windows_zip_pattern))
        if windows_zips:
            windows_zip = windows_zips[0]
            new_name = artifacts_dir / f"{APP_NAME}-{version}-Windows.zip"
            shutil.copy(windows_zip, new_name)
            renamed_artifacts.append(new_name)
            print(f"Prepared Windows ZIP: {new_name.name}")
        else:
            print("No Windows ZIP found")
        
        # macOS ZIP
        macos_zips = list(artifacts_dir.glob("**/" + macos_zip_pattern))
        if macos_zips:
            macos_zip = macos_zips[0]
            new_name = artifacts_dir / f"{APP_NAME}-{version}-macOS.zip"
            shutil.copy(macos_zip, new_name)
            renamed_artifacts.append(new_name)
            print(f"Prepared macOS ZIP: {new_name.name}")
        else:
            print("No macOS ZIP found")
        
        # Source code ZIP
        source_zips = list(artifacts_dir.glob("**/" + source_zip_pattern))
        if source_zips:
            source_zip = source_zips[0]
            new_name = artifacts_dir / f"SourceCode-{version}.zip"
            shutil.copy(source_zip, new_name)
            renamed_artifacts.append(new_name)
            print(f"Prepared source code ZIP: {new_name.name}")
        else:
            print("No source code ZIP found")
        
        if not renamed_artifacts:
            print("Warning: No artifacts were found that match the expected patterns.")
            print("Available files:")
            for artifact in artifact_files:
                print(f"  - {artifact.relative_to(artifacts_dir)}")
            
            # If we couldn't find any matching artifacts, just return all artifact files
            return artifact_files
        
        return renamed_artifacts
    except Exception as e:
        print(f"Error downloading workflow artifacts: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_github_release(version):
    """Create a GitHub release with artifacts from GitHub Actions"""
    root_dir = Path(__file__).parent.parent
    tag_name = f"v{version}"
    
    try:
        repo_info = get_repo_info()
    except Exception as e:
        print(f"Error getting repository information: {e}")
        print("Please create the release manually with the following steps:")
        print(f"1. Go to the GitHub repository releases page")
        print(f"2. Create a new release with tag '{tag_name}'")
        print(f"3. Add release notes and upload the artifacts")
        return False
    
    # Check if release already exists
    try:
        check_result = subprocess.run(
            ["gh", "release", "view", tag_name, "--repo", repo_info],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check_result.returncode == 0:
            print(f"Release {tag_name} already exists.")
            
            # Check if we need to upload build artifacts
            if f"{APP_NAME}-{version}" not in check_result.stdout:
                print("Downloading and uploading build artifacts...")
                artifacts = download_workflow_artifacts(version, repo_info, root_dir)
                
                if artifacts:
                    for artifact in artifacts:
                        print(f"Uploading {artifact.name} to release...")
                        upload_result = subprocess.run(
                            ["gh", "release", "upload", tag_name, str(artifact), "--repo", repo_info],
                            cwd=root_dir,
                            capture_output=True,
                            text=True,
                            check=False
                        )
                        
                        if upload_result.returncode == 0:
                            print(f"Successfully uploaded {artifact.name}")
                        else:
                            print(f"Failed to upload {artifact.name}: {upload_result.stderr}")
                else:
                    print("No build artifacts found to upload.")
            else:
                print("Build artifacts already exist in the release.")
                
            return True
    except Exception as e:
        print(f"Error checking existing release: {e}")
    
    # Generate release notes
    release_notes = get_release_notes()
    
    # Download build artifacts
    artifacts = download_workflow_artifacts(version, repo_info, root_dir)
    
    if not artifacts:
        print("No artifacts found. Please check GitHub Actions workflow status.")
        proceed = input("Do you want to continue creating the release without artifacts? (y/n): ")
        if proceed.lower() != 'y':
            print("Aborting release creation.")
            return False
    
    try:
        # Create a GitHub release using GitHub CLI
        create_cmd = [
            "gh", "release", "create", tag_name,
            "--title", f"Release {tag_name}",
            "--notes", release_notes,
            "--repo", repo_info
        ]
        
        # Add artifacts to the command
        for artifact in artifacts:
            create_cmd.append(str(artifact))
        
        create_result = subprocess.run(
            create_cmd,
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if create_result.returncode == 0:
            print(f"Created GitHub release {tag_name} with all artifacts")
            return True
        else:
            print(f"Error creating GitHub release: {create_result.stderr}")
            
            # Check if it's because the release already exists
            if "already exists" in create_result.stderr:
                print(f"Release {tag_name} already exists. Trying to upload artifacts...")
                
                # Upload build artifacts
                for artifact in artifacts:
                    print(f"Uploading {artifact.name} to release...")
                    upload_result = subprocess.run(
                        ["gh", "release", "upload", tag_name, str(artifact), "--repo", repo_info],
                        cwd=root_dir,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if upload_result.returncode == 0:
                        print(f"Successfully uploaded {artifact.name}")
                    else:
                        print(f"Failed to upload {artifact.name}: {upload_result.stderr}")
                
                return True
            
            print("Please create the release manually with the following steps:")
            print(f"1. Go to the GitHub repository releases page")
            print(f"2. Create a new release with tag '{tag_name}'")
            print(f"3. Add the release notes and upload the artifacts")
            return False
    except Exception as e:
        print(f"Error during release creation: {e}")
        print("Please create the release manually with the following steps:")
        print(f"1. Go to the GitHub repository releases page")
        print(f"2. Create a new release with tag '{tag_name}'")
        print(f"3. Add the release notes and upload the artifacts")
        return False


def get_repo_info():
    """Get repository information from version.py"""
    version_file_path = Path(__file__).parent.parent / "version.py"
    repo_owner = None
    repo_name = None
    
    with open(version_file_path, "r") as f:
        for line in f:
            if line.startswith("GITHUB_REPO_OWNER"):
                # Extract the value and remove any comments
                value = line.split("=")[1].strip()
                # Remove any comments that might be present
                if "#" in value:
                    value = value[:value.find("#")].strip()
                # Remove quotes
                repo_owner = value.strip('"\'')
            elif line.startswith("GITHUB_REPO_NAME"):
                # Extract the value and remove any comments
                value = line.split("=")[1].strip()
                # Remove any comments that might be present
                if "#" in value:
                    value = value[:value.find("#")].strip()
                # Remove quotes
                repo_name = value.strip('"\'')
    
    if not repo_owner or not repo_name:
        raise ValueError("Could not determine repository information from version.py")
    
    # Check if these are placeholder values
    if "Replace with actual" in repo_owner or "Replace with actual" in repo_name:
        print("Warning: Repository information in version.py contains placeholder values.")
        print("Please update GITHUB_REPO_OWNER and GITHUB_REPO_NAME in version.py with actual values.")
        
        # Ask for the values interactively
        print("\nPlease provide the actual repository information:")
        input_owner = input("GitHub username/organization: ").strip()
        input_name = input("Repository name: ").strip()
        
        if input_owner and input_name:
            return f"{input_owner}/{input_name}"
        else:
            raise ValueError("Valid repository information is required to continue.")
    
    return f"{repo_owner}/{repo_name}"


def main():
    parser = argparse.ArgumentParser(description="Create a new release of KP Dashboard")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("version_name", help="Version name (e.g., 'Bug Fix Release')")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to GitHub")
    parser.add_argument("--no-wait", action="store_true", help="Skip waiting for GitHub Actions")
    parser.add_argument("--force", action="store_true", help="Force update even if version hasn't changed")
    parser.add_argument("--app-name", default="AstroInsight", help="Application name for release artifacts (default: AstroInsight)")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds for waiting for workflow completion (default: 1800)")
    
    args = parser.parse_args()
    
    # Set global variables
    global APP_NAME
    APP_NAME = args.app_name
    
    print(f"Starting release process for {APP_NAME} v{args.version} ({args.version_name})")
    
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
        
        # Create GitHub release
        print("\nStep 3: Creating GitHub release with artifacts...")
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


# Global variables
APP_NAME = "AstroInsight"  # Default application name, can be overridden by --app-name


if __name__ == "__main__":
    main() 