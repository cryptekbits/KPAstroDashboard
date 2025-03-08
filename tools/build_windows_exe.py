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
    print("Windows executable build is disabled. Exiting.")
    import sys
    sys.exit(0)

if __name__ == "__main__":
    main() 