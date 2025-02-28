"""
Utility functions for KP Astrology calculations.
"""
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import math


def dms_to_decdeg(dms_str: str) -> float:
    """
    Convert Degrees:Minutes:Seconds string to decimal degrees.

    Args:
        dms_str: String in format "DD:MM:SS"

    Returns:
        Decimal degrees as float
    """
    try:
        dms = dms_str.split(':')
        degrees = float(dms[0])
        minutes = float(dms[1]) if len(dms) > 1 else 0
        seconds = float(dms[2]) if len(dms) > 2 else 0

        # Handle negative values consistently
        sign = -1 if degrees < 0 else 1
        return sign * (abs(degrees) + (minutes / 60) + (seconds / 3600))
    except Exception as e:
        print(f"Error converting DMS '{dms_str}' to decimal degrees: {str(e)}")
        return 0.0


def decdeg_to_dms(decimal_degrees: float, precision: int = 0) -> str:
    """
    Convert decimal degrees to Degrees:Minutes:Seconds string.

    Args:
        decimal_degrees: Decimal degrees as float
        precision: Number of decimal places for seconds

    Returns:
        String in format "DD:MM:SS"
    """
    try:
        is_negative = decimal_degrees < 0
        decimal_degrees = abs(decimal_degrees)

        degrees = int(decimal_degrees)
        decimal_minutes = (decimal_degrees - degrees) * 60
        minutes = int(decimal_minutes)
        seconds = (decimal_minutes - minutes) * 60

        if precision == 0:
            seconds = round(seconds)
        else:
            seconds = round(seconds, precision)

        # Handle cases where seconds round up to 60
        if seconds == 60:
            seconds = 0
            minutes += 1
            if minutes == 60:
                minutes = 0
                degrees += 1

        if is_negative and degrees != 0:
            degrees = -degrees

        if precision == 0:
            return f"{degrees}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{degrees}:{minutes:02d}:{seconds:0{precision + 3}.{precision}f}"
    except Exception as e:
        print(f"Error converting {decimal_degrees} to DMS: {str(e)}")
        return "0:00:00"


def dms_to_mins(dms_str: str) -> float:
    """
    Convert Degrees:Minutes:Seconds string to total minutes.

    Args:
        dms_str: String in format "DD:MM:SS"

    Returns:
        Total minutes as float
    """
    try:
        dms = dms_str.split(':')
        degrees = int(dms[0])
        minutes = int(dms[1]) if len(dms) > 1 else 0
        seconds = int(dms[2]) if len(dms) > 2 else 0

        total_minutes = abs(degrees) * 60 + minutes + seconds / 60
        if degrees < 0:
            total_minutes = -total_minutes

        return total_minutes
    except Exception as e:
        print(f"Error converting DMS '{dms_str}' to minutes: {str(e)}")
        return 0.0


def utc_offset_str_to_float(utc_offset: str) -> float:
    """
    Convert UTC offset string to float hours.

    Args:
        utc_offset: String like "+5:30" or "-8:00"

    Returns:
        Offset in decimal hours
    """
    try:
        sign = -1 if utc_offset.startswith('-') else 1
        parts = utc_offset.replace('+', '').replace('-', '').split(':')

        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0

        return sign * (hours + minutes / 60.0)
    except Exception as e:
        print(f"Error converting UTC offset '{utc_offset}' to float: {str(e)}")
        return 0.0


def localize_datetime(dt: datetime, timezone_str: str) -> datetime:
    """
    Ensure a datetime is timezone aware.

    Args:
        dt: Datetime object
        timezone_str: Timezone string (e.g., 'Asia/Kolkata')

    Returns:
        Timezone-aware datetime
    """
    try:
        tz = pytz.timezone(timezone_str)

        # If datetime is naive (no timezone info)
        if dt.tzinfo is None:
            return tz.localize(dt)

        # If datetime already has timezone, convert to requested timezone
        return dt.astimezone(tz)
    except Exception as e:
        print(f"Error localizing datetime to {timezone_str}: {str(e)}")
        # Return the original datetime if there's an error
        return dt


def convert_years_to_dhms(years: float) -> Tuple[int, int, int, int]:
    """
    Convert decimal years to days, hours, minutes, seconds.

    Args:
        years: Number of years as float

    Returns:
        Tuple of (days, hours, minutes, seconds)
    """
    # Approximate conversion
    days = int(years * 365.25)
    remainder = years * 365.25 - days

    hours = int(remainder * 24)
    remainder = remainder * 24 - hours

    minutes = int(remainder * 60)
    remainder = remainder * 60 - minutes

    seconds = int(remainder * 60)

    return days, hours, minutes, seconds


def convert_years_ymdhm(years: float) -> Tuple[int, int, int, int, int]:
    """
    Convert decimal years into years, months, days, hours, and minutes.

    Args:
        years: Number of years as float

    Returns:
        Tuple of (years, months, days, hours, minutes)
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


def compute_new_date(start_date: Union[datetime, Tuple], diff_value: float, direction: str) -> datetime:
    """
    Compute a new date based on a start date and time difference.

    Args:
        start_date: Starting datetime or tuple (year, month, day, hour, minute)
        diff_value: Time difference in years
        direction: 'forward' or 'backward'

    Returns:
        New datetime
    """
    # If start_date is a tuple, convert to datetime
    if isinstance(start_date, tuple):
        year, month, day, hour, minute = start_date
        initial_date = datetime(year, month, day, hour, minute)
    else:
        initial_date = start_date

    # Convert years to components
    years, months, days, hours, minutes = convert_years_ymdhm(diff_value)

    # Compute relativedelta object
    time_difference = relativedelta(
        years=years,
        months=months,
        days=days,
        hours=hours,
        minutes=minutes
    )

    # Compute new date
    if direction == 'backward':
        new_date = initial_date - time_difference
    elif direction == 'forward':
        new_date = initial_date + time_difference
    else:
        raise ValueError("direction must be either 'backward' or 'forward'")

    return new_date


def dms_difference(dms1_str: str, dms2_str: str) -> str:
    """
    Compute the absolute difference between two DMS values.

    Args:
        dms1_str: First DMS string
        dms2_str: Second DMS string

    Returns:
        DMS string representing the difference
    """

    def dms_to_seconds(dms_str):
        dms = dms_str.split(':')
        degrees = int(dms[0])
        minutes = int(dms[1]) if len(dms) > 1 else 0
        seconds = int(dms[2]) if len(dms) > 2 else 0
        total_seconds = abs(degrees) * 3600 + minutes * 60 + seconds
        if degrees < 0:
            total_seconds = -total_seconds
        return total_seconds

    def seconds_to_dms(seconds):
        is_negative = seconds < 0
        seconds = abs(seconds)

        degrees = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if is_negative:
            degrees = -degrees

        return f"{degrees}:{minutes:02d}:{seconds:02d}"

    dms1_seconds = dms_to_seconds(dms1_str)
    dms2_seconds = dms_to_seconds(dms2_str)

    diff_seconds = abs(dms1_seconds - dms2_seconds)

    return seconds_to_dms(diff_seconds)


def get_zodiac_sign(longitude: float) -> str:
    """
    Get the zodiac sign for a given longitude.

    Args:
        longitude: Celestial longitude in decimal degrees

    Returns:
        Zodiac sign name
    """
    # Normalize longitude to [0, 360)
    longitude = longitude % 360

    # Define zodiac signs
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Each sign is 30 degrees
    sign_index = int(longitude / 30)

    return signs[sign_index]


def get_nakshatra(longitude: float) -> Tuple[str, int]:
    """
    Get the nakshatra and pada for a given longitude.

    Args:
        longitude: Celestial longitude in decimal degrees

    Returns:
        Tuple of (nakshatra_name, pada)
    """
    # Normalize longitude to [0, 360)
    longitude = longitude % 360

    # Define nakshatras
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashīrsha",
        "Ardra", "Punarvasu", "Pushya", "Āshleshā", "Maghā",
        "PūrvaPhalgunī", "UttaraPhalgunī", "Hasta", "Chitra", "Svati",
        "Vishakha", "Anuradha", "Jyeshtha", "Mula", "PurvaAshadha",
        "UttaraAshadha", "Shravana", "Dhanishta", "Shatabhisha",
        "PurvaBhādrapadā", "UttaraBhādrapadā", "Revati"
    ]

    # Each nakshatra is 13°20' (13.3333... degrees)
    nakshatra_size = 360 / 27
    nakshatra_index = int(longitude / nakshatra_size)

    # Each pada is 3°20' (3.3333... degrees)
    pada_size = nakshatra_size / 4
    pada = int((longitude % nakshatra_size) / pada_size) + 1

    return nakshatras[nakshatra_index], pada


def get_nakshatra_lord(nakshatra: str) -> str:
    """
    Get the planetary lord of a nakshatra.

    Args:
        nakshatra: Nakshatra name

    Returns:
        Planetary lord name
    """
    # Define the nakshatra lords in order
    nakshatra_lords = {
        "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
        "Rohini": "Moon", "Mrigashīrsha": "Mars", "Ardra": "Rahu",
        "Punarvasu": "Jupiter", "Pushya": "Saturn", "Āshleshā": "Mercury",
        "Maghā": "Ketu", "PūrvaPhalgunī": "Venus", "UttaraPhalgunī": "Sun",
        "Hasta": "Moon", "Chitra": "Mars", "Svati": "Rahu",
        "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
        "Mula": "Ketu", "PurvaAshadha": "Venus", "UttaraAshadha": "Sun",
        "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
        "PurvaBhādrapadā": "Jupiter", "UttaraBhādrapadā": "Saturn", "Revati": "Mercury"
    }

    return nakshatra_lords.get(nakshatra, "Unknown")


def get_sign_lord(sign: str) -> str:
    """
    Get the planetary lord of a zodiac sign.

    Args:
        sign: Zodiac sign name

    Returns:
        Planetary lord name
    """
    # Define the sign lords
    sign_lords = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter"
    }

    return sign_lords.get(sign, "Unknown")


def is_planet_retrograde(planet_speed: float) -> bool:
    """
    Determine if a planet is retrograde based on its daily motion.

    Args:
        planet_speed: Daily motion in degrees

    Returns:
        True if retrograde, False otherwise
    """
    return planet_speed < 0


def calculate_aspect_angle(lon1: float, lon2: float) -> float:
    """
    Calculate the angular separation between two celestial bodies.

    Args:
        lon1: Longitude of first body in decimal degrees
        lon2: Longitude of second body in decimal degrees

    Returns:
        Angular separation in degrees (always positive, <= 180)
    """
    # Calculate absolute difference in longitude
    diff = abs(lon1 - lon2) % 360

    # Return the smaller angle
    return min(diff, 360 - diff)


def is_aspect(angle: float, aspect_type: int, orb: float = 8.0) -> bool:
    """
    Check if an angle forms a specific aspect, considering orb.

    Args:
        angle: Angular separation to check
        aspect_type: Aspect angle (e.g., 0 for conjunction, 180 for opposition)
        orb: Allowed orb in degrees

    Returns:
        True if the angle forms the aspect, False otherwise
    """
    return abs(angle - aspect_type) <= orb


def format_time_range(start_dt: datetime, end_dt: datetime, format_str: str = "%H:%M") -> str:
    """
    Format a time range as a string.

    Args:
        start_dt: Start datetime
        end_dt: End datetime
        format_str: Format string for strftime

    Returns:
        Formatted time range string
    """
    return f"{start_dt.strftime(format_str)} - {end_dt.strftime(format_str)}"


def normalize_date(dt: datetime) -> datetime:
    """
    Normalize a datetime by removing seconds and microseconds.

    Args:
        dt: Datetime to normalize

    Returns:
        Normalized datetime
    """
    return dt.replace(second=0, microsecond=0)


def get_hora_lord(day_of_week: str, hora_number: int) -> str:
    """
    Get the planetary ruler of a hora.

    Args:
        day_of_week: Day of the week (e.g., 'Sunday')
        hora_number: Hora number (1-24)

    Returns:
        Planetary ruler name
    """
    # First hora of each day is ruled by the planet of that day
    first_hora_rulers = {
        "Sunday": "Sun",
        "Monday": "Moon",
        "Tuesday": "Mars",
        "Wednesday": "Mercury",
        "Thursday": "Jupiter",
        "Friday": "Venus",
        "Saturday": "Saturn"
    }

    # Sequence of rulers follows the Chaldean order of planets
    chaldean_order = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

    # Get the ruler of the first hora of the day
    first_ruler = first_hora_rulers.get(day_of_week)
    if not first_ruler:
        return "Unknown"

    # If requesting the first hora, return directly
    if hora_number == 1:
        return first_ruler

    # Find the index of the first ruler in the Chaldean order
    start_index = chaldean_order.index(first_ruler)

    # Calculate the rule of the requested hora by walking through the sequence
    ruler_index = (start_index + hora_number - 1) % 7

    return chaldean_order[ruler_index]


def get_current_hora(dt: datetime) -> int:
    """
    Get the hora number for a given time (1-24).

    Args:
        dt: Datetime to get hora for

    Returns:
        Hora number (1-24)
    """
    # Each hora is 1 hour (approximation for equal hours system)
    hour = dt.hour
    return hour + 1