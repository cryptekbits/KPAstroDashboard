"""
KP Astrology Dashboard - Main Application

This is the main entry point for the KP Astrology Dashboard application.
It initializes logging and starts the PyQt5 application.
"""

import sys
import os
import warnings
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# Filter out specific warnings
warnings.filterwarnings("ignore", message=".*MapWithoutReturnDtypeWarning.*")
warnings.filterwarnings("ignore", message=".*Calling `map_elements` without specifying `return_dtype`.*")

# Import after warnings are filtered
from ui import KPAstrologyApp, setup_logging
from ui.utils.updater import check_for_updates_on_startup


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