import pandas as pd
import numpy as np
from datetime import datetime
import os


class ExcelExporter:
    def __init__(self):
        """Initialize the Excel exporter."""
        pass

    def export_to_excel(self, data_dict, filename):
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

                # Format the data rows
                for row_num in range(1, len(df) + 1):
                    for col_num in range(len(df.columns)):
                        worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], planet_format)

                # Set column widths
                worksheet.set_column('A:A', 12)  # Planet column
                worksheet.set_column('B:B', 12)  # Position column
                worksheet.set_column('C:E', 10)  # Other columns
                worksheet.set_column('F:I', 15)  # Lord columns
                worksheet.set_column('J:J', 20)  # KP Pointer column
                worksheet.set_column('K:K', 40)  # Aspects column

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
                rashi_format = workbook.add_format({
                    'border': 1,
                    'pattern': 1,
                    'fg_color': '#FFD966',  # Light gold
                    'align': 'center'
                })

                nakshatra_format = workbook.add_format({
                    'border': 1,
                    'pattern': 1,
                    'fg_color': '#A9D08E',  # Light green
                    'align': 'center'
                })

                lord_format = workbook.add_format({
                    'border': 1,
                    'pattern': 1,
                    'fg_color': '#9BC2E6',  # Light blue
                    'align': 'center'
                })

                sub_lord_format = workbook.add_format({
                    'border': 1,
                    'pattern': 1,
                    'fg_color': '#F4B084',  # Light orange
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

                # Format the data rows with different colors for different parameters
                for row_num in range(1, len(df) + 1):
                    col_idx = 0

                    # Time columns (Start Time, End Time)
                    worksheet.write(row_num, col_idx, df.iloc[row_num - 1, col_idx], time_format)
                    worksheet.write(row_num, col_idx + 1, df.iloc[row_num - 1, col_idx + 1], time_format)

                    # Position column
                    worksheet.write(row_num, col_idx + 2, df.iloc[row_num - 1, col_idx + 2], position_format)

                    # Rashi column
                    worksheet.write(row_num, col_idx + 3, df.iloc[row_num - 1, col_idx + 3], rashi_format)

                    # Nakshatra column
                    worksheet.write(row_num, col_idx + 4, df.iloc[row_num - 1, col_idx + 4], nakshatra_format)

                    # Lord columns (Rashi Lord, Nakshatra Lord)
                    worksheet.write(row_num, col_idx + 5, df.iloc[row_num - 1, col_idx + 5], lord_format)
                    worksheet.write(row_num, col_idx + 6, df.iloc[row_num - 1, col_idx + 6], lord_format)

                    # Sub Lord and Sub-Sub Lord columns
                    worksheet.write(row_num, col_idx + 7, df.iloc[row_num - 1, col_idx + 7], sub_lord_format)
                    if col_idx + 8 < len(df.columns):
                        worksheet.write(row_num, col_idx + 8, df.iloc[row_num - 1, col_idx + 8], sub_lord_format)

                    # Aspects column (if present)
                    if 'Aspects' in df.columns:
                        aspect_col = df.columns.get_loc('Aspects')
                        worksheet.write(row_num, aspect_col, df.iloc[row_num - 1, aspect_col], aspects_format)

                # Set column widths
                worksheet.set_column('A:B', 10)  # Time columns
                worksheet.set_column('C:C', 12)  # Position column
                worksheet.set_column('D:D', 12)  # Rashi column
                worksheet.set_column('E:E', 15)  # Nakshatra column
                worksheet.set_column('F:I', 15)  # Lord columns
                worksheet.set_column('J:J', 40)  # Aspects column (if present)

            # Add autofilter
            if len(df) > 0:
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

            # Freeze the header row
            worksheet.freeze_panes(1, 0)

        # Close the Pandas Excel writer and output the Excel file
        writer.close()

        print(f"Excel file created: {filename}")

        return filename