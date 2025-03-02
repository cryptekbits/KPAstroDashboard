from datetime import datetime, timedelta
import pytz
import pandas as pd
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kpTools.VedicAstro import VedicHoroscopeData
from kpTools.utils import dms_to_decdeg
from calculations.aspect_calculator import AspectCalculator
from calculations.hora_calculator import HoraCalculator
from calculations.position_calculator import PlanetPositionCalculator
from calculations.transit_calculator import TransitCalculator


class KPDataGenerator:
    """
    Class for generating KP (Krishnamurti Paddhati) astrological data.
    Handles planetary positions, hora timings, transits, and yogas.
    """

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
        print(f"Initializing KP Data Generator with: lat={latitude}, lon={longitude}, tz={timezone}")
        print(f"Using ayanamsa: {ayanamsa}, house system: {house_system}")

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
        """
        Format planet position consistently as degrees within sign.

        Parameters:
        -----------
        planet : object
            The planet object with position data

        Returns:
        --------
        str
            A formatted string representing the planet's position
        """
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
        print(f"Getting planet positions for {dt}")
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

        Parameters:
        -----------
        start_dt : datetime
            The start datetime
        end_dt : datetime
            The end datetime

        Returns:
        --------
        pandas.DataFrame
            DataFrame with hora timing information
        """
        print(f"Getting hora timings from {start_dt} to {end_dt}")
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
        print(f"Getting transitions for {planet_name} from {start_dt} to {end_dt}")
        return self.transit_calculator.get_planet_transitions(planet_name, start_dt, end_dt, check_interval_minutes)

    def calculate_yogas(self, chart, planets_data):
        """
        Calculate all yogas (auspicious and inauspicious planetary combinations) for the given chart.

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : pandas.DataFrame with planet positions

        Returns:
        --------
        list
            List of yoga dictionaries containing yoga information
        """
        # Use the aspect calculator to calculate yogas
        return self.aspect_calculator.calculate_yogas(chart, planets_data)

    def calculate_yogas_for_date_range(self, start_date, end_date, progress_callback=None):
        """
        Calculate yogas for each day in the given date range.

        Parameters:
        -----------
        start_date : datetime
            The start date for yoga calculation
        end_date : datetime
            The end date for yoga calculation
        progress_callback : function, optional
            Callback function to report progress (receives current_progress, total, message)

        Returns:
        --------
        pandas.DataFrame
            DataFrame with yoga information for each day
        """
        print(f"Calculating yogas from {start_date.date()} to {end_date.date()}")

        # List to store all yoga results
        all_yogas = []

        # Calculate the number of days to process
        total_days = (end_date.date() - start_date.date()).days + 1
        days_processed = 0

        # Process each day in the range
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_point = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        while current_date <= end_point:
            # Calculate progress
            if progress_callback:
                progress_callback(days_processed, total_days,
                                  f"Calculating yogas for {current_date.strftime('%Y-%m-%d')}")

            try:
                # Generate chart data for this date
                chart_data = self.create_chart_data(current_date)
                chart = chart_data.generate_chart()

                # Get planetary positions
                planets_data = chart_data.get_planets_data_from_chart(chart)

                # Calculate yogas for this date/time
                yogas = self.calculate_yogas(chart, planets_data)

                # Add date and time information to each yoga
                for yoga in yogas:
                    yoga_entry = {
                        "Date": current_date.strftime("%d/%m/%y"),
                        "Time": current_date.strftime("%I:%M %p"),
                        "Yoga": yoga["name"],
                        "Planets": self._format_planets_for_excel(yoga["planets_info"]),
                        "Nature": yoga.get("nature", "Neutral"),
                        "Description": yoga.get("description", "")
                    }
                    all_yogas.append(yoga_entry)

            except Exception as e:
                print(f"Error calculating yogas for {current_date}: {str(e)}")

            # Increment to next check point (skipping ahead in 6-hour increments for efficiency)
            # This can be adjusted based on how frequently you expect yogas to change
            current_date += timedelta(hours=6)
            days_processed = min((current_date - start_date).total_seconds() / 86400, total_days)

        # Convert the list to a DataFrame
        if not all_yogas:
            # Return empty DataFrame with expected columns if no yogas found
            return pd.DataFrame(columns=["Date", "Time", "Yoga", "Planets", "Nature", "Description"])

        df = pd.DataFrame(all_yogas)

        # Sort by date and time
        df = df.sort_values(["Date", "Time"])

        print(f"Found {len(df)} yogas in the date range")
        return df

    def _format_planets_for_excel(self, planets_info):
        """
        Format planet information for display in Excel.

        Parameters:
        -----------
        planets_info : list
            List of planet information strings

        Returns:
        --------
        str
            Formatted planet information
        """
        return ", ".join(planets_info)