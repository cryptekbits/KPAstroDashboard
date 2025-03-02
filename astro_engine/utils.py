"""
Utility functions for astrological calculations.

This module provides various utility functions for working with
astrological data, including conversions between different time
and angle formats.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta


def clean_select_objects_split_str(input_str):
    """
    Rename and clean certain chart objects like North Node, South Node and Fortuna.
    
    Args:
        input_str (str): The input string to clean.
        
    Returns:
        list: A list of cleaned and split string components.
    """
    cleaned_str = (input_str.strip('<').strip('>')
                          .replace("North Node", "Rahu")
                          .replace("South Node", "Ketu")
                          .replace("Pars Fortuna", "Fortuna"))
    return cleaned_str.split()


def utc_offset_str_to_float(utc_offset: str) -> float:
    """
    Convert a UTC offset string (e.g., '+5:30') to a float value.
    
    Args:
        utc_offset (str): The UTC offset string.
        
    Returns:
        float: The UTC offset as a float value.
    """
    hours, minutes = map(int, utc_offset.split(':'))
    return hours + minutes / 60.0 if utc_offset.startswith('+') else -1 * (abs(hours) + minutes / 60.0)


def pretty_data_table(named_tuple_data: list):
    """
    Convert a list of NamedTuple Collections to a PrettyTable.
    
    Args:
        named_tuple_data (list): A list of named tuples.
        
    Returns:
        PrettyTable: A formatted table of the data.
    """
    from prettytable import PrettyTable
    # Create a PrettyTable instance
    table = PrettyTable()

    # Add field names (column headers)
    table.field_names = named_tuple_data[0]._fields 

    # Add rows
    for data in named_tuple_data:
        table.add_row(data)

    return table


def dms_to_decdeg(dms_str: str) -> float:
    """
    Convert a string input in Degrees:Mins:Secs to Decimal Degrees.
    
    Args:
        dms_str (str): A string in the format "degrees:minutes:seconds".
        
    Returns:
        float: The decimal degree equivalent.
    """
    dms = dms_str.split(':')
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    return round(degrees + (minutes/60) + (seconds/3600), 4)


def dms_to_mins(dms_str: str) -> float:
    """
    Convert a string input in Degrees:Mins:Secs to total minutes.
    
    Args:
        dms_str (str): A string in the format "degrees:minutes:seconds".
        
    Returns:
        float: The total minutes.
    """
    dms = dms_str.split(':')
    degrees = int(dms[0])
    minutes = int(dms[1])
    seconds = int(dms[2])
    total_minutes = degrees * 60 + minutes + seconds / 60
    return round(total_minutes, 2)


def dms_difference(dms1_str: str, dms2_str: str) -> str:
    """
    Compute the difference between two degree:mins:secs string objects
    and return the difference as a degree:mins:secs string.
    
    Args:
        dms1_str (str): First DMS string.
        dms2_str (str): Second DMS string.
        
    Returns:
        str: The difference as a DMS string.
    """
    def dms_to_seconds(dms_str):
        dms = dms_str.split(':')
        degrees = int(dms[0])
        minutes = int(dms[1])
        seconds = int(dms[2])
        total_seconds = degrees * 3600 + minutes * 60 + seconds
        return total_seconds

    def seconds_to_dms(seconds):
        degrees = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{int(degrees)}:{int(minutes)}:{int(seconds)}"

    dms1_seconds = dms_to_seconds(dms1_str)
    dms2_seconds = dms_to_seconds(dms2_str)

    diff_seconds = abs(dms1_seconds - dms2_seconds)

    return seconds_to_dms(diff_seconds)


def convert_years_ymdhm(years: float) -> tuple:
    """
    Convert decimal years into years, months, days, hours, and minutes.
    
    Args:
        years (float): The number of years as a decimal.
        
    Returns:
        tuple: A tuple of (years, months, days, hours, minutes).
    """
    # Constants
    months_per_year = 12
    days_per_month = 30  # Approximation
    hours_per_day = 24
    minutes_per_hour = 60

    # Compute the breakdown
    whole_years = int(years)
    months = (years - whole_years) * months_per_year
    whole_months = int(months)
    days = (months - whole_months) * days_per_month
    whole_days = int(days)
    hours = (days - whole_days) * hours_per_day
    whole_hours = int(hours)
    minutes = (hours - whole_hours) * minutes_per_hour
    whole_minutes = int(minutes)

    return whole_years, whole_months, whole_days, whole_hours, whole_minutes


def compute_new_date(start_date: tuple, diff_value: float, direction: str) -> datetime:
    """
    Compute a new date and time given an initial date and time and a time difference.
    
    Args:
        start_date (tuple): A tuple of (year, month, day, hour, minute).
        diff_value (float): The time difference in years.
        direction (str): Either 'backward' or 'forward'.
        
    Returns:
        datetime: The new date and time.
        
    Raises:
        ValueError: If direction is not 'backward' or 'forward'.
    """
    # Unpack start_date and diff_params
    year, month, day, hour, minute = start_date
    years, months, days, hours, minutes = convert_years_ymdhm(diff_value)

    # Create initial datetime object
    initial_date = datetime(year, month, day, hour, minute)

    # Compute relativedelta object
    time_difference = relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes)

    # Compute new date
    if direction == 'backward':
        new_date = initial_date - time_difference
    elif direction == 'forward':
        new_date = initial_date + time_difference
    else:
        raise ValueError("direction must be either 'backward' or 'forward'")

    return new_date 