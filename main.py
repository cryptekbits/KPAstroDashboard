#!/usr/bin/env python3
"""
KP Astrology Dashboard
A high-precision Krishnamurti Paddhati (KP) astrology calculator with convenient UI.
"""
import sys
import os
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# Import main application window
from ui.main_window import MainWindow
from config import app_config


def setup_environment():
    """Configure the application environment."""
    # Set application ID for Windows
    try:
        import ctypes
        app_id = 'kp.astrology.dashboard.v1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (ImportError, AttributeError):
        pass  # Not on Windows or other issue

    # Add the project root to PATH for easier imports
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Create data directories if they don't exist
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Set up logging
    import logging
    log_dir = os.path.join(root_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'kp_astrology_{datetime.now().strftime("%Y%m%d")}.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    return root_dir


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler."""
    # Log the exception
    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback))

    # Show error dialog if GUI is available
    try:
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        QMessageBox.critical(None, "Error",
                             f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
                             f"The error has been logged.")
    except:
        # If GUI not available, print to console
        print("CRITICAL ERROR:", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    # Terminate the application
    sys.exit(1)


def main():
    """Main application entry point."""
    print("Starting KP Astrology Dashboard...")

    # Set up application environment
    root_dir = setup_environment()

    # Set up exception handling
    sys.excepthook = handle_exception

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("KP Astrology Dashboard")
    app.setApplicationVersion("1.0.0")

    # Set app icon
    icon_path = os.path.join(root_dir, 'resources', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Show splash screen
    splash_path = os.path.join(root_dir, 'resources', 'splash.png')
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    else:
        splash = None

    # Create and display main window
    try:
        # Load config
        config = app_config.load_config()

        # Create main window
        window = MainWindow()

        # Close splash after a delay
        if splash:
            QTimer.singleShot(1500, splash.close)

        # Show main window
        window.show()

        # Start the application event loop
        sys.exit(app.exec_())

    except Exception as e:
        if splash:
            splash.close()
        logging.error(f"Error starting application: {str(e)}")
        QMessageBox.critical(None, "Startup Error",
                             f"Error starting the application:\n\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()