"""
Horary chart calculations for KP Astrology.
Handles horary number mapping to ascendant degrees and precise timing calculations.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import swisseph as swe
import os
import sys
from pathlib import Path

# Import from core modules
from .utils import dms_to_decdeg, utc_offset_str_to_float
from .vedic_astro import VedicChart

# Mapping of ayanamsas to swisseph constants
SWE_AYANAMSAS = {
    "Krishnamurti": swe.SIDM_KRISHNAMURTI,
    "Krishnamurti_New": swe.SIDM_KRISHNAMURTI_VP291,
    "Lahiri_1940": swe.SIDM_LAHIRI_1940,
    "Lahiri_VP285": swe.SIDM_LAHIRI_VP285,
    "Lahiri_ICRC": swe.SIDM_LAHIRI_ICRC,
    "Raman": swe.SIDM_RAMAN,
    "Yukteshwar": swe.SIDM_YUKTESHWAR
}


class HoraryCalculator:
    """Calculator for horary chart timing and analysis."""

    def __init__(self, kp_data_path: str = None):
        """
        Initialize the horary calculator.

        Args:
            kp_data_path: Path to KP sublord divisions data CSV file
        """
        self.kp_data_path = kp_data_path
        self.kp_sl_data = self._load_kp_sublord_data()
        print(f"HoraryCalculator initialized with {len(self.kp_sl_data)} KP sublord divisions")

    def _load_kp_sublord_data(self) -> pd.DataFrame:
        """
        Load KP sublord division data from CSV.

        Returns:
            DataFrame with KP sublord data
        """
        try:
            # Try to locate the file
            if self.kp_data_path:
                csv_path = self.kp_data_path
            else:
                # Look in standard locations
                possible_paths = [
                    os.path.join("core", "data", "KP_SL_Divisions.csv"),
                    os.path.join("data", "KP_SL_Divisions.csv"),
                    os.path.join(os.path.dirname(__file__), "..", "data", "KP_SL_Divisions.csv")
                ]

                csv_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        csv_path = path
                        break

                if not csv_path:
                    raise FileNotFoundError("KP_SL_Divisions.csv not found in standard locations")

            # Read and preprocess the data
            kp_data = pd.read_csv(csv_path)

            # Convert DMS columns to decimal degrees
            kp_data['From_DecDeg'] = kp_data['From_DMS'].apply(dms_to_decdeg)
            kp_data['To_DecDeg'] = kp_data['To_DMS'].apply(dms_to_decdeg)

            # Add division number for lookup
            kp_data['SL_Div_Nr'] = range(1, len(kp_data) + 1)

            # Convert DMS to integers for faster comparison
            kp_data['From_DMS_int'] = kp_data['From_DMS'].str.replace(':', '').astype(int)
            kp_data['To_DMS_int'] = kp_data['To_DMS'].str.replace(':', '').astype(int)

            return kp_data

        except Exception as e:
            print(f"Error loading KP sublord data: {str(e)}")
            # Return empty DataFrame as fallback
            return pd.DataFrame(columns=['Sign', 'Nakshatra', 'From_DMS', 'To_DMS',
                                         'RasiLord', 'NakshatraLord', 'SubLord',
                                         'From_DecDeg', 'To_DecDeg', 'SL_Div_Nr'])

    def get_horary_ascendant_degree(self, horary_number: int) -> Dict:
        """
        Convert a horary number to ascendant degree of the starting subdivision.

        Args:
            horary_number: KP horary number (1-249)

        Returns:
            Dictionary with horary details or None if invalid
        """
        try:
            if not 1 <= horary_number <= 249:
                raise ValueError(f"Horary number must be between 1 and 249, got {horary_number}")

            # Find the row for this horary number
            row = self.kp_sl_data[self.kp_sl_data['SL_Div_Nr'] == horary_number]

            if row.empty:
                raise ValueError(f"No data found for horary number {horary_number}")

            data = row.iloc[0].to_dict()

            # Convert the sign to its starting degree in the zodiac
            sign_order = {
                'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
                'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
                'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330
            }

            sign_start_degree = sign_order.get(data['Sign'], 0)

            # Calculate absolute zodiac position
            zodiac_degree_location = sign_start_degree + data['From_DecDeg']
            data['ZodiacDegreeLocation'] = zodiac_degree_location

            return data

        except Exception as e:
            print(f"Error getting horary ascendant degree: {str(e)}")
            return None

    def jd_to_datetime(self, jdt: float, tz_offset: float) -> datetime:
        """
        Convert Julian date to datetime.

        Args:
            jdt: Julian date
            tz_offset: Timezone offset in hours

        Returns:
            Datetime object
        """
        try:
            # Convert Julian date to UTC
            utc = swe.jdut1_to_utc(jdt)

            # Convert UTC to local time
            year, month, day, hour, minute, seconds = swe.utc_time_zone(*utc, offset=-tz_offset)

            # Convert fractional seconds to microseconds
            microseconds = int(seconds % 1 * 1_000_000)

            return datetime(year, month, day, hour, minute, int(seconds), microseconds)

        except Exception as e:
            print(f"Error converting Julian date to datetime: {str(e)}")
            # Return current time as fallback
            return datetime.now()

    def find_exact_ascendant_time(self,
                                  year: int,
                                  month: int,
                                  day: int,
                                  utc_offset: str,
                                  latitude: float,
                                  longitude: float,
                                  horary_number: int,
                                  ayanamsa: str = "Krishnamurti") -> Tuple[datetime, Dict, List]:
        """
        Find the exact time when the Ascendant matches a horary number's degree.

        Args:
            year: Year of horary question
            month: Month of horary question
            day: Day of horary question
            utc_offset: UTC offset string (e.g., '+5:30')
            latitude: Latitude of location
            longitude: Longitude of location
            horary_number: Horary number (1-249)
            ayanamsa: Ayanamsa system to use

        Returns:
            Tuple of (matched_time, chart_data, houses_data)
        """
        try:
            # Get horary ascendant details
            horary_asc = self.get_horary_ascendant_degree(horary_number)
            if not horary_asc:
                raise ValueError(f"Could not get ascendant details for horary number {horary_number}")

            horary_asc_deg = horary_asc["ZodiacDegreeLocation"]
            req_sublord = horary_asc["SubLord"]

            # Convert UTC offset string to float
            utc_float = utc_offset_str_to_float(utc_offset)

            # Calculate Julian date for the start of the day
            utc = swe.utc_time_zone(year, month, day, hour=0, minutes=0, seconds=0, offset=utc_float)
            _, jd_start = swe.utc_to_jd(*utc)
            jd_end = jd_start + 1  # End of the day

            # Set the ayanamsa
            swe_ayanamsa = SWE_AYANAMSAS.get(ayanamsa, swe.SIDM_KRISHNAMURTI)
            swe.set_sid_mode(swe_ayanamsa)

            # Initialize search
            current_time = jd_start
            counter = 0
            max_iterations = 5000  # Safety limit

            print(f"Searching for ascendant time for horary number {horary_number} "
                  f"(degree: {horary_asc_deg:.4f}°, sublord: {req_sublord})")

            while current_time <= jd_end and counter < max_iterations:
                # Calculate houses for the current time
                cusps, _ = swe.houses_ex(current_time, latitude, longitude,
                                         b'P', flags=swe.FLG_SIDEREAL)

                # Get current ascendant longitude
                asc_lon_deg = cusps[0]

                # Calculate difference from target
                asc_deg_diff = asc_lon_deg - horary_asc_deg
                asc_deg_diff_abs = abs(asc_deg_diff)

                # Adjust step size based on how close we are
                if asc_deg_diff_abs > 10:
                    inc_factor = 0.005  # Large steps when far away
                elif asc_deg_diff_abs >= 1.0:
                    inc_factor = 1  # Medium steps
                elif asc_deg_diff_abs >= 0.1:
                    inc_factor = 10  # Small steps when close
                else:
                    inc_factor = 100  # Very small steps when very close

                # Special handling for the boundary case (horary_number == 1)
                if asc_lon_deg > 355 and horary_asc_deg == 0.0:
                    inc_factor = 100  # Very small steps

                # Debug progress every 100 iterations
                if counter % 100 == 0:
                    current_time_dt = self.jd_to_datetime(current_time, utc_float)
                    print(f"Iteration {counter}: Time={current_time_dt.strftime('%H:%M:%S')}, "
                          f"Current={asc_lon_deg:.4f}°, Target={horary_asc_deg:.4f}°, "
                          f"Diff={asc_deg_diff_abs:.4f}°")

                # Check if we're close enough
                if 0.0001 < asc_deg_diff_abs <= 0.001:
                    # Close enough to check sublord
                    matched_time = self.jd_to_datetime(current_time, utc_float)

                    # Create a chart to verify sublord
                    vhd = VedicChart(
                        dt=matched_time,
                        latitude=latitude,
                        longitude=longitude,
                        timezone_str="UTC",  # We'll handle timezone conversion separately
                        ayanamsa=ayanamsa,
                        house_system="Placidus"
                    )

                    # Get houses data
                    houses_data = vhd.houses_data

                    # Check ascendant's sublord
                    asc = houses_data[0]

                    if asc.SubLord == req_sublord:
                        print(f"Match found at {matched_time.strftime('%H:%M:%S.%f')} "
                              f"after {counter} iterations")

                        chart_data = {
                            "horary_number": horary_number,
                            "target_degree": horary_asc_deg,
                            "actual_degree": asc_lon_deg,
                            "sublord": req_sublord
                        }

                        return matched_time, chart_data, houses_data

                # Increment time and counter
                current_time += 1.0 / (24 * 60 * 60 * inc_factor)
                counter += 1

            # If we reach here, no match was found
            raise ValueError(f"No matching ascendant time found within {counter} iterations")

        except Exception as e:
            print(f"Error finding exact ascendant time: {str(e)}")
            return None, {}, []