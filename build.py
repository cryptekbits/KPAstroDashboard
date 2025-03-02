#!/usr/bin/env python3
"""
Build script for KP Astrology Dashboard

This script packages the application into a standalone executable using PyInstaller.
It handles both Windows and macOS builds.
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
import zipfile
from pathlib import Path

# Import version information
from version import VERSION

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build KP Astrology Dashboard")
    parser.add_argument("--onefile", action="store_true", default=True, help="Create a single executable file")
    parser.add_argument("--onedir", action="store_true", help="Create a directory with the executable and dependencies")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--no-icon", action="store_true", help="Do not include an icon in the build")
    parser.add_argument("--portable", action="store_true", help="Create a portable application (no installer)")
    parser.add_argument("--zip", action="store_true", help="Create a ZIP archive of the portable application")
    parser.add_argument("--target-platform", choices=["auto", "windows", "macos", "linux"], default="auto", 
                        help="Target platform for the build (default: auto-detect)")
    parser.add_argument("--target-arch", choices=["auto", "x64", "arm64"], default="auto",
                        help="Target architecture for the build (default: auto-detect)")
    parser.add_argument("--all-platforms", action="store_true", 
                        help="Build for all supported platforms (requires Docker)")
    args = parser.parse_args()
    
    # If building for all platforms, use Docker to build for each platform
    if args.all_platforms:
        return build_all_platforms(args)
    
    # Determine current platform and architecture
    current_platform = platform.system().lower()
    if current_platform == "darwin":
        current_platform = "macos"
    
    current_arch = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x64"
    
    # Determine target platform and architecture
    target_platform = current_platform if args.target_platform == "auto" else args.target_platform
    target_arch = current_arch if args.target_arch == "auto" else args.target_arch
    
    # Check if we're building for a different platform than the current one
    if target_platform != current_platform or target_arch != current_arch:
        print(f"Cross-compiling from {current_platform}-{current_arch} to {target_platform}-{target_arch}")
        return cross_compile(target_platform, target_arch, args)
    
    # Build for the current platform
    return main_build(args)

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
    try:
        if is_macos:
            # For macOS, we need to zip the .app directory
            app_path = f"dist/{output_name}.app"
            zip_path = f"dist/{output_name}-portable.zip"
            if os.path.exists(app_path):
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(app_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, "dist"))
                print(f"ZIP archive created at {zip_path}")
            else:
                print(f"Error: {app_path} not found.")
        else:
            # For Windows and Linux, zip the directory
            dir_path = f"dist/{output_name}"
            zip_path = f"dist/{output_name}-portable.zip"
            if os.path.exists(dir_path):
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, "dist"))
                print(f"ZIP archive created at {zip_path}")
            else:
                print(f"Error: {dir_path} not found.")
    except Exception as e:
        print(f"Failed to create ZIP archive: {e}")
        print(f"Failed to create ZIP archive.")

def cross_compile(target_platform, target_arch, args):
    """
    Cross-compile for a different platform using Docker
    """
    # Check if Docker is installed
    if not shutil.which("docker"):
        print("Error: Docker is required for cross-compilation but not found.")
        print("Please install Docker and try again.")
        return 1
    
    # Define Docker images for each platform/architecture
    docker_images = {
        "windows-x64": "cdrx/pyinstaller-windows:python3",
        "linux-x64": "python:3.9-slim",
        "linux-arm64": "arm64v8/python:3.9-slim",
        "macos-x64": None,  # Not directly supported via Docker
        "macos-arm64": None,  # Not directly supported via Docker
    }
    
    target_key = f"{target_platform}-{target_arch}"
    if target_key not in docker_images or docker_images[target_key] is None:
        print(f"Error: Cross-compilation to {target_key} is not supported via Docker.")
        print("You need to build directly on the target platform.")
        return 1
    
    docker_image = docker_images[target_key]
    
    # Create Docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/src",
        "-w", "/src",
        docker_image
    ]
    
    # Prepare build command for the Docker container
    build_args = []
    if args.onefile:
        build_args.append("--onefile")
    if args.onedir:
        build_args.append("--onedir")
    if args.clean:
        build_args.append("--clean")
    if args.no_icon:
        build_args.append("--no-icon")
    if args.portable:
        build_args.append("--portable")
    if args.zip:
        build_args.append("--zip")
    
    # Add target platform and architecture
    build_args.extend(["--target-platform", target_platform, "--target-arch", target_arch])
    
    if target_platform == "windows":
        # For Windows, use the pyinstaller-windows Docker image
        docker_cmd.extend([
            "bash", "-c",
            f"pip install -r requirements.txt && python build.py {' '.join(build_args)}"
        ])
    else:
        # For Linux, use the standard Python Docker image
        docker_cmd.extend([
            "bash", "-c",
            f"pip install pyinstaller && pip install -r requirements.txt && python build.py {' '.join(build_args)}"
        ])
    
    print(f"Running Docker for cross-compilation to {target_platform}-{target_arch}...")
    print(f"Docker command: {' '.join(docker_cmd)}")
    
    # Run Docker command
    try:
        subprocess.run(docker_cmd, check=True)
        print(f"Cross-compilation for {target_platform}-{target_arch} completed successfully.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error during cross-compilation: {e}")
        return 1

def build_all_platforms(args):
    """
    Build for all supported platforms
    """
    platforms = ["windows", "linux"]  # macOS builds need to be done on macOS
    architectures = ["x64", "arm64"]  # arm64 for Linux only
    
    results = {}
    
    # Build for the current platform first
    current_platform = platform.system().lower()
    if current_platform == "darwin":
        current_platform = "macos"
    
    current_arch = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x64"
    
    print(f"Building for current platform: {current_platform}-{current_arch}")
    
    # Create a copy of args without --all-platforms to avoid recursion
    current_args = argparse.Namespace(**vars(args))
    current_args.all_platforms = False
    current_args.target_platform = current_platform
    current_args.target_arch = current_arch
    
    # Run the main function for the current platform
    main_result = main_build(current_args)
    results[f"{current_platform}-{current_arch}"] = main_result == 0
    
    # Build for other platforms using Docker
    for target_platform in platforms:
        for target_arch in architectures:
            # Skip the current platform (already built)
            if target_platform == current_platform and target_arch == current_arch:
                continue
                
            # Skip macOS (needs to be built on macOS)
            if target_platform == "macos":
                continue
                
            # Skip arm64 for Windows (not well supported)
            if target_platform == "windows" and target_arch == "arm64":
                continue
                
            print(f"\nBuilding for {target_platform}-{target_arch}...")
            result = cross_compile(target_platform, target_arch, args)
            results[f"{target_platform}-{target_arch}"] = result == 0
    
    # Print summary
    print("\nBuild Summary:")
    for platform_arch, success in results.items():
        status = "Success" if success else "Failed"
        print(f"  {platform_arch}: {status}")
    
    # Return 0 if all builds succeeded, 1 otherwise
    return 0 if all(results.values()) else 1

def main_build(args):
    """Main build implementation (extracted from main)"""
    # If both onefile and onedir are specified, onefile takes precedence
    if args.onedir:
        args.onefile = False
        
    # Determine current platform and architecture
    current_platform = platform.system().lower()
    if current_platform == "darwin":
        current_platform = "macos"
    
    current_arch = "arm64" if platform.machine() in ["arm64", "aarch64"] else "x64"
    
    # Determine target platform and architecture
    target_platform = current_platform if args.target_platform == "auto" else args.target_platform
    target_arch = current_arch if args.target_arch == "auto" else args.target_arch
    
    # Determine platform-specific settings
    is_windows = target_platform == "windows"
    is_macos = target_platform == "macos"
    is_linux = target_platform == "linux"
    
    # Set output name based on platform and architecture
    if is_windows:
        output_name = f"KPAstrologyDashboard-v{VERSION}-win-{target_arch}"
        icon_file = "resources/favicon.ico" if not args.no_icon else None
    elif is_macos:
        output_name = f"KPAstrologyDashboard-v{VERSION}-mac-{target_arch}"
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
        output_name = f"KPAstrologyDashboard-v{VERSION}-linux-{target_arch}"
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
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during PyInstaller execution: {e}")
        return 1
    
    # Skip installer creation for portable apps
    if args.portable:
        print(f"Portable app created successfully. Output in dist/{output_name}")
        
        # Create ZIP archive if requested
        if args.zip:
            create_zip_archive(output_name, is_macos)
        
        return 0
    
    # Create installer for Windows using NSIS (if installed and not in portable mode)
    if is_windows and shutil.which("makensis") and not args.portable:
        create_windows_installer(output_name, VERSION)
    
    print(f"Build completed successfully. Output in dist/{output_name}")
    return 0

if __name__ == "__main__":
    main() 