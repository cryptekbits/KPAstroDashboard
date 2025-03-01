import sys
import os
import psutil
import subprocess
import logging
import traceback
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QLineEdit,
                             QDateEdit, QTimeEdit, QCheckBox, QGroupBox, QComboBox,
                             QProgressBar, QMessageBox, QCompleter, QScrollArea,
                             QGridLayout, QSpinBox, QCalendarWidget)
from PyQt5.QtCore import Qt, QDate, QTime, QThread, pyqtSignal

from kp_data_generator import KPDataGenerator
from excel_exporter import ExcelExporter


def setup_logging():
    """Configure logging for the application"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('kp_astrology.log')
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


class GeneratorThread(QThread):
    """
    Thread for generating data without freezing the UI.
    """
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, location, start_datetime, sheets_to_generate, selected_aspects,
                 aspect_planets, yoga_settings=None):
        """
        Initialize the generator thread.

        Parameters:
        -----------
        location : str
            The location for calculations
        start_datetime : datetime
            The main date and time for calculations
        sheets_to_generate : list
            List of sheet names to generate
        selected_aspects : list
            List of aspect angles to calculate
        aspect_planets : list
            List of planets to include in aspect calculations
        yoga_settings : dict, optional
            Settings for yoga calculations including date range
        """
        super().__init__()
        self.location = location
        self.start_datetime = start_datetime
        self.sheets_to_generate = sheets_to_generate
        self.selected_aspects = selected_aspects
        self.aspect_planets = aspect_planets
        self.yoga_settings = yoga_settings

    def run(self):
        try:
            # Locations dictionary - can be expanded with more locations
            locations = {
                "Mumbai": {"latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
                "Delhi": {"latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "Chennai": {"latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata"},
                "Kolkata": {"latitude": 22.5726, "longitude": 88.3639, "timezone": "Asia/Kolkata"},
                "New York": {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
                "London": {"latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
            }

            location_data = locations.get(self.location)
            if not location_data:
                self.error_signal.emit(f"Location {self.location} not found!")
                return

            self.progress_signal.emit(5, "Initializing data generator...")

            # Create data generator
            generator = KPDataGenerator(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                timezone=location_data["timezone"],
                ayanamsa="Krishnamurti",
                house_system="Placidus"
            )

            # Set the selected aspects and aspect planets in the generator
            generator.aspect_calculator.set_selected_aspects(self.selected_aspects)
            generator.aspect_calculator.set_selected_planets(self.aspect_planets)

            # Define end date time (11:55 PM on the same day)
            end_datetime = self.start_datetime.replace(hour=23, minute=55, second=0)

            results = {}

            # Planet positions sheet
            if "Planet Positions" in self.sheets_to_generate:
                self.progress_signal.emit(10, "Generating Planet Positions...")
                results["Planet Positions"] = generator.get_planet_positions(self.start_datetime)

            # Hora timing sheet
            if "Hora Timing" in self.sheets_to_generate:
                self.progress_signal.emit(15, "Generating Hora Timing...")
                results["Hora Timing"] = generator.get_hora_timings(self.start_datetime, end_datetime)

            # Planets data
            planets = [
                "Moon", "Ascendant", "Sun", "Mercury", "Venus",
                "Mars", "Jupiter", "Saturn", "Rahu", "Ketu",
                "Uranus", "Neptune"
            ]

            # Calculate progress distribution for planet transitions
            total_transition_items = sum(1 for p in planets if p in self.sheets_to_generate)
            transition_progress_per_item = 40 / max(total_transition_items, 1)  # Avoid division by zero
            current_progress = 20

            # Process each planet transition
            for planet in planets:
                if planet in self.sheets_to_generate:
                    self.progress_signal.emit(current_progress, f"Generating {planet} data...")
                    results[planet] = generator.get_planet_transitions(
                        planet, self.start_datetime, end_datetime
                    )
                    current_progress += transition_progress_per_item
                    self.progress_signal.emit(current_progress, f"Completed {planet} data")

            # Calculate Yogas if included
            if "Yogas" in self.sheets_to_generate and self.yoga_settings:
                self.progress_signal.emit(current_progress, "Calculating Yogas...")

                yoga_start_date = self.yoga_settings["start_date"]
                yoga_end_date = self.yoga_settings["end_date"]

                # Define a progress callback for yoga calculations
                def yoga_progress_callback(current, total, message):
                    # Calculate percentage based on current/total
                    if total > 0:
                        progress_percent = current / total * 30  # 30% of progress bar for yogas
                        self.progress_signal.emit(
                            int(current_progress + progress_percent),
                            message
                        )

                # Calculate yogas for the date range
                yoga_df = generator.calculate_yogas_for_date_range(
                    yoga_start_date,
                    yoga_end_date,
                    progress_callback=yoga_progress_callback
                )

                # Store the yoga data in results
                results["Yogas"] = yoga_df
                current_progress += 30

            self.progress_signal.emit(95, "Finalizing results...")
            self.finished_signal.emit(results)
            self.progress_signal.emit(100, "Complete!")

        except Exception as e:
            error_msg = f"Error during data generation: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.error_signal.emit(error_msg)


class KPAstrologyApp(QMainWindow):
    """
    Main application window for the KP Astrology tool.
    """

    def __init__(self):
        super().__init__()
        self.aspects = [
            {"angle": 0, "name": "Conjunction", "symbol": "☌", "default": True},
            {"angle": 30, "name": "Semi-Sextile", "symbol": "⚺", "default": False},
            {"angle": 60, "name": "Sextile", "symbol": "⚹", "default": False},
            {"angle": 90, "name": "Square", "symbol": "□", "default": True},
            {"angle": 120, "name": "Trine", "symbol": "△", "default": False},
            {"angle": 150, "name": "Quincunx", "symbol": "⚻", "default": False},
            {"angle": 180, "name": "Opposition", "symbol": "☍", "default": True}
        ]
        self.sheet_names = [
            "Planet Positions", "Hora Timing", "Moon", "Ascendant",
            "Sun", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Yogas"
        ]
        self.initUI()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('KP Astrology Nakshatras Generator')
        self.setGeometry(100, 100, 800, 700)  # Increased height for new sections

        # Create a scroll area for the main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(main_widget)

        # Location selection
        location_group = QGroupBox("Location")
        location_layout = QHBoxLayout()
        location_group.setLayout(location_layout)

        self.location_combo = QComboBox()
        locations = ["Mumbai", "Delhi", "Chennai", "Kolkata", "New York", "London"]
        self.location_combo.addItems(locations)
        self.location_combo.setCurrentText("Mumbai")

        # Add autocomplete
        completer = QCompleter(locations)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.location_combo.setCompleter(completer)

        location_layout.addWidget(QLabel("Location:"))
        location_layout.addWidget(self.location_combo)

        main_layout.addWidget(location_group)

        # Date and time selection for the main calculation
        datetime_group = QGroupBox("Main Date and Time")
        datetime_layout = QVBoxLayout()
        datetime_group.setLayout(datetime_layout)

        # Separate date and time fields
        date_layout = QHBoxLayout()
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Date:"))
        date_layout.addWidget(self.date_picker)

        time_layout = QHBoxLayout()
        self.time_picker = QTimeEdit()
        self.time_picker.setTime(QTime(9, 0))  # Default to 9:00 AM
        self.time_picker.setDisplayFormat("hh:mm AP")
        time_layout.addWidget(QLabel("Time:"))
        time_layout.addWidget(self.time_picker)

        datetime_layout.addLayout(date_layout)
        datetime_layout.addLayout(time_layout)

        main_layout.addWidget(datetime_group)

        # Yoga date range selection
        yoga_group = QGroupBox("Yoga Calculations Date Range")
        yoga_layout = QVBoxLayout()
        yoga_group.setLayout(yoga_layout)

        # Add explanation label
        yoga_layout.addWidget(QLabel("Calculate yogas for the following date range:"))

        # Start date selection
        yoga_start_layout = QHBoxLayout()
        yoga_start_layout.addWidget(QLabel("From:"))
        self.yoga_start_date = QDateEdit()
        self.yoga_start_date.setCalendarPopup(True)

        # Set default to 7 days before current date
        default_start_date = QDate.currentDate().addDays(-7)
        self.yoga_start_date.setDate(default_start_date)

        yoga_start_layout.addWidget(self.yoga_start_date)
        yoga_layout.addLayout(yoga_start_layout)

        # End date selection
        yoga_end_layout = QHBoxLayout()
        yoga_end_layout.addWidget(QLabel("To:"))
        self.yoga_end_date = QDateEdit()
        self.yoga_end_date.setCalendarPopup(True)

        # Set default to 14 days after current date
        default_end_date = QDate.currentDate().addDays(14)
        self.yoga_end_date.setDate(default_end_date)

        yoga_end_layout.addWidget(self.yoga_end_date)
        yoga_layout.addLayout(yoga_end_layout)

        # Quick date range buttons
        quick_range_layout = QHBoxLayout()

        month_btn = QPushButton("1 Month")
        month_btn.clicked.connect(lambda: self.set_yoga_date_range(30))

        quarter_btn = QPushButton("3 Months")
        quarter_btn.clicked.connect(lambda: self.set_yoga_date_range(90))

        half_year_btn = QPushButton("6 Months")
        half_year_btn.clicked.connect(lambda: self.set_yoga_date_range(180))

        year_btn = QPushButton("1 Year")
        year_btn.clicked.connect(lambda: self.set_yoga_date_range(365))

        quick_range_layout.addWidget(month_btn)
        quick_range_layout.addWidget(quarter_btn)
        quick_range_layout.addWidget(half_year_btn)
        quick_range_layout.addWidget(year_btn)

        yoga_layout.addLayout(quick_range_layout)

        main_layout.addWidget(yoga_group)

        # Sheets selection
        sheets_group = QGroupBox("Sheets to Generate")
        sheets_layout = QVBoxLayout()
        sheets_group.setLayout(sheets_layout)

        self.sheet_checkboxes = {}

        # Create a grid layout for checkboxes (2 columns)
        grid_layout = QGridLayout()
        row, col = 0, 0
        max_col = 2  # Number of columns

        for sheet_name in self.sheet_names:
            checkbox = QCheckBox(sheet_name)
            checkbox.setChecked(True)  # All selected by default
            self.sheet_checkboxes[sheet_name] = checkbox
            grid_layout.addWidget(checkbox, row, col)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        sheets_layout.addLayout(grid_layout)
        main_layout.addWidget(sheets_group)

        # Aspect selection
        aspects_group = QGroupBox("Aspects to Calculate")
        aspects_layout = QVBoxLayout()
        aspects_group.setLayout(aspects_layout)

        self.aspect_checkboxes = {}

        # Create a grid layout for aspect checkboxes (3 columns)
        aspect_grid = QGridLayout()
        row, col = 0, 0
        max_col = 3  # Number of columns

        for aspect in self.aspects:
            checkbox_text = f"{aspect['symbol']} {aspect['name']} ({aspect['angle']}°)"
            checkbox = QCheckBox(checkbox_text)
            checkbox.setChecked(aspect["default"])  # Set default selection
            self.aspect_checkboxes[aspect['angle']] = checkbox
            aspect_grid.addWidget(checkbox, row, col)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        aspects_layout.addLayout(aspect_grid)
        main_layout.addWidget(aspects_group)

        # Planets for aspects selection
        aspect_planets_group = QGroupBox("Calculate Aspects For")
        aspect_planets_layout = QVBoxLayout()
        aspect_planets_group.setLayout(aspect_planets_layout)

        self.aspect_planets_checkboxes = {}

        # Define planets for aspects
        self.aspect_planets = [
            {"name": "Sun", "default": True},
            {"name": "Moon", "default": True},
            {"name": "Mercury", "default": True},
            {"name": "Venus", "default": True},
            {"name": "Mars", "default": True},
            {"name": "Jupiter", "default": True},
            {"name": "Saturn", "default": True},
            {"name": "Rahu", "default": True},
            {"name": "Ketu", "default": True},
            {"name": "Ascendant", "default": True},
            {"name": "Uranus", "default": False},
            {"name": "Neptune", "default": False}
        ]

        # Create a grid layout for planet checkboxes (3 columns)
        planet_grid = QGridLayout()
        row, col = 0, 0
        max_col = 3  # Number of columns

        for planet in self.aspect_planets:
            checkbox = QCheckBox(planet["name"])
            checkbox.setChecked(planet["default"])
            self.aspect_planets_checkboxes[planet["name"]] = checkbox
            planet_grid.addWidget(checkbox, row, col)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        aspect_planets_layout.addLayout(planet_grid)
        main_layout.addWidget(aspect_planets_group)

        # Selection buttons
        select_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All Sheets")
        select_all_btn.clicked.connect(self.select_all_sheets)

        select_none_btn = QPushButton("Select No Sheets")
        select_none_btn.clicked.connect(self.select_no_sheets)

        select_all_aspects_btn = QPushButton("Select All Aspects")
        select_all_aspects_btn.clicked.connect(self.select_all_aspects)

        select_no_aspects_btn = QPushButton("Select No Aspects")
        select_no_aspects_btn.clicked.connect(self.select_no_aspects)

        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(select_none_btn)
        select_layout.addWidget(select_all_aspects_btn)
        select_layout.addWidget(select_no_aspects_btn)

        main_layout.addLayout(select_layout)

        # Progress bar and status label
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        # Add status label above progress bar
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)

        # Progress bar with percentage display
        progress_bar_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_bar_layout.addWidget(self.progress_bar)

        progress_layout.addLayout(progress_bar_layout)
        main_layout.addWidget(progress_group)

        # Generate button
        self.generate_btn = QPushButton("Generate Excel")
        self.generate_btn.clicked.connect(self.generate_data)
        main_layout.addWidget(self.generate_btn)

    def set_yoga_date_range(self, days):
        """
        Set the yoga date range based on number of days.

        Parameters:
        -----------
        days : int
            Number of days to set the range for
        """
        # Get the current date
        current_date = QDate.currentDate()

        # Calculate half the days before and half after
        days_before = days // 3
        days_after = days - days_before

        # Set the start and end dates
        self.yoga_start_date.setDate(current_date.addDays(-days_before))
        self.yoga_end_date.setDate(current_date.addDays(days_after))

    def select_all_sheets(self):
        """Select all sheet checkboxes."""
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(True)

    def select_no_sheets(self):
        """Deselect all sheet checkboxes."""
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(False)

    def select_all_aspects(self):
        """Select all aspect checkboxes."""
        for checkbox in self.aspect_checkboxes.values():
            checkbox.setChecked(True)

    def select_no_aspects(self):
        """Deselect all aspect checkboxes."""
        for checkbox in self.aspect_checkboxes.values():
            checkbox.setChecked(False)

    @staticmethod
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

    @staticmethod
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

    def generate_data(self):
        """Generate data and create Excel file."""
        try:
            # Get selected sheets
            selected_sheets = [name for name, checkbox in self.sheet_checkboxes.items()
                               if checkbox.isChecked()]

            if not selected_sheets:
                logging.warning("No sheets selected by user")
                QMessageBox.warning(self, "No Sheets Selected",
                                    "Please select at least one sheet to generate.")
                return

            # Get selected aspects
            selected_aspects = [aspect["angle"] for aspect in self.aspects
                                if self.aspect_checkboxes[aspect["angle"]].isChecked()]

            if not selected_aspects:
                logging.warning("No aspects selected by user")
                QMessageBox.warning(self, "No Aspects Selected",
                                    "Please select at least one aspect to calculate.")
                return

            # Get selected planets for aspects
            selected_aspect_planets = [planet["name"] for planet in self.aspect_planets
                                       if self.aspect_planets_checkboxes[planet["name"]].isChecked()]

            if not selected_aspect_planets:
                logging.warning("No planets selected by user")
                QMessageBox.warning(self, "No Planets Selected",
                                    "Please select at least one planet for aspect calculations.")
                return

            # Get location and datetime
            location = self.location_combo.currentText()
            logging.info(f"Selected location: {location}")

            # Get date and time separately and combine
            qdate = self.date_picker.date()
            qtime = self.time_picker.time()

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
            if self.is_file_open(excel_file):
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
                yoga_start_date = self.yoga_start_date.date()
                yoga_end_date = self.yoga_end_date.date()

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

                yoga_settings = {
                    "start_date": start_dt_yoga,
                    "end_date": end_dt_yoga
                }
                logging.info(f"Yoga calculation range: {start_dt_yoga.date()} to {end_dt_yoga.date()}")

            # Disable UI during generation
            self.generate_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.status_label.setText("Initializing...")

            # Start the generator thread
            logging.info("Starting generator thread")
            self.generator_thread = GeneratorThread(
                location,
                start_dt,
                selected_sheets,
                selected_aspects,
                selected_aspect_planets,
                yoga_settings
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
            self.generate_btn.setEnabled(True)

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
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
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

            self.status_label.setText("Exporting to Excel...")

            # Export to Excel
            exporter = ExcelExporter()
            exporter.export_to_excel(results, filename)
            logging.info("Excel export completed successfully")

            self.status_label.setText("Export complete!")

            # Show success message
            QMessageBox.information(self, "Export Complete",
                                    f"Data has been exported to {filename}")

            # Automatically open the Excel file
            if self.open_excel_file(filename):
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
            self.generate_btn.setEnabled(True)
            self.status_label.setText("Ready")

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
        self.generate_btn.setEnabled(True)
        self.status_label.setText("Error occurred")


if __name__ == "__main__":
    setup_logging()
    logging.info("Starting KP Astrology application")
    try:
        app = QApplication(sys.argv)
        window = KPAstrologyApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Fatal application error: {str(e)}")
        logging.critical(traceback.format_exc())