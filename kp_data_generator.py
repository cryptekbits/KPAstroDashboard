from datetime import datetime, timedelta
import pytz
import pandas as pd
from kpTools.VedicAstro import VedicHoroscopeData
from kpTools.utils import dms_to_decdeg


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
            "Neptune": "Neptune",
            "Pluto": "Pluto"
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

    def get_planet_aspects(self, chart, planet_name):
        """
        Get the major aspects for a specific planet.

        Parameters:
        -----------
        chart : Chart
            The flatlib chart object
        planet_name : str
            The name of the planet to get aspects for

        Returns:
        --------
        list
            A list of aspect strings (only major aspects: 0, 60, 90, 120, 180)
        """
        # Get all aspects from the chart
        aspects_dict = self.create_chart_data(datetime.now(self.tz)).get_planetary_aspects(chart)

        # Major aspects to track (degrees)
        major_aspects = {
            "Conjunction": 0,  # 0 degrees
            "Sextile": 60,  # 60 degrees
            "Square": 90,  # 90 degrees
            "Trine": 120,  # 120 degrees
            "Opposition": 180  # 180 degrees
        }

        # Filter aspects for this planet (only major aspects)
        planet_aspects = []
        for aspect in aspects_dict:
            if aspect["P1"] == planet_name or aspect["P2"] == planet_name:
                if aspect["AspectType"] in major_aspects:
                    other_planet = aspect["P2"] if aspect["P1"] == planet_name else aspect["P1"]
                    planet_aspects.append(f"{aspect['AspectType']} with {other_planet} ({aspect['AspectOrb']}°)")

        return planet_aspects

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
                        "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune"]

        # Create a map for quick lookup
        planet_map = {}
        for planet in planets_data:
            if planet.Object in self.planet_mapping:
                planet_map[self.planet_mapping[planet.Object]] = planet

        # Process planets in specific order
        for planet_name in planet_order:
            if planet_name not in planet_map:
                continue

            planet = planet_map[planet_name]
            obj_name = planet.Object

            # Format position in degrees, minutes, seconds format
            lon_deg = int(planet.LonDecDeg)
            lon_min = int((planet.LonDecDeg - lon_deg) * 60)
            lon_sec = int(((planet.LonDecDeg - lon_deg) * 60 - lon_min) * 60)

            # Format as "14 Aqu 07' 51''"
            sign_abbrev = planet.Rasi[:3]  # First 3 letters of sign
            position_str = f"{lon_deg} {sign_abbrev} {lon_min:02d}' {lon_sec:02d}''"

            # Get aspects for this planet
            aspects = self.get_planet_aspects(chart, obj_name)
            aspects_str = "; ".join(aspects) if aspects else "None"

            # Calculate KP pointer with SubSubLord
            kp_pointer = f"{planet.RasiLord}-{planet.NakshatraLord}-{planet.SubLord}-{planet.SubSubLord}"

            planet_rows.append({
                "Planet": planet_name,
                "Position": position_str,
                "Sign": planet.Rasi,
                "House": planet.HouseNr if planet.HouseNr else "-",
                "Nakshatra": planet.Nakshatra,
                "KP Pointer": kp_pointer,
                "Aspects": aspects_str
            })

        return pd.DataFrame(planet_rows)

    def get_hora_timings(self, start_dt, end_dt):
        """
        Get Hora timings for the given date range.

        Parameters:
        -----------
        start_dt : datetime
            The start datetime
        end_dt : datetime
            The end datetime

        Returns:
        --------
        pandas.DataFrame
            DataFrame with hora timings
        """
        hora_rulers = {
            "Sunday": ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"],
            "Monday": ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"],
            "Tuesday": ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"],
            "Wednesday": ["Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"],
            "Thursday": ["Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn"],
            "Friday": ["Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun"],
            "Saturday": ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        }

        # Ensure datetimes are timezone aware
        if start_dt.tzinfo is None:
            start_dt = self.tz.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = self.tz.localize(end_dt)

        day_of_week = start_dt.strftime("%A")
        current_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)

        hora_rows = []
        hora_index = 0

        while current_dt <= end_dt:
            # Calculate the hour index (0-23)
            hour_of_day = current_dt.hour
            hora_ruler_index = hour_of_day % 7
            hora_ruler = hora_rulers[day_of_week][hora_ruler_index]

            hora_end = (current_dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

            # Only include horas that overlap with our time range
            if hora_end > start_dt and current_dt < end_dt:
                hora_rows.append({
                    "Start Time": max(current_dt, start_dt).strftime("%H:%M"),
                    "End Time": min(hora_end, end_dt).strftime("%H:%M"),
                    "Planet": hora_ruler
                })

            current_dt = hora_end
            hora_index = (hora_index + 1) % 7

            # If we've moved to a new day, update the day of week
            if current_dt.day != start_dt.day:
                day_of_week = current_dt.strftime("%A")

        return pd.DataFrame(hora_rows)

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
        internal_planet_name = self.reverse_planet_mapping.get(planet_name, planet_name)

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
            if planet.Object == internal_planet_name:
                last_planet_data = planet
                break

        if last_planet_data is None:
            return pd.DataFrame()  # Planet not found

        # Initialize tracking
        planet_start_time = current_time
        last_aspects = self.get_planet_aspects(chart, internal_planet_name)

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
                if planet.Object == internal_planet_name:
                    current_planet_data = planet
                    break

            if current_planet_data is None:
                continue  # Skip if planet not found

            # Get current aspects
            current_aspects = self.get_planet_aspects(chart, internal_planet_name)

            # Check if any parameter changed
            position_changed = (
                    last_planet_data.Rasi != current_planet_data.Rasi or
                    last_planet_data.Nakshatra != current_planet_data.Nakshatra or
                    last_planet_data.RasiLord != current_planet_data.RasiLord or
                    last_planet_data.NakshatraLord != current_planet_data.NakshatraLord or
                    last_planet_data.SubLord != current_planet_data.SubLord or
                    last_planet_data.SubSubLord != current_planet_data.SubSubLord or
                    last_aspects != current_aspects
            )

            if position_changed:
                # Add the last period that just ended
                aspects_str = "; ".join(last_aspects) if last_aspects else "None"

                transitions.append({
                    "Start Time": planet_start_time.strftime("%H:%M"),
                    "End Time": current_time.strftime("%H:%M"),
                    "Position": f"{last_planet_data.LonDecDeg:.2f}°",
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
            last_aspects = current_aspects

        # Add final entry if we haven't reached a transition by end_time
        if planet_start_time < end_dt:
            aspects_str = "; ".join(last_aspects) if last_aspects else "None"

            transitions.append({
                "Start Time": planet_start_time.strftime("%H:%M"),
                "End Time": end_dt.strftime("%H:%M"),
                "Position": f"{last_planet_data.LonDecDeg:.2f}°",
                "Rashi": last_planet_data.Rasi,
                "Nakshatra": last_planet_data.Nakshatra,
                "Rashi Lord": last_planet_data.RasiLord,
                "Nakshatra Lord": last_planet_data.NakshatraLord,
                "Sub Lord": last_planet_data.SubLord,
                "Sub-Sub Lord": last_planet_data.SubSubLord,
                "Aspects": aspects_str
            })

        return pd.DataFrame(transitions)