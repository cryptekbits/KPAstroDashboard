import pandas as pd
import numpy as np
from datetime import datetime
import os


class ExcelExporter:
    def __init__(self):
        """Initialize the Excel exporter."""
        pass

    @staticmethod
    def export_to_excel(data_dict, filename):
        """
        Export the provided data to an Excel file with multiple sheets.

        Parameters:
        -----------
        data_dict : dict
            Dictionary where keys are sheet names and values are pandas DataFrames
        filename : str
            Name of the Excel file to create
        """
        # Create a Pandas Excel writer using XlsxWriter as the engine
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        # Iterate through each data frame and save to a different sheet
        for sheet_name, df in data_dict.items():
            # Write the dataframe to the sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Create a format for headers
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # Create a format for the planet positions table
            planet_format = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })

            # Apply conditional formatting for certain sheets
            if sheet_name == "Planet Positions":
                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Get current time to highlight current row
                current_time = datetime.now().strftime('%H:%M')

                # Add conditional formatting to highlight the current time
                highlight_format = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#FFFF00'  # Yellow highlighting
                })

                # Format the data rows
                for row_num in range(1, len(df) + 1):
                    for col_num in range(len(df.columns)):
                        worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], planet_format)

                # Set column widths
                worksheet.set_column('A:A', 12)  # Planet column
                worksheet.set_column('B:B', 18)  # Position column
                worksheet.set_column('C:C', 10)  # Sign column
                worksheet.set_column('D:D', 8)  # House column
                worksheet.set_column('E:E', 14)  # Nakshatra column
                worksheet.set_column('F:F', 25)  # KP Pointer column
                worksheet.set_column('G:G', 40)  # Aspects column

            elif sheet_name == "Hora Timing":
                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Format the data rows
                for row_num in range(1, len(df) + 1):
                    for col_num in range(len(df.columns)):
                        worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], planet_format)

                # Set column widths
                worksheet.set_column('A:B', 12)  # Time columns
                worksheet.set_column('C:C', 10)  # Planet column

            else:
                # This is a planet transition sheet

                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Define color formats for different parameters
                # Using standard format without background coloring as requested
                std_format = workbook.add_format({
                    'border': 1,
                    'align': 'center'
                })

                position_format = workbook.add_format({
                    'border': 1,
                    'align': 'center'
                })

                time_format = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'fg_color': '#E2EFDA'  # Light green
                })

                aspects_format = workbook.add_format({
                    'border': 1,
                    'text_wrap': True,
                    'align': 'left',
                    'valign': 'top'
                })

                # Get current time to highlight current row
                current_time = datetime.now().strftime('%H:%M')

                # Add conditional formatting to highlight the current time
                highlight_format = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'bg_color': '#FFFF00'  # Yellow highlighting
                })

                # Format the data rows without background colors
                for row_num in range(1, len(df) + 1):
                    # Check if this row corresponds to the current time
                    is_current_time = False
                    if 'Start Time' in df.columns and 'End Time' in df.columns:
                        start_time = df.iloc[row_num - 1]['Start Time']
                        end_time = df.iloc[row_num - 1]['End Time']
                        if start_time <= current_time <= end_time:
                            is_current_time = True

                    # Use chosen format based on whether it's current time
                    row_format = highlight_format if is_current_time else std_format

                    # Apply format to all cells in the row
                    for col_idx in range(len(df.columns)):
                        # Use aspects format specifically for the aspects column
                        if df.columns[col_idx] == 'Aspects':
                            aspect_value = df.iloc[row_num - 1, col_idx]

                            # Skip if no aspects or "None"
                            if not aspect_value or aspect_value == "None":
                                worksheet.write(row_num, col_idx, aspect_value, aspects_format)
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

                            # Apply formatting based on yoga type
                            if contains_positive_yoga and not contains_negative_yoga:
                                # Positive yoga - green background
                                positive_format = workbook.add_format({
                                    'border': 1,
                                    'align': 'left',
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'bg_color': '#E2EFDA'  # Light green
                                })
                                worksheet.write(row_num, col_idx, aspect_value, positive_format)

                            elif contains_negative_yoga and not contains_positive_yoga:
                                # Negative yoga - red background
                                negative_format = workbook.add_format({
                                    'border': 1,
                                    'align': 'left',
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'bg_color': '#FFCCCC'  # Light red
                                })
                                worksheet.write(row_num, col_idx, aspect_value, negative_format)

                            elif contains_positive_yoga and contains_negative_yoga:
                                # Mixed yogas - yellow background
                                mixed_format = workbook.add_format({
                                    'border': 1,
                                    'align': 'left',
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'bg_color': '#FFF2CC'  # Light yellow
                                })
                                worksheet.write(row_num, col_idx, aspect_value, mixed_format)

                            else:
                                # No yogas - use the default aspect format
                                worksheet.write(row_num, col_idx, aspect_value, aspects_format)
                        else:
                            worksheet.write(row_num, col_idx, df.iloc[row_num - 1, col_idx], row_format)

                # Set column widths
                worksheet.set_column('A:B', 10)  # Time columns
                worksheet.set_column('C:C', 12)  # Position column
                worksheet.set_column('D:D', 12)  # Rashi column
                worksheet.set_column('E:E', 15)  # Nakshatra column
                worksheet.set_column('F:I', 15)  # Lord columns
                worksheet.set_column('J:J', 40)  # Aspects column (if present)

            # Add auto filter
            if len(df) > 0:
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

            # Freeze the header row
            worksheet.freeze_panes(1, 0)

        # Close the Pandas Excel writer and output the Excel file
        writer.close()

        print(f"Excel file created: {filename}")

        return filename

    # In the ExcelExporter class, add a method to determine if a yoga is positive or negative
    @staticmethod
    def is_positive_yoga(yoga_name):
        """Determine if a yoga is considered positive"""
        negative_yogas = [
            "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
            "Graha Yuddha", "Kemadruma Yoga", "Kala Sarpa Yoga"
        ]

        # If the yoga is in the negative list, it's not positive
        return yoga_name not in negative_yogas
