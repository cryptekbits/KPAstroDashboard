"""
Specialized formatter for transit data in the KP Astrology system.
Provides formatting functionality for transit-specific Excel sheets.
"""
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime


class TransitFormatter:
    """Format transit data for display and export."""

    def __init__(self):
        """Initialize the transit formatter."""
        # Planet display names for formatting
        self.planet_names = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mercury",
            "Venus": "Venus",
            "Mars": "Mars",
            "Jupiter": "Jupiter",
            "Saturn": "Saturn",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
            "Uranus": "Uranus",
            "Neptune": "Neptune",
            "Pluto": "Pluto",
            "Ascendant": "Ascendant"
        }

        # Planet colors for highlighting
        self.planet_colors = {
            "Sun": "#FFD700",  # Gold
            "Moon": "#C0C0C0",  # Silver
            "Mercury": "#C0D9D9",  # Light Blue
            "Venus": "#FFCCFF",  # Light Pink
            "Mars": "#FF6B6B",  # Red
            "Jupiter": "#FFFF99",  # Yellow
            "Saturn": "#CCCCCC",  # Grey
            "Rahu": "#9966CC",  # Purple
            "Ketu": "#CC9966",  # Brown
            "Uranus": "#99CCFF",  # Light Blue
            "Neptune": "#99FFCC",  # Aqua
            "Pluto": "#666666",  # Dark Grey
            "Ascendant": "#FFFFFF"  # White
        }

    def format_transit_data(self, transit_data: pd.DataFrame, planet_name: str) -> pd.DataFrame:
        """
        Format transit data for a specific planet.

        Args:
            transit_data: Original transit DataFrame
            planet_name: Name of the planet

        Returns:
            Formatted DataFrame
        """
        print(f"Formatting transit data for {planet_name}")

        # Create a copy to avoid modifying original
        formatted_df = transit_data.copy()

        # Add planet name column if not present
        if "Planet" not in formatted_df.columns:
            formatted_df["Planet"] = planet_name

        # Ensure proper column order
        preferred_columns = [
            "Start Time", "End Time", "Planet", "Position", "Rashi",
            "Nakshatra", "Rashi Lord", "Nakshatra Lord", "Sub Lord",
            "Sub-Sub Lord", "Aspects"
        ]

        # Keep only columns that exist in the DataFrame
        column_order = [col for col in preferred_columns if col in formatted_df.columns]

        # Add any remaining columns
        for col in formatted_df.columns:
            if col not in column_order:
                column_order.append(col)

        formatted_df = formatted_df[column_order]

        # Format time columns
        try:
            # Convert time strings to proper format if needed
            if "Start Time" in formatted_df.columns and isinstance(formatted_df["Start Time"].iloc[0], str):
                formatted_df["Start Time"] = formatted_df["Start Time"].apply(
                    lambda x: datetime.strptime(x, "%H:%M").strftime("%H:%M") if ":" in x else x
                )

            if "End Time" in formatted_df.columns and isinstance(formatted_df["End Time"].iloc[0], str):
                formatted_df["End Time"] = formatted_df["End Time"].apply(
                    lambda x: datetime.strptime(x, "%H:%M").strftime("%H:%M") if ":" in x else x
                )
        except Exception as e:
            print(f"Error formatting time columns: {str(e)}")

        return formatted_df

    def combine_transit_data(self, transits_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Combine transit data for multiple planets into a single DataFrame.

        Args:
            transits_dict: Dictionary mapping planet names to their transit DataFrames

        Returns:
            Combined DataFrame
        """
        print("Combining transit data for multiple planets")

        # List to hold formatted DataFrames
        formatted_dfs = []

        # Process each planet's data
        for planet_name, df in transits_dict.items():
            if df is not None and not df.empty:
                # Format the DataFrame
                formatted_df = self.format_transit_data(df, planet_name)
                formatted_dfs.append(formatted_df)

        # Combine all DataFrames
        if formatted_dfs:
            combined_df = pd.concat(formatted_dfs, ignore_index=True)

            # Sort by start time
            if "Start Time" in combined_df.columns:
                combined_df = combined_df.sort_values("Start Time")

            return combined_df
        else:
            # Return empty DataFrame with appropriate columns
            return pd.DataFrame(columns=[
                "Start Time", "End Time", "Planet", "Position", "Rashi",
                "Nakshatra", "Rashi Lord", "Nakshatra Lord", "Sub Lord",
                "Sub-Sub Lord", "Aspects"
            ])

    def extract_current_transits(self, transits_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Extract currently active transits from transit data.

        Args:
            transits_dict: Dictionary mapping planet names to their transit DataFrames

        Returns:
            DataFrame with currently active transits
        """
        print("Extracting currently active transits")

        # Current time
        now = datetime.now().strftime("%H:%M")

        # List to hold active transits
        active_transits = []

        # Check each planet's data
        for planet_name, df in transits_dict.items():
            if df is None or df.empty:
                continue

            # Find active transit for this planet
            for i, row in df.iterrows():
                start_time = row.get("Start Time", "")
                end_time = row.get("End Time", "")

                if isinstance(start_time, str) and isinstance(end_time, str):
                    if start_time <= now <= end_time:
                        # This is the active transit for this planet
                        transit_row = row.to_dict()
                        transit_row["Planet"] = planet_name
                        active_transits.append(transit_row)
                        break

        # Create DataFrame from active transits
        if active_transits:
            return pd.DataFrame(active_transits)
        else:
            # Return empty DataFrame with appropriate columns
            return pd.DataFrame(columns=[
                "Start Time", "End Time", "Planet", "Position", "Rashi",
                "Nakshatra", "Rashi Lord", "Nakshatra Lord", "Sub Lord",
                "Sub-Sub Lord", "Aspects"
            ])

    def get_aspect_summary(self, transits_dict: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Extract aspect information from transit data.

        Args:
            transits_dict: Dictionary mapping planet names to their transit DataFrames

        Returns:
            List of aspect strings
        """
        print("Extracting aspect information from transit data")

        # List to hold all aspects
        all_aspects = []

        # Collect aspects from all transit data
        for planet_name, df in transits_dict.items():
            if df is None or df.empty:
                continue

            if "Aspects" in df.columns:
                for aspects_str in df["Aspects"]:
                    if aspects_str and aspects_str != "None" and aspects_str not in all_aspects:
                        # Split multiple aspects if needed
                        if ";" in aspects_str:
                            aspects = [aspect.strip() for aspect in aspects_str.split(";")]
                            all_aspects.extend(aspects)
                        else:
                            all_aspects.append(aspects_str)

        # Remove duplicates and sort
        unique_aspects = sorted(list(set(all_aspects)))

        return unique_aspects

    def format_transit_summary(self, transits_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create a summary of all transits.

        Args:
            transits_dict: Dictionary mapping planet names to their transit DataFrames

        Returns:
            DataFrame with transit summary
        """
        print("Creating transit summary")

        # List to store summary data
        summary_data = []

        # Process each planet
        for planet_name, df in transits_dict.items():
            if df is None or df.empty:
                continue

            # Count transitions
            transitions_count = len(df)

            # Check for retrograde
            retrograde = any("R" in str(planet_name) for _, row in df.iterrows())

            # Get current position
            current_position = None
            current_sign = None
            current_nakshatra = None

            now = datetime.now().strftime("%H:%M")
            for i, row in df.iterrows():
                start_time = row.get("Start Time", "")
                end_time = row.get("End Time", "")

                if isinstance(start_time, str) and isinstance(end_time, str):
                    if start_time <= now <= end_time:
                        current_position = row.get("Position", "")
                        current_sign = row.get("Rashi", "")
                        current_nakshatra = row.get("Nakshatra", "")
                        break

            # Add row to summary
            summary_data.append({
                "Planet": planet_name,
                "Transitions": transitions_count,
                "Retrograde": "Yes" if retrograde else "No",
                "Current Position": current_position,
                "Current Sign": current_sign,
                "Current Nakshatra": current_nakshatra
            })

        # Create DataFrame
        return pd.DataFrame(summary_data)