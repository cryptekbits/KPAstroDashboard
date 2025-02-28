"""
Yoga Calculator module for detecting and tracking yogas in KP Astrology.
"""
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import pandas as pd
from .yoga_base import Yoga, YogaType, YogaResult, YogaRegistry


class YogaCalculator:
    """Calculate and track yogas over time."""

    def __init__(self, use_all_yogas=True, selected_yogas=None):
        """
        Initialize the yoga calculator.

        Args:
            use_all_yogas: Whether to use all registered yogas
            selected_yogas: List of specific yoga names to use (if use_all_yogas is False)
        """
        self.yogas = []

        if use_all_yogas:
            # Load all registered yogas
            self.yogas = YogaRegistry.get_all_yogas()
        elif selected_yogas:
            # Load only selected yogas
            for yoga_name in selected_yogas:
                yoga = YogaRegistry.get_yoga_by_name(yoga_name)
                if yoga:
                    self.yogas.append(yoga)

        # Dictionary to track active yogas
        self.active_yogas: Dict[str, YogaResult] = {}

        # Set to track yoga history (all yogas detected in current calculation period)
        self.yoga_history: Set[str] = set()

        print(f"YogaCalculator initialized with {len(self.yogas)} yogas")

    def check_yogas(self, chart_data: Dict, planets_data: List, timestamp: datetime) -> List[YogaResult]:
        """
        Check for all yogas in a chart.

        Args:
            chart_data: Chart data
            planets_data: Planet data
            timestamp: Current timestamp

        Returns:
            List of active yoga results
        """
        active_yoga_results = []
        currently_active_yogas = set()

        # Check each yoga
        for yoga in self.yogas:
            yoga_name = yoga.name
            is_active = yoga.check_yoga(chart_data, planets_data)

            if is_active:
                currently_active_yogas.add(yoga_name)
                self.yoga_history.add(yoga_name)

                # If yoga was not active before, create new result
                if yoga_name not in self.active_yogas:
                    participating_planets = yoga.get_participating_planets(chart_data, planets_data)
                    strength = yoga.get_yoga_strength(chart_data, planets_data)

                    yoga_result = YogaResult(
                        yoga=yoga,
                        is_active=True,
                        start_time=timestamp,
                        participating_planets=participating_planets,
                        strength=strength
                    )

                    self.active_yogas[yoga_name] = yoga_result

                active_yoga_results.append(self.active_yogas[yoga_name])

        # Check for yogas that were active but are no longer active
        for yoga_name in list(self.active_yogas.keys()):
            if yoga_name not in currently_active_yogas:
                # Yoga ended
                yoga_result = self.active_yogas[yoga_name]
                yoga_result.end(timestamp)
                yoga_result.is_active = False

                # Remove from active yogas
                del self.active_yogas[yoga_name]

        return active_yoga_results

    def calculate_yogas_for_timeframe(self,
                                      chart_generator,
                                      start_time: datetime,
                                      end_time: datetime,
                                      interval_minutes: int = 10) -> List[YogaResult]:
        """
        Calculate yogas for a specified timeframe.

        Args:
            chart_generator: Function to generate chart for a given timestamp
            start_time: Start of timeframe
            end_time: End of timeframe
            interval_minutes: How often to check for yogas (in minutes)

        Returns:
            List of yoga results for the entire timeframe
        """
        print(f"Calculating yogas from {start_time} to {end_time} at {interval_minutes}-minute intervals")

        # Reset tracker variables
        self.active_yogas = {}
        self.yoga_history = set()
        completed_yoga_results = []

        # Process each time step
        current_time = start_time
        time_steps = 0

        while current_time <= end_time:
            try:
                # Generate chart data for current time
                chart_data, planets_data = chart_generator(current_time)

                # Check for yogas
                active_yogas = self.check_yogas(chart_data, planets_data, current_time)

                # Move to next time step
                current_time += timedelta(minutes=interval_minutes)
                time_steps += 1

                # Progress update every 10% of steps
                total_steps = (end_time - start_time).total_seconds() / (interval_minutes * 60)
                if time_steps % max(1, int(total_steps / 10)) == 0:
                    progress = min(100, int((time_steps / total_steps) * 100))
                    print(f"Yoga calculation progress: {progress}% ({time_steps}/{int(total_steps)} steps)")

            except Exception as e:
                print(f"Error calculating yogas at {current_time}: {str(e)}")
                current_time += timedelta(minutes=interval_minutes)

        # Add any yogas that are still active at the end with end_time as their end
        for yoga_name, yoga_result in self.active_yogas.items():
            yoga_result.end(end_time)
            completed_yoga_results.append(yoga_result)

        # Collect completed yoga results
        print(f"Yoga calculation complete. Found {len(completed_yoga_results)} yoga occurrences.")
        return completed_yoga_results

    def convert_results_to_dataframe(self, yoga_results: List[YogaResult]) -> pd.DataFrame:
        """
        Convert yoga results to a pandas DataFrame.

        Args:
            yoga_results: List of yoga results

        Returns:
            DataFrame with yoga information
        """
        records = []

        for result in yoga_results:
            # Format duration
            duration = result.get_duration()
            if duration:
                hours = int(duration)
                minutes = int((duration - hours) * 60)
                duration_str = f"{hours}h {minutes}m"
            else:
                duration_str = "Ongoing"

            records.append({
                "Yoga Name": result.yoga.name,
                "Start Time": result.start_time,
                "End Time": result.end_time if result.end_time else "Ongoing",
                "Duration": duration_str,
                "Planets": result.get_planet_details(),
                "Type": result.yoga.yoga_type.value.capitalize(),
                "Strength": f"{int(result.strength * 100)}%",
                "Description": result.yoga.description
            })

        # Create DataFrame and sort by start time
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("Start Time")

        return df

    def get_yoga_counts_by_type(self, yoga_results: List[YogaResult]) -> Dict[str, int]:
        """
        Get counts of yogas by type.

        Args:
            yoga_results: List of yoga results

        Returns:
            Dictionary of yoga type counts
        """
        counts = {
            "Positive": 0,
            "Negative": 0,
            "Neutral": 0
        }

        for result in yoga_results:
            yoga_type = result.yoga.yoga_type.value.capitalize()
            counts[yoga_type] += 1

        return counts

    def get_most_significant_yogas(self, yoga_results: List[YogaResult], top_n=5) -> List[YogaResult]:
        """
        Get the most significant yogas based on duration and strength.

        Args:
            yoga_results: List of yoga results
            top_n: Number of top yogas to return

        Returns:
            List of the most significant yoga results
        """
        # Score each yoga based on duration and strength
        scored_results = []

        for result in yoga_results:
            duration = result.get_duration()
            if duration:
                # Score = duration (hours) * strength (0-1)
                score = duration * result.strength
                scored_results.append((score, result))

        # Sort by score in descending order
        scored_results.sort(reverse=True)

        # Return top N results
        return [result for _, result in scored_results[:top_n]]

    def get_yogas_by_time_period(self, yoga_results: List[YogaResult]) -> Dict[str, List[YogaResult]]:
        """
        Group yogas by time period (morning, afternoon, evening, night).

        Args:
            yoga_results: List of yoga results

        Returns:
            Dictionary with yogas grouped by time period
        """
        periods = {
            "Morning (6 AM - 12 PM)": [],
            "Afternoon (12 PM - 6 PM)": [],
            "Evening (6 PM - 12 AM)": [],
            "Night (12 AM - 6 AM)": []
        }

        for result in yoga_results:
            hour = result.start_time.hour

            if 6 <= hour < 12:
                periods["Morning (6 AM - 12 PM)"].append(result)
            elif 12 <= hour < 18:
                periods["Afternoon (12 PM - 6 PM)"].append(result)
            elif 18 <= hour < 24:
                periods["Evening (6 PM - 12 AM)"].append(result)
            else:
                periods["Night (12 AM - 6 AM)"].append(result)

        return periods