"""
Transit Calculator module for KP Astrology.
Handles calculations for planetary transits and transitions.
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import pandas as pd
import pytz


class TransitCalculator:
    """Calculate planetary transits and transitions."""

    def __init__(self, position_calculator, aspect_calculator=None):
        """
        Initialize the transit calculator.

        Args:
            position_calculator: Instance of PositionCalculator
            aspect_calculator: Optional instance of AspectCalculator
        """
        self.position_calculator = position_calculator
        self.aspect_calculator = aspect_calculator

        # Track previous data for transitions
        self.previous_data = {}

        # Planet name mappings for display
        self.planet_mapping = {
            "Ascendant": "Asc",
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mer",
            "Venus": "Ven",
            "Mars": "Mars",
            "Jupiter": "Jup",
            "Saturn": "Sat",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
            "Uranus": "Ura",
            "Neptune": "Nep",
            "Pluto": "Plu"
        }

        print(f"TransitCalculator initialized")

    def _position_changed(self, pos1: Dict, pos2: Dict) -> bool:
        """
        Check if position parameters changed between two snapshots.

        Args:
            pos1: First position data
            pos2: Second position data

        Returns:
            True if any relevant parameter changed
        """
        if pos1 is None or pos2 is None:
            return True

        # Check for changes in sign, nakshatra, lords
        return (
                pos1["Sign"] != pos2["Sign"] or
                pos1["Nakshatra"] != pos2["Nakshatra"] or
                pos1["Rashi Lord"] != pos2["Rashi Lord"] or
                pos1["Nakshatra Lord"] != pos2["Nakshatra Lord"] or
                pos1["Sub Lord"] != pos2["Sub Lord"] or
                pos1["Sub-Sub Lord"] != pos2["Sub-Sub Lord"]
        )

    def _retrograde_changed(self, pos1: Dict, pos2: Dict) -> bool:
        """
        Check if retrograde status changed.

        Args:
            pos1: First position data
            pos2: Second position data

        Returns:
            True if retrograde status changed
        """
        if pos1 is None or pos2 is None:
            return False

        # Check if "R" marker is present
        retro1 = "R" in pos1["Planet"]
        retro2 = "R" in pos2["Planet"]

        return retro1 != retro2

    def get_planet_transitions(self, planet_name: str, start_dt: datetime, end_dt: datetime,
                               interval_minutes: int = 1, include_aspects: bool = True) -> pd.DataFrame:
        """
        Track transitions in a planet's position parameters over time.

        Args:
            planet_name: Name of the planet to track
            start_dt: Start datetime
            end_dt: End datetime
            interval_minutes: How often to check for changes (in minutes)
            include_aspects: Whether to include aspect information

        Returns:
            DataFrame with transition data
        """
        print(f"Calculating transitions for {planet_name} from {start_dt} to {end_dt}")

        # Ensure datetimes are timezone aware
        timezone = self.position_calculator.timezone
        if start_dt.tzinfo is None:
            start_dt = timezone.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = timezone.localize(end_dt)

        # Convert to the calculator's timezone
        start_dt = start_dt.astimezone(timezone)
        end_dt = end_dt.astimezone(timezone)

        # Initialize data collection
        transitions = []
        recorded_aspects = set()

        # Initialize with starting time
        current_time = start_dt
        last_position = self.position_calculator.get_planet_position(planet_name, current_time)

        if not last_position:
            print(f"Warning: Could not find position data for {planet_name}")
            return pd.DataFrame()

        planet_start_time = current_time
        all_planets_data = self.position_calculator.get_planet_positions(current_time)

        # Get chart and planets data for aspect calculation
        if include_aspects and self.aspect_calculator:
            chart_data, planets_data = self.position_calculator.get_chart_and_planets_data(current_time)
            last_planets_data = planets_data

        # Track changes
        time_steps = 0
        total_steps = (end_dt - start_dt).total_seconds() / (interval_minutes * 60)

        while current_time <= end_dt:
            # Progress update every 10% of steps
            time_steps += 1
            if time_steps % max(1, int(total_steps / 10)) == 0:
                progress = min(100, int((time_steps / total_steps) * 100))
                print(f"Transit calculation progress: {progress}% ({time_steps}/{int(total_steps)} steps)")

            # Move to next time step
            current_time += timedelta(minutes=interval_minutes)

            # Get current position
            current_position = self.position_calculator.get_planet_position(planet_name, current_time)

            if not current_position:
                continue

            # Get all planets data for aspects
            if include_aspects and self.aspect_calculator:
                all_planets_data = self.position_calculator.get_planet_positions(current_time)
                chart_data, planets_data = self.position_calculator.get_chart_and_planets_data(current_time)

                # Get current aspects
                current_aspects = []
                if self.aspect_calculator:
                    # Get important events using aspect_calculator
                    events = self.aspect_calculator.get_important_events(
                        last_planets_data, planets_data, chart_data
                    )

                    # Filter events relevant to this planet
                    planet_short_name = self.planet_mapping.get(planet_name, planet_name)
                    relevant_events = [e for e in events if planet_short_name in e]

                    # Filter out events we've already recorded
                    current_aspects = [aspect for aspect in relevant_events if aspect not in recorded_aspects]

                    # Add new aspects to the recorded set
                    for aspect in current_aspects:
                        recorded_aspects.add(aspect)

            # Check if any parameter changed
            position_changed = self._position_changed(last_position, current_position)
            retrograde_changed = self._retrograde_changed(last_position, current_position)

            # If position changed or we have new aspects
            if position_changed or retrograde_changed or (include_aspects and current_aspects):
                # Capture this transition
                transitions.append({
                    "Start Time": planet_start_time.strftime("%H:%M"),
                    "End Time": current_time.strftime("%H:%M"),
                    "Position": last_position["Position"],
                    "Rashi": last_position["Sign"],
                    "Nakshatra": last_position["Nakshatra"],
                    "Rashi Lord": last_position["Rashi Lord"],
                    "Nakshatra Lord": last_position["Nakshatra Lord"],
                    "Sub Lord": last_position["Sub Lord"],
                    "Sub-Sub Lord": last_position["Sub-Sub Lord"],
                    "Aspects": "; ".join(current_aspects) if current_aspects else ""
                })

                # Reset start time for new period
                planet_start_time = current_time

                # Record the change
                if position_changed:
                    change_type = "Position"
                elif retrograde_changed:
                    retro_status = "R" in current_position["Planet"]
                    change_type = f"Retrograde {'started' if retro_status else 'ended'}"
                else:
                    change_type = "Aspects"

                print(f"{planet_name} {change_type} change at {current_time.strftime('%H:%M')}")

            # Update last position
            last_position = current_position
            if include_aspects and self.aspect_calculator:
                last_planets_data = planets_data

        # Add final entry if we haven't reached a transition by end_time
        if planet_start_time < end_dt:
            transitions.append({
                "Start Time": planet_start_time.strftime("%H:%M"),
                "End Time": end_dt.strftime("%H:%M"),
                "Position": last_position["Position"],
                "Rashi": last_position["Sign"],
                "Nakshatra": last_position["Nakshatra"],
                "Rashi Lord": last_position["Rashi Lord"],
                "Nakshatra Lord": last_position["Nakshatra Lord"],
                "Sub Lord": last_position["Sub Lord"],
                "Sub-Sub Lord": last_position["Sub-Sub Lord"],
                "Aspects": ""
            })

        print(f"Found {len(transitions)} transitions for {planet_name}")
        return pd.DataFrame(transitions)

    def get_all_transits(self, planets: List[str], start_dt: datetime, end_dt: datetime,
                         interval_minutes: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Get transit data for multiple planets.

        Args:
            planets: List of planet names to include
            start_dt: Start datetime
            end_dt: End datetime
            interval_minutes: How often to check for changes (in minutes)

        Returns:
            Dictionary mapping planet names to their transit DataFrames
        """
        results = {}

        for planet in planets:
            print(f"Processing transits for {planet}...")
            planet_transits = self.get_planet_transitions(
                planet_name=planet,
                start_dt=start_dt,
                end_dt=end_dt,
                interval_minutes=interval_minutes
            )

            results[planet] = planet_transits

        return results

    def get_all_transits_combined(self, planets: List[str], start_dt: datetime, end_dt: datetime,
                                  interval_minutes: int = 5) -> pd.DataFrame:
        """
        Get combined transit data for multiple planets.

        Args:
            planets: List of planet names to include
            start_dt: Start datetime
            end_dt: End datetime
            interval_minutes: How often to check for changes (in minutes)

        Returns:
            DataFrame with all transit data combined
        """
        all_transits = []

        for planet in planets:
            planet_transits = self.get_planet_transitions(
                planet_name=planet,
                start_dt=start_dt,
                end_dt=end_dt,
                interval_minutes=interval_minutes
            )

            # Add planet name to each row
            planet_transits["Planet"] = planet

            all_transits.append(planet_transits)

        # Combine all transits
        if all_transits:
            combined_df = pd.concat(all_transits)
            # Sort by start time
            combined_df = combined_df.sort_values("Start Time")
            return combined_df
        else:
            return pd.DataFrame()

    def get_sign_changes(self, start_dt: datetime, end_dt: datetime,
                         interval_minutes: int = 10) -> pd.DataFrame:
        """
        Get all sign changes for all planets in the specified timeframe.

        Args:
            start_dt: Start datetime
            end_dt: End datetime
            interval_minutes: How often to check for changes (in minutes)

        Returns:
            DataFrame with sign change data
        """
        sign_changes = []
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]

        current_time = start_dt

        # Get initial positions
        last_positions = {}
        for planet in planets:
            last_positions[planet] = self.position_calculator.get_planet_position(planet, current_time)

        while current_time <= end_dt:
            # Move to next time step
            current_time += timedelta(minutes=interval_minutes)

            # Check each planet
            for planet in planets:
                current_position = self.position_calculator.get_planet_position(planet, current_time)

                if not current_position or not last_positions.get(planet):
                    continue

                # Check if sign changed
                if current_position["Sign"] != last_positions[planet]["Sign"]:
                    sign_changes.append({
                        "DateTime": current_time,
                        "Planet": planet,
                        "From Sign": last_positions[planet]["Sign"],
                        "To Sign": current_position["Sign"],
                        "Position": current_position["Position"]
                    })

                    print(
                        f"{planet} changed sign from {last_positions[planet]['Sign']} to {current_position['Sign']} at {current_time}")

                # Update last position
                last_positions[planet] = current_position

        # Create DataFrame
        if sign_changes:
            df = pd.DataFrame(sign_changes)
            df["DateTime"] = df["DateTime"].dt.strftime("%Y-%m-%d %H:%M")
            return df
        else:
            return pd.DataFrame(columns=["DateTime", "Planet", "From Sign", "To Sign", "Position"])

    def get_nakshatra_changes(self, start_dt: datetime, end_dt: datetime,
                              interval_minutes: int = 5) -> pd.DataFrame:
        """
        Get all nakshatra changes for all planets in the specified timeframe.

        Args:
            start_dt: Start datetime
            end_dt: End datetime
            interval_minutes: How often to check for changes (in minutes)

        Returns:
            DataFrame with nakshatra change data
        """
        nakshatra_changes = []
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]

        current_time = start_dt

        # Get initial positions
        last_positions = {}
        for planet in planets:
            last_positions[planet] = self.position_calculator.get_planet_position(planet, current_time)

        while current_time <= end_dt:
            # Move to next time step
            current_time += timedelta(minutes=interval_minutes)

            # Check each planet
            for planet in planets:
                current_position = self.position_calculator.get_planet_position(planet, current_time)

                if not current_position or not last_positions.get(planet):
                    continue

                # Check if nakshatra changed
                if current_position["Nakshatra"] != last_positions[planet]["Nakshatra"]:
                    nakshatra_changes.append({
                        "DateTime": current_time,
                        "Planet": planet,
                        "From Nakshatra": last_positions[planet]["Nakshatra"],
                        "To Nakshatra": current_position["Nakshatra"],
                        "Sign": current_position["Sign"],
                        "Position": current_position["Position"]
                    })

                    print(
                        f"{planet} changed nakshatra from {last_positions[planet]['Nakshatra']} to {current_position['Nakshatra']} at {current_time}")

                # Update last position
                last_positions[planet] = current_position

        # Create DataFrame
        if nakshatra_changes:
            df = pd.DataFrame(nakshatra_changes)
            df["DateTime"] = df["DateTime"].dt.strftime("%Y-%m-%d %H:%M")
            return df
        else:
            return pd.DataFrame(columns=["DateTime", "Planet", "From Nakshatra", "To Nakshatra", "Sign", "Position"])