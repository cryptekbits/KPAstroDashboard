"""
UI utilities package.
Contains utility functions for the KP Astrology application.
"""

from .ui_helpers import is_file_open, open_excel_file
from .logging_utils import setup_logging, handle_exception
from .updater import check_for_updates_on_startup

__all__ = [
    'is_file_open', 
    'open_excel_file', 
    'setup_logging', 
    'handle_exception',
    'check_for_updates_on_startup'
]
