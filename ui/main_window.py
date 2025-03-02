"""
Main window for the KP Astrology application.
"""

import os
import logging
import traceback
import json
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QAction, QMenu
from PyQt5.QtCore import QThread

from exporters.excel_exporter import ExcelExporter
from .generator_thread import GeneratorThread
from .tabs.main_tab import MainTab
from .tabs.config_tab import ConfigTab
from .utils.ui_helpers import is_file_open, open_excel_file
from .utils.updater import check_for_updates_on_startup


class KPAstrologyApp(QMainWindow):
    """
    Main application window for the KP Astrology tool.
    """

    def __init__(self):
        super().__init__()
        
        # Create tabs and components
        self.main_tab = MainTab(self)
        self.config_tab = ConfigTab(self)
        
        # Initialize thread
        self.generator_thread = None
        
        self.initUI()
        
        # Update visibility based on loaded configuration
        self.update_main_tab_visibility()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('KP Astrology Nakshatras Generator')
        self.setGeometry(100, 100, 800, 700)

        # Create a tab widget
        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)
        
        # Create and add the main tab
        main_tab = self.main_tab.setup_tab()
        tab_widget.addTab(main_tab, "Main")
        
        # Create and add the configuration tab
        config_tab = self.config_tab.setup_tab()
        tab_widget.addTab(config_tab, "Configuration")

        # Create menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # Check for updates action
        update_action = QAction('Check for Updates', self)
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)
        
        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def update_main_tab_visibility(self):
        """Update the visibility of components in the main tab based on configuration settings."""
        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        try:
            with open(config_file, 'r') as f:
                config_settings = json.load(f)
                
            # Update main tab visibility based on configuration
            self.main_tab.update_visibility(config_settings)
            
        except Exception as e:
            logging.error(f"Failed to update main tab visibility: {str(e)}")
            traceback.print_exc()

    def generate_data(self):
        """Generate data and create Excel file."""
        try:
            # Get selected sheets
            selected_sheets = self.main_tab.get_selected_sheets()

            if not selected_sheets:
                logging.warning("No sheets selected by user")
                QMessageBox.warning(self, "No Sheets Selected",
                                    "Please select at least one sheet to generate.")
                return
                
            # Apply configuration settings to filter sheets
            config_settings = self.config_tab.get_config_settings()
            
            # Check if any sheets remain after filtering
            if not selected_sheets:
                logging.warning("No sheets remain after applying configuration filters")
                QMessageBox.warning(self, "No Sheets Selected",
                                   "All selected sheets have been disabled in the Configuration tab.")
                return

            # Get selected aspects and aspect planets
            selected_aspects = self.main_tab.aspect_controls.get_selected_aspects()
            selected_aspect_planets = self.main_tab.aspect_controls.get_selected_aspect_planets()

            # If aspects are disabled, clear the selected aspects
            if not config_settings["aspects"]["enabled"]:
                selected_aspects = []

            # Get location and datetime
            location = self.main_tab.location_combo.currentText()
            logging.info(f"Selected location: {location}")

            # Get date and time separately and combine
            qdate = self.main_tab.date_picker.date()
            qtime = self.main_tab.time_picker.time()

            # Convert QDate and QTime to Python datetime
            start_dt = datetime(
                qdate.year(),
                qdate.month(),
                qdate.day(),
                qtime.hour(),
                qtime.minute(),
                qtime.second()
            )
            logging.info(f"Selected date and time: {start_dt}")

            # Check if Excel file is already open
            excel_file = "KP Panchang.xlsx"
            if is_file_open(excel_file):
                logging.warning(f"Excel file {excel_file} is already open")
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText(f"The file '{excel_file}' is currently open.")
                msgBox.setInformativeText("Please close it before generating a new file.")
                msgBox.setWindowTitle("File Open")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return

            # Delete existing file if it exists
            if os.path.exists(excel_file):
                try:
                    os.remove(excel_file)
                    logging.info(f"Removed existing file: {excel_file}")
                except Exception as e:
                    error_msg = f"Could not remove existing file: {str(e)}"
                    logging.error(error_msg)
                    logging.error(traceback.format_exc())
                    QMessageBox.warning(self, "File Error", error_msg)
                    return

            # Prepare yoga settings if Yogas sheet is selected
            yoga_settings = None
            if "Yogas" in selected_sheets:
                # Get the start and end dates for yoga calculations
                yoga_start_date = self.main_tab.yoga_controls.yoga_start_date.date()
                yoga_end_date = self.main_tab.yoga_controls.yoga_end_date.date()

                # Convert QDate to Python datetime
                start_dt_yoga = datetime(
                    yoga_start_date.year(),
                    yoga_start_date.month(),
                    yoga_start_date.day(),
                    0, 0, 0  # Start at midnight
                )

                end_dt_yoga = datetime(
                    yoga_end_date.year(),
                    yoga_end_date.month(),
                    yoga_end_date.day(),
                    23, 59, 59  # End at the end of the day
                )

                # Validate date range
                if end_dt_yoga < start_dt_yoga:
                    QMessageBox.warning(self, "Invalid Date Range",
                                        "End date must be after start date for yoga calculations.")
                    return

                # Get enabled yoga types from configuration
                enabled_yoga_types = [yoga_name for yoga_name, checkbox in self.config_tab.yoga_controls.yoga_types.items()
                                    if checkbox.isChecked()]
                
                yoga_settings = {
                    "start_date": start_dt_yoga,
                    "end_date": end_dt_yoga,
                    "time_interval": self.main_tab.yoga_controls.yoga_time_interval.currentData(),
                    "is_one_day": yoga_start_date.addDays(1) == yoga_end_date.addDays(-1),
                    "enabled_yoga_types": enabled_yoga_types
                }
                logging.info(f"Yoga calculation range: {start_dt_yoga.date()} to {end_dt_yoga.date()}")
                logging.info(f"Yoga time interval: {self.main_tab.yoga_controls.yoga_time_interval.currentData()} hour(s)")
                if yoga_settings["is_one_day"]:
                    logging.info(f"Showing yogas for a single day: {yoga_start_date.addDays(1).toString('yyyy-MM-dd')}")

            # Disable UI during generation
            self.main_tab.generate_btn.setEnabled(False)
            self.main_tab.progress_bar.setValue(0)
            self.main_tab.status_label.setText("Initializing...")

            # Get configuration settings
            config_settings = self.config_tab.get_config_settings()

            # Start the generator thread
            logging.info("Starting generator thread")
            self.generator_thread = GeneratorThread(
                location,
                qdate,
                qtime,
                selected_sheets,
                excel_file,
                selected_aspect_planets,
                yoga_settings,
                qdate,  # Pass the selected date for 1-day yoga calculations
                config_settings  # Pass the configuration settings
            )
            self.generator_thread.progress_signal.connect(self.update_progress)
            self.generator_thread.finished_signal.connect(self.export_to_excel)
            self.generator_thread.error_signal.connect(self.show_error)
            self.generator_thread.start()

        except Exception as e:
            error_msg = f"Error in generate_data: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.show_error(error_msg)
            self.main_tab.generate_btn.setEnabled(True)

    def update_progress(self, value, status):
        """
        Update the progress bar and status label.

        Parameters:
        -----------
        value : int
            Progress value (0-100)
        status : str
            Status message
        """
        self.main_tab.progress_bar.setValue(value)
        self.main_tab.status_label.setText(status)
        logging.debug(f"Progress update: {value}% - {status}")

    def export_to_excel(self, results):
        """
        Export generated data to Excel.

        Parameters:
        -----------
        results : dict
            Dictionary of sheet names to dataframes
        """
        try:
            # Create filename
            filename = "KP Panchang.xlsx"
            logging.info(f"Exporting data to {filename}")

            self.main_tab.status_label.setText("Exporting to Excel...")

            # Export to Excel
            exporter = ExcelExporter()
            exporter.export_to_excel(results, filename)
            logging.info("Excel export completed successfully")

            self.main_tab.status_label.setText("Export complete!")

            # Show success message
            QMessageBox.information(self, "Export Complete",
                                    f"Data has been exported to {filename}")

            # Automatically open the Excel file
            if open_excel_file(filename):
                logging.info(f"Successfully opened {filename}")
            else:
                logging.warning(f"Failed to open {filename}")

        except Exception as e:
            error_msg = f"Failed to export to Excel: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Export Error", error_msg)
        finally:
            # Re-enable UI
            self.main_tab.generate_btn.setEnabled(True)
            self.main_tab.status_label.setText("Ready")

    def show_error(self, error_message):
        """
        Show an error message dialog.

        Parameters:
        -----------
        error_message : str
            Error message to display
        """
        logging.error(f"Application error: {error_message}")
        QMessageBox.critical(self, "Error", error_message)
        self.main_tab.generate_btn.setEnabled(True)
        self.main_tab.status_label.setText("Error occurred")

    def check_for_updates(self):
        """Manually check for updates."""
        check_for_updates_on_startup(self)

    def show_about_dialog(self):
        """Show the about dialog."""
        from version import VERSION, VERSION_NAME, BUILD_DATE
        
        about_text = f"""
        <h2>KP Astrology Dashboard</h2>
        <p>Version: {VERSION} ({VERSION_NAME})</p>
        <p>Build Date: {BUILD_DATE}</p>
        <p>A comprehensive tool for KP Astrology calculations and analysis.</p>
        """
        
        QMessageBox.about(self, "About KP Astrology Dashboard", about_text) 