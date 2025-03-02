"""
Aspect controls for the KP Astrology application.
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QGridLayout)


class AspectControls:
    """Controls for aspect configuration and selection."""

    def __init__(self, parent):
        """
        Initialize aspect controls.
        
        Parameters:
        -----------
        parent : QWidget
            Parent widget to attach the controls
        """
        self.parent = parent
        self.aspect_checkboxes = {}
        self.aspect_planets_checkboxes = {}
        
        # Define default aspects
        self.aspects = [
            {"angle": 0, "name": "Conjunction", "symbol": "☌", "default": True},
            {"angle": 30, "name": "Semi-Sextile", "symbol": "⚺", "default": False},
            {"angle": 60, "name": "Sextile", "symbol": "⚹", "default": False},
            {"angle": 90, "name": "Square", "symbol": "□", "default": True},
            {"angle": 120, "name": "Trine", "symbol": "△", "default": False},
            {"angle": 150, "name": "Quincunx", "symbol": "⚻", "default": False},
            {"angle": 180, "name": "Opposition", "symbol": "☍", "default": True}
        ]
        
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

    def create_aspects_group(self, main_layout):
        """
        Create the aspects selection group box.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the group box to
            
        Returns:
        --------
        QGroupBox
            The created group box
        """
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
        
        return aspects_group

    def create_aspect_planets_group(self, main_layout):
        """
        Create the aspect planets selection group box.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the group box to
            
        Returns:
        --------
        QGroupBox
            The created group box
        """
        # Planets for aspects selection
        aspect_planets_group = QGroupBox("Calculate Aspects For")
        aspect_planets_layout = QVBoxLayout()
        aspect_planets_group.setLayout(aspect_planets_layout)

        self.aspect_planets_checkboxes = {}

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
        
        return aspect_planets_group

    def create_aspect_buttons(self, main_layout):
        """
        Create aspect selection buttons.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the buttons to
        """
        select_layout = QHBoxLayout()

        select_all_aspects_btn = QPushButton("Select All Aspects")
        select_all_aspects_btn.clicked.connect(self.select_all_aspects)

        select_no_aspects_btn = QPushButton("Select No Aspects")
        select_no_aspects_btn.clicked.connect(self.select_no_aspects)

        select_layout.addWidget(select_all_aspects_btn)
        select_layout.addWidget(select_no_aspects_btn)

        main_layout.addLayout(select_layout)

    def setup_aspects_configuration(self, tab_layout):
        """
        Set up the aspects configuration section in the config tab.
        
        Parameters:
        -----------
        tab_layout : QLayout
            Layout to add the aspects configuration to
            
        Returns:
        --------
        tuple
            (QWidget, QCheckBox)
            The tab widget and the aspects enabled checkbox
        """
        from PyQt5.QtWidgets import QWidget
        
        aspects_tab = QWidget()
        aspects_layout = QVBoxLayout(aspects_tab)
        
        # Feature toggle
        aspects_enabled = QCheckBox("Enable Aspects")
        aspects_enabled.setChecked(True)
        aspects_layout.addWidget(aspects_enabled)
        
        # Create aspect selection group
        self.create_aspects_group(aspects_layout)
        
        # Create aspect planets selection group
        self.create_aspect_planets_group(aspects_layout)
        
        # Create aspect selection buttons
        self.create_aspect_buttons(aspects_layout)
        
        # Connect signals to update main tab visibility
        aspects_enabled.toggled.connect(self._update_main_tab_visibility)
        
        # Connect all aspect checkboxes to update main tab visibility
        for checkbox in self.aspect_checkboxes.values():
            checkbox.toggled.connect(self._update_main_tab_visibility)
        
        # Connect all aspect planet checkboxes to update main tab visibility
        for checkbox in self.aspect_planets_checkboxes.values():
            checkbox.toggled.connect(self._update_main_tab_visibility)
        
        return aspects_tab, aspects_enabled

    def _update_main_tab_visibility(self):
        """Update the main tab visibility when aspect configuration changes."""
        from PyQt5.QtWidgets import QApplication
        main_window = QApplication.activeWindow()
        if hasattr(main_window, 'update_main_tab_visibility'):
            main_window.update_main_tab_visibility()

    def select_all_aspects(self):
        """Select all aspect checkboxes."""
        for checkbox in self.aspect_checkboxes.values():
            checkbox.setChecked(True)
        
        # Update main tab visibility
        self._update_main_tab_visibility()

    def select_no_aspects(self):
        """Deselect all aspect checkboxes."""
        for checkbox in self.aspect_checkboxes.values():
            checkbox.setChecked(False)
        
        # Update main tab visibility
        self._update_main_tab_visibility()

    def get_selected_aspects(self):
        """
        Get the selected aspects.
        
        Returns:
        --------
        list
            List of selected aspect angles
        """
        # Only return aspects if the main aspect toggle is enabled
        # This will be checked by the caller, but we add it here for safety
        from PyQt5.QtWidgets import QApplication
        main_window = QApplication.activeWindow()
        if hasattr(main_window, 'config_tab') and hasattr(main_window.config_tab, 'aspects_enabled'):
            if not main_window.config_tab.aspects_enabled.isChecked():
                return []
        
        return [angle for angle, checkbox in self.aspect_checkboxes.items()
                if checkbox.isChecked()]

    def get_selected_aspect_planets(self):
        """
        Get the selected planets for aspects.
        
        Returns:
        --------
        list
            List of selected planet names
        """
        # Only return aspect planets if the main aspect toggle is enabled
        from PyQt5.QtWidgets import QApplication
        main_window = QApplication.activeWindow()
        if hasattr(main_window, 'config_tab') and hasattr(main_window.config_tab, 'aspects_enabled'):
            if not main_window.config_tab.aspects_enabled.isChecked():
                return []
        
        return [name for name, checkbox in self.aspect_planets_checkboxes.items()
                if checkbox.isChecked()]

    def load_aspect_config(self, config_settings):
        """
        Load aspect configuration settings.
        
        Parameters:
        -----------
        config_settings : dict
            Configuration settings dictionary
        """
        if "aspects" not in config_settings:
            return
            
        aspects_config = config_settings["aspects"]
        
        # Load individual aspect settings if available
        if "aspect_list" in aspects_config:
            for angle_str, enabled in aspects_config["aspect_list"].items():
                angle = int(angle_str)  # Convert string key to integer
                if angle in self.aspect_checkboxes:
                    self.aspect_checkboxes[angle].setChecked(enabled)
        
        # Load aspect planets settings if available
        if "aspect_planets" in aspects_config:
            for planet_name, enabled in aspects_config["aspect_planets"].items():
                if planet_name in self.aspect_planets_checkboxes:
                    self.aspect_planets_checkboxes[planet_name].setChecked(enabled)
        
        # Update main tab visibility
        self._update_main_tab_visibility() 