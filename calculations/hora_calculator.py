"""
Hora Calculator module for KP Astrology.
Handles calculations for hora timings based on sunrise/sunset.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pytz
import pandas as pd
import ephem


class HoraCalculator:
    """Calculate hora timings based on sunrise and sunset."""

    def __init__(self, latitude: float, longitude: float, timezone_str: str):
        """
        Initialize the hora calculator.

        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = pytz.timezone(timezone_str)

        # Planet mapping for display
        self.planet_names = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mars": "Mars",
            "Mercury": "Mercury",
            "Jupiter": "Jupiter",
            "Venus": "Venus",
            "Saturn": "Saturn"
        }

        # Map UTC offset for the timezone
        now = datetime.now(self.timezone)
        offset = now.strftime('%z')
        hours, minutes = int(offset[0:3]), int(offset[0] + offset[3:5])
        self.utc_offset = f"{'+' if hours >= 0 else ''}{hours}:{minutes:02d}"

        print(f"HoraCalculator initialized for {latitude}, {longitude} ({timezone_str})")

    def calculate_sunrise_sunset(self, date: datetime) -> Dict[str, datetime]:
        """
        Calculate sunrise and sunset times for a given date.

        Args:
            date: Date to calculate sunrise/sunset for

        Returns:
            Dictionary with 'sunrise' and 'sunset' as datetime objects
        """
        try:
            # Create observer at the specified location
            observer = ephem.Observer()
            observer.lat = str(self.latitude)
            observer.lon = str(self.longitude)
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
                # For these special cases, use nautical twilight as approximation
                observer.horizon = '-12'  # Nautical twilight
                sunrise_utc = observer.next_rising(sun, use_center=True).datetime()
                sunset_utc = observer.next_setting(sun, use_center=True).datetime()

            # Convert UTC times to the local timezone
            sunrise = pytz.utc.localize(sunrise_utc).astimezone(self.timezone)
            sunset = pytz.utc.localize(sunset_utc).astimezone(self.timezone)

            # Get next day's sunrise
            observer.date = (date + timedelta(days=1)).strftime('%Y/%m/%d')
            next_sunrise_utc = observer.next_rising(sun).datetime()
            next_sunrise = pytz.utc.localize(next_sunrise_utc).astimezone(self.timezone)

            return {
                'sunrise': sunrise,
                'sunset': sunset,
                'next_sunrise': next_sunrise
            }

        except Exception as e:
            print(f"Error calculating sunrise/sunset: {str(e)}")
            # Fallback to approximate times if calculation fails
            base_date = date.replace(hour=6, minute=0, second=0, microsecond=0)
            return {
                'sunrise': self.timezone.localize(base_date),
                'sunset': self.timezone.localize(base_date.replace(hour=18)),
                'next_sunrise': self.timezone.localize(base_date + timedelta(days=1))
            }

    def get_hora_rulers_for_day(self, day_of_week: str) -> List[str]:
        """
        Get the correct sequence of hora rulers for a day.

        Args:
            day_of_week: Day of the week (e.g., 'Sunday')

        Returns:
            List of planetary rulers in sequence
        """
        # Hora rulers for each day, starting at sunrise
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

    def calculate_horas(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """
        Calculate all horas between start and end time.

        Args:
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            List of dictionaries with hora information
        """
        # Ensure datetimes are timezone aware
        if start_dt.tzinfo is None:
            start_dt = self.timezone.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.timezone.localize(end_dt)

        print(f"Calculating horas from {start_dt} to {end_dt}")

        # Get sunrise data for the requested date
        sun_data = self.calculate_sunrise_sunset(start_dt.date())

        sunrise = sun_data['sunrise']
        sunset = sun_data['sunset']
        next_sunrise = sun_data['next_sunrise']

        # Calculate Hora durations
        day_duration = (sunset - sunrise).total_seconds()
        night_duration = (next_sunrise - sunset).total_seconds()

        day_hora_duration = day_duration / 12
        night_hora_duration = night_duration / 12

        print(f"Sunrise: {sunrise}, Sunset: {sunset}, Next sunrise: {next_sunrise}")
        print(f"Day hora: {day_hora_duration / 3600:.2f} hours, Night hora: {night_hora_duration / 3600:.2f} hours")

        # Get day of week based on the sunrise time
        day_of_week = sunrise.strftime("%A")
        hora_rulers = self.get_hora_rulers_for_day(day_of_week)

        if not hora_rulers:
            print(f"Warning: No hora rulers found for {day_of_week}")
            hora_rulers = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

        # Calculate hora timings
        horas = []
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
                # Select the appropriate ruler for this hora
                ruler_index = hora_index % 7
                ruler = hora_rulers[ruler_index]

                horas.append({
                    "start_time": max(current_time, start_dt),
                    "end_time": min(hora_end, end_dt),
                    "planet": ruler,
                    "day_night": "Day" if is_day_hora else "Night"
                })

            current_time = hora_end
            hora_index += 1

        print(f"Found {len(horas)} horas in the specified time range")
        return horas

    def get_current_hora(self, dt: datetime = None) -> Dict:
        """
        Get the hora data for a specific time.

        Args:
            dt: Datetime to get hora for (defaults to current time)

        Returns:
            Dictionary with hora information
        """
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)

        # Calculate all horas for the day
        day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        all_horas = self.calculate_horas(day_start, day_end)

        # Find the hora that contains the specified time
        for hora in all_horas:
            if hora["start_time"] <= dt < hora["end_time"]:
                return hora

        # Fallback if no matching hora found
        return {
            "start_time": dt,
            "end_time": dt + timedelta(hours=1),
            "planet": "Unknown",
            "day_night": "Unknown"
        }

    def get_hora_transitions(self, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
        """
        Get all hora transitions in a specific time range as a DataFrame.

        Args:
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            DataFrame with hora transition data
        """
        horas = self.calculate_horas(start_dt, end_dt)

        # Format for DataFrame
        formatted_horas = []
        for hora in horas:
            formatted_horas.append({
                "Start Time": hora["start_time"].strftime("%H:%M"),
                "End Time": hora["end_time"].strftime("%H:%M"),
                "Planet": hora["planet"],
                "Day/Night": hora["day_night"]
            })

        return pd.DataFrame(formatted_horas)