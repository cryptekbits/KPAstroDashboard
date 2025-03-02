"""
KP Astrology Dashboard - Main Application

This is the main entry point for the KP Astrology Dashboard application.
It initializes logging and starts the PyQt5 application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from ui import KPAstrologyApp, setup_logging


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    # Create and run the application
    app = QApplication(sys.argv)
    window = KPAstrologyApp()
    window.show()
    sys.exit(app.exec_())