"""
App Update Module

This module handles checking for updates, downloading new versions,
and applying updates to the application.
"""

import os
import sys
import json
import logging
import tempfile
import subprocess
import platform
import shutil
from pathlib import Path
import requests
from packaging import version
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox

# Import version information
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from version import VERSION, GITHUB_REPO_OWNER, GITHUB_REPO_NAME

# GitHub API URL
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

# Current version
CURRENT_VERSION = VERSION

# Keep references to threads to prevent premature garbage collection
_update_threads = []

def is_frozen():
    """Check if the application is running as a packaged executable"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_application_path():
    """Get the path to the application executable or script"""
    if is_frozen():
        # Running as packaged executable
        if platform.system() == "Windows":
            return os.path.abspath(sys.executable)
        elif platform.system() == "Darwin":
            # For macOS app bundles, we need to go up to the .app directory
            app_path = os.path.abspath(sys.executable)
            if ".app/Contents/MacOS/" in app_path:
                return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(app_path))))
            return app_path
        else:
            return os.path.abspath(sys.executable)
    else:
        # Running as script
        return os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class UpdateChecker(QObject):
    """Class to check for updates from GitHub releases"""
    update_available = pyqtSignal(str, str)  # version, download_url
    update_not_available = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def check_for_updates(self):
        """Check GitHub for newer releases"""
        try:
            self.logger.info(f"Checking for updates. Current version: {CURRENT_VERSION}")
            
            # Get the latest release information from GitHub
            response = requests.get(GITHUB_API_URL, timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            download_url = None
            
            # Find the appropriate asset to download based on platform
            for asset in latest_release['assets']:
                # For simplicity, we're assuming a zip file for all platforms
                # In a real implementation, you might want to check for platform-specific assets
                if asset['name'].endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break
            
            if download_url is None:
                self.error_occurred.emit("No suitable download found in the latest release")
                return
                
            # Compare versions
            if self._is_newer_version(latest_version, CURRENT_VERSION):
                self.logger.info(f"New version available: {latest_version}")
                self.update_available.emit(latest_version, download_url)
            else:
                self.logger.info("No new version available")
                self.update_not_available.emit()
                
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            self.error_occurred.emit(f"Error checking for updates: {str(e)}")
    
    def _is_newer_version(self, latest_version, current_version):
        """
        Compare version strings to determine if latest is newer than current.
        Uses packaging.version for robust comparison.
        """
        try:
            return version.parse(latest_version) > version.parse(current_version)
        except Exception as e:
            self.logger.error(f"Error comparing versions: {str(e)}")
            # Fall back to simple string comparison if packaging.version fails
            latest_parts = [int(x) for x in latest_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            for i in range(max(len(latest_parts), len(current_parts))):
                latest_part = latest_parts[i] if i < len(latest_parts) else 0
                current_part = current_parts[i] if i < len(current_parts) else 0
                
                if latest_part > current_part:
                    return True
                elif latest_part < current_part:
                    return False
                    
            return False  # Versions are equal


class UpdateDownloader(QObject):
    """Class to download and apply updates"""
    download_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)  # path to downloaded file
    download_error = pyqtSignal(str)
    update_complete = pyqtSignal()
    update_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def download_update(self, download_url):
        """Download the update file"""
        try:
            self.logger.info(f"Downloading update from: {download_url}")
            
            # Create a temporary file to download to
            temp_dir = tempfile.gettempdir()
            download_path = os.path.join(temp_dir, "kp_dashboard_update.zip")
            
            # Download the file with progress reporting
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            downloaded = 0
            
            with open(download_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    downloaded += len(data)
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        self.download_progress.emit(progress)
            
            self.logger.info(f"Download complete: {download_path}")
            self.download_complete.emit(download_path)
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")
            self.download_error.emit(f"Error downloading update: {str(e)}")
    
    def apply_update(self, download_path):
        """
        Apply the downloaded update.
        This will extract the update and create a script to replace the application files.
        """
        try:
            self.logger.info(f"Applying update from: {download_path}")
            
            # Create updater script based on platform
            if platform.system() == "Windows":
                self._create_windows_updater(download_path)
            else:  # macOS or Linux
                self._create_unix_updater(download_path)
                
            self.update_complete.emit()
            
        except Exception as e:
            self.logger.error(f"Error applying update: {str(e)}")
            self.update_error.emit(f"Error applying update: {str(e)}")
    
    def _create_windows_updater(self, download_path):
        """Create a batch script to update the application on Windows"""
        app_path = get_application_path()
        app_dir = os.path.dirname(app_path) if is_frozen() else os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, "kp_dashboard_update")
        
        # Get the executable name if running as frozen app
        if is_frozen():
            exe_name = os.path.basename(app_path)
        else:
            exe_name = "main.py"
        
        # Create batch file to:
        # 1. Wait for the application to exit
        # 2. Extract the update
        # 3. Copy the files to the application directory
        # 4. Restart the application
        
        updater_path = os.path.join(temp_dir, "kp_dashboard_updater.bat")
        
        with open(updater_path, 'w') as file:
            file.write(f"""@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak > nul

echo Extracting update...
powershell -command "Expand-Archive -Path '{download_path}' -DestinationPath '{extract_dir}' -Force"

echo Updating application...
xcopy /E /I /Y "{extract_dir}\\*" "{app_dir}"

echo Cleaning up...
rmdir /S /Q "{extract_dir}"
del "{download_path}"

echo Starting application...
cd "{app_dir}"
start "" "{os.path.join(app_dir, exe_name)}"

del "%~f0"
""")
        
        # Run the updater
        subprocess.Popen(["cmd", "/c", updater_path], creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Exit the application
        sys.exit(0)
    
    def _create_unix_updater(self, download_path):
        """Create a shell script to update the application on macOS/Linux"""
        app_path = get_application_path()
        app_dir = os.path.dirname(app_path) if is_frozen() else os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, "kp_dashboard_update")
        
        # Get the executable name or command to start the app
        if is_frozen():
            if platform.system() == "Darwin" and ".app" in app_path:
                # For macOS app bundles
                start_cmd = f"open \"{app_path}\""
            else:
                # For Linux or macOS command line executable
                start_cmd = f"\"{app_path}\""
        else:
            # For running as a script
            start_cmd = f"cd \"{app_dir}\" && python3 main.py"
        
        # Create shell script to:
        # 1. Wait for the application to exit
        # 2. Extract the update
        # 3. Copy the files to the application directory
        # 4. Restart the application
        
        updater_path = os.path.join(temp_dir, "kp_dashboard_updater.sh")
        
        with open(updater_path, 'w') as file:
            file.write(f"""#!/bin/bash
echo "Waiting for application to close..."
sleep 2

echo "Extracting update..."
mkdir -p "{extract_dir}"
unzip -o "{download_path}" -d "{extract_dir}"

echo "Updating application..."
cp -R "{extract_dir}/"* "{app_dir}/"

echo "Cleaning up..."
rm -rf "{extract_dir}"
rm "{download_path}"

echo "Starting application..."
{start_cmd} &

rm "$0"
""")
        
        # Make the script executable
        os.chmod(updater_path, 0o755)
        
        # Run the updater
        subprocess.Popen(["/bin/bash", updater_path])
        
        # Exit the application
        sys.exit(0)


def check_for_updates_on_startup(parent_window):
    """
    Function to check for updates on application startup.
    Shows a dialog if an update is available.
    
    Args:
        parent_window: The main application window
    """
    update_thread = QThread()
    update_checker = UpdateChecker()
    update_checker.moveToThread(update_thread)
    
    # Connect signals
    update_thread.started.connect(update_checker.check_for_updates)
    
    update_checker.update_available.connect(lambda version, url: show_update_dialog(parent_window, version, url))
    update_checker.error_occurred.connect(lambda error: logging.error(f"Update check error: {error}"))
    
    # Clean up when done
    update_checker.update_available.connect(update_thread.quit)
    update_checker.update_not_available.connect(update_thread.quit)
    update_checker.error_occurred.connect(update_thread.quit)
    
    # Make sure the thread and checker are not garbage collected
    _update_threads.append((update_thread, update_checker))
    
    # Connect thread finished to cleanup
    update_thread.finished.connect(lambda: _cleanup_thread(update_thread, update_checker))
    
    # Start the thread
    update_thread.start()


def _cleanup_thread(thread, obj):
    """Clean up thread and object references when thread is finished"""
    # Remove from the global list to allow garbage collection
    for i, (t, o) in enumerate(_update_threads):
        if t == thread and o == obj:
            _update_threads.pop(i)
            break


def show_update_dialog(parent_window, version, download_url):
    """
    Show a dialog asking the user if they want to update.
    
    Args:
        parent_window: The main application window
        version: The new version available
        download_url: URL to download the update from
    """
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("Update Available")
    msg_box.setText(f"A new version ({version}) of KP Dashboard is available.")
    msg_box.setInformativeText("Would you like to download and install it now?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    
    if msg_box.exec_() == QMessageBox.Yes:
        download_and_install_update(parent_window, download_url)


def download_and_install_update(parent_window, download_url):
    """
    Download and install the update.
    
    Args:
        parent_window: The main application window
        download_url: URL to download the update from
    """
    from PyQt5.QtWidgets import QProgressDialog
    
    # Create progress dialog
    progress = QProgressDialog("Downloading update...", "Cancel", 0, 100, parent_window)
    progress.setWindowTitle("Downloading Update")
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    
    # Create downloader in a separate thread
    download_thread = QThread()
    downloader = UpdateDownloader()
    downloader.moveToThread(download_thread)
    
    # Keep references to prevent garbage collection
    _update_threads.append((download_thread, downloader))
    
    # Connect signals
    progress.canceled.connect(download_thread.quit)
    
    download_thread.started.connect(lambda: downloader.download_update(download_url))
    downloader.download_progress.connect(progress.setValue)
    
    downloader.download_complete.connect(lambda path: handle_download_complete(parent_window, path, downloader, progress))
    downloader.download_error.connect(lambda error: handle_download_error(parent_window, error, progress))
    
    downloader.update_complete.connect(progress.close)
    downloader.update_error.connect(lambda error: handle_update_error(parent_window, error, progress))
    
    # Clean up when done
    download_thread.finished.connect(lambda: _cleanup_thread(download_thread, downloader))
    
    # Start the thread
    download_thread.start()
    progress.show()


def handle_download_complete(parent_window, download_path, downloader, progress):
    """Handle completion of download"""
    progress.setLabelText("Installing update...")
    progress.setValue(100)
    
    # Show a message to the user
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("Update Ready")
    msg_box.setText("The update has been downloaded and is ready to install.")
    msg_box.setInformativeText("The application will close and restart with the new version. Continue?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    
    if msg_box.exec_() == QMessageBox.Yes:
        downloader.apply_update(download_path)
    else:
        progress.close()


def handle_download_error(parent_window, error, progress):
    """Handle download error"""
    progress.close()
    
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("Download Error")
    msg_box.setText("An error occurred while downloading the update.")
    msg_box.setInformativeText(error)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.exec_()


def handle_update_error(parent_window, error, progress):
    """Handle update error"""
    progress.close()
    
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("Update Error")
    msg_box.setText("An error occurred while installing the update.")
    msg_box.setInformativeText(error)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.exec_() 