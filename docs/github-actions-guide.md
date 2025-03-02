# GitHub Actions Build Guide for KP Astrology Dashboard

This guide explains how to use GitHub Actions to automatically build the KP Astrology Dashboard application for Windows.

## Workflow Overview

The GitHub Actions workflow (`.github/workflows/windows-build.yml`) is configured to:

1. Build the Windows application automatically on:
   - Any push to `main` or `master` branches
   - Any pull request to `main` or `master` branches
   - When a new tag starting with 'v' is pushed (e.g., `v1.0.4`)
   - Manual trigger from the GitHub UI

2. Upload build artifacts that can be downloaded from the GitHub Actions page
3. Automatically create GitHub Releases when a new version tag is pushed

## Getting Started

To use this workflow, follow these steps:

1. Make sure your project is pushed to GitHub
2. The workflow will start automatically on push/PR to main/master
3. To trigger a manual build:
   - Go to your GitHub repository
   - Click on "Actions"
   - Select "Build Windows Application" from the left sidebar
   - Click "Run workflow" dropdown on the right side
   - Select the branch and click "Run workflow"

## Creating Releases

To create a new release with Windows builds:

1. Tag your code locally:
   ```bash
   git tag v1.0.4
   git push origin v1.0.4
   ```

2. The workflow will automatically:
   - Build the Windows application
   - Create a new GitHub Release with the EXE installer attached
   - Name the release after the tag (e.g., "v1.0.4")

## Downloading Artifacts

For builds that aren't full releases, you can download artifacts:

1. Go to the "Actions" tab on GitHub
2. Find and click on the completed workflow run
3. Scroll down to the "Artifacts" section
4. Click on "kp-dashboard-windows" to download the ZIP file containing the build

## Customizing the Workflow

You can customize the workflow by editing `.github/workflows/windows-build.yml`:

- Change the build parameters by modifying the `python build.py` command
- Adjust which files are included in the artifacts and releases
- Modify the trigger conditions to fit your workflow

## Troubleshooting

If the build fails:

1. Check the logs in the GitHub Actions run for error messages
2. Common issues:
   - Missing dependencies in `requirements.txt`
   - Build script compatibility issues with Windows
   - Path issues specific to Windows environments

## Windows-Specific Considerations

Building on Windows through GitHub Actions eliminates the need for cross-compilation and ensures native compatibility. Some benefits:

- Access to native Windows libraries and dependencies
- No emulation overhead or compatibility issues
- Proper handling of Windows-specific paths and file operations 