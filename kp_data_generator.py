from datetime import datetime, timedelta
import pytz
import pandas as pd
from kpTools.VedicAstro import VedicHoroscopeData
from kpTools.utils import dms_to_decdeg
from aspect_calculator import AspectCalculator
from calculations.hora_calculator import HoraCalculator
from calculations.position_calculator import PlanetPositionCalculator
from calculations.transit_calculator import TransitCalculator


class KPDataGenerator:
    def __init__(self, latitude, longitude, timezone, ayanamsa="Krishnamurti", house_system="Placidus"):
        """
        Initialize the KP Data Generator with location information.

        Parameters:
        -----------
        latitude : float
            The latitude of the location
        longitude : float
            The longitude of the location
        timezone : str
            The timezone string (e.g., 'Asia/Kolkata')
        ayanamsa : str
            The ayanamsa system to use (default: 'Krishnamurti')
        house_system : str
            The house system to use (default: 'Placidus')
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

        # Initialize the specialized calculators
        self.position_calculator = PlanetPositionCalculator(
            latitude, longitude, timezone, ayanamsa, house_system
        )
        self.hora_calculator = HoraCalculator(
            latitude, longitude, timezone
        )
        self.transit_calculator = TransitCalculator(
            latitude, longitude, timezone, self.position_calculator, ayanamsa, house_system
        )

        # Initialize aspect calculator
        self.aspect_calculator = AspectCalculator()

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
        return self.position_calculator.create_chart_data(dt)

    def format_position(self, planet):
        """Format planet position consistently as degrees within sign"""
        return self.position_calculator.format_position(planet)

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
        return self.position_calculator.get_planet_positions(dt)

    def get_sunrise_with_ephem(self, date, latitude, longitude):
        """
        Calculate sunrise and sunset using the ephem library.
        Returns UTC times without timezone info.

        Parameters:
        -----------
        date : datetime.date
            The date to calculate sunrise/sunset for
        latitude : float
            The latitude of the location
        longitude : float
            The longitude of the location

        Returns:
        --------
        dict
            Dictionary with 'sunrise' and 'sunset' as datetime objects in UTC
        """
        return self.hora_calculator.get_sunrise_with_ephem(date, latitude, longitude)

    def get_hora_timings(self, start_dt, end_dt):
        """
        Get accurate Hora timings based on sunrise/sunset for the given date range.
        Properly handles timezone conversions.
        """
        return self.hora_calculator.get_hora_timings(start_dt, end_dt)

    def get_planet_transitions(self, planet_name, start_dt, end_dt, check_interval_minutes=1):
        """
        Track transitions in a planet's position parameters over time.

        Parameters:
        -----------
        planet_name : str
            The name of the planet to track
        start_dt : datetime
            The start datetime
        end_dt : datetime
            The end datetime
        check_interval_minutes : int
            How often to check for changes (in minutes)

        Returns:
        --------
        pandas.DataFrame
            DataFrame with transition data
        """
        return self.transit_calculator.get_planet_transitions(planet_name, start_dt, end_dt, check_interval_minutes)
        
    def calculate_yogas(self, chart, planets_data):
        """
        Calculate all yogas (auspicious and inauspicious planetary combinations) for the given chart.
        
        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : pandas.DataFrame
            DataFrame with planet positions
            
        Returns:
        --------
        list
            List of yoga dictionaries containing yoga information
        """
        # Use the aspect calculator to calculate yogas
        return self.aspect_calculator.calculate_yogas(chart, planets_data)
