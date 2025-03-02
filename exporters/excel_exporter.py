import pandas as pd
from datetime import datetime
import os


class ExcelExporter:
    """
    Class for exporting data to Excel with formatting.
    Handles creating sheets for planetary positions, transits, and yogas.
    """

    def __init__(self):
        """Initialize the Excel exporter."""
        # Define mapping for yoga nature to color codes
        self.yoga_nature_colors = {
            "Excellent": "#D8E4BC",  # Light green
            "Good": "#E2EFDA",  # Pale green
            "Neutral": "#EDEDED",  # Light gray
            "Bad": "#F8CBAD",  # Light red/orange
            "Worst": "#E6B8B7"  # Darker red
        }

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
        print(f"Exporting data to {filename}...")

        # Create a Pandas Excel writer using XlsxWriter as the engine
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        workbook = writer.book

        # Create common formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # Standard cell format
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Create format for each yoga nature
        yoga_formats = {}
        for nature, color in self.yoga_nature_colors.items():
            yoga_formats[nature] = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': color
            })

        # Initialize current time for highlighting in time-based sheets
        current_time = datetime.now().strftime('%H:%M')

        # Iterate through each data frame and save to a different sheet
        for sheet_name, df in data_dict.items():
            print(f"Processing sheet: {sheet_name}")

            # Special handling for Yogas sheet
            if sheet_name == "Yogas":
                self._create_yoga_sheet(df, writer, workbook, header_format, yoga_formats)
            elif sheet_name == "Planet Positions":
                self._create_planet_positions_sheet(df, writer, workbook, header_format, cell_format, current_time)
            elif sheet_name == "Hora Timing":
                self._create_hora_timing_sheet(df, writer, workbook, header_format, cell_format, current_time)
            else:
                # General transit sheets
                self._create_transit_sheet(sheet_name, df, writer, workbook, header_format, cell_format, current_time)

        # Close the Pandas Excel writer and output the Excel file
        writer.close()
        print(f"Excel file created: {filename}")

        return filename

    def _create_yoga_sheet(self, df, writer, workbook, header_format, yoga_formats):
        """
        Create and format the Yogas sheet.

        Parameters:
        -----------
        df : pd.DataFrame
            The yoga data
        writer : pd.ExcelWriter
            Excel writer object
        workbook : xlsxwriter.Workbook
            XlsxWriter workbook object
        header_format : xlsxwriter.Format
            Format for header cells
        yoga_formats : dict
            Dictionary of formats for each yoga nature
        """
        # Sort the dataframe by start date in ascending order
        if 'Start Date' in df.columns:
            # Convert date strings to datetime objects for proper sorting
            df['DateObj'] = pd.to_datetime(df['Start Date'], format='%d/%m/%y')
            df['TimeObj'] = pd.to_datetime(df['Start Time'], format='%I:%M %p').dt.time
            # Sort by date and then by time
            df = df.sort_values(['DateObj', 'TimeObj'])
            df = df.drop(['DateObj', 'TimeObj'], axis=1)
        elif 'Date' in df.columns:
            # Backward compatibility with old format
            df['DateObj'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
            df = df.sort_values('DateObj')
            df = df.drop('DateObj', axis=1)

        # Write the dataframe to the sheet
        df.to_excel(writer, sheet_name="Yogas", index=False)
        worksheet = writer.sheets["Yogas"]

        # Format the headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Create text-aligned format for description column
        description_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        # Special formats for headers that need text wrapping
        planets_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        # Standard cell format (without background color)
        standard_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Today's date format (yellow background)
        today_date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFF00'  # Yellow
        })

        # Get today's date in the same format as in the sheet
        today_str = datetime.now().strftime("%d/%m/%y")

        # Format the data rows
        for row_num in range(1, len(df) + 1):
            # Get the nature of this yoga for color formatting
            nature = df.iloc[row_num - 1].get('Nature', 'Neutral')
            nature_format = yoga_formats.get(nature, yoga_formats['Neutral'])
            
            # Check if this row's date is today for both start and end dates
            start_date = df.iloc[row_num - 1].get('Start Date', '')
            end_date = df.iloc[row_num - 1].get('End Date', '')
            date = df.iloc[row_num - 1].get('Date', '')  # For backward compatibility
            
            start_is_today = (start_date == today_str)
            end_is_today = (end_date == today_str)
            is_today = (date == today_str)  # For backward compatibility
            
            # Apply format to each cell
            for col_num, col_name in enumerate(df.columns):
                value = df.iloc[row_num - 1, col_num]

                # Use description format for Description column
                if col_name == 'Description':
                    worksheet.write(row_num, col_num, value, description_format)
                # Use planets format for Planets column
                elif col_name == 'Planets':
                    worksheet.write(row_num, col_num, value, planets_format)
                # Use nature format only for Nature column
                elif col_name == 'Nature':
                    worksheet.write(row_num, col_num, value, nature_format)
                # Use today's date format for Date column if it's today
                elif col_name == 'Start Date' and start_is_today:
                    worksheet.write(row_num, col_num, value, today_date_format)
                elif col_name == 'End Date' and end_is_today:
                    worksheet.write(row_num, col_num, value, today_date_format)
                elif col_name == 'Date' and is_today:  # For backward compatibility
                    worksheet.write(row_num, col_num, value, today_date_format)
                # Use standard format for other columns
                else:
                    worksheet.write(row_num, col_num, value, standard_format)

        # Set column widths - updated for new format with start/end dates
        if 'Start Date' in df.columns:
            worksheet.set_column('A:A', 12)  # Start Date
            worksheet.set_column('B:B', 10)  # Start Time
            worksheet.set_column('C:C', 12)  # End Date
            worksheet.set_column('D:D', 10)  # End Time
            worksheet.set_column('E:E', 25)  # Yoga Name
            worksheet.set_column('F:F', 40)  # Planets
            worksheet.set_column('G:G', 12)  # Nature
            worksheet.set_column('H:H', 60)  # Description
        else:
            # Backward compatibility with old format
            worksheet.set_column('A:A', 12)  # Date
            worksheet.set_column('B:B', 10)  # Time
            worksheet.set_column('C:C', 20)  # Yoga Name
            worksheet.set_column('D:D', 40)  # Planets
            worksheet.set_column('E:E', 12)  # Nature
            worksheet.set_column('F:F', 60)  # Description

        # Add filter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _create_planet_positions_sheet(self, df, writer, workbook, header_format, cell_format, current_time):
        """
        Create and format the Planet Positions sheet.

        Parameters:
        -----------
        df : pd.DataFrame
            The planet positions data
        writer : pd.ExcelWriter
            Excel writer object
        workbook : xlsxwriter.Workbook
            XlsxWriter workbook object
        header_format : xlsxwriter.Format
            Format for header cells
        cell_format : xlsxwriter.Format
            Format for standard cells
        current_time : str
            Current time string for highlighting
        """
        # Write the dataframe to the sheet
        df.to_excel(writer, sheet_name="Planet Positions", index=False)
        worksheet = writer.sheets["Planet Positions"]

        # Format the headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Format the data rows
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], cell_format)

        # Set column widths
        worksheet.set_column('A:A', 12)  # Planet column
        worksheet.set_column('B:B', 18)  # Position column
        worksheet.set_column('C:C', 10)  # Sign column
        worksheet.set_column('D:D', 8)  # House column
        worksheet.set_column('E:E', 14)  # Nakshatra column
        worksheet.set_column('F:F', 25)  # KP Pointer column
        worksheet.set_column('G:G', 10)  # Retrograde column

        # Add filter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _create_hora_timing_sheet(self, df, writer, workbook, header_format, cell_format, current_time):
        """
        Create and format the Hora Timing sheet.

        Parameters:
        -----------
        df : pd.DataFrame
            The hora timing data
        writer : pd.ExcelWriter
            Excel writer object
        workbook : xlsxwriter.Workbook
            XlsxWriter workbook object
        header_format : xlsxwriter.Format
            Format for header cells
        cell_format : xlsxwriter.Format
            Format for standard cells
        current_time : str
            Current time string for highlighting
        """
        # Write the dataframe to the sheet
        df.to_excel(writer, sheet_name="Hora Timing", index=False)
        worksheet = writer.sheets["Hora Timing"]

        # Format for current time highlighting
        highlight_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFF00'  # Yellow
        })

        # Format the headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Format the data rows with current time highlighting
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            start_time = df.iloc[row_num - 1]['Start Time']
            end_time = df.iloc[row_num - 1]['End Time']

            row_format = cell_format
            if start_time <= current_time <= end_time:
                row_format = highlight_format

            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)

        # Set column widths
        worksheet.set_column('A:B', 12)  # Time columns
        worksheet.set_column('C:C', 10)  # Planet column
        worksheet.set_column('D:D', 12)  # Day/Night column

        # Add filter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def _create_transit_sheet(self, sheet_name, df, writer, workbook, header_format, cell_format, current_time):
        """
        Create and format a transit sheet (Moon, Sun, etc.).

        Parameters:
        -----------
        sheet_name : str
            Name of the sheet
        df : pd.DataFrame
            The transit data
        writer : pd.ExcelWriter
            Excel writer object
        workbook : xlsxwriter.Workbook
            XlsxWriter workbook object
        header_format : xlsxwriter.Format
            Format for header cells
        cell_format : xlsxwriter.Format
            Format for standard cells
        current_time : str
            Current time string for highlighting
        """
        # Write the dataframe to the sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]

        # Format for current time highlighting
        highlight_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFF00'  # Yellow
        })

        # Format for aspects column
        aspects_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        # Format for positive yoga
        positive_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True,
            'bg_color': '#E2EFDA'  # Light green
        })

        # Format for negative yoga
        negative_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True,
            'bg_color': '#FFCCCC'  # Light red
        })

        # Format for mixed yogas
        mixed_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True,
            'bg_color': '#FFF2CC'  # Light yellow
        })

        # Format the headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Define which yogas are negative
        negative_yogas = [
            "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
            "Graha Yuddha", "Kemadruma Yoga", "Kala Sarpa Yoga"
        ]

        # Format the data rows with current time highlighting and aspect coloring
        for row_num in range(1, len(df) + 1):
            # Check if this row corresponds to the current time
            start_time = df.iloc[row_num - 1]['Start Time']
            end_time = df.iloc[row_num - 1]['End Time']

            row_format = cell_format
            if start_time <= current_time <= end_time:
                row_format = highlight_format

            # Apply format to each cell
            for col_num, col_name in enumerate(df.columns):
                value = df.iloc[row_num - 1, col_num]

                # Special handling for Aspects column
                if col_name == 'Aspects' and isinstance(value, str) and value not in ['', 'None']:
                    # Check if the cell contains yoga information
                    contains_positive_yoga = False
                    contains_negative_yoga = False

                    # Check each yoga in the aspects cell
                    if "Yoga" in value:
                        for yoga in value.split("; "):
                            if "Yoga" in yoga:
                                # Check if it matches any negative yoga
                                is_negative = any(neg_yoga in yoga for neg_yoga in negative_yogas)
                                if is_negative:
                                    contains_negative_yoga = True
                                else:
                                    contains_positive_yoga = True

                    # Apply formatting based on yoga type
                    if contains_positive_yoga and not contains_negative_yoga:
                        worksheet.write(row_num, col_num, value, positive_format)
                    elif contains_negative_yoga and not contains_positive_yoga:
                        worksheet.write(row_num, col_num, value, negative_format)
                    elif contains_positive_yoga and contains_negative_yoga:
                        worksheet.write(row_num, col_num, value, mixed_format)
                    else:
                        worksheet.write(row_num, col_num, value, aspects_format)
                else:
                    worksheet.write(row_num, col_num, value, row_format)

        # Set column widths
        worksheet.set_column('A:B', 10)  # Time columns
        worksheet.set_column('C:C', 12)  # Position column
        worksheet.set_column('D:D', 12)  # Rashi column
        worksheet.set_column('E:E', 15)  # Nakshatra column
        worksheet.set_column('F:I', 15)  # Lord columns
        worksheet.set_column('J:J', 40)  # Aspects column (if present)

        # Add filter and freeze panes
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        worksheet.freeze_panes(1, 0)

    def format_yoga_planets(self, planets_list):
        """
        Format a list of planets information for display in the Yoga sheet.

        Parameters:
        -----------
        planets_list : list
            List of planet information strings

        Returns:
        --------
        str
            Formatted planets information string
        """
        if not planets_list:
            return ""

        return "\n".join(planets_list)