"""
Position Calculator module for KP Astrology.
Handles calculations for planetary positions with KP sublord details.
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pytz
import pandas as pd
from collections import namedtuple

# Import the core VedicHoroscopeData class
# In the refactored structure, this would be from core.vedic_astro import VedicHoroscopeData
# For now, assuming we're using the existing class from kpTools
from core.vedic_astro import VedicChart


class PositionCalculator:
    """Calculate planetary positions with KP sublord details."""

    def __init__(self, latitude: float, longitude: float, timezone_str: str,
                 ayanamsa: str = "Krishnamurti", house_system: str = "Placidus"):
        """
        Initialize the position calculator.

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
            ayanamsa: Ayanamsa system to use
            house_system: House system to use
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = pytz.timezone(timezone_str)
        self.ayanamsa = ayanamsa
        self.house_system = house_system

        # Map UTC offset for the timezone
        now = datetime.now(self.timezone)
        offset = now.strftime('%z')
        hours, minutes = int(offset[0:3]), int(offset[0] + offset[3:5])
        self.utc_offset = f"{'+' if hours >= 0 else ''}{hours}:{minutes:02d}"

        # Planet mapping for display
        self.planet_mapping = {
            "Asc": "Ascendant",
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mercury",
            "Venus": "Venus",
            "Mars": "Mars",
            "Jupiter": "Jupiter",
            "Saturn": "Saturn",
            "North Node": "Rahu",
            "South Node": "Ketu",
            "Uranus": "Uranus",
            "Neptune": "Neptune",
            "Pluto": "Pluto"
        }

        # Reverse mapping for lookup
        self.reverse_planet_mapping = {v: k for k, v in self.planet_mapping.items()}

        print(f"PositionCalculator initialized for {latitude}, {longitude} ({timezone_str}) using {ayanamsa} ayanamsa")

    def create_chart_data(self, dt: datetime) -> VedicChart:
        """
        Create VedicHoroscopeData for the given datetime.

        Args:
            dt: The datetime to create the chart for

        Returns:
            VedicHoroscopeData object
        """
        # Make sure datetime is timezone aware
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)

        # Convert to the timezone used by the calculator
        dt = dt.astimezone(self.timezone)

        # Create the chart data
        chart_data = VedicChart(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            utc=self.utc_offset,
            latitude=self.latitude,
            longitude=self.longitude,
            ayanamsa=self.ayanamsa,
            house_system=self.house_system
        )

        return chart_data

    def format_position(self, planet: Any) -> str:
        """
        Format planet position consistently as degrees within sign.

        Args:
            planet: Planet object with position data

        Returns:
            Formatted position string
        """
        # Get absolute longitude
        abs_lon = planet.LonDecDeg

        # Get sign-based degree (0-29)
        sign_deg = int(abs_lon % 30)

        # Calculate minutes and seconds with proper rounding
        remainder = (abs_lon % 30) - sign_deg
        lon_min = int(remainder * 60)
        lon_sec = round(((remainder * 60) - lon_min) * 60)

        # Handle case where seconds round up to 60
        if lon_sec == 60:
            lon_sec = 0
            lon_min += 1
            if lon_min == 60:
                lon_min = 0
                sign_deg += 1

        # Get sign abbreviation
        sign_abbrev = planet.Rasi[:3]

        # Format the position string
        return f"{sign_deg}° {sign_abbrev} {lon_min:02d}' {lon_sec:02d}\""

    def get_planet_positions(self, dt: datetime) -> pd.DataFrame:
        """
        Get positions of all planets at the given datetime.

        Args:
            dt: Datetime to get positions for

        Returns:
            DataFrame with planet positions
        """
        try:
            # Create chart data
            chart_data = self.create_chart_data(dt)
            chart = chart_data.generate_chart()

            # Get planetary positions
            planets_data = chart_data.get_planets_data_from_chart(chart)
            houses_data = chart_data.get_houses_data_from_chart(chart)

            # Create DataFrame
            planet_rows = []

            # Specific planet order for display
            planet_order = ["Ascendant", "Sun", "Moon", "Mercury", "Venus", "Mars",
                            "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]

            # Create a map for quick lookup
            planet_map = {}
            for planet in planets_data:
                # Map North Node to Rahu and South Node to Ketu explicitly
                display_name = None
                if planet.Object == "Rahu" or planet.Object == "North Node":
                    display_name = "Rahu"
                elif planet.Object == "Ketu" or planet.Object == "South Node":
                    display_name = "Ketu"
                elif planet.Object == "Asc":
                    display_name = "Ascendant"
                elif planet.Object in self.planet_mapping:
                    display_name = self.planet_mapping[planet.Object]

                if display_name:
                    planet_map[display_name] = planet

            # Process planets in specific order
            for planet_name in planet_order:
                if planet_name not in planet_map:
                    continue

                planet = planet_map[planet_name]

                # Format position in degrees, minutes, seconds format
                position_str = self.format_position(planet)

                # Get retrograde status
                retrograde = "R" if planet.isRetroGrade else ""

                # Calculate KP pointer with SubSubLord
                kp_pointer = f"{planet.RasiLord}-{planet.NakshatraLord}-{planet.SubLord}-{planet.SubSubLord}"

                planet_rows.append({
                    "Planet": f"{planet_name}{retrograde}",
                    "Position": position_str,
                    "Sign": planet.Rasi,
                    "House": planet.HouseNr if planet.HouseNr else "-",
                    "Nakshatra": planet.Nakshatra,
                    "KP Pointer": kp_pointer,
                    "Rashi Lord": planet.RasiLord,
                    "Nakshatra Lord": planet.NakshatraLord,
                    "Sub Lord": planet.SubLord,
                    "Sub-Sub Lord": planet.SubSubLord,
                    "Longitude": planet.LonDecDeg
                })

            print(f"Calculated positions for {len(planet_rows)} planets at {dt}")
            return pd.DataFrame(planet_rows)

        except Exception as e:
            print(f"Error calculating planet positions: {str(e)}")
            # Return empty DataFrame on error
            return pd.DataFrame(columns=["Planet", "Position", "Sign", "House", "Nakshatra",
                                         "KP Pointer", "Rashi Lord", "Nakshatra Lord",
                                         "Sub Lord", "Sub-Sub Lord", "Longitude"])

    def get_houses_data(self, dt: datetime) -> pd.DataFrame:
        """
        Get house cusps data at the given datetime.

        Args:
            dt: Datetime to get house data for

        Returns:
            DataFrame with house data
        """
        try:
            # Create chart data
            chart_data = self.create_chart_data(dt)
            chart = chart_data.generate_chart()

            # Get houses data
            houses_data = chart_data.get_houses_data_from_chart(chart)

            # Create DataFrame
            house_rows = []

            for house in houses_data:
                house_rows.append({
                    "House": house.Object,  # Roman numeral
                    "House Nr": house.HouseNr,  # Numeric
                    "Sign": house.Rasi,
                    "Longitude": house.LonDecDeg,
                    "Position": f"{house.SignLonDMS}",
                    "Size": f"{house.DegSize:.2f}°",
                    "Nakshatra": house.Nakshatra,
                    "Rashi Lord": house.RasiLord,
                    "Nakshatra Lord": house.NakshatraLord,
                    "Sub Lord": house.SubLord,
                    "Sub-Sub Lord": house.SubSubLord
                })

            print(f"Calculated data for {len(house_rows)} houses at {dt}")
            return pd.DataFrame(house_rows)

        except Exception as e:
            print(f"Error calculating house data: {str(e)}")
            # Return empty DataFrame on error
            return pd.DataFrame(columns=["House", "House Nr", "Sign", "Longitude", "Position",
                                         "Size", "Nakshatra", "Rashi Lord", "Nakshatra Lord",
                                         "Sub Lord", "Sub-Sub Lord"])

    def get_consolidated_chart_data(self, dt: datetime) -> Dict:
        """
        Get consolidated chart data with planets and houses by sign.

        Args:
            dt: Datetime to get chart data for

        Returns:
            Dictionary with consolidated chart data
        """
        try:
            # Create chart data
            chart_data = self.create_chart_data(dt)
            chart = chart_data.generate_chart()

            # Get data
            planets_data = chart_data.get_planets_data_from_chart(chart)
            houses_data = chart_data.get_houses_data_from_chart(chart)

            # Get consolidated data in "dataframe_records" style
            consolidated_data = chart_data.get_consolidated_chart_data(
                planets_data=planets_data,
                houses_data=houses_data,
                return_style="dataframe_records"
            )

            return consolidated_data

        except Exception as e:
            print(f"Error getting consolidated chart data: {str(e)}")
            return {}

    def get_planet_position(self, planet_name: str, dt: datetime) -> Optional[Dict]:
        """
        Get position data for a specific planet.

        Args:
            planet_name: Name of the planet
            dt: Datetime to get position for

        Returns:
            Dictionary with planet position data or None if not found
        """
        # Get all planet positions
        all_positions = self.get_planet_positions(dt)

        # Find the specific planet
        for _, row in all_positions.iterrows():
            # Strip any retrograde marker from the name for comparison
            row_planet = row["Planet"].replace("R", "").strip()
            if row_planet == planet_name:
                return row.to_dict()

        return None

    def get_chart_and_planets_data(self, dt: datetime) -> Tuple[Dict, List]:
        """
        Get raw chart and planets data for use with yoga calculator.

        Args:
            dt: Datetime to get data for

        Returns:
            Tuple of (chart_data, planets_data)
        """
        # Create chart data
        chart_data_obj = self.create_chart_data(dt)
        chart = chart_data_obj.generate_chart()

        # Get planets data
        planets_data = chart_data_obj.get_planets_data_from_chart(chart)

        # Create a dict representation of the chart
        chart_data = {
            "ayanamsa": self.ayanamsa,
            "house_system": self.house_system,
            "datetime": dt.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude
        }

        return chart_data, planets_data