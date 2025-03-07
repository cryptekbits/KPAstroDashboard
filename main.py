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

def ensure_ephemeris_files_exist():
    """Ensure Swiss Ephemeris files exist and set the path only once at startup."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
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
    """Main application entry point"""
    # Set up logging
    setup_logging()
    
    # Set up global exception handler
    sys.excepthook = exception_hook
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'favicon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    try:
        window = KPAstrologyApp()
        window.show()
        
        # Check for updates after a short delay to ensure UI is responsive
        QTimer.singleShot(2000, lambda: check_for_updates_on_startup(window))
        
        # Start the application event loop
        return app.exec_()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "Startup Error", 
                            f"Failed to start application:\n\n{str(e)}\n\nSee log for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())