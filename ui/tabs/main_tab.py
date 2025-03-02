"""
Main tab for the KP Astrology application.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QGridLayout, QScrollArea, 
                            QComboBox, QDateEdit, QTimeEdit, QCompleter,
                            QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTime

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

        # Selection buttons for aspects
        self.aspect_controls.create_aspect_buttons(main_layout)

        # Selection buttons for sheets
        self.create_selection_buttons(main_layout)

        # Progress bar and status label
        self.create_progress_section(main_layout)

        # Generate button
        self.generate_btn = QPushButton("Generate Excel")
        self.generate_btn.clicked.connect(self.parent.generate_data)
        main_layout.addWidget(self.generate_btn)
        
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

        self.location_combo = QComboBox()
        self.location_combo.setObjectName("location_combo")
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

    def create_selection_buttons(self, main_layout):
        """
        Create sheet selection buttons.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the buttons to
        """
        select_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All Sheets")
        select_all_btn.clicked.connect(self.select_all_sheets)

        select_none_btn = QPushButton("Select No Sheets")
        select_none_btn.clicked.connect(self.select_no_sheets)

        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(select_none_btn)

        main_layout.addLayout(select_layout)

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
        
        # 5. Update aspect controls visibility
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
                    if angle in self.aspect_controls.aspect_checkboxes:
                        # Only show enabled aspects if the main aspect toggle is enabled
                        self.aspect_controls.aspect_checkboxes[angle].setVisible(
                            config_settings["aspects"]["enabled"] and enabled
                        )
        
            # 6. Update aspect planet checkboxes based on configuration
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