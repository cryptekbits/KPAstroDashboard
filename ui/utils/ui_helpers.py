"""
UI helper functions for the KP Astrology application.
"""

import os
import sys
import psutil
import subprocess
import logging
import traceback


def is_file_open(filepath):
    """
    Check if a file is currently open by another process.

    Parameters:
    -----------
    filepath : str
        Path to the file to check

    Returns:
    --------
    bool
        True if the file is open, False otherwise
    """
    if not os.path.exists(filepath):
        return False

    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if filepath == item.path:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def open_excel_file(filepath):
    """
    Open the Excel file using the default application.

    Parameters:
    -----------
    filepath : str
        Path to the Excel file

    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', filepath])
        else:  # Linux
            subprocess.call(['xdg-open', filepath])
        return True
    except Exception as e:
        logging.error(f"Error opening Excel file: {str(e)}")
        logging.error(traceback.format_exc())
        print(f"Error opening Excel file: {str(e)}")
        return False 