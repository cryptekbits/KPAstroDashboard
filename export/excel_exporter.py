"""
Excel export functionality for KP Astrology data.
Handles formatting and exporting data to Excel files.
"""
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from datetime import datetime
import os


class ExcelExporter:
    """Export KP Astrology data to Excel."""

    def __init__(self):
        """Initialize the Excel exporter."""
        # Define reusable formats dictionary to be created when the workbook is initialized
        self.formats = {}

    def export_to_excel(self, data_dict: Dict[str, pd.DataFrame], filename: str) -> str:
        """
        Export multiple DataFrames to Excel sheets.

        Args:
            data_dict: Dictionary mapping sheet names to DataFrames
            filename: Name of Excel file to create

        Returns:
            Path to created Excel file
        """
        try:
            print(f"Exporting data to Excel file: {filename}")

            # Create a Pandas Excel writer using XlsxWriter as the engine
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book

            # Create reusable formats
            self._create_formats(workbook)

            # Process each DataFrame
            for sheet_name, df in data_dict.items():
                print(f"Processing sheet: {sheet_name}")

                # Write the DataFrame to the sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Get the worksheet
                worksheet = writer.sheets[sheet_name]

                # Apply appropriate formatting based on sheet type
                if "Planet" in sheet_name and "Position" in sheet_name:
                    self._format_planet_positions_sheet(worksheet, df)
                elif "Hora" in sheet_name:
                    self._format_hora_sheet(worksheet, df)
                elif any(planet in sheet_name for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars",
                                                             "Jupiter", "Saturn", "Rahu", "Ketu",
                                                             "Uranus", "Neptune", "Ascendant"]):
                    self._format_planet_transit_sheet(worksheet, df)
                elif "Yoga" in sheet_name:
                    self._format_yoga_sheet(worksheet, df)
                else:
                    # Default formatting
                    self._format_default_sheet(worksheet, df)

            # Close the Excel writer
            writer.close()
            print(f"Export complete: {filename}")

            return filename

        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            raise

    def _create_formats(self, workbook) -> None:
        """
        Create reusable cell formats.

        Args:
            workbook: XlsxWriter workbook object
        """
        # Header format
        self.formats["header"] = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # Standard cell format
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
            'fg_color': '#E2EFDA'  # Light green
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
            'bg_color': '#FFFF00'  # Yellow
        })

        # Positive yoga format
        self.formats["positive_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#E2EFDA'  # Light green
        })

        # Negative yoga format
        self.formats["negative_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#FFCCCC'  # Light red
        })

        # Neutral yoga format
        self.formats["neutral_yoga"] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#FFF2CC'  # Light yellow
        })

    def _format_planet_positions_sheet(self, worksheet, df: pd.DataFrame) -> None:
        """
        Format the planet positions sheet.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame with planet positions data
        """
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Get current time to highlight current row
        current_time = datetime.now().strftime('%H:%M')

        # Format data rows
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num],
                                self.formats["cell"])

        # Set column widths
        worksheet.set_column('A:A', 12)  # Planet column
        worksheet.set_column('B:B', 18)  # Position column
        worksheet.set_column('C:C', 10)  # Sign column
        worksheet.set_column('D:D', 8)  # House column
        worksheet.set_column('E:E', 14)  # Nakshatra column
        worksheet.set_column('F:F', 25)  # KP Pointer column

        # Add autofilter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _format_hora_sheet(self, worksheet, df: pd.DataFrame) -> None:
        """
        Format the hora timing sheet.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame with hora data
        """
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Get current time to highlight current row
        current_time = datetime.now().strftime('%H:%M')

        # Format data rows
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            is_current_time = False
            if 'Start Time' in df.columns and 'End Time' in df.columns:
                start_time = df.iloc[row_num - 1]['Start Time']
                end_time = df.iloc[row_num - 1]['End Time']
                if start_time <= current_time <= end_time:
                    is_current_time = True

            # Format time columns
            for col_num in range(len(df.columns)):
                format_to_use = self.formats["highlight"] if is_current_time else self.formats["cell"]
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], format_to_use)

        # Set column widths
        worksheet.set_column('A:B', 12)  # Time columns
        worksheet.set_column('C:C', 10)  # Planet column
        worksheet.set_column('D:D', 15)  # Day/Night column

        # Add autofilter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _format_planet_transit_sheet(self, worksheet, df: pd.DataFrame) -> None:
        """
        Format a planet transit sheet.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame with transit data
        """
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Get current time to highlight current row
        current_time = datetime.now().strftime('%H:%M')

        # Format data rows
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            is_current_time = False
            if 'Start Time' in df.columns and 'End Time' in df.columns:
                start_time = df.iloc[row_num - 1]['Start Time']
                end_time = df.iloc[row_num - 1]['End Time']
                if start_time <= current_time <= end_time:
                    is_current_time = True

            # Apply format to all cells in the row
            for col_idx in range(len(df.columns)):
                # Use special format for the aspects column
                if df.columns[col_idx] == 'Aspects':
                    aspect_value = df.iloc[row_num - 1, col_idx]

                    # Skip if no aspects or "None"
                    if not aspect_value or aspect_value == "None":
                        worksheet.write(row_num, col_idx, aspect_value, self.formats["aspect"])
                        continue

                    # Check if the cell contains yoga information
                    contains_positive_yoga = False
                    contains_negative_yoga = False

                    # Define which yogas are negative
                    negative_yogas = [
                        "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
                        "Graha Yuddha", "Kemadruma Yoga", "Kala Sarpa Yoga"
                    ]

                    # Check each yoga in the aspects cell
                    if isinstance(aspect_value, str) and "Yoga" in aspect_value:
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
                        worksheet.write(row_num, col_idx, aspect_value, self.formats["positive_yoga"])
                    elif contains_negative_yoga and not contains_positive_yoga:
                        worksheet.write(row_num, col_idx, aspect_value, self.formats["negative_yoga"])
                    elif contains_positive_yoga and contains_negative_yoga:
                        worksheet.write(row_num, col_idx, aspect_value, self.formats["neutral_yoga"])
                    else:
                        worksheet.write(row_num, col_idx, aspect_value, self.formats["aspect"])
                else:
                    # For non-aspect columns
                    row_format = self.formats["highlight"] if is_current_time else self.formats["cell"]
                    worksheet.write(row_num, col_idx, df.iloc[row_num - 1, col_idx], row_format)

        # Set column widths
        worksheet.set_column('A:B', 10)  # Time columns
        worksheet.set_column('C:C', 12)  # Position column
        worksheet.set_column('D:D', 12)  # Rashi column
        worksheet.set_column('E:E', 15)  # Nakshatra column
        worksheet.set_column('F:I', 15)  # Lord columns
        worksheet.set_column('J:J', 40)  # Aspects column (if present)

        # Add autofilter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _format_yoga_sheet(self, worksheet, df: pd.DataFrame) -> None:
        """
        Format a yoga results sheet.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame with yoga data
        """
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Format data rows
        for row_num in range(1, len(df) + 1):
            # Check yoga type for coloring
            yoga_type = None
            if 'Type' in df.columns:
                yoga_type = df.iloc[row_num - 1]['Type']

            for col_idx in range(len(df.columns)):
                cell_value = df.iloc[row_num - 1, col_idx]

                # Apply color based on yoga type
                if yoga_type:
                    if yoga_type.lower() == 'positive':
                        format_to_use = self.formats["positive_yoga"]
                    elif yoga_type.lower() == 'negative':
                        format_to_use = self.formats["negative_yoga"]
                    elif yoga_type.lower() == 'neutral':
                        format_to_use = self.formats["neutral_yoga"]
                    else:
                        format_to_use = self.formats["cell"]
                else:
                    format_to_use = self.formats["cell"]

                worksheet.write(row_num, col_idx, cell_value, format_to_use)

        # Set column widths
        worksheet.set_column('A:A', 20)  # Yoga Name
        worksheet.set_column('B:C', 15)  # Start/End Time
        worksheet.set_column('D:D', 10)  # Duration
        worksheet.set_column('E:E', 40)  # Planets
        worksheet.set_column('F:F', 10)  # Type
        worksheet.set_column('G:G', 10)  # Strength
        worksheet.set_column('H:H', 50)  # Description

        # Add autofilter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _format_default_sheet(self, worksheet, df: pd.DataFrame) -> None:
        """
        Apply default formatting to a worksheet.

        Args:
            worksheet: XlsxWriter worksheet object
            df: DataFrame with data
        """
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, self.formats["header"])

        # Format data rows
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num],
                                self.formats["cell"])

        # Set default column widths
        for col_num in range(len(df.columns)):
            worksheet.set_column(col_num, col_num, 15)

        # Add autofilter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def is_positive_yoga(self, yoga_name: str) -> bool:
        """
        Determine if a yoga is considered positive.

        Args:
            yoga_name: Name of the yoga

        Returns:
            True if positive, False otherwise
        """
        negative_yogas = [
            "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
            "Graha Yuddha", "Kemadruma Yoga", "Kala Sarpa Yoga",
            "Daridra Yoga", "Shakat Yoga"
        ]

        return yoga_name not in negative_yogas