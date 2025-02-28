"""
Transit display widget for KP Astrology Dashboard.
Shows planetary transit data with transitions and aspects.
"""
from typing import Dict, List, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QComboBox, QFrame, QGridLayout, QCheckBox,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QColor, QBrush, QFont, QIcon


class TransitDisplay(QWidget):
    """Widget for displaying planetary transit data."""

    def __init__(self, transit_data: Dict, parent=None):
        """
        Initialize the transit display.

        Args:
            transit_data: Dictionary mapping planet names to transit DataFrames
            parent: Parent widget
        """
        super().__init__(parent)
        self.transit_data = transit_data
        self.init_ui()

    def init_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Header section with title and controls
        header_layout = QHBoxLayout()

        title_label = QLabel("Planetary Transits")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)

        # Add filter controls
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Events", "Sign Changes", "Nakshatra Changes",
                                    "Retrograde Events", "Aspects Only"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)

        filter_label = QLabel("Filter:")
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.filter_combo)

        # Add highlighting checkbox
        self.highlight_current_cb = QCheckBox("Highlight Current Time")
        self.highlight_current_cb.setChecked(True)
        self.highlight_current_cb.stateChanged.connect(self.refresh_displays)
        header_layout.addWidget(self.highlight_current_cb)

        header_layout.addStretch()

        # Add export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_transits)
        header_layout.addWidget(export_btn)

        main_layout.addLayout(header_layout)

        # Create tabs for different planets
        self.tab_widget = QTabWidget()

        # Info message if no data
        if not self.transit_data:
            info_label = QLabel("No transit data available. Calculate transits to view results.")
            info_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(info_label)
        else:
            # Add overview tab first
            overview_tab = self.create_overview_tab()
            self.tab_widget.addTab(overview_tab, "Overview")

            # Add tabs for each planet in transit data
            for planet, data in self.transit_data.items():
                if not data.empty:
                    tab = self.create_planet_tab(planet, data)
                    self.tab_widget.addTab(tab, planet)

            main_layout.addWidget(self.tab_widget)

        # Add status label at bottom
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Update status with counts
        self.update_status()

    def create_overview_tab(self):
        """Create a tab showing overview of all transits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Create splitter for top and bottom sections
        splitter = QSplitter(Qt.Vertical)

        # Top section: Summary grid
        summary_widget = QWidget()
        summary_layout = QGridLayout(summary_widget)

        # Count events by type
        event_counts = self.count_events_by_type()

        # Add title
        summary_title = QLabel("Transit Summary")
        summary_title.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(summary_title, 0, 0, 1, 2)

        # Add counts
        row = 1
        for event_type, count in event_counts.items():
            type_label = QLabel(f"{event_type}:")
            count_label = QLabel(str(count))
            count_label.setAlignment(Qt.AlignRight)

            summary_layout.addWidget(type_label, row, 0)
            summary_layout.addWidget(count_label, row, 1)
            row += 1

        # Add spacer
        summary_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum,
                                           QSizePolicy.Expanding), row, 0)

        # Bottom section: Timeline of significant events
        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)

        timeline_title = QLabel("Significant Events Timeline")
        timeline_title.setFont(QFont("Arial", 12, QFont.Bold))
        timeline_layout.addWidget(timeline_title)

        # Create table for significant events
        timeline_table = QTableWidget()
        timeline_table.setColumnCount(4)
        timeline_table.setHorizontalHeaderLabels(["Time", "Planet", "Event", "Details"])
        timeline_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        timeline_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        timeline_table.setAlternatingRowColors(True)

        # Populate with significant events
        significant_events = self.get_significant_events()
        timeline_table.setRowCount(len(significant_events))

        for i, event in enumerate(significant_events):
            time_item = QTableWidgetItem(event.get("time", ""))
            planet_item = QTableWidgetItem(event.get("planet", ""))
            event_item = QTableWidgetItem(event.get("event", ""))
            details_item = QTableWidgetItem(event.get("details", ""))

            # Set colors based on event type
            if "Retrograde" in event.get("event", ""):
                event_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow
            elif "entered" in event.get("event", ""):
                event_item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
            elif "aspect" in event.get("event", "").lower():
                event_item.setBackground(QBrush(QColor("#DDEBF7")))  # Light blue

            timeline_table.setItem(i, 0, time_item)
            timeline_table.setItem(i, 1, planet_item)
            timeline_table.setItem(i, 2, event_item)
            timeline_table.setItem(i, 3, details_item)

        timeline_layout.addWidget(timeline_table)

        # Add to splitter
        splitter.addWidget(summary_widget)
        splitter.addWidget(timeline_widget)

        # Set initial sizes
        splitter.setSizes([200, 600])

        layout.addWidget(splitter)
        return tab

    def create_planet_tab(self, planet_name: str, planet_data):
        """
        Create a tab for displaying transit data for a specific planet.

        Args:
            planet_name: Name of the planet
            planet_data: DataFrame with transit data

        Returns:
            QWidget: Tab widget with transit display
        """
        # Create tab widget
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Add planet info header
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QHBoxLayout(info_frame)

        planet_label = QLabel(f"{planet_name} Transits")
        planet_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(planet_label)

        # Add count of transitions
        count_label = QLabel(f"Total Transitions: {len(planet_data)}")
        info_layout.addWidget(count_label)

        info_layout.addStretch()

        tab_layout.addWidget(info_frame)

        # Create table for displaying transit data
        table = QTableWidget()
        self.setup_transit_table(table, planet_data)

        tab_layout.addWidget(table)
        return tab

    def setup_transit_table(self, table: QTableWidget, data):
        """
        Set up a table with transit data.

        Args:
            table: QTableWidget to populate
            data: DataFrame with transit data
        """
        if data.empty:
            return

        # Set up columns based on data columns
        columns = data.columns.tolist()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Set row count
        table.setRowCount(len(data))

        # Get current time for highlighting
        current_time = datetime.now().strftime("%H:%M")

        # Populate table with data
        for row_idx, (_, row_data) in enumerate(data.iterrows()):
            # Check if this period includes current time
            is_current = False
            if self.highlight_current_cb.isChecked():
                start_time = row_data.get("Start Time", "")
                end_time = row_data.get("End Time", "")
                if start_time and end_time and start_time <= current_time <= end_time:
                    is_current = True

            # Add each column
            for col_idx, col_name in enumerate(columns):
                value = row_data.get(col_name, "")
                item = QTableWidgetItem(str(value))

                # Set colors based on column and values
                if col_name == "Aspects" and value:
                    # Check for aspects, yogas, etc.
                    if "Yoga" in str(value):
                        if "Positive" in str(value):
                            item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
                        elif "Negative" in str(value):
                            item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
                        else:
                            item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow
                    elif "Square" in str(value) or "Opposition" in str(value):
                        item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
                    elif "Trine" in str(value) or "Sextile" in str(value):
                        item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green

                # Highlight current time row
                if is_current:
                    item.setBackground(QBrush(QColor("#FFFF00")))  # Yellow for current time

                table.setItem(row_idx, col_idx, item)

        # Set column widths
        table.setColumnWidth(0, 80)  # Start Time
        table.setColumnWidth(1, 80)  # End Time

        # Make the aspects column stretch
        header = table.horizontalHeader()
        for i in range(2, len(columns) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        if "Aspects" in columns:
            aspects_idx = columns.index("Aspects")
            header.setSectionResizeMode(aspects_idx, QHeaderView.Stretch)

        # Add sorting capability
        table.setSortingEnabled(True)

        # Make table read-only
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def count_events_by_type(self) -> Dict[str, int]:
        """
        Count events by type across all planet data.

        Returns:
            Dictionary with event type counts
        """
        event_counts = {
            "Sign Changes": 0,
            "Nakshatra Changes": 0,
            "Retrograde Events": 0,
            "Aspects": 0,
            "Other Transitions": 0
        }

        for planet, data in self.transit_data.items():
            if data.empty:
                continue

            # Count rows as transitions
            event_counts["Other Transitions"] += len(data)

            # Count aspects
            if "Aspects" in data.columns:
                for aspect in data["Aspects"]:
                    if aspect and aspect != "None":
                        # Count multiple aspects in one cell
                        aspects = str(aspect).split("; ")
                        for a in aspects:
                            if "entered" in a and ("nakshatra" in a.lower()):
                                event_counts["Nakshatra Changes"] += 1
                                event_counts["Other Transitions"] -= 1
                            elif "entered" in a:
                                event_counts["Sign Changes"] += 1
                                event_counts["Other Transitions"] -= 1
                            elif "Retrograde" in a:
                                event_counts["Retrograde Events"] += 1
                                event_counts["Other Transitions"] -= 1
                            elif a:  # Any other non-empty aspect
                                event_counts["Aspects"] += 1

        return event_counts

    def get_significant_events(self) -> List[Dict]:
        """
        Extract significant events from all planet data.

        Returns:
            List of dictionaries with event information
        """
        significant_events = []

        for planet, data in self.transit_data.items():
            if data.empty:
                continue

            for _, row in data.iterrows():
                # Check for aspects/events
                if "Aspects" in data.columns and row["Aspects"] and row["Aspects"] != "None":
                    aspects = str(row["Aspects"]).split("; ")

                    for aspect in aspects:
                        if not aspect:
                            continue

                        event_type = "Aspect"
                        if "entered" in aspect:
                            event_type = "Transition"
                        elif "Retrograde" in aspect:
                            event_type = "Retrograde"

                        # Get time range
                        time_str = f"{row.get('Start Time', '')} - {row.get('End Time', '')}"

                        # Add to significant events
                        significant_events.append({
                            "time": time_str,
                            "planet": planet,
                            "event": aspect,
                            "details": f"{row.get('Rashi', '')}, {row.get('Nakshatra', '')}"
                        })

        # Sort by start time
        significant_events.sort(key=lambda x: x["time"])

        return significant_events

    def apply_filters(self):
        """Apply selected filters to transit displays."""
        filter_type = self.filter_combo.currentText()

        # Currently, we're not implementing actual filtering
        # but we would update the displays here based on the filter

        # Update status label
        self.status_label.setText(f"Filter applied: {filter_type}")

    def refresh_displays(self):
        """Refresh all transit displays."""
        # Get the current tab index
        current_idx = self.tab_widget.currentIndex()

        # Refresh the overview tab
        if current_idx == 0:
            # Remove and recreate the overview tab
            self.tab_widget.removeTab(0)
            overview_tab = self.create_overview_tab()
            self.tab_widget.insertTab(0, overview_tab, "Overview")
        else:
            # Get the current planet
            planet_name = self.tab_widget.tabText(current_idx)

            if planet_name in self.transit_data:
                # Remove and recreate the planet tab
                self.tab_widget.removeTab(current_idx)
                planet_tab = self.create_planet_tab(planet_name, self.transit_data[planet_name])
                self.tab_widget.insertTab(current_idx, planet_tab, planet_name)

        # Set back to the current tab
        self.tab_widget.setCurrentIndex(current_idx)

    def update_status(self):
        """Update the status label with data summary."""
        if not self.transit_data:
            self.status_label.setText("No transit data available")
            return

        total_transitions = sum(len(data) for data in self.transit_data.values())
        planet_count = len(self.transit_data)

        self.status_label.setText(
            f"Displaying {total_transitions} transitions for {planet_count} planets"
        )

    def export_transits(self):
        """Export transit data to Excel."""
        # This would connect to the export system
        print("Export functionality would be implemented here")
        self.status_label.setText("Export requested (not implemented in this version)")