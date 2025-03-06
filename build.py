#!/usr/bin/env python3
"""
Build script for KP Astrology Dashboard

This script packages the application into standalone executables using PyInstaller.
It supports building for multiple platforms and architectures:
- Windows (x64)
- macOS (x64, arm64)
- Linux (x64, arm64)

Cross-compilation is supported using Docker containers, allowing you to build
for Windows and Linux from any platform.

Usage examples:
  # Build for the current platform
  python build.py --clean
  
  # Build for Windows x64 (requires Docker)
  python build.py --clean --target-platform windows --target-arch x64
  
  # Build for all supported platforms (requires Docker)
  python build.py --clean --all-platforms
  
  # Build for Windows on Apple Silicon Mac using alternative Docker image
  python build.py --clean --target-platform windows --target-arch x64 --alt-win-image
  
  # Create a ZIP archive of the portable application
  python build.py --clean --zip
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
import zipfile
import tempfile
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
    parser.add_argument("--no-zip", action="store_true", help="Skip creating a ZIP archive of the application")
    parser.add_argument("--target-platform", choices=["auto", "windows", "macos", "linux"], default="auto", 
                        help="Target platform for the build (default: auto-detect)")
    parser.add_argument("--target-arch", choices=["auto", "x64", "arm64"], default="auto",
                        help="Target architecture for the build (default: auto-detect)")
    parser.add_argument("--all-platforms", action="store_true", 
                        help="Build for all supported platforms (requires Docker)")
    parser.add_argument("--alt-win-image", action="store_true",
                        help="Use alternative Docker image for Windows builds (useful for Apple Silicon Macs)")
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

def create_windows_installer(output_name, version, is_onefile=True):
    """Create a Windows installer using NSIS"""
    print("Creating Windows installer with NSIS...")
    
    # Determine the file or directory to include based on build mode
    if is_onefile:
        file_command = f'File "dist\\{output_name}.exe"'
        exe_path = f"$INSTDIR\\{output_name}.exe"
    else:
        file_command = f'File /r "dist\\{output_name}\\*.*"'
        exe_path = f"$INSTDIR\\{output_name}.exe"
    
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
        {file_command}
        
        # Create shortcut
        CreateDirectory "$SMPROGRAMS\\KP Astrology Dashboard"
        CreateShortcut "$SMPROGRAMS\\KP Astrology Dashboard\\KP Astrology Dashboard.lnk" "{exe_path}"
        CreateShortcut "$DESKTOP\\KP Astrology Dashboard.lnk" "{exe_path}"
        
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
    
    # Determine the source path to zip
    if is_macos:
        # On macOS, use the .app bundle if it exists
        source_path = f"dist/{output_name}.app"
        if not os.path.exists(source_path):
            source_path = f"dist/{output_name}"
            if not os.path.exists(source_path):
                print(f"Error: No source path found to create ZIP archive")
                return
    else:
        # For Windows/Linux, use the main executable if in onefile mode
        if os.path.exists(f"dist/{output_name}.exe"):
            source_path = f"dist/{output_name}.exe"
        elif os.path.exists(f"dist/{output_name}"):
            source_path = f"dist/{output_name}"
        else:
            print(f"Error: No source path found to create ZIP archive")
            return
    
    # Create the ZIP file
    zip_path = f"dist/{output_name}-portable.zip"
    try:
        if os.path.isdir(source_path):
            # For directories (app bundles or onedir builds)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(source_path)))
        else:
            # For single files (onefile builds)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source_path, os.path.basename(source_path))
        
        print(f"ZIP archive created at {zip_path}")
    except Exception as e:
        print(f"Failed to create ZIP archive: {e}")

def create_cross_compile_requirements(target_platform, target_arch):
    """
    Create a simplified requirements file for cross-compilation to avoid problematic dependencies
    """
    print("Creating modified requirements file for cross-compilation...")
    
    # Read the original requirements file
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    
    # Create a backup of the original requirements file
    shutil.copy("requirements.txt", "requirements.txt.bak")
    
    # Filter out problematic dependencies based on target platform
    filtered_reqs = []
    problematic_packages = []
    
    for req in requirements:
        req = req.strip()
        # Skip empty lines and comments
        if not req or req.startswith("#"):
            filtered_reqs.append(req)
            continue
        
        package_name = req.split(">=")[0].split("==")[0].strip()
        
        # Check for problematic packages
        if package_name == "PyQt5":
            if target_platform == "windows":
                # For Windows, use an older version of PyQt5 that has pre-built wheels
                filtered_reqs.append("PyQt5==5.15.6")
            elif target_platform == "linux" and target_arch == "arm64":
                # For Linux ARM64, skip PyQt5 for now
                filtered_reqs.append("# PyQt5 is skipped for ARM64 Linux - will be installed manually")
                problematic_packages.append(package_name)
            else:
                filtered_reqs.append(req)
        elif package_name == "flatlib":
            # Handle flatlib separately
            problematic_packages.append(package_name)
            filtered_reqs.append("# flatlib is skipped - will be installed manually")
        elif package_name in ["polars", "numpy", "pandas"] and target_arch == "arm64":
            # These packages need special handling for ARM64
            problematic_packages.append(package_name)
            filtered_reqs.append(f"# {package_name} needs special handling for ARM64")
        else:
            filtered_reqs.append(req)
    
    # Write the modified requirements file
    with open("requirements.cross.txt", "w") as f:
        f.write("\n".join(filtered_reqs))
    
    print("Modified requirements.cross.txt created for cross-compilation")
    
    # Create a script to handle problematic packages
    if problematic_packages:
        create_package_handler_script(target_platform, target_arch, problematic_packages)
    
    return "requirements.cross.txt"

def create_package_handler_script(target_platform, target_arch, problematic_packages):
    """
    Create a script to handle problematic packages
    """
    print(f"Creating script to handle problematic packages: {', '.join(problematic_packages)}")
    
    script_content = [
        "#!/bin/bash",
        "# Script to handle problematic packages for cross-compilation",
        f"# Target: {target_platform}-{target_arch}",
        ""
    ]
    
    # Add commands for each problematic package
    for package in problematic_packages:
        if package == "PyQt5" and target_platform == "linux" and target_arch == "arm64":
            script_content.extend([
                "# Installing Qt dependencies",
                "apt-get update",
                "apt-get install -y qt5-default qttools5-dev-tools",
                "# Try to install PyQt5 from source",
                "pip install PyQt5 --no-binary PyQt5"
            ])
        elif package == "flatlib":
            script_content.extend([
                "# Installing flatlib dependencies",
                "pip install pyswisseph==2.10.3.2 --no-deps",
                "pip install flatlib --no-deps"
            ])
        elif package in ["polars", "numpy", "pandas"] and target_arch == "arm64":
            script_content.extend([
                f"# Installing {package} for ARM64",
                f"pip install --no-binary :{package}: {package}"
            ])
    
    # Write the script
    with open("handle_packages.sh", "w") as f:
        f.write("\n".join(script_content))
    
    # Make the script executable
    os.chmod("handle_packages.sh", 0o755)
    
    print("Created handle_packages.sh script")

def cross_compile(target_platform, target_arch, args):
    """
    Cross-compile for a different platform using Docker
    """
    try:
        # Check if Docker is installed
        if not shutil.which("docker"):
            print("Error: Docker is required for cross-compilation but not found.")
            print("Please install Docker and try again.")
            return 1
        
        # Special handling for Windows on Apple Silicon
        is_apple_silicon = platform.system().lower() == "darwin" and platform.machine() == "arm64"
        if target_platform == "windows" and is_apple_silicon:
            return build_windows_on_apple_silicon(target_arch)
        
        # Create a simplified requirements file for cross-compilation
        create_cross_compile_requirements(target_platform, target_arch)
        
        # Define Docker images for each platform/architecture
        docker_images = {
            "windows-x64": "cdrx/pyinstaller-windows:python3" if not args.alt_win_image else "mcci/windows-docker:latest",
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
        
        # Check if we're on Apple Silicon Mac
        is_apple_silicon = platform.system().lower() == "darwin" and platform.machine() == "arm64"
        
        # Create Docker command
        docker_cmd = ["docker", "run", "--rm"]
        
        # Add platform flag if needed (for Apple Silicon Macs running x64 images)
        if is_apple_silicon and target_arch == "x64" and not args.alt_win_image:
            docker_cmd.extend(["--platform", "linux/amd64"])
        
        docker_cmd.extend([
            "-v", f"{os.getcwd()}:/src",
            "-w", "/src",
            docker_image
        ])
        
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
            # The cdrx/pyinstaller-windows image can be problematic on Apple Silicon
            if is_apple_silicon:
                print("Note: Building Windows executables on Apple Silicon may have issues.")
                print("If this fails, consider using --alt-win-image or building on an Intel Mac/PC.")
                
            # Use a more robust command that handles potential issues with the image
            if args.alt_win_image:
                # For the alternative wine-based image
                docker_cmd.extend([
                    "bash", "-c",
                    f"apt-get update && " +
                    f"apt-get install -y python3 python3-pip python3-dev build-essential git && " +
                    f"pip3 install --upgrade pip && " +
                    f"pip3 install pyinstaller wheel setuptools && " +
                    f"pip3 install -r requirements.cross.txt && " +
                    f"chmod +x handle_packages.sh && " +
                    f"./handle_packages.sh && " +
                    f"python3 build.py {' '.join(build_args)}"
                ])
            else:
                # For the standard cdrx/pyinstaller-windows image
                docker_cmd.extend([
                    "bash", "-c",
                    f"pip install --upgrade pip && " +
                    f"pip install wheel setuptools && " +
                    f"pip install -r requirements.cross.txt && " +
                    f"chmod +x handle_packages.sh && " +
                    f"./handle_packages.sh && " +
                    f"python -m pip install pyinstaller && " +
                    f"python build.py {' '.join(build_args)}"
                ])
        else:
            # For Linux, use the standard Python Docker image with necessary build dependencies
            docker_cmd.extend([
                "bash", "-c",
                f"apt-get update && " +
                f"apt-get install -y build-essential gcc g++ libgl1-mesa-dev && " +
                f"pip install --upgrade pip && " +
                f"pip install pyinstaller wheel setuptools && " +
                f"pip install -r requirements.cross.txt && " +
                f"chmod +x handle_packages.sh && " +
                f"./handle_packages.sh && " +
                f"python build.py {' '.join(build_args)}"
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
    finally:
        # Clean up cross-compilation files
        cleanup_cross_compile_files()

def build_windows_on_apple_silicon(target_arch):
    """Special handling for building Windows on Apple Silicon."""
    print("Detected Apple Silicon Mac building for Windows.")
    print("Using specialized build approach for Windows on Apple Silicon.")
    print("Setting up specialized Windows cross-compilation on Apple Silicon...")
    
    # Create a modified requirements file for cross-compilation
    create_cross_compile_requirements("windows", target_arch)
    
    # No need to create a script to handle problematic packages here
    # The create_cross_compile_requirements function already does this
    
    print("\n================================================================================")
    print("WINDOWS BUILD ON APPLE SILICON")
    print("================================================================================")
    print("\nBuilding Windows applications on Apple Silicon is challenging due to architecture differences.")
    print("Here are the recommended approaches:")
    print("\n1. Use UTM or Parallels to run a Windows VM, then build natively:")
    print("   - Install UTM (free) or Parallels (paid) on your Mac")
    print("   - Install Windows 11 ARM64 edition in the VM")
    print("   - Set up the development environment in Windows")
    print("   - Run the build script directly in Windows")
    print("\n2. Use a CI/CD service for cross-platform builds:")
    print("   - Set up GitHub Actions to build for Windows")
    print("   - Configure the workflow to run on Windows runners")
    print("   - Push your code to GitHub and let the workflow build it")
    print("\n3. Use a free Windows EC2 instance on AWS:")
    print("   - Set up a t2.micro Windows instance (free tier eligible)")
    print("   - Install Python and dependencies")
    print("   - Build the application on the Windows instance")
    print("\n4. Manual build with Wine (limited success):")
    print("   - Install Wine on your Mac: brew install --cask wine-stable")
    print("   - Set up Python in Wine: wine python-3.9.6-amd64.exe")
    print("   - Run PyInstaller through Wine")
    print("\nFor detailed instructions on any of these methods, refer to the documentation.")
    print("================================================================================\n")
    
    # Clean up cross-compilation files
    cleanup_cross_compile_files()
    
    return False  # Indicate build was not successful

def print_alternative_build_method():
    """
    Print alternative build method instructions for Windows on Apple Silicon
    """
    print("\n" + "="*80)
    print("ALTERNATIVE BUILD METHOD FOR WINDOWS ON APPLE SILICON")
    print("="*80)
    print("""
Since Docker-based cross-compilation for Windows on Apple Silicon can be challenging,
consider these alternative approaches:

1. Use UTM or Parallels to run a Windows VM, then build natively:
   - Install UTM (free) or Parallels (paid) on your Mac
   - Install Windows 11 ARM64 edition in the VM
   - Set up the development environment in Windows
   - Run the build script directly in Windows

2. Use a CI/CD service for cross-platform builds:
   - Set up GitHub Actions to build for Windows
   - Configure the workflow to run on Windows runners
   - Push your code to GitHub and let the workflow build it

3. Use a free Windows EC2 instance on AWS:
   - Set up a t2.micro Windows instance (free tier eligible)
   - Install Python and dependencies
   - Build the application on the Windows instance

4. Manual build without Docker:
   - Install Wine on your Mac: brew install --cask wine-stable
   - Set up Python in Wine: wine python-3.9.6-amd64.exe
   - Run PyInstaller through Wine
   
For detailed instructions on any of these methods, refer to the documentation.
""")
    print("="*80 + "\n")

def cleanup_cross_compile_files():
    """
    Clean up temporary files created for cross-compilation
    """
    print("Cleaning up cross-compilation files...")
    
    # Restore original requirements file
    if os.path.exists("requirements.txt.bak"):
        shutil.move("requirements.txt.bak", "requirements.txt")
    
    # Remove cross-compilation requirements file
    if os.path.exists("requirements.cross.txt"):
        os.remove("requirements.cross.txt")
    
    # Remove package handler script
    if os.path.exists("handle_packages.sh"):
        os.remove("handle_packages.sh")
    
    print("Cross-compilation files cleaned up")

def build_all_platforms(args):
    """
    Build portable executables for Windows and macOS
    """
    # Only build for Windows and macOS (no Linux)
    platforms = ["windows"]  # macOS builds need to be done on macOS
    architectures = ["x64"]  # Only x64 architecture
    
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
    
    # Force portable mode and zip creation
    current_args.portable = True
    current_args.zip = True
    current_args.no_zip = False
    
    # Run the main function for the current platform
    main_result = main_build(current_args)
    results[f"{current_platform}-{current_arch}"] = main_result == 0
    
    # Check if we're on Apple Silicon Mac
    is_apple_silicon = platform.system().lower() == "darwin" and platform.machine() == "arm64"
    
    # Build for Windows using Docker if we're on macOS
    if current_platform == "macos":
        for target_platform in platforms:
            for target_arch in architectures:
                # Skip the current platform (already built)
                if target_platform == current_platform and target_arch == current_arch:
                    continue
                    
                # For Apple Silicon Macs building Windows, suggest using the alternative image
                if is_apple_silicon and target_platform == "windows" and not args.alt_win_image:
                    print("\nNote: Building Windows on Apple Silicon Mac. Consider using --alt-win-image if this fails.")
                    
                print(f"\nBuilding for {target_platform}-{target_arch}...")
                
                # Create a copy of args with portable and zip flags set
                platform_args = argparse.Namespace(**vars(args))
                platform_args.portable = True
                platform_args.zip = True
                platform_args.no_zip = False
                
                result = cross_compile(target_platform, target_arch, platform_args)
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
    # If both onefile and onedir are specified, onedir takes precedence
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
    
    # Disable backup/restore to prevent preserving old artifacts
    backup_dir = None
    
    # Clean build directories if requested
    if args.clean:
        print("Cleaning build directories...")
        try:
            if os.path.exists("build"):
                shutil.rmtree("build", ignore_errors=True)
            if os.path.exists("dist"):
                # Remove the entire dist directory for a fresh build
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
    
    # Add local flatlib directory if it exists
    if os.path.exists("flatlib") and os.path.isdir("flatlib"):
        cmd.extend([
            "--add-data", f"flatlib{os.pathsep}flatlib",  # Add the local flatlib directory
        ])
        print("Added local flatlib directory to the build")
    
    # Add flatlib data files - if installed via pip, include those too for compatibility
    try:
        import flatlib
        flatlib_import_path = os.path.dirname(flatlib.__file__)
        
        # If there's no local flatlib directory, or if the imported flatlib is different from our local one, add the imported one
        if not os.path.exists("flatlib") or not os.path.isdir("flatlib") or not os.path.samefile(flatlib_import_path, os.path.join(os.getcwd(), 'flatlib')):
            cmd.extend([
                "--add-data", f"{flatlib_import_path}{os.pathsep}flatlib",
            ])
            print(f"Added imported flatlib data files from {flatlib_import_path}")
        
        # Create a runtime hook for flatlib
        hook_dir = os.path.join(os.getcwd(), "build", "hooks")
        os.makedirs(hook_dir, exist_ok=True)
        
        with open(os.path.join(hook_dir, "hook-flatlib.py"), "w") as f:
            f.write("""
# PyInstaller hook for flatlib
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('flatlib')

# Collect all data files
datas = collect_data_files('flatlib')
""")
        
        cmd.extend([
            "--additional-hooks-dir", hook_dir,
        ])
        print(f"Created runtime hook for flatlib in {hook_dir}")
    except ImportError:
        print("Warning: Could not import flatlib to add its data files")
    
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
        "--hidden-import", "flatlib.const",
        "--hidden-import", "flatlib.chart",
        "--hidden-import", "flatlib.geopos",
        "--hidden-import", "flatlib.datetime",
        "--hidden-import", "flatlib.object",
        "--hidden-import", "flatlib.aspects",
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
        
        # Create ZIP archive only if explicitly requested and not disabled
        if args.zip and not args.no_zip:
            create_zip_archive(output_name, is_macos)
        else:
            print("Skipping ZIP archive creation")
        
        return 0
    
    # Create installer for Windows using NSIS (if installed and not in portable mode)
    if is_windows and shutil.which("makensis") and not args.portable:
        create_windows_installer(output_name, VERSION, args.onefile)
    
    print(f"Build completed successfully. Output in dist/{output_name}")
    
    # After build is complete, we no longer restore backed up files
    # This was causing issues with preserving old artifacts
    return 0

if __name__ == "__main__":
    main() 