"""
Yoga panel for KP Astrology Dashboard.
"""
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QGroupBox, QTableWidget, QTableWidgetItem,
    QSplitter, QComboBox, QCheckBox, QHeaderView, QTextEdit,
    QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QFont


class YogaPanel(QWidget):
    """Panel for displaying yoga information."""

    def __init__(self, parent=None):
        """Initialize the yoga panel."""
        super().__init__(parent)
        self.init_ui()

        # Store yoga data
        self.yoga_results = None
        self.yoga_counts = None
        self.significant_yogas = None
        self.yoga_by_period = None

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Top controls area
        controls_layout = QHBoxLayout()

        # Yoga filter controls
        filter_group = QGroupBox("Filter Yogas")
        filter_layout = QHBoxLayout(filter_group)

        self.positive_cb = QCheckBox("Positive")
        self.positive_cb.setChecked(True)
        self.positive_cb.stateChanged.connect(self.apply_filters)

        self.negative_cb = QCheckBox("Negative")
        self.negative_cb.setChecked(True)
        self.negative_cb.stateChanged.connect(self.apply_filters)

        self.neutral_cb = QCheckBox("Neutral")
        self.neutral_cb.setChecked(True)
        self.neutral_cb.stateChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.positive_cb)
        filter_layout.addWidget(self.negative_cb)
        filter_layout.addWidget(self.neutral_cb)

        # Timeframe filter
        timeframe_group = QGroupBox("Timeframe")
        timeframe_layout = QHBoxLayout(timeframe_group)

        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems([
            "All",
            "Today",
            "This Week",
            "This Month",
            "Active Now"
        ])
        self.timeframe_combo.currentIndexChanged.connect(self.apply_filters)

        timeframe_layout.addWidget(QLabel("Show:"))
        timeframe_layout.addWidget(self.timeframe_combo)

        # Add filter controls to layout
        controls_layout.addWidget(filter_group)
        controls_layout.addWidget(timeframe_group)
        controls_layout.addStretch()

        # Main content area with tabs
        self.tab_widget = QTabWidget()

        # Create tabs
        self.create_summary_tab()
        self.create_list_tab()
        self.create_timeline_tab()
        self.create_analysis_tab()

        # Add layouts to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.tab_widget, 1)  # Give the tab widget a stretch factor to fill space

    def create_summary_tab(self):
        """Create the summary tab."""
        summary_widget = QScrollArea()
        summary_widget.setWidgetResizable(True)

        summary_content = QWidget()
        summary_layout = QVBoxLayout(summary_content)

        # Title
        title_label = QLabel("Yoga Analysis Summary")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        summary_layout.addWidget(title_label)

        # Stats overview
        stats_group = QGroupBox("Yoga Statistics")
        stats_layout = QGridLayout(stats_group)

        # Create labels for stats (will be populated with data later)
        self.total_yogas_label = QLabel("0")
        self.total_yogas_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.positive_yogas_label = QLabel("0")
        self.positive_yogas_label.setFont(QFont("Arial", 14))
        self.negative_yogas_label = QLabel("0")
        self.negative_yogas_label.setFont(QFont("Arial", 14))
        self.neutral_yogas_label = QLabel("0")
        self.neutral_yogas_label.setFont(QFont("Arial", 14))

        # Add to layout
        stats_layout.addWidget(QLabel("Total Yogas:"), 0, 0)
        stats_layout.addWidget(self.total_yogas_label, 0, 1)
        stats_layout.addWidget(QLabel("Positive Yogas:"), 1, 0)
        stats_layout.addWidget(self.positive_yogas_label, 1, 1)
        stats_layout.addWidget(QLabel("Negative Yogas:"), 2, 0)
        stats_layout.addWidget(self.negative_yogas_label, 2, 1)
        stats_layout.addWidget(QLabel("Neutral Yogas:"), 3, 0)
        stats_layout.addWidget(self.neutral_yogas_label, 3, 1)

        summary_layout.addWidget(stats_group)

        # Significant yogas
        significant_group = QGroupBox("Most Significant Yogas")
        significant_layout = QVBoxLayout(significant_group)

        self.significant_table = QTableWidget()
        self.significant_table.setColumnCount(5)
        self.significant_table.setHorizontalHeaderLabels(["Yoga", "Type", "Start", "End", "Planets"])
        self.significant_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.significant_table.setAlternatingRowColors(True)

        significant_layout.addWidget(self.significant_table)

        summary_layout.addWidget(significant_group)

        # Time period distribution
        period_group = QGroupBox("Yoga Distribution by Time Period")
        period_layout = QVBoxLayout(period_group)

        self.period_table = QTableWidget()
        self.period_table.setColumnCount(4)
        self.period_table.setHorizontalHeaderLabels(["Time Period", "Total Yogas", "Positive", "Negative"])
        self.period_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.period_table.setAlternatingRowColors(True)

        period_layout.addWidget(self.period_table)

        summary_layout.addWidget(period_group)

        # Add to scroll area
        summary_widget.setWidget(summary_content)

        # Add to tab widget
        self.tab_widget.addTab(summary_widget, "Summary")

    def create_list_tab(self):
        """Create the yoga list tab."""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        # Create table for yoga list
        self.yoga_table = QTableWidget()
        self.yoga_table.setColumnCount(8)
        self.yoga_table.setHorizontalHeaderLabels([
            "Yoga Name", "Type", "Start Time", "End Time",
            "Duration", "Planets", "Strength", "Description"
        ])
        self.yoga_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.yoga_table.setAlternatingRowColors(True)

        # Set column widths
        self.yoga_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.yoga_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)

        list_layout.addWidget(self.yoga_table)

        # Add to tab widget
        self.tab_widget.addTab(list_widget, "Yoga List")

    def create_timeline_tab(self):
        """Create the timeline visualization tab."""
        timeline_widget = QScrollArea()
        timeline_widget.setWidgetResizable(True)

        timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(timeline_content)

        # Title
        title_label = QLabel("Yoga Timeline")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.timeline_layout.addWidget(title_label)

        # Timeline will be populated when data is available
        self.timeline_container = QWidget()
        self.timeline_container_layout = QVBoxLayout(self.timeline_container)

        self.timeline_layout.addWidget(self.timeline_container)
        self.timeline_layout.addStretch()

        timeline_widget.setWidget(timeline_content)

        # Add to tab widget
        self.tab_widget.addTab(timeline_widget, "Timeline")

    def create_analysis_tab(self):
        """Create the analysis tab for detailed interpretations."""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)

        # Create a split view
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Yoga selection list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Select Yoga for Analysis:"))

        self.yoga_list_widget = QTableWidget()
        self.yoga_list_widget.setColumnCount(2)
        self.yoga_list_widget.setHorizontalHeaderLabels(["Yoga", "Type"])
        self.yoga_list_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.yoga_list_widget.setAlternatingRowColors(True)
        self.yoga_list_widget.itemSelectionChanged.connect(self.update_yoga_analysis)

        left_layout.addWidget(self.yoga_list_widget)

        # Right side: Yoga details and interpretation
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Yoga details group
        details_group = QGroupBox("Yoga Details")
        details_layout = QVBoxLayout(details_group)

        self.yoga_details_text = QTextEdit()
        self.yoga_details_text.setReadOnly(True)

        details_layout.addWidget(self.yoga_details_text)

        # Interpretation group
        interpretation_group = QGroupBox("Interpretation & Effects")
        interpretation_layout = QVBoxLayout(interpretation_group)

        self.yoga_interpretation_text = QTextEdit()
        self.yoga_interpretation_text.setReadOnly(True)

        interpretation_layout.addWidget(self.yoga_interpretation_text)

        # Add groups to right layout
        right_layout.addWidget(details_group)
        right_layout.addWidget(interpretation_group)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Set initial sizes
        splitter.setSizes([300, 700])

        # Add splitter to layout
        analysis_layout.addWidget(splitter)

        # Add to tab widget
        self.tab_widget.addTab(analysis_widget, "Analysis")

    def update_yoga_results(self, results: Dict):
        """
        Update the panel with new yoga results.

        Args:
            results: Dictionary with yoga results data
        """
        # Store the data
        self.yoga_results = results.get("yoga_results")
        self.yoga_counts = results.get("yoga_counts")
        self.significant_yogas = results.get("significant_yogas")
        self.yoga_by_period = results.get("yoga_by_period")

        # Update UI components
        self.update_summary_tab()
        self.update_list_tab()
        self.update_timeline_tab()
        self.update_analysis_tab()

        # Apply any active filters
        self.apply_filters()

    def update_summary_tab(self):
        """Update the summary tab with current data."""
        if not self.yoga_counts:
            return

        # Update statistics
        self.total_yogas_label.setText(str(self.yoga_counts.get("Positive", 0) +
                                           self.yoga_counts.get("Negative", 0) +
                                           self.yoga_counts.get("Neutral", 0)))
        self.positive_yogas_label.setText(str(self.yoga_counts.get("Positive", 0)))
        self.negative_yogas_label.setText(str(self.yoga_counts.get("Negative", 0)))
        self.neutral_yogas_label.setText(str(self.yoga_counts.get("Neutral", 0)))

        # Update significant yogas table
        if self.significant_yogas:
            # Initialize table
            self.significant_table.setRowCount(len(self.significant_yogas))

            for i, yoga in enumerate(self.significant_yogas):
                # Get yoga data
                yoga_name = yoga.get("yoga_name", "")
                yoga_type = yoga.get("Type", "")
                start_time = yoga.get("Start Time", "")
                end_time = yoga.get("End Time", "")
                planets = yoga.get("Planets", "")

                # Create items
                name_item = QTableWidgetItem(yoga_name)
                type_item = QTableWidgetItem(yoga_type)
                start_item = QTableWidgetItem(str(start_time))
                end_item = QTableWidgetItem(str(end_time))
                planets_item = QTableWidgetItem(planets)

                # Set colors based on yoga type
                if yoga_type == "Positive":
                    type_item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
                elif yoga_type == "Negative":
                    type_item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
                else:
                    type_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow

                # Add items to table
                self.significant_table.setItem(i, 0, name_item)
                self.significant_table.setItem(i, 1, type_item)
                self.significant_table.setItem(i, 2, start_item)
                self.significant_table.setItem(i, 3, end_item)
                self.significant_table.setItem(i, 4, planets_item)

        # Update period distribution table
        if self.yoga_by_period:
            # Initialize table
            self.period_table.setRowCount(len(self.yoga_by_period))

            row = 0
            for period, yogas in self.yoga_by_period.items():
                # Count yoga types
                positive_count = sum(
                    1 for y in yogas if getattr(y, "yoga", {}).yoga_type.value.capitalize() == "Positive")
                negative_count = sum(
                    1 for y in yogas if getattr(y, "yoga", {}).yoga_type.value.capitalize() == "Negative")
                total_count = len(yogas)

                # Create items
                period_item = QTableWidgetItem(period)
                total_item = QTableWidgetItem(str(total_count))
                positive_item = QTableWidgetItem(str(positive_count))
                negative_item = QTableWidgetItem(str(negative_count))

                # Add items to table
                self.period_table.setItem(row, 0, period_item)
                self.period_table.setItem(row, 1, total_item)
                self.period_table.setItem(row, 2, positive_item)
                self.period_table.setItem(row, 3, negative_item)

                row += 1

    def update_list_tab(self):
        """Update the yoga list tab with current data."""
        if not self.yoga_results:
            return

        # Clear existing data
        self.yoga_table.setRowCount(0)

        # Add each yoga to the table
        for i, row in self.yoga_results.iterrows():
            self.yoga_table.insertRow(i)

            # Process row data
            yoga_name = row.get("Yoga Name", "")
            yoga_type = row.get("Type", "")
            start_time = row.get("Start Time", "")
            end_time = row.get("End Time", "")
            duration = row.get("Duration", "")
            planets = row.get("Planets", "")
            strength = row.get("Strength", "")
            description = row.get("Description", "")

            # Create items
            name_item = QTableWidgetItem(yoga_name)
            type_item = QTableWidgetItem(yoga_type)
            start_item = QTableWidgetItem(str(start_time))
            end_item = QTableWidgetItem(str(end_time))
            duration_item = QTableWidgetItem(str(duration))
            planets_item = QTableWidgetItem(planets)
            strength_item = QTableWidgetItem(str(strength))
            desc_item = QTableWidgetItem(description)

            # Set colors based on yoga type
            if yoga_type == "Positive":
                type_item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
            elif yoga_type == "Negative":
                type_item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
            else:
                type_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow

            # Add items to table
            self.yoga_table.setItem(i, 0, name_item)
            self.yoga_table.setItem(i, 1, type_item)
            self.yoga_table.setItem(i, 2, start_item)
            self.yoga_table.setItem(i, 3, end_item)
            self.yoga_table.setItem(i, 4, duration_item)
            self.yoga_table.setItem(i, 5, planets_item)
            self.yoga_table.setItem(i, 6, strength_item)
            self.yoga_table.setItem(i, 7, desc_item)

    def update_timeline_tab(self):
        """Update the timeline visualization tab with current data."""
        if not self.yoga_results:
            return

        # Clear existing timeline
        self._clear_layout(self.timeline_container_layout)

        # Sort yogas by start time
        if 'Start Time' in self.yoga_results.columns:
            sorted_yogas = self.yoga_results.sort_values(by='Start Time')
        else:
            sorted_yogas = self.yoga_results

        # Create a timeline entry for each yoga
        for i, row in sorted_yogas.iterrows():
            # Create timeline entry
            entry = self._create_timeline_entry(row)
            self.timeline_container_layout.addWidget(entry)

        # Add a stretcher at the end
        self.timeline_container_layout.addStretch()

    def update_analysis_tab(self):
        """Update the analysis tab with current data."""
        if not self.yoga_results:
            return

        # Clear existing data
        self.yoga_list_widget.setRowCount(0)

        # Get unique yogas
        unique_yogas = {}
        for i, row in self.yoga_results.iterrows():
            yoga_name = row.get("Yoga Name", "")
            yoga_type = row.get("Type", "")

            if yoga_name not in unique_yogas:
                unique_yogas[yoga_name] = yoga_type

        # Add yogas to list
        for i, (name, yoga_type) in enumerate(unique_yogas.items()):
            self.yoga_list_widget.insertRow(i)

            name_item = QTableWidgetItem(name)
            type_item = QTableWidgetItem(yoga_type)

            # Set colors based on yoga type
            if yoga_type == "Positive":
                type_item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
            elif yoga_type == "Negative":
                type_item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
            else:
                type_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow

            self.yoga_list_widget.setItem(i, 0, name_item)
            self.yoga_list_widget.setItem(i, 1, type_item)

    def update_yoga_analysis(self):
        """Update the yoga analysis display based on selection."""
        # Get selected yoga
        selected_items = self.yoga_list_widget.selectedItems()
        if not selected_items:
            return

        yoga_name = self.yoga_list_widget.item(selected_items[0].row(), 0).text()

        # Find yoga data
        yoga_data = None
        for i, row in self.yoga_results.iterrows():
            if row.get("Yoga Name", "") == yoga_name:
                yoga_data = row
                break

        if not yoga_data:
            return

        # Update details display
        details_text = f"<h2>{yoga_name}</h2>"
        details_text += f"<p><b>Type:</b> {yoga_data.get('Type', '')}</p>"
        details_text += f"<p><b>Planets Involved:</b> {yoga_data.get('Planets', '')}</p>"
        details_text += f"<p><b>Start Time:</b> {yoga_data.get('Start Time', '')}</p>"
        details_text += f"<p><b>End Time:</b> {yoga_data.get('End Time', '')}</p>"
        details_text += f"<p><b>Duration:</b> {yoga_data.get('Duration', '')}</p>"
        details_text += f"<p><b>Strength:</b> {yoga_data.get('Strength', '')}</p>"

        self.yoga_details_text.setHtml(details_text)

        # Update interpretation display
        interpretation_text = f"<h3>{yoga_name} Interpretation</h3>"
        interpretation_text += f"<p>{yoga_data.get('Description', '')}</p>"

        # Add general effects
        interpretation_text += "<h3>General Effects</h3>"

        yoga_type = yoga_data.get('Type', '')
        if yoga_type == "Positive":
            interpretation_text += "<p>This is a <span style='color: green;'><b>beneficial yoga</b></span> that typically brings positive effects to your life. It indicates a favorable planetary alignment that supports success and well-being.</p>"
        elif yoga_type == "Negative":
            interpretation_text += "<p>This is a <span style='color: red;'><b>challenging yoga</b></span> that may present obstacles or difficulties. It indicates a planetary alignment that requires caution and mindfulness.</p>"
        else:
            interpretation_text += "<p>This is a <span style='color: orange;'><b>neutral yoga</b></span> that can have mixed effects depending on other factors in your chart. It indicates a planetary alignment with both opportunities and challenges.</p>"

        # Add analysis of timing
        interpretation_text += "<h3>Timing Analysis</h3>"
        interpretation_text += "<p>The effects of this yoga are most pronounced during its active period. You may wish to plan activities accordingly, especially around peak times of influence.</p>"

        # Add more personalized details based on yoga type
        if yoga_type == "Positive":
            interpretation_text += "<h3>Recommended Actions</h3>"
            interpretation_text += "<ul>"
            interpretation_text += "<li>Take advantage of this favorable period for important endeavors</li>"
            interpretation_text += "<li>Begin new projects or initiatives</li>"
            interpretation_text += "<li>Make important decisions or commitments</li>"
            interpretation_text += "<li>Focus on areas related to the planets involved</li>"
            interpretation_text += "</ul>"
        elif yoga_type == "Negative":
            interpretation_text += "<h3>Recommended Precautions</h3>"
            interpretation_text += "<ul>"
            interpretation_text += "<li>Exercise caution in matters related to the planets involved</li>"
            interpretation_text += "<li>Postpone major decisions if possible</li>"
            interpretation_text += "<li>Practice patience and mindfulness</li>"
            interpretation_text += "<li>Consider remedial measures appropriate for the planets involved</li>"
            interpretation_text += "</ul>"

        self.yoga_interpretation_text.setHtml(interpretation_text)

    def apply_filters(self):
        """Apply filters to yoga display."""
        if not self.yoga_results:
            return

        # Get filter settings
        show_positive = self.positive_cb.isChecked()
        show_negative = self.negative_cb.isChecked()
        show_neutral = self.neutral_cb.isChecked()
        timeframe = self.timeframe_combo.currentText()

        # Create filtered copy of data
        filtered_df = self.yoga_results.copy()

        # Apply type filter
        type_conditions = []
        if show_positive:
            type_conditions.append("Type == 'Positive'")
        if show_negative:
            type_conditions.append("Type == 'Negative'")
        if show_neutral:
            type_conditions.append("Type == 'Neutral'")

        if type_conditions:
            type_query = " | ".join(type_conditions)
            filtered_df = filtered_df.query(type_query)

        # Apply timeframe filter
        now = datetime.now()

        if timeframe == "Today":
            today_str = now.strftime("%Y-%m-%d")
            if 'Start Time' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Start Time'].str.contains(today_str)]
        elif timeframe == "This Week":
            # Simple approximation - past 7 days
            if 'Start Time' in filtered_df.columns:
                filtered_df = filtered_df[
                    pd.to_datetime(filtered_df['Start Time']) > (now - pd.Timedelta(days=7))
                    ]
        elif timeframe == "This Month":
            # Simple approximation - past 30 days
            if 'Start Time' in filtered_df.columns:
                filtered_df = filtered_df[
                    pd.to_datetime(filtered_df['Start Time']) > (now - pd.Timedelta(days=30))
                    ]
        elif timeframe == "Active Now":
            # Yogas that are currently active
            now_str = now.strftime("%Y-%m-%d %H:%M")
            if 'Start Time' in filtered_df.columns and 'End Time' in filtered_df.columns:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['Start Time']) <= now) &
                    ((pd.to_datetime(filtered_df['End Time']) >= now) |
                     (filtered_df['End Time'] == "Ongoing"))
                    ]

        # Update UI with filtered data
        self._update_list_with_filter(filtered_df)

    def _update_list_with_filter(self, filtered_df):
        """
        Update the yoga list with filtered data.

        Args:
            filtered_df: Filtered DataFrame
        """
        # Clear existing data
        self.yoga_table.setRowCount(0)

        # Add each yoga to the table
        for i, row in filtered_df.iterrows():
            self.yoga_table.insertRow(i)

            # Process row data
            yoga_name = row.get("Yoga Name", "")
            yoga_type = row.get("Type", "")
            start_time = row.get("Start Time", "")
            end_time = row.get("End Time", "")
            duration = row.get("Duration", "")
            planets = row.get("Planets", "")
            strength = row.get("Strength", "")
            description = row.get("Description", "")

            # Create items
            name_item = QTableWidgetItem(yoga_name)
            type_item = QTableWidgetItem(yoga_type)
            start_item = QTableWidgetItem(str(start_time))
            end_item = QTableWidgetItem(str(end_time))
            duration_item = QTableWidgetItem(str(duration))
            planets_item = QTableWidgetItem(planets)
            strength_item = QTableWidgetItem(str(strength))
            desc_item = QTableWidgetItem(description)

            # Set colors based on yoga type
            if yoga_type == "Positive":
                type_item.setBackground(QBrush(QColor("#E2EFDA")))  # Light green
            elif yoga_type == "Negative":
                type_item.setBackground(QBrush(QColor("#FFCCCC")))  # Light red
            else:
                type_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow

            # Add items to table
            self.yoga_table.setItem(i, 0, name_item)
            self.yoga_table.setItem(i, 1, type_item)
            self.yoga_table.setItem(i, 2, start_item)
            self.yoga_table.setItem(i, 3, end_item)
            self.yoga_table.setItem(i, 4, duration_item)
            self.yoga_table.setItem(i, 5, planets_item)
            self.yoga_table.setItem(i, 6, strength_item)
            self.yoga_table.setItem(i, 7, desc_item)

    def _create_timeline_entry(self, row):
        """
        Create a timeline entry widget for a yoga.

        Args:
            row: Row data for a yoga

        Returns:
            QFrame: Timeline entry widget
        """
        # Create frame
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(1)
        frame.setMinimumHeight(80)
        frame.setMaximumHeight(100)

        # Set frame color based on yoga type
        yoga_type = row.get("Type", "")
        if yoga_type == "Positive":
            frame.setStyleSheet("QFrame { background-color: #E2EFDA; }")  # Light green
        elif yoga_type == "Negative":
            frame.setStyleSheet("QFrame { background-color: #FFCCCC; }")  # Light red
        else:
            frame.setStyleSheet("QFrame { background-color: #FFF2CC; }")  # Light yellow

        # Create layout
        layout = QHBoxLayout(frame)

        # Time column
        time_layout = QVBoxLayout()

        start_time = str(row.get("Start Time", ""))
        end_time = str(row.get("End Time", ""))

        start_label = QLabel(f"Start: {start_time}")
        start_label.setFont(QFont("Arial", 8))

        end_label = QLabel(f"End: {end_time}")
        end_label.setFont(QFont("Arial", 8))

        time_layout.addWidget(start_label)
        time_layout.addWidget(end_label)

        # Yoga info column
        info_layout = QVBoxLayout()

        yoga_name = row.get("Yoga Name", "")
        name_label = QLabel(yoga_name)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))

        planets = row.get("Planets", "")
        planets_label = QLabel(f"Planets: {planets}")
        planets_label.setFont(QFont("Arial", 8))

        description = row.get("Description", "")
        if len(description) > 100:
            description = description[:97] + "..."
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 8))
        desc_label.setWordWrap(True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(planets_label)
        info_layout.addWidget(desc_label)

        # Add columns to layout
        layout.addLayout(time_layout, 1)
        layout.addLayout(info_layout, 3)

        return frame

    def _clear_layout(self, layout):
        """
        Clear all items from a layout.

        Args:
            layout: Layout to clear
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())