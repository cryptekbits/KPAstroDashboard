from datetime import datetime, timedelta
import pytz
import pandas as pd
from kpTools.VedicAstro import VedicHoroscopeData
from kpTools.utils import dms_to_decdeg
from aspect_calculator import AspectCalculator


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
        """Format planet position consistently as degrees within sign"""
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
        for planet in planets_data:
            # Debug: print the planet Object to see what's coming from flatlib
            # print(f"Planet from flatlib: {planet.Object}")

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
                # Debug: print missing planets
                # print(f"Missing planet: {planet_name}")
                continue

            planet = planet_map[planet_name]
            obj_name = planet.Object

            # Format position in degrees, minutes, seconds format
            lon_deg = int(planet.LonDecDeg)
            lon_min = int((planet.LonDecDeg - lon_deg) * 60)
            lon_sec = int(((planet.LonDecDeg - lon_deg) * 60 - lon_min) * 60)

            # Format as "14 Aqu 07' 51''"
            sign_abbrev = planet.Rasi[:3]  # First 3 letters of sign
            # position_str = f"{lon_deg} {sign_abbrev} {lon_min:02d}' {lon_sec:02d}''"
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
        import ephem
        from datetime import datetime

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
        """
        # Ensure datetimes are timezone aware
        if start_dt.tzinfo is None:
            start_dt = self.tz.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.tz.localize(end_dt)

        # Get sunrise data for the requested date in the correct timezone
        sun_data = self.get_sunrise_with_ephem(start_dt.date(), self.latitude, self.longitude)

        # Convert UTC times to the local timezone
        sunrise = pytz.utc.localize(sun_data['sunrise']).astimezone(self.tz)
        sunset = pytz.utc.localize(sun_data['sunset']).astimezone(self.tz)

        # Get next day's sunrise
        next_day = start_dt.date() + timedelta(days=1)
        next_sun_data = self.get_sunrise_with_ephem(next_day, self.latitude, self.longitude)
        next_sunrise = pytz.utc.localize(next_sun_data['sunrise']).astimezone(self.tz)

        # Calculate Hora durations
        day_duration = (sunset - sunrise).total_seconds()
        night_duration = (next_sunrise - sunset).total_seconds()

        day_hora_duration = day_duration / 12
        night_hora_duration = night_duration / 12

        # Get day of week based on the sunrise time in local timezone
        day_of_week = sunrise.strftime("%A")
        hora_rulers = self._get_hora_rulers_for_day(day_of_week)

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
                hora_rows.append({
                    "Start Time": max(current_time, start_dt).strftime("%H:%M"),
                    "End Time": min(hora_end, end_dt).strftime("%H:%M"),
                    "Planet": hora_rulers[hora_index % 7],
                    "Day/Night": "Day" if is_day_hora else "Night"
                })

            current_time = hora_end
            hora_index += 1

        return pd.DataFrame(hora_rows)

    def _get_hora_rulers_for_day(self, day_of_week):
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
        # Convert display name to internal name
        if planet_name == "Rahu":
            # We need to check for both possible names
            def planet_match(p):
                return p.Object == "North Node" or p.Object == "Rahu"
        elif planet_name == "Ketu":
            # We need to check for both possible names
            def planet_match(p):
                return p.Object == "South Node" or p.Object == "Ketu"
        else:
            internal_planet_name = self.reverse_planet_mapping.get(planet_name, planet_name)

            def planet_match(p):
                return p.Object == internal_planet_name

        # Ensure datetimes are timezone aware
        if start_dt.tzinfo is None:
            start_dt = self.tz.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.tz.localize(end_dt)

        # Initialize data collection
        transitions = []

        # Initialize with starting time
        current_time = start_dt

        # Get initial position
        chart_data = self.create_chart_data(current_time)
        chart = chart_data.generate_chart()

        # Get positions data
        planets_data = chart_data.get_planets_data_from_chart(chart)

        # Find the planet we want
        last_planet_data = None
        for planet in planets_data:
            if planet_match(planet):  # Use our new match function
                last_planet_data = planet
                break

        if last_planet_data is None:
            return pd.DataFrame()  # Planet not found

        # Initialize tracking
        planet_start_time = current_time
        last_planets_data = planets_data  # Store all planets for aspect calculations

        # Keep track of aspects that have been recorded
        recorded_aspects = set()

        # Track changes
        while current_time <= end_dt:
            # Move to next time step
            current_time += timedelta(minutes=check_interval_minutes)

            # Create chart data for current time
            chart_data = self.create_chart_data(current_time)
            chart = chart_data.generate_chart()

            # Get current position
            planets_data = chart_data.get_planets_data_from_chart(chart)

            # Find our planet
            current_planet_data = None
            for planet in planets_data:
                if planet_match(planet):  # Use our new match function
                    current_planet_data = planet
                    break

            if current_planet_data is None:
                continue  # Skip if planet not found

            # Get current important events using aspect_calculator
            current_events = self.aspect_calculator.get_important_events(
                last_planets_data, planets_data, chart
            )

            # Filter events relevant to this planet
            planet_display_name = planet_name
            if planet_name == "Rahu":
                planet_short_name = "Rahu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ketu":
                planet_short_name = "Ketu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif internal_planet_name in self.aspect_calculator.planet_short_names:
                planet_short_name = self.aspect_calculator.planet_short_names[internal_planet_name]
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            else:
                relevant_events = []

            # Filter out aspects that have already been recorded
            new_aspects = [aspect for aspect in relevant_events if aspect not in recorded_aspects]

            # Add new aspects to the recorded set
            for aspect in new_aspects:
                recorded_aspects.add(aspect)

            # Check if any parameter changed
            position_changed = (
                    last_planet_data.Rasi != current_planet_data.Rasi or
                    last_planet_data.Nakshatra != current_planet_data.Nakshatra or
                    last_planet_data.RasiLord != current_planet_data.RasiLord or
                    last_planet_data.NakshatraLord != current_planet_data.NakshatraLord or
                    last_planet_data.SubLord != current_planet_data.SubLord or
                    last_planet_data.SubSubLord != current_planet_data.SubSubLord or
                    new_aspects  # Only consider new aspects as changes
            )

            if position_changed:
                # Format planet name with retrograde if applicable
                display_planet_name = planet_name
                if last_planet_data.isRetroGrade:
                    display_planet_name += " (Ret.)"

                # Format position
                lon_deg = int(last_planet_data.LonDecDeg)
                lon_min = int((last_planet_data.LonDecDeg - lon_deg) * 60)
                lon_sec = int(((last_planet_data.LonDecDeg - lon_deg) * 60 - lon_min) * 60)
                sign_abbrev = last_planet_data.Rasi[:3]
                position_str = f"{lon_deg} {sign_abbrev} {lon_min:02d}' {lon_sec:02d}''"

                # Format aspects/events - only show new aspects
                aspects_str = "; ".join(new_aspects) if new_aspects else "None"

                transitions.append({
                    "Start Time": planet_start_time.strftime("%H:%M"),
                    "End Time": current_time.strftime("%H:%M"),
                    "Position": position_str,
                    "Rashi": last_planet_data.Rasi,
                    "Nakshatra": last_planet_data.Nakshatra,
                    "Rashi Lord": last_planet_data.RasiLord,
                    "Nakshatra Lord": last_planet_data.NakshatraLord,
                    "Sub Lord": last_planet_data.SubLord,
                    "Sub-Sub Lord": last_planet_data.SubSubLord,
                    "Aspects": aspects_str
                })

                # Reset start time for new period
                planet_start_time = current_time

            # Update last position
            last_planet_data = current_planet_data
            last_planets_data = planets_data

        # Add final entry if we haven't reached a transition by end_time
        if planet_start_time < end_dt:
            # Format planet name with retrograde if applicable
            display_planet_name = planet_name
            if last_planet_data.isRetroGrade:
                display_planet_name += " (Ret.)"

            # Format position
            lon_deg = int(last_planet_data.LonDecDeg)
            lon_min = int((last_planet_data.LonDecDeg - lon_deg) * 60)
            lon_sec = int(((last_planet_data.LonDecDeg - lon_deg) * 60 - lon_min) * 60)
            sign_abbrev = last_planet_data.Rasi[:3]
            position_str = f"{lon_deg} {sign_abbrev} {lon_min:02d}' {lon_sec:02d}''"

            # Get final aspects
            final_events = self.aspect_calculator.get_important_events(
                last_planets_data, planets_data, chart
            )

            # Filter events relevant to this planet
            if planet_name == "Rahu":
                planet_short_name = "Rahu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ketu":
                planet_short_name = "Ketu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif internal_planet_name in self.aspect_calculator.planet_short_names:
                planet_short_name = self.aspect_calculator.planet_short_names[internal_planet_name]
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            else:
                relevant_events = []

            # Filter out aspects that have already been recorded
            new_aspects = [aspect for aspect in relevant_events if aspect not in recorded_aspects]

            # Add new aspects to the recorded set
            for aspect in new_aspects:
                recorded_aspects.add(aspect)

            aspects_str = "; ".join(new_aspects) if new_aspects else "None"

            transitions.append({
                "Start Time": planet_start_time.strftime("%H:%M"),
                "End Time": end_dt.strftime("%H:%M"),
                "Position": position_str,
                "Rashi": last_planet_data.Rasi,
                "Nakshatra": last_planet_data.Nakshatra,
                "Rashi Lord": last_planet_data.RasiLord,
                "Nakshatra Lord": last_planet_data.NakshatraLord,
                "Sub Lord": last_planet_data.SubLord,
                "Sub-Sub Lord": last_planet_data.SubSubLord,
                "Aspects": aspects_str
            })

        return pd.DataFrame(transitions)