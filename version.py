"""
Version information for the KP Dashboard application.
This file is updated with each release.
"""
import os
from datetime import datetime

# Default version information
VERSION = "1.3.0"
VERSION_NAME = "AI 1.3.0 - Ephemeris Handling & User Experience Improvements Release"
BUILD_DATE = "2024-03-06"

# Check for environment variables that might override the version
# This is useful for CI/CD pipelines like GitHub Actions
if os.environ.get("CI_VERSION"):
    VERSION = os.environ.get("CI_VERSION")
    
    # If this is a development build, add the development tag
    if "-dev" in VERSION:
        VERSION_NAME = f"AI {VERSION} - Development Build"
        BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

# GitHub repository information
GITHUB_REPO_OWNER = "cryptekbits"  # Replace with actual GitHub username
GITHUB_REPO_NAME = "KPAstroDashboard"  # Replace with actual repository name

# Function to determine if this is a development version
def is_dev_version():
    return "-dev" in VERSION 