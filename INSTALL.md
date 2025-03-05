# KP Astrology Dashboard - Installation Guide

This guide explains how to install and run the KP Astrology Dashboard application on Windows and macOS.

## Prerequisites

The application requires Python 3.9 or later. The installation scripts will automatically install Python if it's not already present on your system.

## Installation Instructions

### Windows Installation

1. Download the `KPAstrologyDashboard-Windows-Installer.bat` file from the [latest release](https://github.com/cryptekbits/KPAstroDashboard/releases/latest)
2. Double-click the downloaded `.bat` file to run it
3. The installer will:
   - Download the latest application package directly from GitHub
   - Check if Python is installed (and install it if necessary)
   - Install all required packages
   - Create a desktop shortcut for easy access

### macOS Installation

#### Option 1: Using the clickable installer (Recommended)

1. Download the `KPAstrologyDashboard-macOS-Installer.command` file from the [latest release](https://github.com/cryptekbits/KPAstroDashboard/releases/latest)
2. Double-click the downloaded `.command` file to run it
   - If you get a security warning, right-click (or control+click) the file and select "Open"
3. The installer will:
   - Download the latest application package directly from GitHub
   - Check if Python is installed (and install it via Homebrew if necessary)
   - Install all required packages
   - Create a desktop shortcut for easy access

#### Option 2: Using the shell script

1. Download the `KPAstrologyDashboard-macOS-Installer.sh` file from the [latest release](https://github.com/cryptekbits/KPAstroDashboard/releases/latest)
2. Open Terminal and navigate to the directory containing the downloaded file
3. Make the script executable with the command: `chmod +x KPAstrologyDashboard-macOS-Installer.sh`
4. Run the script with: `./KPAstrologyDashboard-macOS-Installer.sh`
5. The installer will perform the same operations as the clickable installer

## Manual Installation

If you prefer to install manually or if the installation scripts don't work for you:

1. Download the source code directly from the [latest release tag](https://github.com/cryptekbits/KPAstroDashboard/archive/refs/tags/v1.1.3.zip) (replace v1.1.3 with the latest version)
   - You can also download `KPAstrologyDashboard-[version].zip` from the [releases page](https://github.com/cryptekbits/KPAstroDashboard/releases/latest) if available
2. Extract the ZIP file to a location of your choice
3. Ensure Python 3.9 or later is installed on your system
4. Open a terminal/command prompt and navigate to the extracted directory
5. Install the required packages with: `pip install -r requirements.txt`
6. Run the application with: `python main.py`

## Troubleshooting

### Common Issues

1. **Download Failure**
   - Ensure you have a stable internet connection
   - Try downloading the files directly from the GitHub releases page
   - If the installer can't download the source code, you can manually download it from the GitHub tags page

2. **Python Installation Issues**
   - Windows: Try installing Python manually from [python.org](https://www.python.org/downloads/)
   - macOS: Ensure Homebrew is installed or install Python manually from [python.org](https://www.python.org/downloads/)

3. **Package Installation Errors**
   - Ensure you're connected to the internet
   - Try running the installation with administrator privileges
   - If specific packages fail, try installing them manually with `pip install [package-name]`

4. **Application Won't Start**
   - Check if Python is in your system PATH
   - Ensure all dependencies are installed
   - Try running the application from the command line to see detailed error messages

### Getting Help

If you continue to experience issues, please:
1. Check the [GitHub Issues](https://github.com/cryptekbits/KPAstroDashboard/issues) for known problems and solutions
2. Create a new issue with details about your problem and system configuration

For additional help, please open an issue on GitHub. 