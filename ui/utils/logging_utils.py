"""
Logging utility functions for the KP Astrology application.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import platform


def setup_logging():
    """
    Configure logging for the application using date-based rolling logs
    stored in the application's installation directory.
    """
    # Determine the application's installation directory
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as packaged executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as a script
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create logs directory inside the application directory
    logs_dir = os.path.join(app_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create a log filename with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f'kp_astrology.log')
    
    # Configure logging with rotating file handler
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # Add a timed rotating file handler (rotates at midnight each day)
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,  # Daily rotation
        backupCount=30,  # Keep logs for 30 days
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.suffix = "%Y-%m-%d.log"  # Set the suffix for the rotated logs
    root_logger.addHandler(file_handler)
    
    # Log system information at startup
    logging.info(f"Application started - Version: {get_app_version()}")
    logging.info(f"System: {platform.system()} {platform.release()} ({platform.platform()})")
    logging.info(f"Python: {platform.python_version()}")
    logging.info(f"Log directory: {logs_dir}")
    
    # Set up global exception handling
    sys.excepthook = handle_exception


def get_app_version():
    """Get the application version"""
    try:
        # Try to import from the version module
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from version import VERSION
        return VERSION
    except ImportError:
        return "Unknown"


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions by logging them"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt (Ctrl+C)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback)) 