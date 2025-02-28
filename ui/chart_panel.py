"""
Chart panel for KP Astrology Dashboard.
Displays planetary positions, house data, and chart wheel.
"""
from typing import Dict, List, Optional
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QGroupBox, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter, QPen, QFont


class ChartPanel(QWidget):
    """Panel for displaying chart data and visualizations."""

    def __init__(self, parent=None):
        """Initialize the chart panel."""
        super().__init__(parent)
        self.init_ui()

        # Store data
        self.planet_positions = None
        self.house_positions = None
        self.hora_timings = None

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Create a splitter for resizable sections
        self.splitter = QSplitter(Qt.Vertical)

        # Upper section: Chart wheel and summary
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)

        # Chart wheel display
        self.chart_wheel = ChartWheel()

        # Chart info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)

        # Current time and location
        self.chart_info_label = QLabel("Chart Information")
        self.chart_info_label.setAlignment(Qt.AlignCenter)
        self.chart_info_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Chart settings
        settings_group = QGroupBox("Chart Settings")
        settings_grid = QGridLayout(settings_group)

        settings_grid.addWidget(QLabel("Ayanamsa:"), 0, 0)
        self.ayanamsa_label = QLabel("Krishnamurti")
        settings_grid.addWidget(self.ayanamsa_label, 0, 1)

        settings_grid.addWidget(QLabel("House System:"), 1, 0)
        self.house_system_label = QLabel("Placidus")
        settings_grid.addWidget(self.house_system_label, 1, 1)

        # Current period highlights
        highlight_group = QGroupBox("Current Periods")
        highlight_grid = QGridLayout(highlight_group)

        highlight_grid.addWidget(QLabel("Current Hora:"), 0, 0)
        self.current_hora_label = QLabel("Sun")
        highlight_grid.addWidget(self.current_hora_label, 0, 1)

        highlight_grid.addWidget(QLabel("Current Moon Sign:"), 1, 0)
        self.moon_sign_label = QLabel("Cancer")
        highlight_grid.addWidget(self.moon_sign_label, 1, 1)

        highlight_grid.addWidget(QLabel("Rising Sign:"), 2, 0)
        self.asc_sign_label = QLabel("Libra")
        highlight_grid.addWidget(self.asc_sign_label, 2, 1)

        # Add to info layout
        info_layout.addWidget(self.chart_info_label)
        info_layout.addWidget(settings_group)
        info_layout.addWidget(highlight_group)
        info_layout.addStretch()

        # Add chart wheel and info to upper layout
        upper_layout.addWidget(self.chart_wheel, 2)
        upper_layout.addWidget(info_widget, 1)

        # Lower section: Tabbed data panels
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)

        # Create tabs for different data views
        self.tab_widget = QTabWidget()

        # Create data tabs
        self.create_planets_tab()
        self.create_houses_tab()
        self.create_aspects_tab()
        self.create_hora_tab()

        lower_layout.addWidget(self.tab_widget)

        # Add widgets to splitter
        self.splitter.addWidget(upper_widget)
        self.splitter.addWidget(lower_widget)

        # Set initial sizes
        self.splitter.setSizes([400, 400])

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def create_planets_tab(self):
        """Create the planets data tab."""
        planets_widget = QWidget()
        planets_layout = QVBoxLayout(planets_widget)

        # Create table for planet positions
        self.planets_table = QTableWidget()
        self.planets_table.setColumnCount(9)
        self.planets_table.setHorizontalHeaderLabels([
            "Planet", "Sign", "Position", "House", "Nakshatra",
            "Rashi Lord", "Nakshatra Lord", "Sub Lord", "Sub-Sub Lord"
        ])
        self.planets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.planets_table.setAlternatingRowColors(True)

        planets_layout.addWidget(self.planets_table)

        self.tab_widget.addTab(planets_widget, "Planet Positions")

    def create_houses_tab(self):
        """Create the houses data tab."""
        houses_widget = QWidget()
        houses_layout = QVBoxLayout(houses_widget)

        # Create table for house data
        self.houses_table = QTableWidget()
        self.houses_table.setColumnCount(8)
        self.houses_table.setHorizontalHeaderLabels([
            "House", "Sign", "Cusp Position", "Size",
            "Nakshatra", "Rashi Lord", "Nakshatra Lord", "Sub Lord"
        ])
        self.houses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.houses_table.setAlternatingRowColors(True)

        houses_layout.addWidget(self.houses_table)

        self.tab_widget.addTab(houses_widget, "House Data")

    def create_aspects_tab(self):
        """Create the aspects data tab."""
        aspects_widget = QWidget()
        aspects_layout = QVBoxLayout(aspects_widget)

        # Create table for aspects
        self.aspects_table = QTableWidget()
        self.aspects_table.setColumnCount(4)
        self.aspects_table.setHorizontalHeaderLabels([
            "Planet 1", "Planet 2", "Aspect Type", "Orb"
        ])
        self.aspects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aspects_table.setAlternatingRowColors(True)

        aspects_layout.addWidget(self.aspects_table)

        self.tab_widget.addTab(aspects_widget, "Aspects")

    def create_hora_tab(self):
        """Create the hora timings tab."""
        hora_widget = QWidget()
        hora_layout = QVBoxLayout(hora_widget)

        # Create table for hora timings
        self.hora_table = QTableWidget()
        self.hora_table.setColumnCount(4)
        self.hora_table.setHorizontalHeaderLabels([
            "Start Time", "End Time", "Planet", "Day/Night"
        ])
        self.hora_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hora_table.setAlternatingRowColors(True)

        hora_layout.addWidget(self.hora_table)

        self.tab_widget.addTab(hora_widget, "Hora Timings")

    def update_planet_positions(self, planet_data):
        """
        Update planet positions display.

        Args:
            planet_data: DataFrame with planet position data
        """
        self.planet_positions = planet_data
        if not planet_data:
            return

        # Update table
        self.planets_table.setRowCount(len(planet_data))

        for i, (_, row) in enumerate(planet_data.iterrows()):
            # Create items
            planet_item = QTableWidgetItem(row.get("Planet", ""))
            sign_item = QTableWidgetItem(row.get("Sign", ""))
            position_item = QTableWidgetItem(row.get("Position", ""))
            house_item = QTableWidgetItem(str(row.get("House", "")))
            nakshatra_item = QTableWidgetItem(row.get("Nakshatra", ""))
            rashi_lord_item = QTableWidgetItem(row.get("Rashi Lord", ""))
            nakshatra_lord_item = QTableWidgetItem(row.get("Nakshatra Lord", ""))
            sub_lord_item = QTableWidgetItem(row.get("Sub Lord", ""))
            subsub_lord_item = QTableWidgetItem(row.get("Sub-Sub Lord", ""))

            # Add items to table
            self.planets_table.setItem(i, 0, planet_item)
            self.planets_table.setItem(i, 1, sign_item)
            self.planets_table.setItem(i, 2, position_item)
            self.planets_table.setItem(i, 3, house_item)
            self.planets_table.setItem(i, 4, nakshatra_item)
            self.planets_table.setItem(i, 5, rashi_lord_item)
            self.planets_table.setItem(i, 6, nakshatra_lord_item)
            self.planets_table.setItem(i, 7, sub_lord_item)
            self.planets_table.setItem(i, 8, subsub_lord_item)

        # Update chart wheel
        self.chart_wheel.update_planets(planet_data)

        # Update info panel
        self._update_info_panel()

    def update_house_positions(self, house_data):
        """
        Update house positions display.

        Args:
            house_data: DataFrame with house position data
        """
        self.house_positions = house_data
        if not house_data:
            return

        # Update table
        self.houses_table.setRowCount(len(house_data))

        for i, (_, row) in enumerate(house_data.iterrows()):
            # Create items
            house_item = QTableWidgetItem(row.get("House", ""))
            sign_item = QTableWidgetItem(row.get("Sign", ""))
            position_item = QTableWidgetItem(row.get("Position", ""))
            size_item = QTableWidgetItem(row.get("Size", ""))
            nakshatra_item = QTableWidgetItem(row.get("Nakshatra", ""))
            rashi_lord_item = QTableWidgetItem(row.get("Rashi Lord", ""))
            nakshatra_lord_item = QTableWidgetItem(row.get("Nakshatra Lord", ""))
            sub_lord_item = QTableWidgetItem(row.get("Sub Lord", ""))

            # Add items to table
            self.houses_table.setItem(i, 0, house_item)
            self.houses_table.setItem(i, 1, sign_item)
            self.houses_table.setItem(i, 2, position_item)
            self.houses_table.setItem(i, 3, size_item)
            self.houses_table.setItem(i, 4, nakshatra_item)
            self.houses_table.setItem(i, 5, rashi_lord_item)
            self.houses_table.setItem(i, 6, nakshatra_lord_item)
            self.houses_table.setItem(i, 7, sub_lord_item)

        # Update chart wheel
        self.chart_wheel.update_houses(house_data)

    def update_hora_timings(self, hora_data):
        """
        Update hora timings display.

        Args:
            hora_data: DataFrame with hora timing data
        """
        self.hora_timings = hora_data
        if not hora_data:
            return

        # Update table
        self.hora_table.setRowCount(len(hora_data))

        for i, (_, row) in enumerate(hora_data.iterrows()):
            # Create items
            start_item = QTableWidgetItem(row.get("Start Time", ""))
            end_item = QTableWidgetItem(row.get("End Time", ""))
            planet_item = QTableWidgetItem(row.get("Planet", ""))
            day_night_item = QTableWidgetItem(row.get("Day/Night", ""))

            # Highlight current hora
            import datetime
            now = datetime.datetime.now().strftime("%H:%M")
            if (row.get("Start Time", "") <= now <= row.get("End Time", "")):
                start_item.setBackground(QBrush(QColor("#FFF2CC")))  # Light yellow
                end_item.setBackground(QBrush(QColor("#FFF2CC")))
                planet_item.setBackground(QBrush(QColor("#FFF2CC")))
                day_night_item.setBackground(QBrush(QColor("#FFF2CC")))

                # Update current hora in info panel
                self.current_hora_label.setText(
                    f"{row.get('Planet', '')} ({row.get('Start Time', '')}-{row.get('End Time', '')})")

            # Add items to table
            self.hora_table.setItem(i, 0, start_item)
            self.hora_table.setItem(i, 1, end_item)
            self.hora_table.setItem(i, 2, planet_item)
            self.hora_table.setItem(i, 3, day_night_item)

    def _update_info_panel(self):
        """Update the chart info panel with current data."""
        if not self.planet_positions:
            return

        # Find Moon sign
        for i, row in self.planet_positions.iterrows():
            if row.get("Planet", "") == "Moon":
                self.moon_sign_label.setText(row.get("Sign", ""))
            elif row.get("Planet", "") == "Ascendant":
                self.asc_sign_label.setText(row.get("Sign", ""))


class ChartWheel(QFrame):
    """Widget for displaying the chart wheel visualization."""

    def __init__(self, parent=None):
        """Initialize the chart wheel."""
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)

        # Store data
        self.planet_data = None
        self.house_data = None

        # Planet symbols
        self.planet_symbols = {
            "Sun": "☉",
            "Moon": "☽",
            "Mercury": "☿",
            "Venus": "♀",
            "Mars": "♂",
            "Jupiter": "♃",
            "Saturn": "♄",
            "Rahu": "☊",
            "Ketu": "☋",
            "Uranus": "♅",
            "Neptune": "♆",
            "Pluto": "♇",
            "Ascendant": "ASC"
        }

        # Sign symbols
        self.sign_symbols = {
            "Aries": "♈",
            "Taurus": "♉",
            "Gemini": "♊",
            "Cancer": "♋",
            "Leo": "♌",
            "Virgo": "♍",
            "Libra": "♎",
            "Scorpio": "♏",
            "Sagittarius": "♐",
            "Capricorn": "♑",
            "Aquarius": "♒",
            "Pisces": "♓"
        }

        # Sign colors
        self.sign_colors = {
            "Aries": QColor(255, 200, 200),  # Light red
            "Taurus": QColor(200, 255, 200),  # Light green
            "Gemini": QColor(255, 255, 200),  # Light yellow
            "Cancer": QColor(200, 200, 255),  # Light blue
            "Leo": QColor(255, 200, 200),  # Light red
            "Virgo": QColor(200, 255, 200),  # Light green
            "Libra": QColor(255, 255, 200),  # Light yellow
            "Scorpio": QColor(200, 200, 255),  # Light blue
            "Sagittarius": QColor(255, 200, 200),  # Light red
            "Capricorn": QColor(200, 255, 200),  # Light green
            "Aquarius": QColor(255, 255, 200),  # Light yellow
            "Pisces": QColor(200, 200, 255)  # Light blue
        }

    def update_planets(self, planet_data):
        """
        Update planet data for the chart wheel.

        Args:
            planet_data: DataFrame with planet position data
        """
        self.planet_data = planet_data
        self.update()

    def update_houses(self, house_data):
        """
        Update house data for the chart wheel.

        Args:
            house_data: DataFrame with house position data
        """
        self.house_data = house_data
        self.update()

    def paintEvent(self, event):
        """Paint the chart wheel visualization."""
        super().paintEvent(event)

        if not self.planet_data or not self.house_data:
            # Draw placeholder if no data
            self._draw_placeholder()
            return

        # Initialize painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Calculate radius for different chart elements
        outer_radius = min(width, height) / 2 - 10
        sign_radius = outer_radius - 20
        house_radius = sign_radius - 30
        planet_radius = house_radius - 40

        # Draw outer circle
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center_x - outer_radius, center_y - outer_radius,
                            outer_radius * 2, outer_radius * 2)

        # Draw sign circle
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(center_x - sign_radius, center_y - sign_radius,
                            sign_radius * 2, sign_radius * 2)

        # Draw house circle
        painter.drawEllipse(center_x - house_radius, center_y - house_radius,
                            house_radius * 2, house_radius * 2)

        # Draw inner circle
        painter.drawEllipse(center_x - planet_radius, center_y - planet_radius,
                            planet_radius * 2, planet_radius * 2)

        # Draw house cusps and signs
        self._draw_houses(painter, center_x, center_y, house_radius, sign_radius, outer_radius)

        # Draw planets
        self._draw_planets(painter, center_x, center_y, planet_radius)

        # Draw center
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(center_x - 5, center_y - 5, 10, 10)

    def _draw_placeholder(self):
        """Draw a placeholder when no data is available."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set font
        font = QFont("Arial", 12)
        painter.setFont(font)

        # Draw message
        text = "Chart data not available"
        painter.drawText(self.rect(), Qt.AlignCenter, text)

    def _draw_houses(self, painter, center_x, center_y, house_radius, sign_radius, outer_radius):
        """
        Draw house cusps and signs.

        Args:
            painter: QPainter instance
            center_x: X-coordinate of chart center
            center_y: Y-coordinate of chart center
            house_radius: Radius for house circle
            sign_radius: Radius for sign circle
            outer_radius: Radius for outer circle
        """
        if not self.house_data:
            return

        # Set up pen and brush
        painter.setPen(QPen(Qt.black, 1))

        # Draw each house cusp
        for i, row in self.house_data.iterrows():
            house_num = i + 1  # 1-based house number
            cusp_deg = row.get("LonDecDeg", 0)
            sign = row.get("Sign", "")

            # Convert zodiac degrees to angle in degrees (0 at top, clockwise)
            angle_deg = 90 - cusp_deg
            angle_rad = angle_deg * 3.14159 / 180

            # Calculate endpoints for house line
            x1 = center_x + house_radius * -1 * (angle_rad % 6.28)
            y1 = center_y + house_radius * -1 * (angle_rad % 6.28)
            x2 = center_x + outer_radius * -1 * (angle_rad % 6.28)
            y2 = center_y + outer_radius * -1 * (angle_rad % 6.28)

            # Draw house line
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

            # Draw house number
            text_x = center_x + (house_radius - 15) * (angle_rad % 6.28)
            text_y = center_y + (house_radius - 15) * (angle_rad % 6.28)
            painter.drawText(int(text_x - 5), int(text_y + 5), str(house_num))

            # Draw sign if this is the start of a sign
            if i % 12 == 0 or (i > 0 and row.get("Sign") != self.house_data.iloc[i - 1].get("Sign")):
                # Draw sign background
                mid_radius = (sign_radius + house_radius) / 2
                next_cusp_deg = self.house_data.iloc[(i + 1) % 12].get("LonDecDeg", cusp_deg + 30)

                # Simple handling for wrapping around the zodiac
                if next_cusp_deg < cusp_deg:
                    next_cusp_deg += 360

                # Calculate start and sweep angles
                start_angle = 90 - cusp_deg
                sweep_angle = cusp_deg - next_cusp_deg

                # Draw sign symbol at midpoint
                mid_angle_deg = cusp_deg + (next_cusp_deg - cusp_deg) / 2
                mid_angle_rad = (90 - mid_angle_deg) * 3.14159 / 180

                text_x = center_x + mid_radius * (mid_angle_rad % 6.28)
                text_y = center_y + mid_radius * (mid_angle_rad % 6.28)

                sign_symbol = self.sign_symbols.get(sign, "?")
                painter.drawText(int(text_x - 5), int(text_y + 5), sign_symbol)

    def _draw_planets(self, painter, center_x, center_y, planet_radius):
        """
        Draw planets in the chart.

        Args:
            painter: QPainter instance
            center_x: X-coordinate of chart center
            center_y: Y-coordinate of chart center
            planet_radius: Radius for planet circle
        """
        if not self.planet_data:
            return

        # Set up pen, brush, and font
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.white))
        font = QFont("Arial", 8)
        painter.setFont(font)

        # Calculate reasonable spacing
        num_planets = len(self.planet_data)
        angle_step = 360 / max(num_planets, 12)  # At least 30 degrees apart

        # Track angles to avoid overlapping
        used_angles = []
        min_angle_diff = 15  # Minimum angle difference in degrees

        # Draw each planet
        for i, row in self.planet_data.iterrows():
            planet_name = row.get("Planet", "").split("(")[0].strip()  # Remove retrograde marker if present
            planet_deg = row.get("Longitude", 0)
            house = row.get("House", "")

            # Get symbol
            symbol = self.planet_symbols.get(planet_name, planet_name[:3])

            # Convert zodiac degrees to angle in degrees (0 at top, clockwise)
            angle_deg = 90 - planet_deg

            # Avoid overlapping by adjusting angle if necessary
            for used_angle in used_angles:
                while abs((angle_deg - used_angle + 180) % 360 - 180) < min_angle_diff:
                    angle_deg += min_angle_diff

            used_angles.append(angle_deg)
            angle_rad = angle_deg * 3.14159 / 180

            # Calculate position on the circle
            circle_x = center_x + planet_radius * (angle_rad % 6.28)
            circle_y = center_y + planet_radius * (angle_rad % 6.28)

            # Draw planet circle
            painter.drawEllipse(int(circle_x - 8), int(circle_y - 8), 16, 16)

            # Draw planet symbol
            painter.drawText(int(circle_x - 4), int(circle_y + 4), symbol)