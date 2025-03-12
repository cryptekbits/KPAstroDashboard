"""
KP Astrology Dashboard - Main Application

This is the main entry point for the KP Astrology Dashboard application.
It initializes logging and starts the PyQt5 application.
"""

import sys
import os
import warnings
import logging
import shutil
import urllib.request
import zipfile
import platform

# Set environment variable to skip polars CPU check to avoid compatibility issues
os.environ["POLARS_SKIP_CPU_CHECK"] = "1"

from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# Filter out specific warnings
warnings.filterwarnings("ignore", message=".*MapWithoutReturnDtypeWarning.*")
warnings.filterwarnings("ignore", message=".*Calling `map_elements` without specifying `return_dtype`.*")
# Also ignore polars CPU feature warnings
warnings.filterwarnings("ignore", message=".*Missing required CPU features.*")

# Import after warnings are filtered
from ui import KPAstrologyApp, setup_logging
from ui.utils.updater import check_for_updates_on_startup

# Set up Swiss Ephemeris path
import flatlib
from flatlib.ephem import setPath

def get_application_path():
    """
    Get the application path, handling both normal execution and PyInstaller bundled execution.
    
    Returns:
        str: The absolute path to the application directory
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running in normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

def ensure_ephemeris_files_exist():
    """Ensure Swiss Ephemeris files exist and set the path only once at startup."""
    app_dir = get_application_path()
    
    # Use only the built-in path for swefiles
    swefiles_path = os.path.join(app_dir, 'flatlib', 'resources', 'swefiles')
    
    # Check if the directory exists and contains .se1 files
    if not os.path.exists(swefiles_path):
        logging.error(f"SwissEph directory not found: {swefiles_path}")
        QMessageBox.critical(None, "Missing Ephemeris Files", 
                           f"The Swiss Ephemeris files directory was not found at:\n{swefiles_path}\n\n"
                           f"Please ensure the application is installed correctly.")
        return False
    
    # Check if the directory contains the required files
    required_files = ["seas_18.se1", "sepl_18.se1", "semo_18.se1", "fixstars.cat"]
    missing_files = [f for f in required_files if not os.path.isfile(os.path.join(swefiles_path, f))]
    
    if missing_files:
        logging.error(f"Missing SwissEph files: {', '.join(missing_files)}")
        QMessageBox.critical(None, "Missing Ephemeris Files", 
                           f"The following required Swiss Ephemeris files are missing:\n{', '.join(missing_files)}\n\n"
                           f"Please download these files and place them in:\n{swefiles_path}")
        return False
    
    # On Windows, normalize the path to use forward slashes
    normalized_path = swefiles_path
    if platform.system() == "Windows":
        normalized_path = swefiles_path.replace('\\', '/')
    
    # Set the path once
    logging.info(f"Setting SwissEph path to: {normalized_path}")
    setPath(normalized_path)
    
    # Test if the path works by making a simple calculation
    try:
        import swisseph
        # Try a simple calculation to verify the path works
        test_jd = 2459000.5  # A random Julian date
        test_result = swisseph.calc_ut(test_jd, 0, 2)  # Calculate Sun position with SEFLG_SWIEPH flag
        logging.info(f"SwissEph test calculation successful: {test_result}")
        return True
    except Exception as e:
        logging.error(f"SwissEph test calculation failed: {e}")
        
        # Special handling for Windows if the test fails
        if platform.system() == "Windows":
            # Inform the user about the issue and possible solutions
            QMessageBox.critical(None, "SwissEph Configuration Error", 
                               f"There was an error configuring the Swiss Ephemeris library:\n\n{str(e)}\n\n"
                               f"This is a known issue with the SwissEph library on Windows.\n\n"
                               f"Please try one of the following solutions:\n"
                               f"1. Reinstall the application\n"
                               f"2. Manually copy the files from {swefiles_path} to C:\\sweph\\ephe\\\n"
                               f"3. Contact support for assistance")
        else:
            # Generic error for other platforms
            QMessageBox.critical(None, "SwissEph Configuration Error", 
                               f"There was an error configuring the Swiss Ephemeris library:\n\n{str(e)}")
        return False

# Ensure Swiss Ephemeris files exist
ensure_ephemeris_files_exist()

def verify_swisseph_functionality(parent_window=None):
    """
    Verify Swiss Ephemeris functionality in the background.
    If it fails, check if files exist and provide appropriate guidance.
    """
    app_dir = get_application_path()
    swefiles_path = os.path.join(app_dir, 'flatlib', 'resources', 'swefiles')
    system_swefiles_path = "C:\\sweph\\ephe" if platform.system() == "Windows" else "/usr/local/share/sweph/ephe"
    
    # Required files
    required_files = ["seas_18.se1", "sepl_18.se1", "semo_18.se1", "fixstars.cat"]
    
    try:
        # Try to use the Swiss Ephemeris functionality
        import swisseph
        from flatlib.ephem import swe
        
        # Test with a simple calculation using the sweObject function
        test_jd = 2459000.5  # A random Julian date
        test_obj = swe.sweObject('Sun', test_jd)
        logging.info(f"SwissEph functionality test successful: {test_obj}")
        return True
    except Exception as e:
        logging.error(f"SwissEph functionality test failed: {e}")
        
        # Check if files exist in the application directory
        app_files_exist = all(os.path.isfile(os.path.join(swefiles_path, f)) for f in required_files)
        
        # Check if files exist in the system-wide directory
        system_dir_exists = os.path.exists(system_swefiles_path)
        system_files_exist = False
        if system_dir_exists:
            system_files_exist = all(os.path.isfile(os.path.join(system_swefiles_path, f)) for f in required_files)
        
        # Only show message if parent_window is provided (UI is running)
        if parent_window:
            if app_files_exist and not system_files_exist:
                # Files exist in app directory but not in system directory
                response = QMessageBox.warning(parent_window, "Swiss Ephemeris Configuration Issue", 
                                  f"The Swiss Ephemeris files are present in the application directory but the library cannot access them.\n\n"
                                  f"Would you like to copy these files to the system-wide location?\n"
                                  f"This may require administrator privileges.",
                                  QMessageBox.Yes | QMessageBox.No)
                
                # If user agrees, try to copy files to system directory
                if response == QMessageBox.Yes:
                    try:
                        # Create system directory if it doesn't exist
                        if not os.path.exists(system_swefiles_path):
                            if platform.system() == "Windows":
                                # Use PowerShell to run as admin
                                import subprocess
                                cmd = f'powershell -Command "Start-Process -FilePath \'cmd.exe\' -ArgumentList \'/c mkdir \"{system_swefiles_path}\"\' -Verb RunAs -Wait"'
                                subprocess.run(cmd, shell=True)
                            else:
                                # Use sudo on macOS/Linux
                                import subprocess
                                cmd = f'sudo mkdir -p "{system_swefiles_path}"'
                                subprocess.run(cmd, shell=True)
                        
                        # Copy files to system directory
                        for file in required_files:
                            src = os.path.join(swefiles_path, file)
                            if os.path.exists(src):
                                if platform.system() == "Windows":
                                    cmd = f'powershell -Command "Start-Process -FilePath \'cmd.exe\' -ArgumentList \'/c copy \"{src}\" \"{os.path.join(system_swefiles_path, file)}\"\' -Verb RunAs -Wait"'
                                    subprocess.run(cmd, shell=True)
                                else:
                                    cmd = f'sudo cp "{src}" "{os.path.join(system_swefiles_path, file)}"'
                                    subprocess.run(cmd, shell=True)
                        
                        QMessageBox.information(parent_window, "Files Copied", 
                                             "Swiss Ephemeris files have been copied to the system-wide location.\n"
                                             "Please restart the application.")
                    except Exception as copy_error:
                        logging.error(f"Failed to copy files: {copy_error}")
                        QMessageBox.critical(parent_window, "Copy Failed", 
                                          f"Failed to copy Swiss Ephemeris files to the system-wide location.\n\n"
                                          f"Error: {str(copy_error)}\n\n"
                                          f"Please contact your system administrator for assistance.")
            elif not app_files_exist:
                # Files don't exist in app directory
                QMessageBox.critical(parent_window, "Missing Swiss Ephemeris Files", 
                                   f"The required Swiss Ephemeris files are missing from the application directory.\n\n"
                                   f"Please ensure the application package is complete or contact support for assistance.")
            else:
                # Files exist in both places but there's still an error
                QMessageBox.critical(parent_window, "Swiss Ephemeris Error", 
                                   f"There was an error using the Swiss Ephemeris library despite the files being present.\n\n"
                                   f"Error: {str(e)}\n\n"
                                   f"Please contact your system administrator for assistance.")
        
        return False

def exception_hook(exctype, value, traceback):
    """
    Global exception handler to show error messages in a dialog
    instead of crashing silently.
    """
    logging.error("Uncaught exception", exc_info=(exctype, value, traceback))
    error_msg = f"{exctype.__name__}: {value}"
    QMessageBox.critical(None, "Error", 
                        f"An unexpected error occurred:\n\n{error_msg}\n\nSee log for details.")
    sys.__excepthook__(exctype, value, traceback)


def main():
    """Main entry point for the application"""
    # Set up logging
    setup_logging()
    
    # Set up exception handling
    sys.excepthook = exception_hook
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("KP Astrology Dashboard")
    
    # Set application icon
    icon_path = os.path.join(get_application_path(), 'resources', 'favicon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create splash screen
    splash_path = os.path.join(get_application_path(), 'resources', 'splash.png')
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    else:
        splash = None
    
    # Create and show main window
    try:
        window = KPAstrologyApp()
        window.show()
        
        # Check for updates after a short delay to ensure UI is responsive
        QTimer.singleShot(2000, lambda: check_for_updates_on_startup(window))
        
        # Verify Swiss Ephemeris functionality in the background
        QTimer.singleShot(3000, lambda: verify_swisseph_functionality(window))
        
        # Start the application event loop
        return app.exec_()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "Startup Error", 
                            f"Failed to start application:\n\n{str(e)}\n\nSee log for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())