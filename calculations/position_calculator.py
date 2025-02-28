import pandas as pd
from kpTools.VedicAstro import VedicHoroscopeData
import pytz
from datetime import datetime

class PlanetPositionCalculator:
    """
    Class for calculating and formatting planetary positions.
    """
    
    def __init__(self, latitude, longitude, timezone, ayanamsa="Krishnamurti", house_system="Placidus"):
        """
        Initialize with location information.
        
        Parameters:
        -----------
        latitude : float
            The latitude of the location
        longitude : float
            The longitude of the location
        timezone : str
            The timezone string (e.g. 'UTC', 'Asia/Kolkata')
        ayanamsa : str, optional
            The ayanamsa to use (default is "Krishnamurti")
        house_system : str, optional
            The house system to use (default is "Placidus")
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.ayanamsa = ayanamsa
        self.house_system = house_system
        self.tz = pytz.timezone(timezone)

        # Map UTC offset for the timezone
        now = datetime.now(self.tz)
        offset = now.strftime('%z')
        hours, minutes = int(offset[0:3]), int(offset[0] + offset[3:5])
        self.utc_offset = f"{'+' if hours >= 0 else ''}{hours}:{minutes:02d}"
        
        # Planet mapping (name in library to display name)
        self.planet_mapping = {
            "Moon": "Moon",
            "Asc": "Ascendant",
            "Sun": "Sun",
            "Mercury": "Mercury",
            "Venus": "Venus",
            "Mars": "Mars",
            "Jupiter": "Jupiter",
            "Saturn": "Saturn",
            "North Node": "Rahu",
            "South Node": "Ketu",
            "Uranus": "Uranus",
            "Neptune": "Neptune"
        }

        # Reverse mapping for lookup
        self.reverse_planet_mapping = {v: k for k, v in self.planet_mapping.items()}
        
    def create_chart_data(self, dt):
        """
        Create VedicHoroscopeData for the given datetime.

        Parameters:
        -----------
        dt : datetime
            The datetime to create the chart for

        Returns:
        --------
        VedicHoroscopeData
            The chart data object
        """
        from datetime import datetime
        
        # Make sure datetime is timezone aware
        if dt.tzinfo is None:
            dt = self.tz.localize(dt)

        chart_data = VedicHoroscopeData(
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
        
    def format_position(self, planet):
        """
        Format planet position consistently as degrees within sign
        
        Parameters:
        -----------
        planet : object
            The planet object with position data
            
        Returns:
        --------
        str
            A formatted string representing the planet's position
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
        
    def get_planet_positions(self, dt):
        """
        Get positions of all planets at the given datetime.

        Parameters:
        -----------
        dt : datetime
            The datetime to get positions for

        Returns:
        --------
        pandas.DataFrame
            DataFrame with planet positions
        """
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
        for planet in planets_
            # Map North Node to Rahu and South Node to Ketu explicitly
            display_name = None
            if planet.Object == "Rahu" or planet.Object == "North Node":
                display_name = "Rahu"
            elif planet.Object == "Ketu" or planet.Object == "South Node":
                display_name = "Ketu"
            elif planet.Object in self.planet_mapping:
                display_name = self.planet_mapping[planet.Object]

            if display_name:
                planet_map[display_name] = planet

        # Process planets in specific order
        for planet_name in planet_order:
            if planet_name not in planet_map:
                continue

            planet = planet_map[planet_name]
            obj_name = planet.Object

            # Format position in degrees, minutes, seconds format
            position_str = self.format_position(planet)

            # Get retrograde status
            retrograde = "Y" if planet.isRetroGrade else "N"

            # Calculate KP pointer with SubSubLord
            kp_pointer = f"{planet.RasiLord}-{planet.NakshatraLord}-{planet.SubLord}-{planet.SubSubLord}"

            planet_rows.append({
                "Planet": planet_name,
                "Position": position_str,
                "Sign": planet.Rasi,
                "House": planet.HouseNr if planet.HouseNr else "-",
                "Nakshatra": planet.Nakshatra,
                "KP Pointer": kp_pointer,
                "Retrograde": retrograde
            })

        return pd.DataFrame(planet_rows)
