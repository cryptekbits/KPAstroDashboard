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
    """Ensure Swiss Ephemeris files exist, download them if needed."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    swefiles_paths = [
        os.path.join(app_dir, 'flatlib', 'resources', 'swefiles'),
        os.path.join(app_dir, 'resources', 'swefiles'),
        os.path.join(app_dir, 'swefiles'),
    ]
    
    # First try to set the path to an existing directory with .se1 files
    for path in swefiles_paths:
        if os.path.exists(path) and any(f.endswith('.se1') for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))):
            setPath(path)
            logging.info(f"Using Swiss Ephemeris files from: {path}")
            return True
    
    # If no files found, create a message box to inform the user
    logging.warning("Swiss Ephemeris files not found. Will prompt user to download.")
    
    # Create the target directory if it doesn't exist
    target_dir = swefiles_paths[0]  # Use the first path as the target
    os.makedirs(target_dir, exist_ok=True)
    
    # Create a message box asking if the user wants to download the files
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("Missing Ephemeris Files")
    msg_box.setText("The Swiss Ephemeris files required for astrological calculations are missing.")
    msg_box.setInformativeText("Would you like to download the necessary files (about 5MB)?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    
    if msg_box.exec_() == QMessageBox.Yes:
        try:
            # Create a progress dialog
            progress = QMessageBox()
            progress.setWindowTitle("Downloading Files")
            progress.setText("Downloading Swiss Ephemeris files...\nThis may take a few moments.")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()
            QApplication.processEvents()
            
            # Files needed for modern astrology (1800-2400 CE)
            required_files = [
                "seas_18.se1",  # Main asteroid file for 1800-2399 CE
                "sepl_18.se1",  # Planetary file for 1800-2399 CE
                "semo_18.se1",  # Moon file for 1800-2399 CE
                "fixstars.cat"  # Fixed stars
            ]
            
            # Base URL for Swiss Ephemeris files - use the official GitHub repo
            base_url = "https://github.com/aloistr/swisseph/raw/master/ephe/"
            
            # Download each file individually
            for filename in required_files:
                file_url = f"{base_url}{filename}"
                file_path = os.path.join(target_dir, filename)
                
                try:
                    # Try direct download
                    urllib.request.urlretrieve(file_url, file_path)
                    logging.info(f"Downloaded {filename}")
                except Exception as e:
                    logging.error(f"Failed to download {filename} from {file_url}: {str(e)}")
                    
                    # Fall back to alternative sources if available
                    alt_sources = [
                        f"https://github.com/flatangle/flatlib/raw/master/flatlib/resources/swefiles/{filename}",
                        f"https://github.com/chapagain/php-swiss-ephemeris/raw/master/sweph/{filename}"
                    ]
                    
                    for alt_url in alt_sources:
                        try:
                            urllib.request.urlretrieve(alt_url, file_path)
                            logging.info(f"Downloaded {filename} from alternative source {alt_url}")
                            break
                        except Exception as alt_e:
                            logging.error(f"Failed to download {filename} from {alt_url}: {str(alt_e)}")
                    else:
                        logging.error(f"Failed to download {filename} from all sources")
            
            # Close the progress dialog
            progress.close()
            
            # Set the ephemeris path
            setPath(target_dir)
            logging.info(f"Downloaded Swiss Ephemeris files to: {target_dir}")
            
            QMessageBox.information(None, "Download Complete", 
                                  "Swiss Ephemeris files have been downloaded successfully.")
            return True
            
        except Exception as e:
            logging.error(f"Failed to download Swiss Ephemeris files: {str(e)}")
            QMessageBox.critical(None, "Download Failed", 
                               f"Failed to download Swiss Ephemeris files: {str(e)}")
            return False
    else:
        # User chose not to download
        error_msg = (
            "Swiss Ephemeris files are missing. These files are required for astrological calculations.\n\n"
            "Please download the ephemeris files and place them in one of these directories:\n"
        )
        for path in swefiles_paths:
            error_msg += f"- {path}\n"
        
        QMessageBox.critical(None, "Missing Ephemeris Files", error_msg)
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