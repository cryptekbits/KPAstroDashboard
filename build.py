#!/usr/bin/env python3
"""
Build script for KP Astrology Dashboard

This script packages the application into a standalone executable using PyInstaller.
It handles both Windows and macOS builds.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse

# Import version information
from version import VERSION

def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description="Build KP Astrology Dashboard")
    parser.add_argument("--onefile", action="store_true", help="Create a single executable file", default=True)
    parser.add_argument("--onedir", action="store_true", help="Create a directory with executable and dependencies")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--no-icon", action="store_true", help="Build without an icon")
    parser.add_argument("--portable", action="store_true", help="Create a portable app without installer", default=True)
    parser.add_argument("--zip", action="store_true", help="Create a ZIP archive of the portable app")
    args = parser.parse_args()
    
    # If both onefile and onedir are specified, onefile takes precedence
    if args.onedir:
        args.onefile = False
    
    # Determine platform-specific settings
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    
    # Set output name based on platform
    if is_windows:
        output_name = f"KPAstrologyDashboard-v{VERSION}"
        icon_file = "resources/favicon.ico" if not args.no_icon else None
    elif is_macos:
        output_name = f"KPAstrologyDashboard-v{VERSION}"
        # On macOS, we need .icns format or Pillow installed for conversion
        try:
            import PIL
            icon_file = "resources/favicon.ico" if not args.no_icon else None
            print("Pillow is installed. Icon will be automatically converted for macOS.")
        except ImportError:
            print("Pillow not installed. To use an icon on macOS, install Pillow with: pip install pillow")
            if not args.no_icon:
                print("Attempting to build with icon anyway. If this fails, use --no-icon option.")
            icon_file = "resources/favicon.ico" if not args.no_icon else None
    else:  # Linux
        output_name = f"kp-astrology-dashboard-v{VERSION}"
        icon_file = "resources/favicon.ico" if not args.no_icon else None
    
    # Clean build directories if requested
    if args.clean:
        print("Cleaning build directories...")
        try:
            if os.path.exists("build"):
                shutil.rmtree("build", ignore_errors=True)
            if os.path.exists("dist"):
                shutil.rmtree("dist", ignore_errors=True)
            print("Build directories cleaned successfully.")
        except Exception as e:
            print(f"Warning: Could not clean directories completely: {e}")
            # Try to create them if they don't exist
            os.makedirs("build", exist_ok=True)
            os.makedirs("dist", exist_ok=True)
    
    # Create PyInstaller command
    cmd = ["pyinstaller", "--name", output_name]
    
    # Add icon if available
    if icon_file:
        cmd.extend(["--icon", icon_file])
    
    # Add platform-specific options
    if is_macos:
        cmd.append("--windowed")  # Create a Mac app bundle
    
    # Add onefile option if requested
    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    # Add noconfirm option to avoid interactive prompts
    cmd.append("--noconfirm")
    
    # Add data files
    cmd.extend([
        "--add-data", f"config.json{os.pathsep}.",
        "--add-data", f"resources{os.pathsep}resources",
        "--add-data", f"astro_engine/data{os.pathsep}astro_engine/data",
        "--add-data", f"data_generators/locations.json{os.pathsep}data_generators",
    ])
    
    # Look for additional data files that might be needed
    print("Scanning for additional data files...")
    for root, dirs, files in os.walk("."):
        if ".git" in root or "venv" in root or "__pycache__" in root or "build" in root or "dist" in root:
            continue
            
        # Include all JSON files that might contain configuration or data
        for file in files:
            if file.endswith(".json") and not any(p in file for p in ["package", "tsconfig"]):
                rel_dir = os.path.relpath(root, ".")
                if rel_dir == ".":
                    # Files in the root directory
                    if file != "config.json":  # Already added above
                        print(f"Adding data file: {file}")
                        cmd.extend(["--add-data", f"{file}{os.pathsep}."])
                else:
                    # Skip files already explicitly added
                    if rel_dir == "data_generators" and file == "locations.json":
                        continue
                        
                    print(f"Adding data file: {os.path.join(rel_dir, file)}")
                    cmd.extend(["--add-data", f"{os.path.join(rel_dir, file)}{os.pathsep}{rel_dir}"])
                    
        # Include all data directories
        if "data" in dirs:
            data_dir = os.path.join(root, "data")
            rel_dir = os.path.relpath(data_dir, ".")
            
            # Skip directories already explicitly added
            if rel_dir == "astro_engine/data":
                continue
                
            print(f"Adding data directory: {rel_dir}")
            cmd.extend(["--add-data", f"{rel_dir}{os.pathsep}{rel_dir}"])
    
    # Add hidden imports for libraries that might not be automatically detected
    cmd.extend([
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "PyQt5",
        "--hidden-import", "requests",
        "--hidden-import", "packaging",
        "--hidden-import", "geopy",
        "--hidden-import", "polars",
        "--hidden-import", "flatlib",
        "--hidden-import", "tabulate",
        "--hidden-import", "psutil",
        "--hidden-import", "ephem",
        "--hidden-import", "dateutil",
    ])
    
    # Exclude unnecessary modules to reduce size
    cmd.extend([
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
    ])
    
    # Add main script
    cmd.append("main.py")
    
    # Run PyInstaller
    print(f"Running PyInstaller with command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Skip installer creation for portable apps
    if args.portable:
        print(f"Portable app created successfully. Output in dist/{output_name}")
        
        # Create ZIP archive if requested
        if args.zip:
            create_zip_archive(output_name, is_macos)
        
        return
    
    # Create installer for Windows using NSIS (if installed and not in portable mode)
    if is_windows and shutil.which("makensis") and not args.portable:
        create_windows_installer(output_name, VERSION)
    
    print(f"Build completed successfully. Output in dist/{output_name}")

def create_windows_installer(output_name, version):
    """Create a Windows installer using NSIS"""
    print("Creating Windows installer with NSIS...")
    
    # Create NSIS script
    nsis_script = f"""
    !include "MUI2.nsh"
    
    Name "KP Astrology Dashboard v{version}"
    OutFile "dist/KPAstrologyDashboard-v{version}-Setup.exe"
    InstallDir "$PROGRAMFILES\\KP Astrology Dashboard"
    
    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_DIRECTORY
    !insertmacro MUI_PAGE_INSTFILES
    !insertmacro MUI_PAGE_FINISH
    
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
    
    !insertmacro MUI_LANGUAGE "English"
    
    Section "Install"
        SetOutPath "$INSTDIR"
        File /r "dist\\{output_name}\\*.*"
        
        # Create shortcut
        CreateDirectory "$SMPROGRAMS\\KP Astrology Dashboard"
        CreateShortcut "$SMPROGRAMS\\KP Astrology Dashboard\\KP Astrology Dashboard.lnk" "$INSTDIR\\{output_name}.exe"
        CreateShortcut "$DESKTOP\\KP Astrology Dashboard.lnk" "$INSTDIR\\{output_name}.exe"
        
        # Create uninstaller
        WriteUninstaller "$INSTDIR\\Uninstall.exe"
        
        # Add uninstaller to Add/Remove Programs
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KPAstrologyDashboard" \\
                         "DisplayName" "KP Astrology Dashboard"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KPAstrologyDashboard" \\
                         "UninstallString" "$\\"$INSTDIR\\Uninstall.exe$\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KPAstrologyDashboard" \\
                         "DisplayVersion" "{version}"
    SectionEnd
    
    Section "Uninstall"
        # Remove files and directories
        RMDir /r "$INSTDIR"
        
        # Remove shortcuts
        Delete "$SMPROGRAMS\\KP Astrology Dashboard\\KP Astrology Dashboard.lnk"
        RMDir "$SMPROGRAMS\\KP Astrology Dashboard"
        Delete "$DESKTOP\\KP Astrology Dashboard.lnk"
        
        # Remove registry entries
        DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KPAstrologyDashboard"
    SectionEnd
    """
    
    # Write NSIS script to file
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Run NSIS compiler
    subprocess.run(["makensis", "installer.nsi"], check=True)
    
    # Clean up
    os.remove("installer.nsi")
    
    print(f"Installer created: dist/KPAstrologyDashboard-v{version}-Setup.exe")

def create_zip_archive(output_name, is_macos):
    """Create a ZIP archive of the portable application"""
    print(f"Creating ZIP archive of the portable application...")
    
    # Determine the source directory to zip
    if is_macos:
        # On macOS, we have both the .app bundle and the directory
        source_path = f"dist/{output_name}.app" if os.path.exists(f"dist/{output_name}.app") else f"dist/{output_name}"
    else:
        source_path = f"dist/{output_name}"
    
    # Create the ZIP file
    zip_filename = f"{output_name}-portable.zip"
    shutil.make_archive(
        base_name=output_name,
        format="zip",
        root_dir="dist",
        base_dir=os.path.basename(source_path)
    )
    
    # Move the ZIP file to the dist directory
    if os.path.exists(f"{output_name}.zip"):
        shutil.move(f"{output_name}.zip", f"dist/{zip_filename}")
        print(f"ZIP archive created: dist/{zip_filename}")
    else:
        print(f"Failed to create ZIP archive.")

if __name__ == "__main__":
    main() 