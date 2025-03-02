"""
Horary chart calculations for KP astrology.

This module provides functions for calculating horary charts
according to the Krishnamurti Paddhati (KP) system of astrology.
"""

import os
import polars as pl
import swisseph as swe
from datetime import datetime

from .utils import dms_to_decdeg, utc_offset_str_to_float

# Global Constants
SWE_AYANAMAS = {
    "Krishnamurti": swe.SIDM_KRISHNAMURTI,
    "Krishnamurti_New": swe.SIDM_KRISHNAMURTI_VP291,
    "Lahiri_1940": swe.SIDM_LAHIRI_1940,
    "Lahiri_VP285": swe.SIDM_LAHIRI_VP285,
    "Lahiri_ICRC": swe.SIDM_LAHIRI_ICRC,
    "Raman": swe.SIDM_RAMAN,
    "Yukteshwar": swe.SIDM_YUKTESHWAR
}

# Determine the absolute path to the directory where this script is located
current_dir = os.path.abspath(os.path.dirname(__file__))
csv_file_path = os.path.join(current_dir, "data", "KP_SL_Divisions.csv")

# Read KP SubLord Divisions CSV File
KP_SL_DMS_DATA = pl.read_csv(csv_file_path)
KP_SL_DMS_DATA = KP_SL_DMS_DATA\
                .with_columns(pl.arange(1, KP_SL_DMS_DATA.height + 1).alias("SL_Div_Nr"))\
                .with_columns([
                    pl.col('From_DMS').map_elements(dms_to_decdeg).alias('From_DecDeg'),
                    pl.col('To_DMS').map_elements(dms_to_decdeg).alias('To_DecDeg'),
                    pl.col("From_DMS").str.replace_all(":", "").cast(pl.Int32).alias("From_DMS_int"),
                    pl.col("To_DMS").str.replace_all(":", "").cast(pl.Int32).alias("To_DMS_int")
                ])


def jd_to_datetime(jdt: float, tz_offset: float) -> datetime:
    """
    Convert Julian Day Time to a datetime object.
    
    Args:
        jdt (float): Julian Day Time.
        tz_offset (float): Timezone offset in hours.
        
    Returns:
        datetime: The corresponding datetime object.
    """
    utc = swe.jdut1_to_utc(jdt) 
    # Convert UTC to local time - note negative sign before tzoffset to convert from UTC to local time
    year, month, day, hour, minute, seconds = swe.utc_time_zone(*utc, offset=-tz_offset)
    # Convert the fractional seconds to microseconds
    microseconds = int(seconds % 1 * 1_000_000)
    return datetime(year, month, day, hour, minute, int(seconds), microseconds)


def get_horary_ascendant_degree(horary_number: int) -> dict:
    """
    Convert a horary number to ascendant degree of the starting subdivision.
    
    Args:
        horary_number (int): The horary number (1-249).
        
    Returns:
        dict: A dictionary containing sign, DMS, decimal degree, and sublord information.
        
    Raises:
        ValueError: If horary_number is out of range.
    """
    if 1 <= horary_number <= 249:
        row = KP_SL_DMS_DATA.filter(pl.col("SL_Div_Nr") == horary_number).select(["Sign", "From_DMS", "From_DecDeg", "SubLord"])
        data = row.to_dicts()[0]

        # Convert the sign to its starting degree in the zodiac circle
        sign_order = {
            'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
            'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
            'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330 
        }
        
        sign_start_degree = sign_order[data['Sign']]

        # Convert From_DecDeg to zodiac degree location
        zodiac_degree_location = sign_start_degree + data['From_DecDeg']
        data['ZodiacDegreeLocation'] = zodiac_degree_location
        return data
    else:
        raise ValueError("SL Div Nr. out of range. Please provide a number between 1 and 249.")


def find_exact_ascendant_time(year: int, month: int, day: int, utc_offset: str, lat: float, lon: float, 
                             horary_number: int, ayanamsa: str) -> tuple:
    """
    Find the exact time when the Ascendant is at the desired degree.

    Args:
        year (int): Year of the horary question (prasna).
        month (int): Month of the horary question.
        day (int): Day of the horary question.
        utc_offset (str): The UTC offset of the horary question's location (e.g., '+5:30').
        lat (float): Latitude pertaining to the horary question's predictor (astrologer).
        lon (float): Longitude pertaining to the horary question's predictor (astrologer).
        horary_number (int): The horary number for which to retrieve the ascendant details.
        ayanamsa (str): The ayanamsa to be used when constructing the chart.

    Returns:
        tuple: A tuple containing (matched_time, houses_chart, houses_data) if a match is found,
               or None if no match is found within the day.
    """
    # Import here to avoid circular imports
    from .core import VedicHoroscopeData
    
    # Retrieve Horary Asc Details from given horary_number
    horary_asc = get_horary_ascendant_degree(horary_number) 
    horary_asc_deg = horary_asc["ZodiacDegreeLocation"]
    req_sublord = horary_asc["SubLord"]   
    utc_float = utc_offset_str_to_float(utc_offset)

    utc = swe.utc_time_zone(year, month, day, hour=0, minutes=0, seconds=0, offset=utc_float)
    _, jd_start = swe.utc_to_jd(*utc)  # Unpacks utc tuple
    jd_end = jd_start + 1  # end of the day

    swe.set_sid_mode(SWE_AYANAMAS.get(ayanamsa))  # set the ayanamsa
    current_time = jd_start
    counter = 0
    
    while current_time <= jd_end:
        cusps, _ = swe.houses_ex(current_time, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
        asc_lon_deg = cusps[0]
        asc_deg_diff = asc_lon_deg - horary_asc_deg
        asc_deg_diff_abs = abs(asc_deg_diff)

        # Adjust increment factor based on the magnitude of degree difference
        if asc_deg_diff_abs > 10:
            inc_factor = 0.005  # largest steps when far away
        elif asc_deg_diff_abs >= 1.0:
            inc_factor = 1  # larger steps when moderately away
        elif asc_deg_diff_abs >= 0.1:
            inc_factor = 10  # smaller steps when getting closer
        else:
            inc_factor = 100  # very small steps when very close

        # Special handling for cyclical transition near 360 degrees for horary_number == 1
        if (asc_lon_deg > 355 and horary_asc_deg == 0.0):
            inc_factor = 100  # Use very small steps to avoid overshooting the target

        if 0.0001 < asc_deg_diff <= 0.001:
            matched_time = jd_to_datetime(current_time, utc_float)
            secs_final = matched_time.second + (matched_time.microsecond) / 1_000_000
            vhd_hora = VedicHoroscopeData(
                year, month, day, matched_time.hour, matched_time.minute, 
                secs_final, utc_offset, lat, lon, ayanamsa, "Placidus"
            )
            houses_chart = vhd_hora.generate_chart()
            houses_data = vhd_hora.get_houses_data_from_chart(houses_chart)
            asc = houses_data[0]
            
            if asc.SubLord == req_sublord:
                return matched_time, houses_chart, houses_data
        
        current_time += 1.0 / (24 * 60 * 60 * inc_factor)  # Adjust time increment based on the factor
        counter += 1

    return None 