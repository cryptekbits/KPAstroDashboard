import sys
import os
import psutil
import subprocess
from datetime import datetime, timedelta
import pandas as pd
import pytz
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QLineEdit,
                             QDateEdit, QTimeEdit, QCheckBox, QGroupBox, QComboBox,
                             QProgressBar, QMessageBox, QCompleter)
from PyQt5.QtCore import Qt, QDate, QTime, QThread, pyqtSignal

from kp_data_generator import KPDataGenerator
from excel_exporter import ExcelExporter


class GeneratorThread(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, location, start_datetime, sheets_to_generate):
        super().__init__()
        self.location = location
        self.start_datetime = start_datetime
        self.sheets_to_generate = sheets_to_generate

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

            # Create data generator
            generator = KPDataGenerator(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                timezone=location_data["timezone"],
                ayanamsa="Krishnamurti",
                house_system="Placidus"
            )

            # Define end date time (11:55 PM on the same day)
            end_datetime = self.start_datetime.replace(hour=23, minute=55, second=0)

            results = {}

            # Planet positions sheet
            if "Planet Positions" in self.sheets_to_generate:
                self.progress_signal.emit(5, "Generating Planet Positions...")
                results["Planet Positions"] = generator.get_planet_positions(self.start_datetime)

            # Hora timing sheet
            if "Hora Timing" in self.sheets_to_generate:
                self.progress_signal.emit(10, "Generating Hora Timing...")
                results["Hora Timing"] = generator.get_hora_timings(self.start_datetime, end_datetime)

            # Planets data
            planets = [
                "Moon", "Ascendant", "Sun", "Mercury", "Venus",
                "Mars", "Jupiter", "Saturn", "Rahu", "Ketu",
                "Uranus", "Neptune"
            ]

            total_planets = sum(1 for p in planets if p in self.sheets_to_generate)
            current_progress = 15
            progress_per_planet = 70 / (total_planets or 1)  # Avoid division by zero

            for planet in planets:
                if planet in self.sheets_to_generate:
                    self.progress_signal.emit(current_progress, f"Generating {planet} data...")
                    results[planet] = generator.get_planet_transitions(
                        planet, self.start_datetime, end_datetime
                    )
                    current_progress += progress_per_planet
                    self.progress_signal.emit(current_progress, f"Completed {planet} data")

            self.progress_signal.emit(95, "Finalizing results...")
            self.finished_signal.emit(results)
            self.progress_signal.emit(100, "Complete!")

        except Exception as e:
            self.error_signal.emit(f"Error during data generation: {str(e)}")


class KPAstrologyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('KP Astrology Nakshatras Generator')
        self.setGeometry(100, 100, 600, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
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

        # Date and time selection
        datetime_group = QGroupBox("Date and Time")
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

        # Sheets selection
        sheets_group = QGroupBox("Sheets to Generate")
        sheets_layout = QVBoxLayout()
        sheets_group.setLayout(sheets_layout)

        self.sheet_checkboxes = {}
        self.sheet_names = [
            "Planet Positions", "Hora Timing", "Moon", "Ascendant",
            "Sun", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Rahu", "Ketu", "Uranus", "Neptune"
        ]

        for sheet_name in self.sheet_names:
            checkbox = QCheckBox(sheet_name)
            checkbox.setChecked(True)  # All selected by default
            self.sheet_checkboxes[sheet_name] = checkbox
            sheets_layout.addWidget(checkbox)

        main_layout.addWidget(sheets_group)

        # Selection buttons
        select_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_sheets)

        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_no_sheets)

        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(select_none_btn)

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

    def select_all_sheets(self):
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(True)

    def select_no_sheets(self):
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(False)

    def is_file_open(self, filepath):
        """Check if a file is currently open by another process"""
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

    def open_excel_file(self, filepath):
        """Open the Excel file using the default application"""
        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux
                subprocess.call(['xdg-open', filepath])
            return True
        except Exception as e:
            print(f"Error opening Excel file: {str(e)}")
            return False

    def generate_data(self):
        # Get selected sheets
        selected_sheets = [name for name, checkbox in self.sheet_checkboxes.items()
                           if checkbox.isChecked()]

        if not selected_sheets:
            QMessageBox.warning(self, "No Sheets Selected",
                                "Please select at least one sheet to generate.")
            return

        # Get location and datetime
        location = self.location_combo.currentText()

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

        # Check if excel file is already open
        excel_file = "KP Panchang.xlsx"
        if self.is_file_open(excel_file):
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
            except Exception as e:
                QMessageBox.warning(self, "File Error",
                                    f"Could not remove existing file: {str(e)}")
                return

        # Disable UI during generation
        self.generate_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")

        # Start the generator thread
        self.generator_thread = GeneratorThread(location, start_dt, selected_sheets)
        self.generator_thread.progress_signal.connect(self.update_progress)
        self.generator_thread.finished_signal.connect(self.export_to_excel)
        self.generator_thread.error_signal.connect(self.show_error)
        self.generator_thread.start()

    def update_progress(self, value, status):
        self.progress_bar.setValue(value)
        self.status_label.setText(status)

    def export_to_excel(self, results):
        try:
            # Create filename
            filename = "KP Panchang.xlsx"

            self.status_label.setText("Exporting to Excel...")

            # Export to Excel
            exporter = ExcelExporter()
            exporter.export_to_excel(results, filename)

            self.status_label.setText("Export complete!")

            # Show success message
            QMessageBox.information(self, "Export Complete",
                                    f"Data has been exported to {filename}")

            # Automatically open the Excel file
            self.open_excel_file(filename)

        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"Failed to export to Excel: {str(e)}")
        finally:
            # Re-enable UI
            self.generate_btn.setEnabled(True)
            self.status_label.setText("Ready")

    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.generate_btn.setEnabled(True)
        self.status_label.setText("Error occurred")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KPAstrologyApp()
    window.show()
    sys.exit(app.exec_())