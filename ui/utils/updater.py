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
import glob
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
            
            # Create download URL using the tag format instead of asset download URL
            # This ensures it will download from the GitHub tag archive directly
            download_url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/archive/refs/tags/v{latest_version}.zip"
            
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
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    update_applied = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
        self.update_zip = None
    
    def download_update(self, download_url):
        """Download the update from the specified URL"""
        try:
            self.logger.info(f"Downloading update from: {download_url}")
            
            # Create a temporary file to download to
            self.update_zip = os.path.join(self.temp_dir, "update.zip")
            
            # Download the file with progress tracking
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress tracking
            downloaded_size = 0
            with open(self.update_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # Update progress
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.logger.info("Download complete.")
            
            # Extract to separate temporary directory to handle the nested folder structure
            extract_dir = os.path.join(self.temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extract the ZIP file
            import zipfile
            with zipfile.ZipFile(self.update_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # The extracted content will be in a nested directory with the format REPO_NAME-VERSION
            # Find the nested directory
            nested_dirs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
            if nested_dirs:
                # Use the first directory found (should be the only one)
                nested_dir = os.path.join(extract_dir, nested_dirs[0])
                # Use this as the update source directory
                self.download_complete.emit(nested_dir)
            else:
                self.error_occurred.emit("No valid update directory found in the downloaded package")
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")
            self.error_occurred.emit(f"Error downloading update: {str(e)}")
    
    def apply_update(self, download_path):
        """
        Apply the downloaded update.
        This will extract the update and create a script to replace the application files
        while preserving user preferences.
        """
        try:
            self.logger.info(f"Applying update from: {download_path}")
            
            # Create updater script based on platform
            if platform.system() == "Windows":
                self._create_windows_updater(download_path)
            else:  # macOS or Linux
                self._create_unix_updater(download_path)
                
            self.update_applied.emit()
            
        except Exception as e:
            self.logger.error(f"Error applying update: {str(e)}")
            self.error_occurred.emit(f"Error applying update: {str(e)}")
    
    def _merge_config_json(self, current_config_path, new_config_path, output_path):
        """
        Merge the current config.json with the new one, preserving user preferences
        and adding any new fields.
        
        Args:
            current_config_path: Path to the current config.json
            new_config_path: Path to the new config.json from the update
            output_path: Path to save the merged config.json
        """
        # Load current config
        with open(current_config_path, 'r') as f:
            current_config = json.load(f)
        
        # Load new config
        with open(new_config_path, 'r') as f:
            new_config = json.load(f)
        
        # Function to recursively merge dictionaries
        def merge_dicts(current, new):
            merged = current.copy()
            for key, value in new.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    merged[key] = merge_dicts(merged[key], value)
                elif key not in merged:
                    # Add new fields from the new config
                    merged[key] = value
                # Existing fields keep their values
            return merged
        
        # Merge configs
        merged_config = merge_dicts(current_config, new_config)
        
        # Save merged config
        with open(output_path, 'w') as f:
            json.dump(merged_config, f, indent=4)
    
    def _create_windows_updater(self, download_path):
        """Create a batch script to update the application on Windows"""
        app_path = get_application_path()
        app_dir = os.path.dirname(app_path) if is_frozen() else os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        temp_dir = tempfile.gettempdir()
        extract_dir = os.path.join(temp_dir, "kp_dashboard_update")
        
        # Get the executable name if running as frozen app
        if is_frozen():
            exe_name = os.path.basename(app_path)
            python_cmd = "python"
        else:
            exe_name = "main.py"
        
        # Create batch file for the update process
        updater_path = os.path.join(temp_dir, "kp_dashboard_updater.bat")
        
        with open(updater_path, 'w') as file:
            file.write(f"""@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak > nul

echo Extracting update...
if exist "{extract_dir}" rmdir /S /Q "{extract_dir}"
powershell -command "Expand-Archive -Path '{download_path}' -DestinationPath '{extract_dir}' -Force"

echo Backing up user config...
copy "{app_dir}\\config.json" "{temp_dir}\\config_backup.json"

echo Merging configurations...
powershell -Command "
try {{
    # Load current config
    $currentConfig = Get-Content '{app_dir}\\config.json' | ConvertFrom-Json
    
    # Load new config
    $newConfig = Get-Content '{extract_dir}\\config.json' | ConvertFrom-Json
    
    # Create a function to merge objects recursively
    function Merge-Objects($current, $new) {{
        $merged = $current.PSObject.Copy()
        foreach ($property in $new.PSObject.Properties) {{
            $propertyName = $property.Name
            if (-not ($merged.PSObject.Properties.Name -contains $propertyName)) {{
                # Add new fields from the new config
                $merged | Add-Member -MemberType NoteProperty -Name $propertyName -Value $property.Value
            }} elseif ($merged.$propertyName -is [PSCustomObject] -and $property.Value -is [PSCustomObject]) {{
                # Recursively merge nested objects
                $merged.$propertyName = Merge-Objects $merged.$propertyName $property.Value
            }}
            # Keep existing values for existing fields
        }}
        return $merged
    }}
    
    # Merge the configs
    $mergedConfig = Merge-Objects $currentConfig $newConfig
    
    # Save merged config to the backup location
    $mergedConfig | ConvertTo-Json -Depth 100 | Set-Content '{temp_dir}\\config_merged.json'
    Write-Host 'Config files merged successfully'
}} catch {{
    Write-Host 'Error merging config files: $_'
    Write-Host 'Keeping original config file'
    Copy-Item '{app_dir}\\config.json' '{temp_dir}\\config_merged.json'
}}"

echo Checking for new requirements...
if exist "{extract_dir}\\requirements.txt" (
    powershell -Command "(Get-Content '{extract_dir}\\requirements.txt') -replace '; platform_system==\"Windows\"', '' -replace '; platform_system==\"Darwin\"', '' | Set-Content '{extract_dir}\\requirements_clean.txt'"
    
    echo Installing any new requirements...
    cd /d "{extract_dir}"
    python -m pip install -r requirements_clean.txt --upgrade
)

echo Updating application files...
:: First, back up the entire app directory
xcopy /E /I /Y "{app_dir}" "{temp_dir}\\kp_dashboard_backup"

:: Now copy the new files
xcopy /E /I /Y "{extract_dir}\\*" "{app_dir}"

:: Restore the merged config
copy "{temp_dir}\\config_merged.json" "{app_dir}\\config.json"

echo Cleaning up...
rmdir /S /Q "{extract_dir}"
del "{download_path}"

echo Starting application...
cd "{app_dir}"
start "" "{os.path.join(app_dir, exe_name)}"

echo Update completed successfully!
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
        
        # Create shell script for the update process
        updater_path = os.path.join(temp_dir, "kp_dashboard_updater.sh")
        
        with open(updater_path, 'w') as file:
            file.write(f"""#!/bin/bash
echo "Waiting for application to close..."
sleep 2

echo "Extracting update..."
rm -rf "{extract_dir}"
mkdir -p "{extract_dir}"
unzip -o "{download_path}" -d "{extract_dir}"

echo "Backing up user config..."
cp "{app_dir}/config.json" "{temp_dir}/config_backup.json"

echo "Merging configurations..."
# Function to merge JSON objects
merge_configs() {{
    python3 -c "
import json
import sys

def merge_dicts(current, new):
    merged = current.copy()
    for key, value in new.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            merged[key] = merge_dicts(merged[key], value)
        elif key not in merged:
            # Add new fields from the new config
            merged[key] = value
    return merged

try:
    # Load current config
    with open('{app_dir}/config.json', 'r') as f:
        current_config = json.load(f)
    
    # Load new config
    with open('{extract_dir}/config.json', 'r') as f:
        new_config = json.load(f)
    
    # Merge configs
    merged_config = merge_dicts(current_config, new_config)
    
    # Save merged config
    with open('{temp_dir}/config_merged.json', 'w') as f:
        json.dump(merged_config, f, indent=4)
    
    print('Config files merged successfully')
except Exception as e:
    print(f'Error merging config files: {{e}}')
    print('Keeping original config file')
    import shutil
    shutil.copy('{app_dir}/config.json', '{temp_dir}/config_merged.json')
"
}}

merge_configs

echo "Checking for new requirements..."
if [ -f "{extract_dir}/requirements.txt" ]; then
    # Remove platform-specific markers
    cat "{extract_dir}/requirements.txt" | sed 's/; platform_system=="Windows"//g' | sed 's/; platform_system=="Darwin"//g' > "{extract_dir}/requirements_clean.txt"
    
    echo "Installing any new requirements..."
    cd "{extract_dir}"
    python3 -m pip install -r requirements_clean.txt --upgrade
fi

echo "Updating application files..."
# First, back up the entire app directory
mkdir -p "{temp_dir}/kp_dashboard_backup"
cp -R "{app_dir}/"* "{temp_dir}/kp_dashboard_backup/"

# Now copy the new files
cp -R "{extract_dir}/"* "{app_dir}/"

# Restore the merged config
cp "{temp_dir}/config_merged.json" "{app_dir}/config.json"

echo "Cleaning up..."
rm -rf "{extract_dir}"
rm "{download_path}"

echo "Starting application..."
{start_cmd} &

echo "Update completed successfully!"
rm "$0"
""")
        
        # Make the script executable
        os.chmod(updater_path, 0o755)
        
        # Run the updater
        subprocess.Popen(["/bin/bash", updater_path])
        
        # Exit the application
        sys.exit(0)


def check_for_updates_on_startup(window):
    """Check for updates when the application starts"""
    # Check for updates in a separate thread to avoid blocking the main UI
    update_checker = UpdateChecker()
    update_thread = QThread()
    
    # Move the update checker to the thread
    update_checker.moveToThread(update_thread)
    
    # Keep references to prevent garbage collection
    _update_threads.append((update_thread, update_checker))
    
    # Connect signals
    update_thread.started.connect(update_checker.check_for_updates)
    update_checker.update_available.connect(lambda version, url: show_update_dialog(window, version, url))
    
    # Clean up when done
    update_checker.update_available.connect(update_thread.quit)
    update_checker.update_not_available.connect(update_thread.quit)
    update_checker.error_occurred.connect(update_thread.quit)
    
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
    msg_box.setInformativeText("Would you like to download and install it now? Your preferences will be preserved.")
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
    downloader.progress_updated.connect(progress.setValue)
    
    downloader.download_complete.connect(lambda path: handle_download_complete(parent_window, path, downloader, progress))
    downloader.error_occurred.connect(lambda error: handle_download_error(parent_window, error, progress))
    
    downloader.update_applied.connect(progress.close)
    downloader.error_occurred.connect(lambda error: handle_update_error(parent_window, error, progress))
    
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
    msg_box.setInformativeText("The application will close and restart with the new version. Your preferences will be preserved. Continue?")
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
    msg_box.setText("Failed to download the update.")
    msg_box.setInformativeText(error)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.exec_()


def handle_update_error(parent_window, error, progress):
    """Handle update installation error"""
    progress.close()
    
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("Update Error")
    msg_box.setText("Failed to install the update.")
    msg_box.setInformativeText(error)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.exec_() 