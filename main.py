"""
KP Astrology Dashboard - Main Application

This is the main entry point for the KP Astrology Dashboard application.
It initializes logging and starts the PyQt5 application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from ui import KPAstrologyApp, setup_logging
from ui.utils.updater import check_for_updates_on_startup


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    # Create and run the application
    app = QApplication(sys.argv)
    window = KPAstrologyApp()
    window.show()
    
    # Check for updates after the window is shown
    check_for_updates_on_startup(window)
    
    sys.exit(app.exec_())