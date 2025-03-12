"""
Main tab for the KP Astrology application.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QGridLayout, QScrollArea, 
                            QComboBox, QDateEdit, QTimeEdit, QCompleter,
                            QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTime
import json
import os
import logging

from ui.components.yoga_controls import YogaControls
from ui.components.aspect_controls import AspectControls


class MainTab:
    """Main tab for the KP Astrology application."""

    def __init__(self, parent):
        """
        Initialize main tab.
        
        Parameters:
        -----------
        parent : QWidget
            Parent widget to attach the tab to
        """
        self.parent = parent
        self.main_layout = None
        self.sheet_checkboxes = {}
        self.yoga_controls = YogaControls(parent)
        self.aspect_controls = AspectControls(parent)
        self.date_picker = None
        self.time_picker = None
        self.location_combo = None
        self.status_label = None
        self.progress_bar = None
        self.generate_btn = None
        self.aspect_group = None
        self.aspect_planets_group = None
        
        # Load default settings after UI is created
        self.default_settings = self.load_default_settings()

    def setup_tab(self):
        """
        Set up the main tab.
        
        Returns:
        --------
        QWidget
            The main tab widget
        """
        # Create the main tab
        main_tab = QWidget()
        
        # Create a scroll area for the main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        
        # Set the scroll area as the main tab's layout
        main_tab_layout = QVBoxLayout(main_tab)
        main_tab_layout.addWidget(scroll_area)

        main_layout = QVBoxLayout(main_widget)
        
        # Store the main layout for later reference
        self.main_layout = main_layout

        # Location selection
        self.create_location_section(main_layout)

        # Date and time selection for the main calculation
        self.create_datetime_section(main_layout)

        # Yoga date range selection
        self.yoga_controls.create_yoga_group(main_layout)

        # Sheets selection
        self.create_sheets_section(main_layout)

        # Aspect selection
        self.aspect_group = self.aspect_controls.create_aspects_group(main_layout)
        
        # Planets for aspects selection
        self.aspect_planets_group = self.aspect_controls.create_aspect_planets_group(main_layout)

        # Progress bar and status label
        self.create_progress_section(main_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Generate button
        self.generate_btn = QPushButton("Generate Excel")
        self.generate_btn.clicked.connect(self.parent.generate_data)
        buttons_layout.addWidget(self.generate_btn)
        
        # Save Default button
        save_default_btn = QPushButton("Save Default")
        save_default_btn.setToolTip("Save current selections as default for next time")
        save_default_btn.clicked.connect(self.save_default)
        buttons_layout.addWidget(save_default_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Apply default settings after all UI components are created
        self.apply_default_settings()
        
        return main_tab

    def create_location_section(self, main_layout):
        """
        Create the location selection section.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the section to
        """
        location_group = QGroupBox("Location")
        location_layout = QHBoxLayout()
        location_group.setLayout(location_layout)

        # Create location dropdown
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)  # Make the combo box editable to work with QCompleter
        
        # Load locations from file
        locations = []
        try:
            locations_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                         'data_generators', 'locations.json')
            with open(locations_file, 'r') as f:
                locations_data = json.load(f)
                locations = [loc["name"] for loc in locations_data]
        except Exception as e:
            logging.error(f"Failed to load locations: {str(e)}")
            locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]

        self.location_combo.addItems(locations)
        self.location_combo.setCurrentText("Mumbai")

        # Add autocomplete
        completer = QCompleter(locations)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.location_combo.setCompleter(completer)

        location_layout.addWidget(QLabel("Location:"))
        location_layout.addWidget(self.location_combo)

        main_layout.addWidget(location_group)

    def create_datetime_section(self, main_layout):
        """
        Create the date and time selection section.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the section to
        """
        datetime_group = QGroupBox("Main Date and Time")
        datetime_layout = QVBoxLayout()
        datetime_group.setLayout(datetime_layout)

        # Separate date and time fields
        date_layout = QHBoxLayout()
        self.date_picker = QDateEdit()
        self.date_picker.setObjectName("date_picker")
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Date:"))
        date_layout.addWidget(self.date_picker)

        time_layout = QHBoxLayout()
        self.time_picker = QTimeEdit()
        self.time_picker.setObjectName("time_picker")
        self.time_picker.setTime(QTime(9, 0))  # Default to 9:00 AM
        self.time_picker.setDisplayFormat("hh:mm AP")
        time_layout.addWidget(QLabel("Time:"))
        time_layout.addWidget(self.time_picker)

        datetime_layout.addLayout(date_layout)
        datetime_layout.addLayout(time_layout)

        main_layout.addWidget(datetime_group)

    def create_sheets_section(self, main_layout):
        """
        Create the sheets selection section.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the section to
        """
        sheets_group = QGroupBox("Sheets to Generate")
        sheets_layout = QVBoxLayout()
        sheets_group.setLayout(sheets_layout)

        self.sheet_checkboxes = {}
        sheet_names = [
            "Planet Positions", "Hora Timing", "Moon", "Ascendant",
            "Sun", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Yogas"
        ]

        # Create a grid layout for checkboxes (2 columns)
        grid_layout = QGridLayout()
        row, col = 0, 0
        max_col = 2  # Number of columns

        for sheet_name in sheet_names:
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

    def create_progress_section(self, main_layout):
        """
        Create progress bar and status section.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the section to
        """
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

    def select_all_sheets(self):
        """Select all sheet checkboxes."""
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(True)

    def select_no_sheets(self):
        """Deselect all sheet checkboxes."""
        for checkbox in self.sheet_checkboxes.values():
            checkbox.setChecked(False)

    def update_visibility(self, config_settings):
        """
        Update the visibility of components in the main tab based on configuration settings.
        
        Parameters:
        -----------
        config_settings : dict
            Dictionary of configuration settings
        """
        # 1. Planet Positions (affects the Sheets to Generate section)
        if "Planet Positions" in self.sheet_checkboxes:
            self.sheet_checkboxes["Planet Positions"].setEnabled(config_settings["planet_pos"]["enabled"])
            if not config_settings["planet_pos"]["enabled"]:
                self.sheet_checkboxes["Planet Positions"].setChecked(False)
        
        # 2. Hora Timing checkbox
        if "Hora Timing" in self.sheet_checkboxes:
            self.sheet_checkboxes["Hora Timing"].setEnabled(config_settings["hora"]["enabled"])
            if not config_settings["hora"]["enabled"]:
                self.sheet_checkboxes["Hora Timing"].setChecked(False)
        
        # 3. Yogas checkbox
        if "Yogas" in self.sheet_checkboxes:
            self.sheet_checkboxes["Yogas"].setEnabled(config_settings["yoga"]["enabled"])
            if not config_settings["yoga"]["enabled"]:
                self.sheet_checkboxes["Yogas"].setChecked(False)
        
        # 4. Planet Transit checkboxes
        transit_sheets = ["Moon", "Ascendant", "Sun", "Mercury", "Venus", 
                         "Mars", "Jupiter", "Saturn", "Rahu", "Ketu",
                         "Uranus", "Neptune"]
        for sheet in transit_sheets:
            if sheet in self.sheet_checkboxes:
                self.sheet_checkboxes[sheet].setEnabled(config_settings["transit"]["enabled"])
                if not config_settings["transit"]["enabled"]:
                    self.sheet_checkboxes[sheet].setChecked(False)
                    
        # 5. Individual planet visibility based on planet_pos configuration
        if "planet_pos" in config_settings and "planets" in config_settings["planet_pos"]:
            planet_config = config_settings["planet_pos"]["planets"]
            for planet_name, enabled in planet_config.items():
                if planet_name in self.sheet_checkboxes:
                    # First reset the enabled state based on transit settings
                    if planet_name in transit_sheets:
                        is_transit_enabled = config_settings["transit"]["enabled"]
                        self.sheet_checkboxes[planet_name].setEnabled(is_transit_enabled)
                    
                    # Then apply planet_pos configuration
                    if not enabled and planet_name in self.sheet_checkboxes:
                        self.sheet_checkboxes[planet_name].setEnabled(False)
                        self.sheet_checkboxes[planet_name].setChecked(False)
        
        # 6. Update aspect controls visibility
        if "aspects" in config_settings:
            # Show/hide the entire aspect groups based on the main aspect toggle
            if self.aspect_group:
                self.aspect_group.setVisible(config_settings["aspects"]["enabled"])
            
            if self.aspect_planets_group:
                self.aspect_planets_group.setVisible(config_settings["aspects"]["enabled"])
            
            # Show/hide individual aspect checkboxes if aspect_list is available
            if "aspect_list" in config_settings["aspects"]:
                for angle_str, enabled in config_settings["aspects"]["aspect_list"].items():
                    angle = int(angle_str)
                    for checkbox in self.aspect_controls.aspect_checkboxes:
                        if hasattr(checkbox, 'angle') and checkbox.angle == angle:
                            # Only show enabled aspects if the main aspect toggle is enabled
                            checkbox.setVisible(
                                config_settings["aspects"]["enabled"] and enabled
                            )
        
            # 7. Update aspect planet checkboxes based on configuration
            if "aspect_planets" in config_settings["aspects"]:
                for planet_name, enabled in config_settings["aspects"]["aspect_planets"].items():
                    if planet_name in self.aspect_controls.aspect_planets_checkboxes:
                        # Only show enabled aspect planets if the main aspect toggle is enabled
                        self.aspect_controls.aspect_planets_checkboxes[planet_name].setVisible(
                            config_settings["aspects"]["enabled"] and enabled
                        )

    def get_selected_sheets(self):
        """
        Get the selected sheets.
        
        Returns:
        --------
        list
            List of selected sheet names
        """
        return [name for name, checkbox in self.sheet_checkboxes.items()
                if checkbox.isChecked()]

    def save_default(self):
        """
        Save the current user selections as default settings.
        This will save location, selected sheets, yoga time interval, and aspect settings,
        but not date or time values as these should default to today/current time.
        """
        try:
            import json
            import os
            from PyQt5.QtWidgets import QMessageBox
            
            # Get the config file path
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
            
            # Load existing config
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # If user_defaults doesn't exist, create it
            if 'user_defaults' not in config:
                config['user_defaults'] = {}
                
            # Save location
            config['user_defaults']['location'] = self.location_combo.currentText()
            
            # We do NOT save date and time as they should default to today and 9:00 AM
            
            # Save selected sheets
            config['user_defaults']['selected_sheets'] = self.get_selected_sheets()
            
            # Save yoga settings - only save time interval, not dates
            yoga_time_interval = self.yoga_controls.yoga_time_interval.currentText() if self.yoga_controls.yoga_time_interval else None
            
            if 'yoga' not in config['user_defaults']:
                config['user_defaults']['yoga'] = {}
                
            config['user_defaults']['yoga']['time_interval'] = yoga_time_interval
            # We do NOT save yoga start_date and end_date as they should default to yesterday and tomorrow
            
            # Save aspect settings
            config['user_defaults']['aspects'] = self.aspect_controls.get_selected_aspects()
            config['user_defaults']['aspect_planets'] = self.aspect_controls.get_selected_aspect_planets()
            
            # Save to file
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
                
            # Show success message
            QMessageBox.information(self.parent, "Default Settings Saved", 
                                  "Your current selections have been saved as default settings.")
                                  
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import logging
            logging.error(f"Failed to save default settings: {str(e)}")
            QMessageBox.warning(self.parent, "Save Default Error", 
                               f"Failed to save default settings: {str(e)}")
                               
    def load_default_settings(self):
        """
        Load default settings from config file.
        
        Returns:
        --------
        dict
            Dictionary of default settings or None if not found
        """
        try:
            import json
            import os
            import logging
            
            # Get the config file path
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
            
            # Load config
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Return user defaults if they exist
            if 'user_defaults' in config:
                return config['user_defaults']
                
        except Exception as e:
            logging.error(f"Failed to load default settings: {str(e)}")
            
        return None
        
    def apply_default_settings(self):
        """
        Apply the loaded default settings to the UI components.
        This should be called after the UI components are created.
        """
        # Set default date to today and time to 9:00 AM, regardless of saved settings
        if self.date_picker:
            from PyQt5.QtCore import QDate
            self.date_picker.setDate(QDate.currentDate())
            
        if self.time_picker:
            from PyQt5.QtCore import QTime
            self.time_picker.setTime(QTime(9, 0))
            
        # Set default yoga date range to yesterday to tomorrow
        if self.yoga_controls.yoga_start_date:
            from PyQt5.QtCore import QDate
            self.yoga_controls.yoga_start_date.setDate(QDate.currentDate().addDays(-1))
            
        if self.yoga_controls.yoga_end_date:
            from PyQt5.QtCore import QDate
            self.yoga_controls.yoga_end_date.setDate(QDate.currentDate().addDays(1))
            
        # If no saved defaults, return after setting the built-in defaults
        if not self.default_settings:
            return
            
        try:
            # Apply location
            if 'location' in self.default_settings and self.location_combo:
                index = self.location_combo.findText(self.default_settings['location'])
                if index >= 0:
                    self.location_combo.setCurrentIndex(index)
                   
            # We no longer apply date and time from saved settings
            
            # Apply selected sheets
            if 'selected_sheets' in self.default_settings and self.sheet_checkboxes:
                selected_sheets = self.default_settings['selected_sheets']
                # First uncheck all
                for checkbox in self.sheet_checkboxes.values():
                    checkbox.setChecked(False)
                # Then check only the selected ones
                for sheet_name in selected_sheets:
                    if sheet_name in self.sheet_checkboxes:
                        self.sheet_checkboxes[sheet_name].setChecked(True)
                        
            # Apply yoga settings - only apply time interval, not dates
            if 'yoga' in self.default_settings:
                yoga_defaults = self.default_settings['yoga']
                
                # Apply yoga time interval
                if 'time_interval' in yoga_defaults and yoga_defaults['time_interval'] and self.yoga_controls.yoga_time_interval:
                    index = self.yoga_controls.yoga_time_interval.findText(yoga_defaults['time_interval'])
                    if index >= 0:
                        self.yoga_controls.yoga_time_interval.setCurrentIndex(index)
                        
            # Apply aspect settings
            if 'aspects' in self.default_settings and self.aspect_controls.aspect_checkboxes:
                aspects = self.default_settings['aspects']
                for angle_str, is_selected in aspects.items():
                    angle = int(angle_str)
                    for aspect_checkbox in self.aspect_controls.aspect_checkboxes:
                        if hasattr(aspect_checkbox, 'angle') and aspect_checkbox.angle == angle:
                            aspect_checkbox.setChecked(is_selected)
                            
            # Apply aspect planets
            if 'aspect_planets' in self.default_settings and self.aspect_controls.aspect_planets_checkboxes:
                aspect_planets = self.default_settings['aspect_planets']
                for planet, is_selected in aspect_planets.items():
                    if planet in self.aspect_controls.aspect_planets_checkboxes:
                        self.aspect_controls.aspect_planets_checkboxes[planet].setChecked(is_selected)
                        
        except Exception as e:
            import logging
            logging.error(f"Failed to apply default settings: {str(e)}") 