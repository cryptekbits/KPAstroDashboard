"""
Yoga controls for the KP Astrology application.
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QScrollArea, QGridLayout,
                            QDateEdit, QComboBox, QWidget)
from PyQt5.QtCore import QDate

from yogas import YogaManager


class YogaControls:
    """Controls for yoga configuration and selection."""

    def __init__(self, parent):
        """
        Initialize yoga controls.
        
        Parameters:
        -----------
        parent : QWidget
            Parent widget to attach the controls
        """
        self.parent = parent
        self.yoga_types = {}
        self.yoga_start_date = None
        self.yoga_end_date = None
        self.yoga_time_interval = None

    def create_yoga_group(self, main_layout):
        """
        Create the yoga date range selection group box.
        
        Parameters:
        -----------
        main_layout : QLayout
            Layout to add the group box to
            
        Returns:
        --------
        QGroupBox
            The created group box
        """
        # Yoga date range selection
        yoga_group = QGroupBox("Yoga Calculations Date Range")
        yoga_layout = QVBoxLayout()
        yoga_group.setLayout(yoga_layout)

        # Add explanation label
        yoga_layout.addWidget(QLabel("Calculate yogas for the following date range:"))

        # Start date selection
        yoga_start_layout = QHBoxLayout()
        yoga_start_layout.addWidget(QLabel("From:"))
        self.yoga_start_date = self.parent.findChild(QDateEdit, "yoga_start_date")
        if not self.yoga_start_date:
            # Create a new date edit widget
            self.yoga_start_date = QDateEdit()
            self.yoga_start_date.setObjectName("yoga_start_date")
            self.yoga_start_date.setCalendarPopup(True)

            # Set default to yesterday
            default_start_date = QDate.currentDate().addDays(-1)
            self.yoga_start_date.setDate(default_start_date)

        yoga_start_layout.addWidget(self.yoga_start_date)
        yoga_layout.addLayout(yoga_start_layout)

        # End date selection
        yoga_end_layout = QHBoxLayout()
        yoga_end_layout.addWidget(QLabel("To:"))
        self.yoga_end_date = self.parent.findChild(QDateEdit, "yoga_end_date")
        if not self.yoga_end_date:
            # Create a new date edit widget
            self.yoga_end_date = QDateEdit()
            self.yoga_end_date.setObjectName("yoga_end_date")
            self.yoga_end_date.setCalendarPopup(True)

            # Set default to tomorrow
            default_end_date = QDate.currentDate().addDays(1)
            self.yoga_end_date.setDate(default_end_date)

        yoga_end_layout.addWidget(self.yoga_end_date)
        yoga_layout.addLayout(yoga_end_layout)

        # Quick date range buttons
        quick_range_layout = QHBoxLayout()

        day_btn = QPushButton("1 Day")
        day_btn.clicked.connect(lambda: self.set_yoga_date_range(1))

        month_btn = QPushButton("1 Month")
        month_btn.clicked.connect(lambda: self.set_yoga_date_range(30))

        quarter_btn = QPushButton("3 Months")
        quarter_btn.clicked.connect(lambda: self.set_yoga_date_range(90))

        half_year_btn = QPushButton("6 Months")
        half_year_btn.clicked.connect(lambda: self.set_yoga_date_range(180))

        year_btn = QPushButton("1 Year")
        year_btn.clicked.connect(lambda: self.set_yoga_date_range(365))

        quick_range_layout.addWidget(day_btn)
        quick_range_layout.addWidget(month_btn)
        quick_range_layout.addWidget(quarter_btn)
        quick_range_layout.addWidget(half_year_btn)
        quick_range_layout.addWidget(year_btn)

        yoga_layout.addLayout(quick_range_layout)

        # Add time interval selection for yoga calculations
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Calculate yogas every:"))
        
        self.yoga_time_interval = QComboBox()
        self.yoga_time_interval.addItem("1 minute (highest precision)", 1/60)
        self.yoga_time_interval.addItem("5 minutes (very precise)", 5/60)
        self.yoga_time_interval.addItem("15 minutes (precise)", 15/60)
        self.yoga_time_interval.addItem("30 minutes (balanced)", 30/60)
        self.yoga_time_interval.addItem("1 hour (standard)", 1)
        self.yoga_time_interval.setCurrentIndex(2)  # Default to 15 minutes
        
        interval_layout.addWidget(self.yoga_time_interval)
        yoga_layout.addLayout(interval_layout)
        
        # Add note about yoga tracking
        note_label = QLabel("Note: Yogas are tracked by their start and end times, "
                           "showing when each yoga comes into effect and disappears. "
                           "A higher precision setting will detect shorter-lived yogas.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #555; font-style: italic;")
        yoga_layout.addWidget(note_label)
        
        # Add some spacing
        yoga_layout.addSpacing(10)

        main_layout.addWidget(yoga_group)
        
        return yoga_group

    def setup_yoga_configuration(self, tab_layout):
        """
        Set up the yoga configuration section in the config tab.
        
        Parameters:
        -----------
        tab_layout : QLayout
            Layout to add the yoga configuration to
            
        Returns:
        --------
        tuple
            (QWidget, QCheckBox, dict)
            The tab widget, the yoga enabled checkbox, and the yoga columns checkboxes
        """
        yoga_tab = QWidget()
        yoga_layout = QVBoxLayout(yoga_tab)
        
        # Feature toggle
        yoga_enabled = QCheckBox("Enable Yoga Calculations")
        yoga_enabled.setChecked(True)
        yoga_layout.addWidget(yoga_enabled)
        
        # Columns toggle group
        yoga_columns_group = QGroupBox("Columns to Display")
        yoga_columns_layout = QGridLayout()
        
        # Yoga columns
        yoga_columns = {
            "Start Date": QCheckBox("Start Date"),
            "Start Time": QCheckBox("Start Time"),
            "End Date": QCheckBox("End Date"),
            "End Time": QCheckBox("End Time"),
            "Yoga": QCheckBox("Yoga Name"),
            "Planets": QCheckBox("Planets"),
            "Nature": QCheckBox("Nature"),
            "Description": QCheckBox("Description")
        }
        
        row, col = 0, 0
        max_col = 3
        for name, checkbox in yoga_columns.items():
            checkbox.setChecked(True)
            yoga_columns_layout.addWidget(checkbox, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1
                
        yoga_columns_group.setLayout(yoga_columns_layout)
        yoga_layout.addWidget(yoga_columns_group)
        
        # Create layout for yoga selection buttons
        yoga_selection_layout = QVBoxLayout()
        
        # First row - All/None buttons
        first_row_layout = QHBoxLayout()
        select_all_yogas_btn = QPushButton("Select All Yogas")
        select_all_yogas_btn.clicked.connect(self.select_all_yogas)
        select_no_yogas_btn = QPushButton("Select No Yogas")
        select_no_yogas_btn.clicked.connect(self.select_no_yogas)
        first_row_layout.addWidget(select_all_yogas_btn)
        first_row_layout.addWidget(select_no_yogas_btn)
        yoga_selection_layout.addLayout(first_row_layout)
        
        # Second row - Nature-specific buttons
        second_row_layout = QHBoxLayout()
        
        # Add buttons for selecting yogas by nature
        select_excellent_btn = QPushButton("Only Excellent")
        select_excellent_btn.clicked.connect(lambda: self.select_yogas_by_nature("Excellent"))
        second_row_layout.addWidget(select_excellent_btn)
        
        select_good_btn = QPushButton("Only Good")
        select_good_btn.clicked.connect(lambda: self.select_yogas_by_nature("Good"))
        second_row_layout.addWidget(select_good_btn)
        
        select_neutral_btn = QPushButton("Only Neutral")
        select_neutral_btn.clicked.connect(lambda: self.select_yogas_by_nature("Neutral"))
        second_row_layout.addWidget(select_neutral_btn)
        
        select_bad_btn = QPushButton("Only Bad")
        select_bad_btn.clicked.connect(lambda: self.select_yogas_by_nature("Bad"))
        second_row_layout.addWidget(select_bad_btn)
        
        select_worst_btn = QPushButton("Only Worst")
        select_worst_btn.clicked.connect(lambda: self.select_yogas_by_nature("Worst"))
        second_row_layout.addWidget(select_worst_btn)
        
        yoga_selection_layout.addLayout(second_row_layout)
        
        # Third row - Nature-specific filter buttons
        third_row_layout = QHBoxLayout()
        
        # Add buttons for filtering yogas by nature
        filter_all_btn = QPushButton("Show All")
        filter_all_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature(None))
        third_row_layout.addWidget(filter_all_btn)
        
        filter_excellent_btn = QPushButton("Show Excellent")
        filter_excellent_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature("Excellent"))
        third_row_layout.addWidget(filter_excellent_btn)
        
        filter_good_btn = QPushButton("Show Good")
        filter_good_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature("Good"))
        third_row_layout.addWidget(filter_good_btn)
        
        filter_neutral_btn = QPushButton("Show Neutral")
        filter_neutral_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature("Neutral"))
        third_row_layout.addWidget(filter_neutral_btn)
        
        filter_bad_btn = QPushButton("Show Bad")
        filter_bad_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature("Bad"))
        third_row_layout.addWidget(filter_bad_btn)
        
        filter_worst_btn = QPushButton("Show Worst")
        filter_worst_btn.clicked.connect(lambda: self.filter_yoga_types_by_nature("Worst"))
        third_row_layout.addWidget(filter_worst_btn)
        
        yoga_selection_layout.addLayout(third_row_layout)
        
        yoga_layout.addLayout(yoga_selection_layout)
        
        # Yoga types toggle group
        yoga_types_group = QGroupBox("Yoga Types")
        yoga_types_layout = QVBoxLayout()
        yoga_types_group.setLayout(yoga_types_layout)
        
        # Get yoga metadata from YogaManager
        yoga_manager = YogaManager()
        
        # Organize yogas by nature
        yogas_by_nature = {}
        for yoga_name, metadata in yoga_manager.yoga_metadata.items():
            nature = metadata["nature"]
            if nature not in yogas_by_nature:
                yogas_by_nature[nature] = []
            yogas_by_nature[nature].append((yoga_name, metadata["description"]))
        
        # Create checkboxes for each yoga
        self.yoga_types = {}
        
        # Add yogas by nature in a table-like format
        for nature in ["Excellent", "Good", "Neutral", "Bad", "Worst"]:
            if nature in yogas_by_nature:
                # Add a label for the nature
                nature_label = QLabel(f"<b>{nature} Yogas:</b>")
                yoga_types_layout.addWidget(nature_label)
                
                # Create a table-like layout for this nature group
                table_widget = QWidget()
                table_layout = QGridLayout(table_widget)
                table_layout.setSpacing(10)
                
                # Add header row
                header_checkbox = QLabel("")
                header_name = QLabel("<b>Yoga Name</b>")
                header_desc = QLabel("<b>Description</b>")
                
                table_layout.addWidget(header_checkbox, 0, 0)
                table_layout.addWidget(header_name, 0, 1)
                table_layout.addWidget(header_desc, 0, 2)
                
                # Set column stretch to make description take more space
                table_layout.setColumnStretch(0, 1)  # Checkbox column
                table_layout.setColumnStretch(1, 3)  # Name column
                table_layout.setColumnStretch(2, 6)  # Description column
                
                # Add rows for each yoga
                row = 1
                for yoga_name, description in yogas_by_nature[nature]:
                    # Create a brief description (max 50 words)
                    words = description.split()
                    brief_desc = " ".join(words[:min(len(words), 50)])
                    if len(words) > 50:
                        brief_desc += "..."
                    
                    # Create checkbox, name label and description label
                    checkbox = QCheckBox()
                    checkbox.setChecked(True)
                    self.yoga_types[yoga_name] = checkbox
                    
                    name_label = QLabel(yoga_name)
                    desc_label = QLabel(brief_desc)
                    desc_label.setWordWrap(True)
                    
                    # Add to table layout
                    table_layout.addWidget(checkbox, row, 0)
                    table_layout.addWidget(name_label, row, 1)
                    table_layout.addWidget(desc_label, row, 2)
                    
                    row += 1
                
                # Add the table widget to the main layout
                yoga_types_layout.addWidget(table_widget)
                
                # Add a spacer after each nature group
                yoga_types_layout.addSpacing(15)
        
        # Create a scroll area for the yoga types
        yoga_scroll = QScrollArea()
        yoga_scroll.setWidgetResizable(True)
        yoga_scroll.setWidget(yoga_types_group)
        yoga_layout.addWidget(yoga_scroll)
        
        return yoga_tab, yoga_enabled, yoga_columns

    def set_yoga_date_range(self, days):
        """
        Set the yoga date range based on number of days.

        Parameters:
        -----------
        days : int
            Number of days to set the range for
        """
        main_date_picker = self.parent.findChild(QDateEdit, "date_picker")
        
        if days == 1 and main_date_picker:
            # For 1 Day option, use the date selected in the main date picker
            # but expand the range to include the previous and next day to catch yogas that span days
            selected_date = main_date_picker.date()
            
            # Set start date to the beginning of the previous day
            self.yoga_start_date.setDate(selected_date.addDays(-1))
            
            # Set end date to the end of the next day
            self.yoga_end_date.setDate(selected_date.addDays(1))
        else:
            # Get the current date
            current_date = QDate.currentDate()

            # Calculate half the days before and half after
            days_before = days // 3
            days_after = days - days_before

            # Set the start and end dates
            self.yoga_start_date.setDate(current_date.addDays(-days_before))
            self.yoga_end_date.setDate(current_date.addDays(days_after))

    def select_all_yogas(self):
        """Select all yoga checkboxes."""
        for checkbox in self.yoga_types.values():
            checkbox.setChecked(True)

    def select_no_yogas(self):
        """Deselect all yoga checkboxes."""
        for checkbox in self.yoga_types.values():
            checkbox.setChecked(False)

    def select_yogas_by_nature(self, target_nature):
        """
        Select all yoga checkboxes of a specific nature.
        
        Parameters:
        -----------
        target_nature : str
            The nature to select ("Excellent", "Good", "Neutral", "Bad", "Worst")
        """
        # First, deselect all yogas
        self.select_no_yogas()
        
        # Get yoga metadata from YogaManager
        yoga_manager = YogaManager()
        
        # Select yogas of the specified nature
        for yoga_name, checkbox in self.yoga_types.items():
            # Get the base yoga name (without any qualifiers)
            base_name = yoga_name
            if " - " in yoga_name:
                base_name = yoga_name.split(" - ")[0]
            
            # Get the metadata for this yoga
            metadata = yoga_manager.get_yoga_metadata(base_name)
            
            # Check if the nature matches
            if metadata.get("nature") == target_nature:
                checkbox.setChecked(True)

    def filter_yoga_types_by_nature(self, target_nature=None):
        """
        Show or hide yoga checkboxes based on their nature.
        
        Parameters:
        -----------
        target_nature : str or None
            The nature to filter by ("Excellent", "Good", "Neutral", "Bad", "Worst")
            If None, show all yoga types
        """
        if not hasattr(self, 'yoga_types') or not self.yoga_types:
            return
            
        # Get yoga metadata from YogaManager
        yoga_manager = YogaManager()
        
        for yoga_name, checkbox in self.yoga_types.items():
            # If no filter is applied, show all
            if target_nature is None:
                checkbox.setVisible(True)
                continue
                
            # Get the base yoga name (without any qualifiers)
            base_name = yoga_name
            if " - " in yoga_name:
                base_name = yoga_name.split(" - ")[0]
            
            # Get the metadata for this yoga
            metadata = yoga_manager.get_yoga_metadata(base_name)
            
            # Show only if the nature matches
            checkbox.setVisible(metadata.get("nature") == target_nature)
            
    def load_yoga_config(self, yoga_config):
        """
        Load yoga configuration settings.
        
        Parameters:
        -----------
        yoga_config : dict
            Yoga configuration settings
        """
        if not yoga_config or "types" not in yoga_config:
            return
            
        # Load yoga type selections
        for yoga_name, enabled in yoga_config["types"].items():
            if yoga_name in self.yoga_types:
                self.yoga_types[yoga_name].setChecked(enabled) 