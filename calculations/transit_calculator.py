from datetime import datetime, timedelta
import pytz
import pandas as pd
from .aspect_calculator import AspectCalculator


class TransitCalculator:
    """
    Class for calculating planetary transits and transitions.
    """

    def __init__(self, latitude, longitude, timezone, position_calculator, ayanamsa="Krishnamurti",
                 house_system="Placidus"):
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
        position_calculator : PlanetPositionCalculator
            A position calculator instance to generate chart data
        ayanamsa : str, optional
            The ayanamsa to use (default is "Krishnamurti")
        house_system : str, optional
            The house system to use (default is "Placidus")
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.position_calculator = position_calculator
        self.ayanamsa = ayanamsa
        self.house_system = house_system
        self.tz = pytz.timezone(timezone)

        # Initialize aspect calculator for finding aspects during transits
        self.aspect_calculator = AspectCalculator()

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
        # Create mapping function to handle node aliases
        global internal_planet_name
        if planet_name == "Rahu":
            # We need to check for both possible names
            def planet_match(p):
                return p.Object == "North Node" or p.Object == "Rahu"
        elif planet_name == "Ketu":
            # We need to check for both possible names
            def planet_match(p):
                return p.Object == "South Node" or p.Object == "Ketu"
        elif planet_name == "Ascendant":
            def planet_match(p):
                return p.Object == "Asc"
        else:
            internal_planet_name = self.position_calculator.reverse_planet_mapping.get(planet_name, planet_name)

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
        chart_data = self.position_calculator.create_chart_data(current_time)
        chart = chart_data.generate_chart()

        # Get positions data
        planets_data = chart_data.get_planets_data_from_chart(chart)

        # Find the planet we want
        last_planet_data = None
        for planet in planets_data:
            if planet_match(planet):  # Use our match function
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
            chart_data = self.position_calculator.create_chart_data(current_time)
            chart = chart_data.generate_chart()

            # Get current position
            planets_data = chart_data.get_planets_data_from_chart(chart)

            # Find our planet
            current_planet_data = None
            for planet in planets_data:
                if planet_match(planet):  # Use our match function
                    current_planet_data = planet
                    break

            if current_planet_data is None:
                continue  # Skip if planet not found

            # Get current important events using aspect_calculator
            current_events = self.aspect_calculator.get_important_events(
                last_planets_data, planets_data, chart
            )

            # Filter events relevant to this planet
            if planet_name == "Rahu":
                planet_short_name = "Rahu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ketu":
                planet_short_name = "Ketu"
                relevant_events = [e for e in current_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ascendant":
                planet_short_name = "Asc"
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
                position_str = self.position_calculator.format_position(last_planet_data)

                # Format aspects/events - only show new aspects
                aspects_str = "; ".join(new_aspects) if new_aspects else ""

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
            position_str = self.position_calculator.format_position(last_planet_data)

            # Get final aspects
            final_events = self.aspect_calculator.get_important_events(
                last_planets_data, planets_data, chart
            )

            # Filter events relevant to this planet
            if planet_name == "Rahu":
                planet_short_name = "Rahu"
                relevant_events = [e for e in final_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ketu":
                planet_short_name = "Ketu"
                relevant_events = [e for e in final_events if planet_short_name in e and "entered" not in e]
            elif planet_name == "Ascendant":
                planet_short_name = "Asc"
                relevant_events = [e for e in final_events if planet_short_name in e and "entered" not in e]
            elif internal_planet_name in self.aspect_calculator.planet_short_names:
                planet_short_name = self.aspect_calculator.planet_short_names[internal_planet_name]
                relevant_events = [e for e in final_events if planet_short_name in e and "entered" not in e]
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
