import pytz
from datetime import datetime, timedelta
import ephem


class HoraCalculator:
    """
    Class for calculating hora (planetary hour) timings.
    In Vedic astrology, each day is divided into 24 horas, each ruled by a different planet.
    """

    def __init__(self, latitude, longitude, timezone):
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
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.tz = pytz.timezone(timezone)

    @staticmethod
    def _get_hora_rulers_for_day(day_of_week):
        """Get the correct sequence of hora rulers starting at sunrise for a given day"""
        hora_rulers = {
            "Sunday": ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"],
            "Monday": ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"],
            "Tuesday": ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"],
            "Wednesday": ["Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"],
            "Thursday": ["Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn"],
            "Friday": ["Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun"],
            "Saturday": ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        }

        return hora_rulers.get(day_of_week, [])

    def get_sunrise_with_ephem(self, date, latitude=None, longitude=None):
        """
        Calculate sunrise and sunset using the ephem library.
        Returns UTC times without timezone info.

        Parameters:
        -----------
        date : datetime.date
            The date to calculate sunrise/sunset for
        latitude : float, optional
            The latitude of the location (defaults to self.latitude)
        longitude : float, optional
            The longitude of the location (defaults to self.longitude)

        Returns:
        --------
        dict
            Dictionary with 'sunrise' and 'sunset' as datetime objects in UTC
        """
        if latitude is None:
            latitude = self.latitude
        if longitude is None:
            longitude = self.longitude

        # Create observer at the specified location
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.date = date.strftime('%Y/%m/%d')
        observer.pressure = 0  # Ignore atmospheric refraction
        observer.horizon = '-0:34'  # Standard solar disc adjustment

        # Calculate sunrise and sunset (these will be in UTC)
        sun = ephem.Sun()

        try:
            sunrise_utc = observer.next_rising(sun).datetime()
            sunset_utc = observer.next_setting(sun).datetime()
        except (ephem.AlwaysUpError, ephem.NeverUpError):
            # Handle polar cases where sun might not rise or set
            # For these special cases, use nautical twilight as an approximation
            observer.horizon = '-12'  # Nautical twilight
            sunrise_utc = observer.next_rising(sun, use_center=True).datetime()
            sunset_utc = observer.next_setting(sun, use_center=True).datetime()

        return {
            'sunrise': sunrise_utc,  # UTC time without timezone info
            'sunset': sunset_utc  # UTC time without timezone info
        }

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
        import pandas as pd

        # Ensure datetimes are timezone aware
        if start_dt.tzinfo is None:
            start_dt = self.tz.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.tz.localize(end_dt)

        # Get sunrise data for the requested date in the correct timezone
        sun_data = self.get_sunrise_with_ephem(start_dt.date())

        # Convert UTC times to the local timezone
        sunrise = pytz.utc.localize(sun_data['sunrise']).astimezone(self.tz)
        sunset = pytz.utc.localize(sun_data['sunset']).astimezone(self.tz)

        # Get next day's sunrise
        next_day = start_dt.date() + timedelta(days=1)
        next_sun_data = self.get_sunrise_with_ephem(next_day)
        next_sunrise = pytz.utc.localize(next_sun_data['sunrise']).astimezone(self.tz)

        # Calculate Hora durations
        day_duration = (sunset - sunrise).total_seconds()
        night_duration = (next_sunrise - sunset).total_seconds()

        day_hora_duration = day_duration / 12
        night_hora_duration = night_duration / 12

        # Get day of week based on the sunrise time in local timezone
        day_of_week = sunrise.strftime("%A")
        hora_rulers = self._get_hora_rulers_for_day(day_of_week)
        
        # Get the day lord (ruler of the day)
        day_lord = hora_rulers[0]  # First ruler in the sequence is the day lord

        # Calculate hora timings
        hora_rows = []
        current_time = sunrise
        hora_index = 0

        while current_time < next_sunrise:
            # Determine if this is a day or night hora
            is_day_hora = current_time < sunset

            # Calculate hora end time
            if is_day_hora:
                hora_end = current_time + timedelta(seconds=day_hora_duration)
            else:
                hora_end = current_time + timedelta(seconds=night_hora_duration)

            # Only include horas that overlap with our time range
            if hora_end > start_dt and current_time < end_dt:
                hora_lord = hora_rulers[hora_index % 7]
                
                hora_rows.append({
                    "Start Time": max(current_time, start_dt).strftime("%H:%M"),
                    "End Time": min(hora_end, end_dt).strftime("%H:%M"),
                    "Planet": hora_lord,
                    "Hora Lord": hora_lord,
                    "Day Lord": day_lord,
                    "Day/Night": "Day" if is_day_hora else "Night"
                })

            current_time = hora_end
            hora_index += 1

        return pd.DataFrame(hora_rows)
