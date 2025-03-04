# KP Astrology Dashboard - Installation Guide

This guide explains how to install and run the KP Astrology Dashboard application on Windows and macOS.

## Prerequisites

The application requires Python 3.9 or later. The installation scripts will automatically install Python if it's not already present on your system.

## Windows Installation

1. Download the latest Windows installer (`KPAstrologyDashboard-Windows-Installer.bat`) from the [Releases page](https://github.com/yourusername/kpDashboard/releases).
2. Double-click the downloaded installer script.
3. The script will:
   - Download the latest application package
   - Extract it to a folder in your user directory
   - Check if Python is installed, and install it if needed
   - Install the required Python packages
   - Create a shortcut on your desktop to run the application

4. Once installation is complete, you can run the application by double-clicking the shortcut on your desktop.

## macOS Installation

1. Download the latest macOS installer (`KPAstrologyDashboard-macOS-Installer.sh`) from the [Releases page](https://github.com/yourusername/kpDashboard/releases).
2. Open Terminal and navigate to the folder containing the downloaded installer:
   ```
   cd ~/Downloads
   ```
3. Make the installer executable:
   ```
   chmod +x KPAstrologyDashboard-macOS-Installer.sh
   ```
4. Run the installer:
   ```
   ./KPAstrologyDashboard-macOS-Installer.sh
   ```
5. The script will:
   - Download the latest application package
   - Extract it to a folder in your home directory
   - Check if Python is installed, and install it if needed (using Homebrew)
   - Install the required Python packages
   - Create a shortcut on your desktop to run the application

6. Once installation is complete, you can run the application by double-clicking the shortcut on your desktop.

## Manual Installation

If you prefer to install manually or if the installation scripts don't work for you:

1. Download the source code zip file from the [Releases page](https://github.com/yourusername/kpDashboard/releases)
2. Extract the zip file to a location on your computer
3. Install Python 3.9 or later from [python.org](https://www.python.org/downloads/)
4. Open a terminal or command prompt
5. Navigate to the extracted application folder
6. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
7. Run the application:
   ```
   python main.py
   ```

## Troubleshooting

If you encounter any issues during installation:

1. **Download Fails**: 
   - Check your internet connection
   - Try downloading the installer again
   - You can alternatively download the source code zip file directly

2. **Python Installation Fails**: 
   - Install Python manually from [python.org](https://www.python.org/downloads/)
   - On macOS, you can also use Homebrew: `brew install python@3.9`

3. **Package Installation Fails**: 
   - Try installing packages manually:
     ```
     pip install pandas geopy requests pytz polars-lts-cpu PyQt5 tabulate psutil ephem python-dateutil numpy packaging
     ```

4. **Application Won't Start**: 
   - Make sure all dependencies are installed correctly
   - Check the logs folder for error messages

For additional help, please open an issue on GitHub. 