"""
Main window for the KP Astrology Dashboard.
"""
import sys
import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QTabWidget, QSplitter,
    QStatusBar, QProgressBar, QAction, QMenu, QToolBar, QFileDialog,
    QStackedWidget
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

# Import UI components
from .date_time_panel import DateTimePanel
from .settings_panel import SettingsPanel
from .yoga_panel import YogaPanel
from .chart_panel import ChartPanel
from .export_panel import ExportPanel
from .progress_dialog import ProgressDialog
from .message_panel import MessagePanel


class CalculationThread(QThread):
    """Background thread for calculations."""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, settings: Dict, calculation_type: str, **kwargs):
        """
        Initialize the calculation thread.

        Args:
            settings: Dictionary with calculation settings
            calculation_type: Type of calculation to perform
            **kwargs: Additional parameters for specific calculations
        """
        super().__init__()
        self.settings = settings
        self.calculation_type = calculation_type
        self.kwargs = kwargs

    def run(self):
        """Run the calculation thread."""
        try:
            self.progress_signal.emit(5, f"Starting {self.calculation_type} calculation...")

            if self.calculation_type == "transit":
                # Import calculator here to avoid circular imports
                from calculations.transit_calculator import TransitCalculator
                from calculations.position_calculator import PositionCalculator
                from calculations.aspect_calculator import AspectCalculator

                # Set up calculators
                self.progress_signal.emit(10, "Initializing calculators...")
                position_calc = PositionCalculator(
                    latitude=self.settings["latitude"],
                    longitude=self.settings["longitude"],
                    timezone_str=self.settings["timezone"],
                    ayanamsa=self.settings["ayanamsa"],
                    house_system=self.settings["house_system"]
                )
                aspect_calc = AspectCalculator()
                transit_calc = TransitCalculator(position_calc, aspect_calc)

                # Configure calculators
                aspect_calc.set_selected_aspects(self.settings.get("aspects", [0, 90, 180]))
                aspect_calc.set_selected_planets(self.settings.get("aspect_planets", ["Sun", "Moon", "Mercury"]))

                # Get parameters
                start_time = self.kwargs.get("start_time", datetime.now())
                end_time = self.kwargs.get("end_time", start_time + timedelta(hours=24))
                planets = self.kwargs.get("planets", ["Sun", "Moon", "Mercury", "Ascendant"])
                interval = self.kwargs.get("interval", 5)  # minutes

                # Calculate transits
                results = {}
                total_planets = len(planets)
                for i, planet in enumerate(planets):
                    progress = 10 + int(85 * i / total_planets)
                    self.progress_signal.emit(progress, f"Calculating {planet} transits...")

                    df = transit_calc.get_planet_transitions(
                        planet_name=planet,
                        start_dt=start_time,
                        end_dt=end_time,
                        interval_minutes=interval,
                        include_aspects=True
                    )
                    results[planet] = df

                self.progress_signal.emit(95, "Finalizing transit results...")
                self.finished_signal.emit(results)

            elif self.calculation_type == "yoga":
                # Import calculator
                from yogas.yoga_calculator import YogaCalculator
                from calculations.position_calculator import PositionCalculator

                # Set up calculators
                self.progress_signal.emit(10, "Initializing calculators...")
                position_calc = PositionCalculator(
                    latitude=self.settings["latitude"],
                    longitude=self.settings["longitude"],
                    timezone_str=self.settings["timezone"],
                    ayanamsa=self.settings["ayanamsa"],
                    house_system=self.settings["house_system"]
                )
                yoga_calc = YogaCalculator(
                    use_all_yogas=True,
                    selected_yogas=self.settings.get("selected_yogas")
                )

                # Get parameters
                start_time = self.kwargs.get("start_time", datetime.now())
                end_time = self.kwargs.get("end_time", start_time + timedelta(days=7))
                interval = self.kwargs.get("interval", 30)  # minutes

                # Create chart generator function
                def chart_generator(dt):
                    # Return chart data and planets data for the given time
                    return position_calc.get_chart_and_planets_data(dt)

                # Calculate yogas
                self.progress_signal.emit(20, "Calculating yogas...")
                yoga_results = yoga_calc.calculate_yogas_for_timeframe(
                    chart_generator=chart_generator,
                    start_time=start_time,
                    end_time=end_time,
                    interval_minutes=interval
                )

                # Convert to DataFrame
                self.progress_signal.emit(80, "Processing yoga results...")
                results_df = yoga_calc.convert_results_to_dataframe(yoga_results)

                # Calculate statistics
                yoga_counts = yoga_calc.get_yoga_counts_by_type(yoga_results)
                significant_yogas = yoga_calc.get_most_significant_yogas(yoga_results)
                yoga_by_period = yoga_calc.get_yogas_by_time_period(yoga_results)

                self.progress_signal.emit(95, "Finalizing yoga results...")
                self.finished_signal.emit({
                    "yoga_results": results_df,
                    "yoga_counts": yoga_counts,
                    "significant_yogas": significant_yogas,
                    "yoga_by_period": yoga_by_period
                })

            elif self.calculation_type == "hora":
                # Import calculator
                from calculations.hora_calculator import HoraCalculator

                # Set up calculator
                self.progress_signal.emit(10, "Initializing calculator...")
                hora_calc = HoraCalculator(
                    latitude=self.settings["latitude"],
                    longitude=self.settings["longitude"],
                    timezone_str=self.settings["timezone"]
                )

                # Get parameters
                start_time = self.kwargs.get("start_time", datetime.now())
                end_time = self.kwargs.get("end_time", start_time + timedelta(hours=24))

                # Calculate hora timings
                self.progress_signal.emit(30, "Calculating hora timings...")
                hora_df = hora_calc.get_hora_transitions(start_time, end_time)

                self.progress_signal.emit(95, "Finalizing hora results...")
                self.finished_signal.emit({"hora_timings": hora_df})

            elif self.calculation_type == "positions":
                # Import calculator
                from calculations.position_calculator import PositionCalculator

                # Set up calculator
                self.progress_signal.emit(10, "Initializing calculator...")
                position_calc = PositionCalculator(
                    latitude=self.settings["latitude"],
                    longitude=self.settings["longitude"],
                    timezone_str=self.settings["timezone"],
                    ayanamsa=self.settings["ayanamsa"],
                    house_system=self.settings["house_system"]
                )

                # Get parameters
                calc_time = self.kwargs.get("time", datetime.now())

                # Calculate positions
                self.progress_signal.emit(30, "Calculating planetary positions...")
                planets_df = position_calc.get_planet_positions(calc_time)

                self.progress_signal.emit(70, "Calculating house positions...")
                houses_df = position_calc.get_houses_data(calc_time)

                self.progress_signal.emit(95, "Finalizing position results...")
                self.finished_signal.emit({
                    "planet_positions": planets_df,
                    "house_positions": houses_df
                })

            else:
                self.error_signal.emit(f"Unknown calculation type: {self.calculation_type}")
                return

            self.progress_signal.emit(100, "Calculation complete!")

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.error_signal.emit(f"Error during {self.calculation_type} calculation: {str(e)}\n{traceback_str}")


class MainWindow(QMainWindow):
    """Main window for the KP Astrology Dashboard application."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.init_ui()

        # Default settings
        self.settings = {
            "latitude": 19.0760,  # Mumbai
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata",
            "ayanamsa": "Krishnamurti",
            "house_system": "Placidus",
            "aspects": [0, 90, 180],
            "aspect_planets": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
            "yoga_days_past": 7,
            "yoga_days_future": 30,
            "calculation_interval": 10,  # minutes
        }

        # History of calculation results
        self.results_history = {}

        # Start a timer to update the status bar clock
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        self.update_clock()

    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("KP Astrology Dashboard")
        self.setMinimumSize(1024, 768)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget for main content
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setTabShape(QTabWidget.Rounded)

        # Create main tabs
        self.create_dashboard_tab()
        self.create_chart_tab()
        self.create_yoga_tab()
        self.create_transits_tab()
        self.create_settings_tab()

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widgets to status bar
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)  # Hide initially
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Add clock to status bar
        self.clock_label = QLabel()
        self.status_bar.addPermanentWidget(self.clock_label)

        # Create menus
        self.create_menus()

        # Create toolbar
        self.create_toolbar()

    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)

        # Add welcome message
        welcome_label = QLabel("KP Astrology Dashboard")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        dashboard_layout.addWidget(welcome_label)

        # Add description
        desc_label = QLabel(
            "A high-precision Krishnamurti Paddhati (KP) astrology calculator with "
            "convenient UI and Excel export functionality."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 12))
        dashboard_layout.addWidget(desc_label)

        # Add date/time panel
        self.date_time_panel = DateTimePanel()
        dashboard_layout.addWidget(self.date_time_panel)

        # Add quick action buttons
        actions_layout = QHBoxLayout()

        calculate_positions_btn = QPushButton("Calculate Current Positions")
        calculate_positions_btn.clicked.connect(self.calculate_current_positions)
        actions_layout.addWidget(calculate_positions_btn)

        calculate_hora_btn = QPushButton("Calculate Hora Timings")
        calculate_hora_btn.clicked.connect(self.calculate_hora_timings)
        actions_layout.addWidget(calculate_hora_btn)

        dashboard_layout.addLayout(actions_layout)

        # Add the tab
        self.tab_widget.addTab(dashboard_widget, "Dashboard")

    def create_chart_tab(self):
        """Create the chart tab."""
        self.chart_panel = ChartPanel()
        self.tab_widget.addTab(self.chart_panel, "Chart")

    def create_yoga_tab(self):
        """Create the yoga tab."""
        self.yoga_panel = YogaPanel()
        self.tab_widget.addTab(self.yoga_panel, "Yogas")

    def create_transits_tab(self):
        """Create the transits tab."""
        transit_widget = QWidget()
        transit_layout = QVBoxLayout(transit_widget)

        # Add transit controls
        controls_layout = QHBoxLayout()

        # Add planet selection
        from .planet_selector import PlanetSelector
        self.planet_selector = PlanetSelector()
        controls_layout.addWidget(self.planet_selector)

        # Add time range selection
        time_range_label = QLabel("Time Range:")
        controls_layout.addWidget(time_range_label)

        from .time_range_selector import TimeRangeSelector
        self.time_range_selector = TimeRangeSelector()
        controls_layout.addWidget(self.time_range_selector)

        # Add calculate button
        calculate_btn = QPushButton("Calculate Transits")
        calculate_btn.clicked.connect(self.calculate_transits)
        controls_layout.addWidget(calculate_btn)

        transit_layout.addLayout(controls_layout)

        # Add transit results area (placeholder)
        self.transit_results_widget = QStackedWidget()
        transit_layout.addWidget(self.transit_results_widget)

        # Add empty message panel initially
        message_panel = MessagePanel("No transit data calculated yet. Click 'Calculate Transits' to begin.")
        self.transit_results_widget.addWidget(message_panel)

        # Add the tab
        self.tab_widget.addTab(transit_widget, "Transits")

    def create_settings_tab(self):
        """Create the settings tab."""
        self.settings_panel = SettingsPanel(self.settings)
        self.settings_panel.settings_changed.connect(self.update_settings)
        self.tab_widget.addTab(self.settings_panel, "Settings")

    def create_menus(self):
        """Create the application menus."""
        # Create main menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        export_action = QAction("&Export to Excel", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Calculate menu
        calc_menu = menu_bar.addMenu("&Calculate")

        positions_action = QAction("Planetary &Positions", self)
        positions_action.triggered.connect(self.calculate_current_positions)
        calc_menu.addAction(positions_action)

        hora_action = QAction("&Hora Timings", self)
        hora_action.triggered.connect(self.calculate_hora_timings)
        calc_menu.addAction(hora_action)

        calc_menu.addSeparator()

        transits_action = QAction("&Transits", self)
        transits_action.triggered.connect(self.calculate_transits)
        calc_menu.addAction(transits_action)

        yogas_action = QAction("&Yogas", self)
        yogas_action.triggered.connect(self.calculate_yogas)
        calc_menu.addAction(yogas_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setFloatable(False)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add toolbar actions
        positions_action = QAction("Positions", self)
        positions_action.triggered.connect(self.calculate_current_positions)
        toolbar.addAction(positions_action)

        hora_action = QAction("Hora", self)
        hora_action.triggered.connect(self.calculate_hora_timings)
        toolbar.addAction(hora_action)

        toolbar.addSeparator()

        transits_action = QAction("Transits", self)
        transits_action.triggered.connect(self.calculate_transits)
        toolbar.addAction(transits_action)

        yogas_action = QAction("Yogas", self)
        yogas_action.triggered.connect(self.calculate_yogas)
        toolbar.addAction(yogas_action)

        toolbar.addSeparator()

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_to_excel)
        toolbar.addAction(export_action)

    def update_clock(self):
        """Update the clock in the status bar."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.setText(current_time)

    def update_settings(self, new_settings):
        """
        Update application settings.

        Args:
            new_settings: Dictionary with updated settings
        """
        self.settings.update(new_settings)
        print("Settings updated:", self.settings)

    def show_progress_dialog(self, title, message):
        """
        Show a progress dialog for long-running operations.

        Args:
            title: Dialog title
            message: Initial message

        Returns:
            ProgressDialog instance
        """
        progress_dialog = ProgressDialog(title, message, self)
        progress_dialog.show()
        return progress_dialog

    def calculate_current_positions(self):
        """Calculate current planetary positions."""
        # Get current time or selected time from date/time panel
        selected_time = self.date_time_panel.get_selected_datetime()

        # Create and start calculation thread
        self.position_thread = CalculationThread(
            settings=self.settings,
            calculation_type="positions",
            time=selected_time
        )

        # Show progress dialog
        self.progress_dialog = self.show_progress_dialog(
            "Calculating Positions",
            "Initializing calculation..."
        )

        # Connect signals
        self.position_thread.progress_signal.connect(self.progress_dialog.update_progress)
        self.position_thread.finished_signal.connect(self.handle_position_results)
        self.position_thread.error_signal.connect(self.handle_calculation_error)

        # Start the calculation
        self.position_thread.start()

    def handle_position_results(self, results):
        """
        Handle results from position calculation.

        Args:
            results: Dictionary with position results
        """
        # Close progress dialog
        self.progress_dialog.accept()

        # Store results
        self.results_history["positions"] = results

        # Update chart panel
        self.chart_panel.update_planet_positions(results.get("planet_positions"))
        self.chart_panel.update_house_positions(results.get("house_positions"))

        # Show success message
        QMessageBox.information(
            self,
            "Calculation Complete",
            "Planetary positions calculated successfully."
        )

        # Switch to chart tab
        self.tab_widget.setCurrentWidget(self.chart_panel)

    def calculate_hora_timings(self):
        """Calculate hora timings for the day."""
        # Get current date or selected date from date/time panel
        selected_date = self.date_time_panel.get_selected_datetime()

        # Set time range for full day
        start_time = selected_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1, seconds=-1)

        # Create and start calculation thread
        self.hora_thread = CalculationThread(
            settings=self.settings,
            calculation_type="hora",
            start_time=start_time,
            end_time=end_time
        )

        # Show progress dialog
        self.progress_dialog = self.show_progress_dialog(
            "Calculating Hora Timings",
            "Initializing calculation..."
        )

        # Connect signals
        self.hora_thread.progress_signal.connect(self.progress_dialog.update_progress)
        self.hora_thread.finished_signal.connect(self.handle_hora_results)
        self.hora_thread.error_signal.connect(self.handle_calculation_error)

        # Start the calculation
        self.hora_thread.start()

    def handle_hora_results(self, results):
        """
        Handle results from hora calculation.

        Args:
            results: Dictionary with hora results
        """
        # Close progress dialog
        self.progress_dialog.accept()

        # Store results
        self.results_history["hora"] = results

        # Update chart panel
        self.chart_panel.update_hora_timings(results.get("hora_timings"))

        # Show success message
        QMessageBox.information(
            self,
            "Calculation Complete",
            "Hora timings calculated successfully."
        )

        # Switch to chart tab
        self.tab_widget.setCurrentWidget(self.chart_panel)

    def calculate_transits(self):
        """Calculate planetary transits."""
        # Get selected planets from planet selector
        selected_planets = self.planet_selector.get_selected_planets()
        if not selected_planets:
            QMessageBox.warning(
                self,
                "No Planets Selected",
                "Please select at least one planet for transit calculation."
            )
            return

        # Get time range from time range selector
        start_time, end_time = self.time_range_selector.get_time_range()
        if not start_time or not end_time:
            QMessageBox.warning(
                self,
                "Invalid Time Range",
                "Please specify a valid time range for transit calculation."
            )
            return

        # Get calculation interval
        interval = self.settings.get("calculation_interval", 10)

        # Create and start calculation thread
        self.transit_thread = CalculationThread(
            settings=self.settings,
            calculation_type="transit",
            start_time=start_time,
            end_time=end_time,
            planets=selected_planets,
            interval=interval
        )

        # Show progress dialog
        self.progress_dialog = self.show_progress_dialog(
            "Calculating Transits",
            "Initializing calculation..."
        )

        # Connect signals
        self.transit_thread.progress_signal.connect(self.progress_dialog.update_progress)
        self.transit_thread.finished_signal.connect(self.handle_transit_results)
        self.transit_thread.error_signal.connect(self.handle_calculation_error)

        # Start the calculation
        self.transit_thread.start()

    def handle_transit_results(self, results):
        """
        Handle results from transit calculation.

        Args:
            results: Dictionary with transit results
        """
        # Close progress dialog
        self.progress_dialog.accept()

        # Store results
        self.results_history["transits"] = results

        # Create transit display widget
        from .transit_display import TransitDisplay
        transit_display = TransitDisplay(results)

        # Replace the placeholder in the stacked widget
        if self.transit_results_widget.count() > 0:
            old_widget = self.transit_results_widget.currentWidget()
            self.transit_results_widget.removeWidget(old_widget)
            old_widget.deleteLater()

        self.transit_results_widget.addWidget(transit_display)
        self.transit_results_widget.setCurrentWidget(transit_display)

        # Show success message
        QMessageBox.information(
            self,
            "Calculation Complete",
            f"Transits calculated successfully for {len(results)} planets."
        )

        # Switch to transits tab
        self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.transit_results_widget.parent()))

    def calculate_yogas(self):
        """Calculate yogas for a time period."""
        # Get current date from date/time panel
        reference_date = self.date_time_panel.get_selected_datetime()

        # Set time range based on settings
        days_past = self.settings.get("yoga_days_past", 7)
        days_future = self.settings.get("yoga_days_future", 30)

        start_time = reference_date - timedelta(days=days_past)
        end_time = reference_date + timedelta(days=days_future)

        # Create and start calculation thread
        self.yoga_thread = CalculationThread(
            settings=self.settings,
            calculation_type="yoga",
            start_time=start_time,
            end_time=end_time,
            interval=self.settings.get("calculation_interval", 30)
        )

        # Show progress dialog
        self.progress_dialog = self.show_progress_dialog(
            "Calculating Yogas",
            "Initializing calculation..."
        )

        # Connect signals
        self.yoga_thread.progress_signal.connect(self.progress_dialog.update_progress)
        self.yoga_thread.finished_signal.connect(self.handle_yoga_results)
        self.yoga_thread.error_signal.connect(self.handle_calculation_error)

        # Start the calculation
        self.yoga_thread.start()

    def handle_yoga_results(self, results):
        """
        Handle results from yoga calculation.

        Args:
            results: Dictionary with yoga results
        """
        # Close progress dialog
        self.progress_dialog.accept()

        # Store results
        self.results_history["yogas"] = results

        # Update yoga panel
        self.yoga_panel.update_yoga_results(results)

        # Show success message
        QMessageBox.information(
            self,
            "Calculation Complete",
            "Yoga calculation completed successfully."
        )

        # Switch to yoga tab
        self.tab_widget.setCurrentWidget(self.yoga_panel)

    def handle_calculation_error(self, error_message):
        """
        Handle error from calculation thread.

        Args:
            error_message: Error message
        """
        # Close progress dialog
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.accept()

        # Show error message
        QMessageBox.critical(
            self,
            "Calculation Error",
            error_message
        )

        # Update status
        self.status_label.setText("Error occurred")

    def export_to_excel(self):
        """Export calculation results to Excel."""
        # Check if we have any results to export
        if not self.results_history:
            QMessageBox.warning(
                self,
                "No Data",
                "No calculation results available to export."
            )
            return

        # Let user choose export location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "KP_Astrology_Report.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return  # User cancelled

        try:
            # Show progress dialog
            progress_dialog = self.show_progress_dialog(
                "Exporting to Excel",
                "Preparing export..."
            )

            # Import exporter here to avoid circular imports
            from export.excel_exporter import ExcelExporter
            exporter = ExcelExporter()

            # Prepare data for export
            progress_dialog.update_progress(10, "Collecting data...")

            export_data = {}

            # Add position data if available
            if "positions" in self.results_history:
                positions = self.results_history["positions"]
                if "planet_positions" in positions:
                    export_data["Planet Positions"] = positions["planet_positions"]
                if "house_positions" in positions:
                    export_data["House Positions"] = positions["house_positions"]

            # Add hora data if available
            if "hora" in self.results_history and "hora_timings" in self.results_history["hora"]:
                export_data["Hora Timing"] = self.results_history["hora"]["hora_timings"]

            # Add transit data if available
            if "transits" in self.results_history:
                for planet, df in self.results_history["transits"].items():
                    export_data[f"{planet} Transits"] = df

            # Add yoga data if available
            if "yogas" in self.results_history and "yoga_results" in self.results_history["yogas"]:
                export_data["Yogas"] = self.results_history["yogas"]["yoga_results"]

            # Perform export
            progress_dialog.update_progress(50, "Exporting to Excel...")
            exporter.export_to_excel(export_data, file_path)

            progress_dialog.update_progress(100, "Export complete!")
            progress_dialog.accept()

            # Show success message
            QMessageBox.information(
                self,
                "Export Complete",
                f"Data has been exported to {file_path}"
            )

            # Open the file
            self.open_excel_file(file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error exporting to Excel: {str(e)}"
            )

    def open_excel_file(self, filepath):
        """
        Open an Excel file using the default application.

        Args:
            filepath: Path to Excel file
        """
        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.call(['open', filepath])
            else:  # Linux
                import subprocess
                subprocess.call(['xdg-open', filepath])
        except Exception as e:
            print(f"Error opening Excel file: {str(e)}")

    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About KP Astrology Dashboard",
            "<h2>KP Astrology Dashboard</h2>"
            "<p>A high-precision Krishnamurti Paddhati (KP) astrology calculator "
            "with convenient UI and Excel export functionality.</p>"
            "<p>Version 1.0.0</p>"
            "<p>&copy; 2025 All rights reserved</p>"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # Check if there are any running calculations
        if hasattr(self, 'position_thread') and self.position_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A calculation is still running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        # Accept the event and close the window
        event.accept()