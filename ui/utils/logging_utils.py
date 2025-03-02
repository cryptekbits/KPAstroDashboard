"""
Logging utility functions for the KP Astrology application.
"""

import os
import sys
import logging
import traceback


def setup_logging():
    """Configure logging for the application"""
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, 'kp_astrology.log')
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )

    # Set up global exception handling
    sys.excepthook = handle_exception


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions by logging them"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt (Ctrl+C)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback)) 