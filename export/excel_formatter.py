"""
Excel formatter module for KP Astrology Dashboard.
Provides styling, formatting, and layout functionality for Excel exports.
"""
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from datetime import datetime


class ExcelFormatter:
    """Format Excel sheets with consistent styling and layouts."""

    def __init__(self):
        """Initialize the Excel formatter."""
        # Store formats that will be created when a workbook is provided
        self.formats = {}

        # Define standard column widths
        self.column_widths = {
            "time": 10,  # For time columns
            "planet": 12,  # For planet names
            "position": 18,  # For positions
            "sign": 10,  # For signs/rashis
            "house": 8,  # For house numbers
            "nakshatra": 15,  # For nakshatras
            "lord": 12,  # For lords
            "aspect": 40,  # For aspects
            "yoga": 25,  # For yoga names
            "duration": 10,  # For durations
            "description": 50,  # For descriptions
            "default": 15  # Default width
        }

        # Color definitions for different elements
        self.colors = {
            "header": "#D7E4BC",  # Light green for headers
            "highlight": "#FFFF00",  # Yellow for highlighting
            "time": "#E2EFDA",  # Light green for time cells
            "positive_yoga": "#E2EFDA",  # Light green for positive yogas
            "negative_yoga": "#FFCCCC",  # Light red for negative yogas
            "neutral_yoga": "#FFF2CC",  # Light yellow for neutral yogas
            "sun": "#FFD700",  # Gold
            "moon": "#C0C0C0",  # Silver
            "mercury": "#C0D9D9",  # Light Blue
            "venus": "#FFCCFF",  # Light Pink
            "mars": "#FF6B6B",  # Red
            "jupiter": "#FFFF99",  # Yellow
            "saturn": "#CCCCCC",  # Grey
            "rahu": "#9966CC",  # Purple
            "ketu": "#CC9966"  # Brown
        }

    def create_formats(self, workbook):
        """
        Create and store reusable cell formats for Excel.

        Args:
            workbook: XlsxWriter workbook object
        """
        print("Creating Excel formats")

        # Header format
        self.formats["header"] = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': self.colors["header"],
            'border': 1
        })

        # Default cell format
        self.formats["cell"] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Time cell format
        self.formats["time"] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': self.colors["time"]
        })

        # Text cell format (left-aligned)
        self.formats["text"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })

        # Aspect cell format
        self.formats["aspect"] = workbook.add_format({
            'border': 1,
            'text_wrap': True,
            'align': 'left',
            'valign': 'top'
        })

        # Highlight format for current time
        self.formats["highlight"] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors["highlight"]
        })

        # Yoga formats
        self.formats["positive_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': self.colors["positive_yoga"]
        })

        self.formats["negative_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': self.colors["negative_yoga"]
        })

        self.formats["neutral_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': self.colors["neutral_yoga"]
        })

        # Create formats for each planet
        for planet, color in {
            "sun": self.colors["sun"],
            "moon": self.colors["moon"],
            "mercury": self.colors["mercury"],
            "venus": self.colors["venus"],
            "mars": self.colors["mars"],
            "jupiter": self.colors["jupiter"],
            "saturn": self.colors["saturn"],
            "rahu": self.colors["rahu"],
            "ketu": self.colors["ketu"],
        }.items():
            self.formats[f"{planet}_highlight"] = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': color
            })

    def set_column_widths(self, worksheet, column_types: Dict[int, str]):
        """
        Set column widths in a worksheet based on content type.

        Args:
            worksheet: XlsxWriter worksheet object
            column_types: Dictionary mapping column indices to content types
        """
        for col_idx, col_type in column_types.items():
            width = self.column_widths.get(col_type, self.column_widths["default"])
            worksheet.set_column(col_idx, col_idx, width)

    def format_worksheet(self, worksheet, df: pd.DataFrame, sheet_type: str):
        """
        Apply formatting to a worksheet based on content type.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame containing the data
            sheet_type: Type of sheet ('planets', 'houses', 'yogas', etc.)
        """
        print(f"Formatting worksheet of type: {sheet_type}")

        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Apply specific formatting based on sheet type
        if sheet_type == "planets":
            self._format_planets_sheet(worksheet, df)
        elif sheet_type == "houses":
            self._format_houses_sheet(worksheet, df)
        elif sheet_type == "yogas":
            self._format_yogas_sheet(worksheet, df)
        elif sheet_type == "hora":
            self._format_hora_sheet(worksheet, df)
        elif sheet_type == "transit":
            self._format_transit_sheet(worksheet, df)
        else:
            self._format_default_sheet(worksheet, df)

        # Add autofilter
        if len(df) > 0:
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

        # Freeze the header row
        worksheet.freeze_panes(1, 0)

    def _format_planets_sheet(self, worksheet, df: pd.DataFrame):
        """Format planets sheet with appropriate styles."""
        # Get current time to highlight current row
        current_time = datetime.now().strftime('%H:%M')

        # Set column types for widths
        column_types = {}
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["Planet"]:
                column_types[col_num] = "planet"
            elif col_name in ["Position"]:
                column_types[col_num] = "position"
            elif col_name in ["Sign", "Rashi"]:
                column_types[col_num] = "sign"
            elif col_name in ["House", "HouseNr"]:
                column_types[col_num] = "house"
            elif col_name in ["Nakshatra"]:
                column_types[col_num] = "nakshatra"
            elif col_name in ["RasiLord", "NakshatraLord", "SubLord", "Sub-Sub Lord"]:
                column_types[col_num] = "lord"
            else:
                column_types[col_num] = "default"

        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]

                # Check column for specialized formatting
                if df.columns[col_num] == "Planet":
                    # Highlight planetary bodies with colors
                    planet_name = str(cell_value).lower().split()[0]
                    if planet_name in ["sun", "moon", "mercury", "venus", "mars",
                                       "jupiter", "saturn", "rahu", "ketu"]:
                        worksheet.write(row_num, col_num, cell_value, self.formats[f"{planet_name}_highlight"])
                    else:
                        worksheet.write(row_num, col_num, cell_value, self.formats["cell"])
                else:
                    worksheet.write(row_num, col_num, cell_value, self.formats["cell"])

    def _format_houses_sheet(self, worksheet, df: pd.DataFrame):
        """Format houses sheet with appropriate styles."""
        # Set column types for widths
        column_types = {}
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["House", "Object"]:
                column_types[col_num] = "house"
            elif col_name in ["HouseNr"]:
                column_types[col_num] = "house"
            elif col_name in ["Position"]:
                column_types[col_num] = "position"
            elif col_name in ["Sign", "Rasi"]:
                column_types[col_num] = "sign"
            elif col_name in ["Nakshatra"]:
                column_types[col_num] = "nakshatra"
            elif col_name in ["RasiLord", "NakshatraLord", "SubLord", "Sub-Sub Lord"]:
                column_types[col_num] = "lord"
            elif col_name in ["Size", "DegSize"]:
                column_types[col_num] = "default"
            else:
                column_types[col_num] = "default"

        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]
                worksheet.write(row_num, col_num, cell_value, self.formats["cell"])

    def _format_yogas_sheet(self, worksheet, df: pd.DataFrame):
        """Format yogas sheet with appropriate styles."""
        # Set column types for widths
        column_types = {}
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["Yoga Name"]:
                column_types[col_num] = "yoga"
            elif col_name in ["Type"]:
                column_types[col_num] = "default"
            elif col_name in ["Start Time", "End Time"]:
                column_types[col_num] = "time"
            elif col_name in ["Duration"]:
                column_types[col_num] = "duration"
            elif col_name in ["Planets"]:
                column_types[col_num] = "aspect"
            elif col_name in ["Description"]:
                column_types[col_num] = "description"
            else:
                column_types[col_num] = "default"

        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            # Determine yoga type for coloring
            yoga_type = None
            if 'Type' in df.columns:
                yoga_type = str(df.iloc[row_num - 1]['Type']).lower()

            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]

                # Apply color based on yoga type
                if yoga_type:
                    if yoga_type == 'positive':
                        format_to_use = self.formats["positive_yoga"]
                    elif yoga_type == 'negative':
                        format_to_use = self.formats["negative_yoga"]
                    elif yoga_type == 'neutral':
                        format_to_use = self.formats["neutral_yoga"]
                    else:
                        format_to_use = self.formats["cell"]
                else:
                    format_to_use = self.formats["cell"]

                # For description, always use text format
                if df.columns[col_num] == "Description":
                    worksheet.write(row_num, col_num, cell_value, self.formats["aspect"])
                # For planets column, use aspect format for better readability
                elif df.columns[col_num] == "Planets":
                    worksheet.write(row_num, col_num, cell_value, self.formats["aspect"])
                else:
                    worksheet.write(row_num, col_num, cell_value, format_to_use)

    def _format_hora_sheet(self, worksheet, df: pd.DataFrame):
        """Format hora timing sheet with appropriate styles."""
        # Get current time to highlight current hora
        current_time = datetime.now().strftime('%H:%M')

        # Set column types for widths
        column_types = {}
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["Start Time", "End Time"]:
                column_types[col_num] = "time"
            elif col_name in ["Planet"]:
                column_types[col_num] = "planet"
            elif col_name in ["Day/Night"]:
                column_types[col_num] = "default"
            else:
                column_types[col_num] = "default"

        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            is_current_time = False
            if 'Start Time' in df.columns and 'End Time' in df.columns:
                start_time = df.iloc[row_num - 1]['Start Time']
                end_time = df.iloc[row_num - 1]['End Time']

                if isinstance(start_time, str) and isinstance(end_time, str):
                    if start_time <= current_time <= end_time:
                        is_current_time = True

            # Format time columns
            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]

                # Use highlight format for current hora
                if is_current_time:
                    worksheet.write(row_num, col_num, cell_value, self.formats["highlight"])
                # Use planet highlight for planet column
                elif df.columns[col_num] == "Planet":
                    planet_name = str(cell_value).lower()
                    if planet_name in ["sun", "moon", "mercury", "venus", "mars",
                                       "jupiter", "saturn", "rahu", "ketu"]:
                        worksheet.write(row_num, col_num, cell_value, self.formats[f"{planet_name}_highlight"])
                    else:
                        worksheet.write(row_num, col_num, cell_value, self.formats["cell"])
                # Use time format for time columns
                elif df.columns[col_num] in ["Start Time", "End Time"]:
                    worksheet.write(row_num, col_num, cell_value, self.formats["time"])
                else:
                    worksheet.write(row_num, col_num, cell_value, self.formats["cell"])

    def _format_transit_sheet(self, worksheet, df: pd.DataFrame):
        """Format transit sheet with appropriate styles."""
        # Get current time to highlight current transit
        current_time = datetime.now().strftime('%H:%M')

        # Set column types for widths
        column_types = {}
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["Start Time", "End Time"]:
                column_types[col_num] = "time"
            elif col_name in ["Planet"]:
                column_types[col_num] = "planet"
            elif col_name in ["Position"]:
                column_types[col_num] = "position"
            elif col_name in ["Rashi", "Sign"]:
                column_types[col_num] = "sign"
            elif col_name in ["Nakshatra"]:
                column_types[col_num] = "nakshatra"
            elif col_name in ["Rashi Lord", "Nakshatra Lord", "Sub Lord", "Sub-Sub Lord"]:
                column_types[col_num] = "lord"
            elif col_name in ["Aspects"]:
                column_types[col_num] = "aspect"
            else:
                column_types[col_num] = "default"

        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            is_current_time = False
            if 'Start Time' in df.columns and 'End Time' in df.columns:
                start_time = df.iloc[row_num - 1]['Start Time']
                end_time = df.iloc[row_num - 1]['End Time']

                if isinstance(start_time, str) and isinstance(end_time, str):
                    if start_time <= current_time <= end_time:
                        is_current_time = True

            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]

                # Special handling for aspects column
                if df.columns[col_num] == 'Aspects':
                    # Skip if no aspects or "None"
                    if not cell_value or cell_value == "None":
                        worksheet.write(row_num, col_num, cell_value, self.formats["aspect"])
                        continue

                    # Check if the cell contains yoga information
                    aspect_value = str(cell_value)
                    contains_positive_yoga = False
                    contains_negative_yoga = False

                    # Define which yogas are negative
                    negative_yogas = [
                        "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
                        "Graha Yuddha", "Kemadruma Yoga", "Kala Sarpa Yoga"
                    ]

                    # Check for yogas in the aspect text
                    if "Yoga" in aspect_value:
                        for yoga in aspect_value.split("; "):
                            if "Yoga" in yoga:
                                # Check if it matches any negative yoga
                                is_negative = any(neg_yoga in yoga for neg_yoga in negative_yogas)
                                if is_negative:
                                    contains_negative_yoga = True
                                else:
                                    contains_positive_yoga = True

                    # Apply appropriate formatting based on yoga type
                    if contains_positive_yoga and not contains_negative_yoga:
                        worksheet.write(row_num, col_num, cell_value, self.formats["positive_yoga"])
                    elif contains_negative_yoga and not contains_positive_yoga:
                        worksheet.write(row_num, col_num, cell_value, self.formats["negative_yoga"])
                    elif contains_positive_yoga and contains_negative_yoga:
                        worksheet.write(row_num, col_num, cell_value, self.formats["neutral_yoga"])
                    else:
                        worksheet.write(row_num, col_num, cell_value, self.formats["aspect"])
                else:
                    # For other columns
                    if is_current_time:
                        worksheet.write(row_num, col_num, cell_value, self.formats["highlight"])
                    elif df.columns[col_num] == "Planet":
                        planet_name = str(cell_value).lower().split()[
                            0]  # Get just the planet name, not retrograde status
                        if planet_name in ["sun", "moon", "mercury", "venus", "mars",
                                           "jupiter", "saturn", "rahu", "ketu"]:
                            worksheet.write(row_num, col_num, cell_value, self.formats[f"{planet_name}_highlight"])
                        else:
                            worksheet.write(row_num, col_num, cell_value, self.formats["cell"])
                    elif df.columns[col_num] in ["Start Time", "End Time"]:
                        worksheet.write(row_num, col_num, cell_value, self.formats["time"])
                    else:
                        worksheet.write(row_num, col_num, cell_value, self.formats["cell"])

    def _format_default_sheet(self, worksheet, df: pd.DataFrame):
        """Apply default formatting to a worksheet."""
        # Set default column widths
        column_types = {col_num: "default" for col_num in range(len(df.columns))}
        self.set_column_widths(worksheet, column_types)

        # Format each row
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_num]
                worksheet.write(row_num, col_num, cell_value, self.formats["cell"])