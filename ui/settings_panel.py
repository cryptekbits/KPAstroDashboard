"""
Settings panel for KP Astrology Dashboard.
"""
from typing import Dict, List, Optional
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QCheckBox, QSlider,
    QSpinBox, QFormLayout, QTabWidget, QScrollArea,
    QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal


class SettingsPanel(QScrollArea):
    """Settings panel for application configuration."""

    # Signal emitted when settings are changed
    settings_changed = pyqtSignal(dict)

    def __init__(self, settings: Dict = None, parent=None):
        """
        Initialize the settings panel.

        Args:
            settings: Initial settings dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings = settings or {}
        self.init_ui()

        # Load settings from file if available
        self.load_settings()

        # Update UI with settings
        self.update_ui_from_settings()

    def init_ui(self):
        """Set up the user interface."""
        # Make the scroll area fill its parent
        self.setWidgetResizable(True)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create tab widget for settings categories
        self.tab_widget = QTabWidget()

        # Create tabs for different setting categories
        self.create_location_tab()
        self.create_calculation_tab()
        self.create_yoga_tab()
        self.create_display_tab()
        self.create_advanced_tab()

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Create save/load/reset buttons
        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)

        self.load_button = QPushButton("Load Settings")
        self.load_button.clicked.connect(self.load_settings_dialog)

        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.reset_button)

        main_layout.addLayout(buttons_layout)

        # Apply button
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)

        main_layout.addWidget(self.apply_button)

    def create_location_tab(self):
        """Create the location settings tab."""
        location_widget = QWidget()
        location_layout = QVBoxLayout(location_widget)

        # Location presets
        presets_group = QGroupBox("Location Presets")
        presets_layout = QVBoxLayout(presets_group)

        preset_selection_layout = QHBoxLayout()
        preset_label = QLabel("Select Preset:")
        self.location_preset_combo = QComboBox()
        self.location_preset_combo.addItems([
            "Mumbai, India",
            "Delhi, India",
            "Chennai, India",
            "Kolkata, India",
            "New York, USA",
            "London, UK",
            "Sydney, Australia",
            "Tokyo, Japan",
            "Custom"
        ])
        self.location_preset_combo.currentIndexChanged.connect(self.on_location_preset_changed)

        preset_selection_layout.addWidget(preset_label)
        preset_selection_layout.addWidget(self.location_preset_combo)

        presets_layout.addLayout(preset_selection_layout)

        # Custom location settings
        custom_location_group = QGroupBox("Custom Location")
        custom_location_layout = QFormLayout(custom_location_group)

        self.latitude_edit = QLineEdit()
        self.latitude_edit.setPlaceholderText("e.g., 19.0760")
        self.latitude_edit.textChanged.connect(self.on_custom_location_changed)

        self.longitude_edit = QLineEdit()
        self.longitude_edit.setPlaceholderText("e.g., 72.8777")
        self.longitude_edit.textChanged.connect(self.on_custom_location_changed)

        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            "Asia/Kolkata",
            "America/New_York",
            "Europe/London",
            "Australia/Sydney",
            "Asia/Tokyo"
        ])
        self.timezone_combo.setEditable(True)
        self.timezone_combo.currentTextChanged.connect(self.on_custom_location_changed)

        custom_location_layout.addRow("Latitude:", self.latitude_edit)
        custom_location_layout.addRow("Longitude:", self.longitude_edit)
        custom_location_layout.addRow("Timezone:", self.timezone_combo)

        # Add groups to layout
        location_layout.addWidget(presets_group)
        location_layout.addWidget(custom_location_group)
        location_layout.addStretch()

        # Add to tab widget
        self.tab_widget.addTab(location_widget, "Location")

    def create_calculation_tab(self):
        """Create the calculation settings tab."""
        calculation_widget = QWidget()
        calculation_layout = QVBoxLayout(calculation_widget)

        # Ayanamsa settings
        ayanamsa_group = QGroupBox("Ayanamsa")
        ayanamsa_layout = QFormLayout(ayanamsa_group)

        self.ayanamsa_combo = QComboBox()
        self.ayanamsa_combo.addItems([
            "Krishnamurti",
            "Lahiri",
            "Raman",
            "Krishnamurti_New",
            "Lahiri_1940",
            "Lahiri_VP285",
            "Lahiri_ICRC",
            "Yukteshwar"
        ])

        ayanamsa_layout.addRow("Ayanamsa System:", self.ayanamsa_combo)

        # House system settings
        house_system_group = QGroupBox("House System")
        house_system_layout = QFormLayout(house_system_group)

        self.house_system_combo = QComboBox()
        self.house_system_combo.addItems([
            "Placidus",
            "Equal",
            "Equal 2",
            "Whole Sign"
        ])

        house_system_layout.addRow("House System:", self.house_system_combo)

        # Calculation interval settings
        interval_group = QGroupBox("Calculation Intervals")
        interval_layout = QFormLayout(interval_group)

        self.calculation_interval_spin = QSpinBox()
        self.calculation_interval_spin.setRange(1, 60)
        self.calculation_interval_spin.setValue(10)
        self.calculation_interval_spin.setSuffix(" minutes")

        interval_layout.addRow("Transit Calculation Interval:", self.calculation_interval_spin)

        # Aspects settings
        aspects_group = QGroupBox("Aspects")
        aspects_layout = QVBoxLayout(aspects_group)

        # Aspect selection
        aspect_selection_layout = QHBoxLayout()

        self.conjunction_cb = QCheckBox("Conjunction (0°)")
        self.conjunction_cb.setChecked(True)

        self.opposition_cb = QCheckBox("Opposition (180°)")
        self.opposition_cb.setChecked(True)

        self.trine_cb = QCheckBox("Trine (120°)")
        self.trine_cb.setChecked(False)

        aspect_selection_layout.addWidget(self.conjunction_cb)
        aspect_selection_layout.addWidget(self.opposition_cb)
        aspect_selection_layout.addWidget(self.trine_cb)

        aspect_selection_layout2 = QHBoxLayout()

        self.square_cb = QCheckBox("Square (90°)")
        self.square_cb.setChecked(True)

        self.sextile_cb = QCheckBox("Sextile (60°)")
        self.sextile_cb.setChecked(False)

        self.quincunx_cb = QCheckBox("Quincunx (150°)")
        self.quincunx_cb.setChecked(False)

        aspect_selection_layout2.addWidget(self.square_cb)
        aspect_selection_layout2.addWidget(self.sextile_cb)
        aspect_selection_layout2.addWidget(self.quincunx_cb)

        aspects_layout.addLayout(aspect_selection_layout)
        aspects_layout.addLayout(aspect_selection_layout2)

        # Planet selection for aspects
        planet_selection_label = QLabel("Calculate aspects for:")
        aspects_layout.addWidget(planet_selection_label)

        planet_selection_layout = QHBoxLayout()

        self.sun_aspect_cb = QCheckBox("Sun")
        self.sun_aspect_cb.setChecked(True)

        self.moon_aspect_cb = QCheckBox("Moon")
        self.moon_aspect_cb.setChecked(True)

        self.mercury_aspect_cb = QCheckBox("Mercury")
        self.mercury_aspect_cb.setChecked(True)

        self.venus_aspect_cb = QCheckBox("Venus")
        self.venus_aspect_cb.setChecked(True)

        planet_selection_layout.addWidget(self.sun_aspect_cb)
        planet_selection_layout.addWidget(self.moon_aspect_cb)
        planet_selection_layout.addWidget(self.mercury_aspect_cb)
        planet_selection_layout.addWidget(self.venus_aspect_cb)

        planet_selection_layout2 = QHBoxLayout()

        self.mars_aspect_cb = QCheckBox("Mars")
        self.mars_aspect_cb.setChecked(True)

        self.jupiter_aspect_cb = QCheckBox("Jupiter")
        self.jupiter_aspect_cb.setChecked(True)

        self.saturn_aspect_cb = QCheckBox("Saturn")
        self.saturn_aspect_cb.setChecked(True)

        self.nodes_aspect_cb = QCheckBox("Rahu/Ketu")
        self.nodes_aspect_cb.setChecked(True)

        planet_selection_layout2.addWidget(self.mars_aspect_cb)
        planet_selection_layout2.addWidget(self.jupiter_aspect_cb)
        planet_selection_layout2.addWidget(self.saturn_aspect_cb)
        planet_selection_layout2.addWidget(self.nodes_aspect_cb)

        aspects_layout.addLayout(planet_selection_layout)
        aspects_layout.addLayout(planet_selection_layout2)

        # Add groups to layout
        calculation_layout.addWidget(ayanamsa_group)
        calculation_layout.addWidget(house_system_group)
        calculation_layout.addWidget(interval_group)
        calculation_layout.addWidget(aspects_group)
        calculation_layout.addStretch()

        # Add to tab widget
        self.tab_widget.addTab(calculation_widget, "Calculation")

    def create_yoga_tab(self):
        """Create the yoga settings tab."""
        yoga_widget = QWidget()
        yoga_layout = QVBoxLayout(yoga_widget)

        # Yoga time range settings
        time_range_group = QGroupBox("Yoga Calculation Time Range")
        time_range_layout = QFormLayout(time_range_group)

        self.yoga_days_past_spin = QSpinBox()
        self.yoga_days_past_spin.setRange(0, 365)
        self.yoga_days_past_spin.setValue(7)
        self.yoga_days_past_spin.setSuffix(" days")

        self.yoga_days_future_spin = QSpinBox()
        self.yoga_days_future_spin.setRange(0, 365)
        self.yoga_days_future_spin.setValue(30)
        self.yoga_days_future_spin.setSuffix(" days")

        time_range_layout.addRow("Look Back:", self.yoga_days_past_spin)
        time_range_layout.addRow("Look Forward:", self.yoga_days_future_spin)

        # Yoga types to include
        yoga_types_group = QGroupBox("Yoga Types to Include")
        yoga_types_layout = QVBoxLayout(yoga_types_group)

        self.positive_yoga_cb = QCheckBox("Positive Yogas")
        self.positive_yoga_cb.setChecked(True)

        self.negative_yoga_cb = QCheckBox("Negative Yogas")
        self.negative_yoga_cb.setChecked(True)

        self.neutral_yoga_cb = QCheckBox("Neutral Yogas")
        self.neutral_yoga_cb.setChecked(True)

        yoga_types_layout.addWidget(self.positive_yoga_cb)
        yoga_types_layout.addWidget(self.negative_yoga_cb)
        yoga_types_layout.addWidget(self.neutral_yoga_cb)

        # Yoga calculation interval
        yoga_interval_group = QGroupBox("Yoga Calculation Precision")
        yoga_interval_layout = QFormLayout(yoga_interval_group)

        self.yoga_interval_spin = QSpinBox()
        self.yoga_interval_spin.setRange(5, 120)
        self.yoga_interval_spin.setValue(30)
        self.yoga_interval_spin.setSuffix(" minutes")

        yoga_interval_layout.addRow("Check Interval:", self.yoga_interval_spin)

        # Add groups to layout
        yoga_layout.addWidget(time_range_group)
        yoga_layout.addWidget(yoga_types_group)
        yoga_layout.addWidget(yoga_interval_group)
        yoga_layout.addStretch()

        # Add to tab widget
        self.tab_widget.addTab(yoga_widget, "Yogas")

    def create_display_tab(self):
        """Create the display settings tab."""
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)

        # Chart display settings
        chart_display_group = QGroupBox("Chart Display")
        chart_display_layout = QVBoxLayout(chart_display_group)

        self.show_aspects_cb = QCheckBox("Show Aspects in Chart")
        self.show_aspects_cb.setChecked(True)

        self.show_dignities_cb = QCheckBox("Show Planetary Dignities")
        self.show_dignities_cb.setChecked(True)

        self.north_indian_style_cb = QCheckBox("Use North Indian Chart Style")
        self.north_indian_style_cb.setChecked(False)

        chart_display_layout.addWidget(self.show_aspects_cb)
        chart_display_layout.addWidget(self.show_dignities_cb)
        chart_display_layout.addWidget(self.north_indian_style_cb)

        # Time format settings
        time_format_group = QGroupBox("Time Format")
        time_format_layout = QVBoxLayout(time_format_group)

        self.use_24hr_cb = QCheckBox("Use 24-hour Format")
        self.use_24hr_cb.setChecked(False)

        self.show_seconds_cb = QCheckBox("Show Seconds")
        self.show_seconds_cb.setChecked(True)

        time_format_layout.addWidget(self.use_24hr_cb)
        time_format_layout.addWidget(self.show_seconds_cb)

        # Add groups to layout
        display_layout.addWidget(chart_display_group)
        display_layout.addWidget(time_format_group)
        display_layout.addStretch()

        # Add to tab widget
        self.tab_widget.addTab(display_widget, "Display")

    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)

        # File paths
        paths_group = QGroupBox("File Paths")
        paths_layout = QFormLayout(paths_group)

        self.kp_data_path_edit = QLineEdit()
        self.kp_data_path_edit.setPlaceholderText("Path to KP_SL_Divisions.csv")

        data_path_layout = QHBoxLayout()
        data_path_layout.addWidget(self.kp_data_path_edit)

        browse_data_btn = QPushButton("Browse...")
        browse_data_btn.clicked.connect(self.browse_kp_data)
        data_path_layout.addWidget(browse_data_btn)

        paths_layout.addRow("KP Data File:", data_path_layout)

        # Swiss Ephemeris settings
        ephemeris_group = QGroupBox("Swiss Ephemeris")
        ephemeris_layout = QFormLayout(ephemeris_group)

        self.ephemeris_path_edit = QLineEdit()

        eph_path_layout = QHBoxLayout()
        eph_path_layout.addWidget(self.ephemeris_path_edit)

        browse_eph_btn = QPushButton("Browse...")
        browse_eph_btn.clicked.connect(self.browse_ephemeris)
        eph_path_layout.addWidget(browse_eph_btn)

        ephemeris_layout.addRow("Ephemeris Path:", eph_path_layout)

        # Memory settings
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QFormLayout(memory_group)

        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" MB")

        memory_layout.addRow("Cache Size:", self.cache_size_spin)

        # Performance settings
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)

        self.parallel_calcs_cb = QCheckBox("Use Parallel Calculations")
        self.parallel_calcs_cb.setChecked(True)

        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 32)
        self.max_threads_spin.setValue(4)

        performance_layout.addRow("", self.parallel_calcs_cb)
        performance_layout.addRow("Max Threads:", self.max_threads_spin)

        # Add groups to layout
        advanced_layout.addWidget(paths_group)
        advanced_layout.addWidget(ephemeris_group)
        advanced_layout.addWidget(memory_group)
        advanced_layout.addWidget(performance_group)
        advanced_layout.addStretch()

        # Add to tab widget
        self.tab_widget.addTab(advanced_widget, "Advanced")

    def on_location_preset_changed(self, index):
        """
        Handle location preset selection change.

        Args:
            index: Selected preset index
        """
        # Define preset coordinates
        presets = {
            "Mumbai, India": {"latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
            "Delhi, India": {"latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
            "Chennai, India": {"latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata"},
            "Kolkata, India": {"latitude": 22.5726, "longitude": 88.3639, "timezone": "Asia/Kolkata"},
            "New York, USA": {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
            "London, UK": {"latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
            "Sydney, Australia": {"latitude": -33.8688, "longitude": 151.2093, "timezone": "Australia/Sydney"},
            "Tokyo, Japan": {"latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo"}
        }

        # Get selected preset name
        preset_name = self.location_preset_combo.currentText()

        # If "Custom" is selected, don't update fields
        if preset_name == "Custom":
            return

        # Update fields with preset values
        preset = presets.get(preset_name)
        if preset:
            self.latitude_edit.setText(str(preset["latitude"]))
            self.longitude_edit.setText(str(preset["longitude"]))

            # Find and select the timezone
            timezone_index = self.timezone_combo.findText(preset["timezone"])
            if timezone_index >= 0:
                self.timezone_combo.setCurrentIndex(timezone_index)
            else:
                self.timezone_combo.setCurrentText(preset["timezone"])

    def on_custom_location_changed(self):
        """Handle changes to custom location fields."""
        # Set combo box to "Custom" when custom fields are modified
        current_preset = self.location_preset_combo.currentText()
        if current_preset != "Custom":
            # Find and select "Custom"
            custom_index = self.location_preset_combo.findText("Custom")
            if custom_index >= 0:
                self.location_preset_combo.setCurrentIndex(custom_index)

    def browse_kp_data(self):
        """Open file dialog to select KP data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select KP Data File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            self.kp_data_path_edit.setText(file_path)

    def browse_ephemeris(self):
        """Open file dialog to select ephemeris directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Ephemeris Directory"
        )

        if directory:
            self.ephemeris_path_edit.setText(directory)

    def get_settings(self):
        """
        Get current settings from UI controls.

        Returns:
            dict: Settings dictionary
        """
        # Location settings
        try:
            latitude = float(self.latitude_edit.text())
        except ValueError:
            latitude = 0.0

        try:
            longitude = float(self.longitude_edit.text())
        except ValueError:
            longitude = 0.0

        timezone = self.timezone_combo.currentText()

        # Calculation settings
        ayanamsa = self.ayanamsa_combo.currentText()
        house_system = self.house_system_combo.currentText()
        calculation_interval = self.calculation_interval_spin.value()

        # Aspect settings
        aspects = []
        if self.conjunction_cb.isChecked():
            aspects.append(0)
        if self.opposition_cb.isChecked():
            aspects.append(180)
        if self.trine_cb.isChecked():
            aspects.append(120)
        if self.square_cb.isChecked():
            aspects.append(90)
        if self.sextile_cb.isChecked():
            aspects.append(60)
        if self.quincunx_cb.isChecked():
            aspects.append(150)

        # Planet selection for aspects
        aspect_planets = []
        if self.sun_aspect_cb.isChecked():
            aspect_planets.append("Sun")
        if self.moon_aspect_cb.isChecked():
            aspect_planets.append("Moon")
        if self.mercury_aspect_cb.isChecked():
            aspect_planets.append("Mercury")
        if self.venus_aspect_cb.isChecked():
            aspect_planets.append("Venus")
        if self.mars_aspect_cb.isChecked():
            aspect_planets.append("Mars")
        if self.jupiter_aspect_cb.isChecked():
            aspect_planets.append("Jupiter")
        if self.saturn_aspect_cb.isChecked():
            aspect_planets.append("Saturn")
        if self.nodes_aspect_cb.isChecked():
            aspect_planets.append("Rahu")
            aspect_planets.append("Ketu")

        # Yoga settings
        yoga_days_past = self.yoga_days_past_spin.value()
        yoga_days_future = self.yoga_days_future_spin.value()

        # Yoga types to include
        yoga_types = []
        if self.positive_yoga_cb.isChecked():
            yoga_types.append("positive")
        if self.negative_yoga_cb.isChecked():
            yoga_types.append("negative")
        if self.neutral_yoga_cb.isChecked():
            yoga_types.append("neutral")

        yoga_interval = self.yoga_interval_spin.value()

        # Display settings
        show_aspects = self.show_aspects_cb.isChecked()
        show_dignities = self.show_dignities_cb.isChecked()
        north_indian_style = self.north_indian_style_cb.isChecked()
        use_24hr = self.use_24hr_cb.isChecked()
        show_seconds = self.show_seconds_cb.isChecked()

        # Advanced settings
        kp_data_path = self.kp_data_path_edit.text()
        ephemeris_path = self.ephemeris_path_edit.text()
        cache_size = self.cache_size_spin.value()
        parallel_calcs = self.parallel_calcs_cb.isChecked()
        max_threads = self.max_threads_spin.value()

        # Combine all settings
        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "ayanamsa": ayanamsa,
            "house_system": house_system,
            "calculation_interval": calculation_interval,
            "aspects": aspects,
            "aspect_planets": aspect_planets,
            "yoga_days_past": yoga_days_past,
            "yoga_days_future": yoga_days_future,
            "yoga_types": yoga_types,
            "yoga_interval": yoga_interval,
            "show_aspects": show_aspects,
            "show_dignities": show_dignities,
            "north_indian_style": north_indian_style,
            "use_24hr": use_24hr,
            "show_seconds": show_seconds,
            "kp_data_path": kp_data_path,
            "ephemeris_path": ephemeris_path,
            "cache_size": cache_size,
            "parallel_calcs": parallel_calcs,
            "max_threads": max_threads
        }

    def update_ui_from_settings(self):
        """Update UI controls with current settings."""
        # Location settings
        latitude = self.settings.get("latitude", 0.0)
        longitude = self.settings.get("longitude", 0.0)
        timezone = self.settings.get("timezone", "UTC")

        self.latitude_edit.setText(str(latitude))
        self.longitude_edit.setText(str(longitude))

        # Find and select the timezone
        timezone_index = self.timezone_combo.findText(timezone)
        if timezone_index >= 0:
            self.timezone_combo.setCurrentIndex(timezone_index)
        else:
            self.timezone_combo.setCurrentText(timezone)

        # Try to find matching preset
        found_preset = False
        for i in range(self.location_preset_combo.count()):
            preset_name = self.location_preset_combo.itemText(i)
            if preset_name == "Custom":
                continue

            # Define preset coordinates
            presets = {
                "Mumbai, India": {"latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
                "Delhi, India": {"latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "Chennai, India": {"latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata"},
                "Kolkata, India": {"latitude": 22.5726, "longitude": 88.3639, "timezone": "Asia/Kolkata"},
                "New York, USA": {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
                "London, UK": {"latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
                "Sydney, Australia": {"latitude": -33.8688, "longitude": 151.2093, "timezone": "Australia/Sydney"},
                "Tokyo, Japan": {"latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo"}
            }

            preset = presets.get(preset_name)
            if preset and abs(preset["latitude"] - latitude) < 0.001 and abs(preset["longitude"] - longitude) < 0.001:
                self.location_preset_combo.setCurrentIndex(i)
                found_preset = True
                break

        if not found_preset:
            # Set to "Custom"
            custom_index = self.location_preset_combo.findText("Custom")
            if custom_index >= 0:
                self.location_preset_combo.setCurrentIndex(custom_index)

        # Calculation settings
        ayanamsa = self.settings.get("ayanamsa", "Krishnamurti")
        house_system = self.settings.get("house_system", "Placidus")
        calculation_interval = self.settings.get("calculation_interval", 10)

        # Find and select ayanamsa
        ayanamsa_index = self.ayanamsa_combo.findText(ayanamsa)
        if ayanamsa_index >= 0:
            self.ayanamsa_combo.setCurrentIndex(ayanamsa_index)

        # Find and select house system
        house_system_index = self.house_system_combo.findText(house_system)
        if house_system_index >= 0:
            self.house_system_combo.setCurrentIndex(house_system_index)

        # Set calculation interval
        self.calculation_interval_spin.setValue(calculation_interval)

        # Aspect settings
        aspects = self.settings.get("aspects", [0, 90, 180])
        self.conjunction_cb.setChecked(0 in aspects)
        self.opposition_cb.setChecked(180 in aspects)
        self.trine_cb.setChecked(120 in aspects)
        self.square_cb.setChecked(90 in aspects)
        self.sextile_cb.setChecked(60 in aspects)
        self.quincunx_cb.setChecked(150 in aspects)

        # Planet selection for aspects
        aspect_planets = self.settings.get("aspect_planets", [])
        self.sun_aspect_cb.setChecked("Sun" in aspect_planets)
        self.moon_aspect_cb.setChecked("Moon" in aspect_planets)
        self.mercury_aspect_cb.setChecked("Mercury" in aspect_planets)
        self.venus_aspect_cb.setChecked("Venus" in aspect_planets)
        self.mars_aspect_cb.setChecked("Mars" in aspect_planets)
        self.jupiter_aspect_cb.setChecked("Jupiter" in aspect_planets)
        self.saturn_aspect_cb.setChecked("Saturn" in aspect_planets)
        self.nodes_aspect_cb.setChecked("Rahu" in aspect_planets or "Ketu" in aspect_planets)

        # Yoga settings
        yoga_days_past = self.settings.get("yoga_days_past", 7)
        yoga_days_future = self.settings.get("yoga_days_future", 30)
        yoga_interval = self.settings.get("yoga_interval", 30)

        self.yoga_days_past_spin.setValue(yoga_days_past)
        self.yoga_days_future_spin.setValue(yoga_days_future)
        self.yoga_interval_spin.setValue(yoga_interval)

        # Yoga types to include
        yoga_types = self.settings.get("yoga_types", ["positive", "negative", "neutral"])
        self.positive_yoga_cb.setChecked("positive" in yoga_types)
        self.negative_yoga_cb.setChecked("negative" in yoga_types)
        self.neutral_yoga_cb.setChecked("neutral" in yoga_types)

        # Display settings
        show_aspects = self.settings.get("show_aspects", True)
        show_dignities = self.settings.get("show_dignities", True)
        north_indian_style = self.settings.get("north_indian_style", False)
        use_24hr = self.settings.get("use_24hr", False)
        show_seconds = self.settings.get("show_seconds", True)

        self.show_aspects_cb.setChecked(show_aspects)
        self.show_dignities_cb.setChecked(show_dignities)
        self.north_indian_style_cb.setChecked(north_indian_style)
        self.use_24hr_cb.setChecked(use_24hr)
        self.show_seconds_cb.setChecked(show_seconds)

        # Advanced settings
        kp_data_path = self.settings.get("kp_data_path", "")
        ephemeris_path = self.settings.get("ephemeris_path", "")
        cache_size = self.settings.get("cache_size", 100)
        parallel_calcs = self.settings.get("parallel_calcs", True)
        max_threads = self.settings.get("max_threads", 4)

        self.kp_data_path_edit.setText(kp_data_path)
        self.ephemeris_path_edit.setText(ephemeris_path)
        self.cache_size_spin.setValue(cache_size)
        self.parallel_calcs_cb.setChecked(parallel_calcs)
        self.max_threads_spin.setValue(max_threads)

    def apply_settings(self):
        """Apply the current settings."""
        settings = self.get_settings()
        self.settings = settings
        self.settings_changed.emit(settings)

    def save_settings(self):
        """Save settings to file."""
        # Get current settings
        settings = self.get_settings()

        # Let user choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Settings",
            "kp_astrology_settings.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return  # User cancelled

        try:
            # Save settings to file
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=4)

            # Update internal settings
            self.settings = settings
            self.settings_changed.emit(settings)

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"Failed to save settings: {str(e)}"
            )

    def load_settings_dialog(self):
        """Load settings from file via dialog."""
        # Let user choose file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Settings",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return  # User cancelled

        self.load_settings_from_file(file_path)

    def load_settings(self):
        """Load settings from default file."""
        # Look for settings file in standard locations
        possible_paths = [
            "kp_astrology_settings.json",
            os.path.join(os.path.dirname(__file__), "..", "kp_astrology_settings.json"),
            os.path.expanduser("~/.kp_astrology_settings.json")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.load_settings_from_file(path)
                return

    def load_settings_from_file(self, file_path):
        """
        Load settings from a specific file.

        Args:
            file_path: Path to settings file
        """
        try:
            # Load settings from file
            with open(file_path, 'r') as f:
                settings = json.load(f)

            # Update settings
            self.settings = settings

            # Update UI
            self.update_ui_from_settings()

            # Emit signal
            self.settings_changed.emit(settings)

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error Loading Settings",
                f"Failed to load settings: {str(e)}"
            )

    def reset_settings(self):
        """Reset settings to defaults."""
        # Default settings
        default_settings = {
            "latitude": 19.0760,  # Mumbai
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata",
            "ayanamsa": "Krishnamurti",
            "house_system": "Placidus",
            "calculation_interval": 10,
            "aspects": [0, 90, 180],
            "aspect_planets": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"],
            "yoga_days_past": 7,
            "yoga_days_future": 30,
            "yoga_types": ["positive", "negative", "neutral"],
            "yoga_interval": 30,
            "show_aspects": True,
            "show_dignities": True,
            "north_indian_style": False,
            "use_24hr": False,
            "show_seconds": True,
            "kp_data_path": "",
            "ephemeris_path": "",
            "cache_size": 100,
            "parallel_calcs": True,
            "max_threads": 4
        }

        # Confirm with user
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Update settings
            self.settings = default_settings

            # Update UI
            self.update_ui_from_settings()

            # Emit signal
            self.settings_changed.emit(default_settings)