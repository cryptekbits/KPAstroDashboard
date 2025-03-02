"""
Configuration tab for the KP Astrology application.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QGridLayout, QScrollArea,
                            QTabWidget)
import os
import json

from ui.components.yoga_controls import YogaControls
from ui.components.aspect_controls import AspectControls


class ConfigTab:
    """Configuration tab for the KP Astrology application."""

    def __init__(self, parent):
        """
        Initialize configuration tab.
        
        Parameters:
        -----------
        parent : QWidget
            Parent widget to attach the tab to
        """
        self.parent = parent
        self.yoga_controls = YogaControls(parent)
        self.aspect_controls = AspectControls(parent)
        
        # Configuration components
        self.planet_pos_enabled = None
        self.planet_pos_columns = {}
        self.planet_pos_planets = {}
        self.hora_enabled = None
        self.hora_columns = {}
        self.transit_enabled = None
        self.transit_columns = {}
        self.aspects_enabled = None
        self.yoga_enabled = None
        self.yoga_columns = {}
        
        # Config file path
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')

    def setup_tab(self):
        """
        Set up the configuration tab.
        
        Returns:
        --------
        QWidget
            The configuration tab widget
        """
        # Create the configuration tab
        config_tab = QWidget()
        
        # Create a scroll area for the configuration content
        config_scroll = QScrollArea()
        config_scroll.setWidgetResizable(True)
        
        config_widget = QWidget()
        config_scroll.setWidget(config_widget)
        
        # Set the scroll area as the config tab's layout
        config_tab_layout = QVBoxLayout(config_tab)
        config_tab_layout.addWidget(config_scroll)
        
        config_layout = QVBoxLayout(config_widget)
        
        # Add a title label
        title_label = QLabel("Feature Configuration")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        config_layout.addWidget(title_label)
        
        # Create sub-tabs for each component
        config_sub_tabs = QTabWidget()
        config_layout.addWidget(config_sub_tabs)
        
        # 1. Planet Position Configuration Tab
        planet_pos_tab, self.planet_pos_enabled, self.planet_pos_columns, self.planet_pos_planets = self.setup_planet_pos_configuration()
        config_sub_tabs.addTab(planet_pos_tab, "Planet Position")
        
        # 2. Hora Configuration Tab
        hora_tab, self.hora_enabled, self.hora_columns = self.setup_hora_configuration()
        config_sub_tabs.addTab(hora_tab, "Hora Timing")
        
        # 3. Planet Transit Configuration Tab
        transit_tab, self.transit_enabled, self.transit_columns = self.setup_transit_configuration()
        config_sub_tabs.addTab(transit_tab, "Planet Transit")
        
        # 4. Aspects Configuration Tab
        aspects_tab, self.aspects_enabled = self.aspect_controls.setup_aspects_configuration(None)
        config_sub_tabs.addTab(aspects_tab, "Aspects")
        
        # 5. Yoga Configuration Tab
        yoga_tab, self.yoga_enabled, self.yoga_columns = self.yoga_controls.setup_yoga_configuration(None)
        config_sub_tabs.addTab(yoga_tab, "Yogas")
        
        # Save Configuration button
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_configuration)
        config_layout.addWidget(save_btn)
        
        # Connect toggle signals to update visibility in main tab
        self.planet_pos_enabled.toggled.connect(self.parent.update_main_tab_visibility)
        self.hora_enabled.toggled.connect(self.parent.update_main_tab_visibility)
        self.transit_enabled.toggled.connect(self.parent.update_main_tab_visibility)
        self.aspects_enabled.toggled.connect(self.parent.update_main_tab_visibility)
        self.yoga_enabled.toggled.connect(self.parent.update_main_tab_visibility)
        
        # Load configuration if exists
        self.load_configuration()
        
        return config_tab

    def setup_planet_pos_configuration(self):
        """
        Set up the planet position configuration section.
        
        Returns:
        --------
        tuple
            (QWidget, QCheckBox, dict, dict)
            The tab widget, the planet position enabled checkbox, the columns checkboxes, and the planets checkboxes
        """
        planet_pos_tab = QWidget()
        planet_pos_layout = QVBoxLayout(planet_pos_tab)
        
        # Feature toggle
        planet_pos_enabled = QCheckBox("Enable Planet Position")
        planet_pos_enabled.setChecked(True)
        planet_pos_layout.addWidget(planet_pos_enabled)
        
        # Columns toggle group
        columns_group = QGroupBox("Columns to Display")
        columns_layout = QGridLayout()
        
        # Planet position columns
        planet_pos_columns = {
            "Rashi": QCheckBox("Rashi"),
            "Nakshatra": QCheckBox("Nakshatra"),
            "Rashi Lord": QCheckBox("Rashi Lord"),
            "Nakshatra Lord": QCheckBox("Nakshatra Lord"),
            "Sub Lord": QCheckBox("Sub Lord"),
            "Sub-Sub Lord": QCheckBox("Sub-Sub Lord"),
            "Position": QCheckBox("Position"),
            "Retrograde": QCheckBox("Retrograde")
        }
        
        row, col = 0, 0
        max_col = 3
        for name, checkbox in planet_pos_columns.items():
            checkbox.setChecked(True)
            columns_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1
                
        columns_group.setLayout(columns_layout)
        planet_pos_layout.addWidget(columns_group)
        
        # Planets toggle group
        planets_group = QGroupBox("Planets to Display")
        planets_layout = QGridLayout()
        
        # Planet toggles
        planet_pos_planets = {
            "Sun": QCheckBox("Sun"),
            "Moon": QCheckBox("Moon"),
            "Mercury": QCheckBox("Mercury"),
            "Venus": QCheckBox("Venus"),
            "Mars": QCheckBox("Mars"),
            "Jupiter": QCheckBox("Jupiter"),
            "Saturn": QCheckBox("Saturn"),
            "Rahu": QCheckBox("Rahu"),
            "Ketu": QCheckBox("Ketu"),
            "Uranus": QCheckBox("Uranus"),
            "Neptune": QCheckBox("Neptune"),
            "Ascendant": QCheckBox("Ascendant")
        }
        
        row, col = 0, 0
        max_col = 3
        for name, checkbox in planet_pos_planets.items():
            checkbox.setChecked(True)
            planets_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1
                
        planets_group.setLayout(planets_layout)
        planet_pos_layout.addWidget(planets_group)
        
        return planet_pos_tab, planet_pos_enabled, planet_pos_columns, planet_pos_planets

    def setup_hora_configuration(self):
        """
        Set up the hora timing configuration section.
        
        Returns:
        --------
        tuple
            (QWidget, QCheckBox, dict)
            The tab widget, the hora enabled checkbox, and the columns checkboxes
        """
        hora_tab = QWidget()
        hora_layout = QVBoxLayout(hora_tab)
        
        # Feature toggle
        hora_enabled = QCheckBox("Enable Hora Timing")
        hora_enabled.setChecked(True)
        hora_layout.addWidget(hora_enabled)
        
        # Columns toggle group
        hora_columns_group = QGroupBox("Columns to Display")
        hora_columns_layout = QGridLayout()
        
        # Hora columns
        hora_columns = {
            "Start Time": QCheckBox("Start Time"),
            "End Time": QCheckBox("End Time"),
            "Hora Lord": QCheckBox("Hora Lord"),
            "Day Lord": QCheckBox("Day Lord")
        }
        
        row, col = 0, 0
        max_col = 3
        for name, checkbox in hora_columns.items():
            checkbox.setChecked(True)
            hora_columns_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1
                
        hora_columns_group.setLayout(hora_columns_layout)
        hora_layout.addWidget(hora_columns_group)
        
        return hora_tab, hora_enabled, hora_columns

    def setup_transit_configuration(self):
        """
        Set up the planet transit configuration section.
        
        Returns:
        --------
        tuple
            (QWidget, QCheckBox, dict)
            The tab widget, the transit enabled checkbox, and the columns checkboxes
        """
        transit_tab = QWidget()
        transit_layout = QVBoxLayout(transit_tab)
        
        # Feature toggle
        transit_enabled = QCheckBox("Enable Planet Transit")
        transit_enabled.setChecked(True)
        transit_layout.addWidget(transit_enabled)
        
        # Columns toggle group
        transit_columns_group = QGroupBox("Columns to Display")
        transit_columns_layout = QGridLayout()
        
        # Transit columns
        transit_columns = {
            "Start Time": QCheckBox("Start Time"),
            "End Time": QCheckBox("End Time"),
            "Position": QCheckBox("Position"),
            "Rashi": QCheckBox("Rashi"),
            "Nakshatra": QCheckBox("Nakshatra"),
            "Rashi Lord": QCheckBox("Rashi Lord"),
            "Nakshatra Lord": QCheckBox("Nakshatra Lord"),
            "Sub Lord": QCheckBox("Sub Lord"),
            "Sub-Sub Lord": QCheckBox("Sub-Sub Lord"),
            "Aspects": QCheckBox("Aspects")
        }
        
        row, col = 0, 0
        max_col = 3
        for name, checkbox in transit_columns.items():
            checkbox.setChecked(True)
            transit_columns_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1
                
        transit_columns_group.setLayout(transit_columns_layout)
        transit_layout.addWidget(transit_columns_group)
        
        return transit_tab, transit_enabled, transit_columns

    def save_configuration(self):
        """Save the configuration settings to a JSON file."""
        try:
            # Get current configuration
            config_settings = self.get_config_settings()
            
            # Save to JSON file
            with open(self.config_file, 'w') as f:
                json.dump(config_settings, f, indent=4)
                
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self.parent, "Configuration Saved", 
                                  "Configuration settings have been saved successfully.")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent, "Configuration Save Error", 
                               f"Failed to save configuration: {str(e)}")
            import logging
            logging.error(f"Failed to save configuration: {str(e)}")
    
    def load_configuration(self):
        """Load configuration settings from JSON file if it exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_settings = json.load(f)
                
                # Apply loaded settings
                self._apply_loaded_config(config_settings)
        except Exception as e:
            import logging
            logging.error(f"Failed to load configuration: {str(e)}")
    
    def _apply_loaded_config(self, config_settings):
        """Apply loaded configuration settings to UI controls."""
        # Planet Position settings
        if "planet_pos" in config_settings:
            planet_pos = config_settings["planet_pos"]
            if "enabled" in planet_pos:
                self.planet_pos_enabled.setChecked(planet_pos["enabled"])
            
            # Columns
            if "columns" in planet_pos:
                for name, value in planet_pos["columns"].items():
                    if name in self.planet_pos_columns:
                        self.planet_pos_columns[name].setChecked(value)
            
            # Planets
            if "planets" in planet_pos:
                for name, value in planet_pos["planets"].items():
                    if name in self.planet_pos_planets:
                        self.planet_pos_planets[name].setChecked(value)
        
        # Hora settings
        if "hora" in config_settings:
            hora = config_settings["hora"]
            if "enabled" in hora:
                self.hora_enabled.setChecked(hora["enabled"])
            
            # Columns
            if "columns" in hora:
                for name, value in hora["columns"].items():
                    if name in self.hora_columns:
                        self.hora_columns[name].setChecked(value)
        
        # Transit settings
        if "transit" in config_settings:
            transit = config_settings["transit"]
            if "enabled" in transit:
                self.transit_enabled.setChecked(transit["enabled"])
            
            # Columns
            if "columns" in transit:
                for name, value in transit["columns"].items():
                    if name in self.transit_columns:
                        self.transit_columns[name].setChecked(value)
        
        # Aspects settings
        if "aspects" in config_settings and "enabled" in config_settings["aspects"]:
            self.aspects_enabled.setChecked(config_settings["aspects"]["enabled"])
            self.aspect_controls.load_aspect_config(config_settings)
        
        # Yoga settings
        if "yoga" in config_settings:
            yoga = config_settings["yoga"]
            if "enabled" in yoga:
                self.yoga_enabled.setChecked(yoga["enabled"])
            
            # Columns
            if "columns" in yoga:
                for name, value in yoga["columns"].items():
                    if name in self.yoga_columns:
                        self.yoga_columns[name].setChecked(value)
            
            # Types (pass to yoga controls)
            if "types" in yoga:
                self.yoga_controls.load_yoga_config(yoga)

    def get_config_settings(self):
        """
        Get the current configuration settings.
        
        Returns:
        --------
        dict
            Dictionary of configuration settings
        """
        config_settings = {
            # Planet Position settings
            "planet_pos": {
                "enabled": self.planet_pos_enabled.isChecked(),
                "columns": {name: checkbox.isChecked() for name, checkbox in self.planet_pos_columns.items()},
                "planets": {name: checkbox.isChecked() for name, checkbox in self.planet_pos_planets.items()}
            },
            # Hora settings
            "hora": {
                "enabled": self.hora_enabled.isChecked(),
                "columns": {name: checkbox.isChecked() for name, checkbox in self.hora_columns.items()}
            },
            # Transit settings
            "transit": {
                "enabled": self.transit_enabled.isChecked(),
                "columns": {name: checkbox.isChecked() for name, checkbox in self.transit_columns.items()}
            },
            # Aspects settings
            "aspects": {
                "enabled": self.aspects_enabled.isChecked(),
                "aspect_list": {str(angle): checkbox.isChecked() for angle, checkbox in self.aspect_controls.aspect_checkboxes.items()},
                "aspect_planets": {name: checkbox.isChecked() for name, checkbox in self.aspect_controls.aspect_planets_checkboxes.items()}
            },
            # Yoga settings
            "yoga": {
                "enabled": self.yoga_enabled.isChecked(),
                "columns": {name: checkbox.isChecked() for name, checkbox in self.yoga_columns.items()},
                "types": {name: checkbox.isChecked() for name, checkbox in self.yoga_controls.yoga_types.items()}
            }
        }
        
        return config_settings 