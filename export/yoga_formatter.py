"""
Specialized formatter for yoga data in the KP Astrology system.
Provides formatting functionality for yoga-specific Excel sheets.
"""
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime


class YogaFormatter:
    """Format yoga data for display and export."""

    def __init__(self):
        """Initialize the yoga formatter."""
        # Define yoga types for categorization
        self.positive_yogas = set([
            "Budha-Aditya Yoga", "Gaja-Kesari Yoga", "Raja Yoga", "Dhana Yoga",
            "Ruchaka Yoga", "Bhadra Yoga", "Hamsa Yoga", "Malavya Yoga", "Sasa Yoga",
            "Amala Yoga", "Chamunda Yoga", "Lakshmi Yoga", "Guru-Mangala Yoga",
            "Guru-Shukra Yoga", "Gajakesari Yoga", "Neech Bhanga Raja Yoga"
        ])

        self.negative_yogas = set([
            "Kala Sarpa Yoga", "Vish Yoga", "Angarak Yoga", "Guru Chandala Yoga",
            "Graha Yuddha", "Kemadruma Yoga", "Daridra Yoga", "Shakat Yoga"
        ])

        self.neutral_yogas = set([
            "Parivartana Yoga", "Shubha-Kartari Yoga", "Chandra-Mangala Yoga",
            "Adhi Yoga", "Mala Yoga", "Gada Yoga", "Sarpa Yoga", "Ubhayachari Yoga",
            "Durdhura Yoga", "Graha Malika Yoga"
        ])

    def categorize_yoga(self, yoga_name: str) -> str:
        """
        Categorize a yoga as positive, negative, or neutral.

        Args:
            yoga_name: Name of the yoga

        Returns:
            'Positive', 'Negative', or 'Neutral'
        """
        # Extract base yoga name without additional details
        base_name = yoga_name
        if "(" in yoga_name:
            base_name = yoga_name.split("(")[0].strip()

        if base_name in self.positive_yogas:
            return "Positive"
        elif base_name in self.negative_yogas:
            return "Negative"
        elif base_name in self.neutral_yogas:
            return "Neutral"
        else:
            # Default to neutral for unknown yogas
            return "Neutral"

    def get_yoga_color(self, yoga_type: str) -> str:
        """
        Get the color code for a yoga type.

        Args:
            yoga_type: 'Positive', 'Negative', or 'Neutral'

        Returns:
            Hex color code
        """
        if yoga_type == "Positive":
            return "#E2EFDA"  # Light green
        elif yoga_type == "Negative":
            return "#FFCCCC"  # Light red
        else:
            return "#FFF2CC"  # Light yellow

    def format_yoga_results(self, yoga_results: List[Dict]) -> pd.DataFrame:
        """
        Format yoga results for display.

        Args:
            yoga_results: List of yoga result dictionaries

        Returns:
            Formatted DataFrame
        """
        # Create DataFrame from results
        df = pd.DataFrame(yoga_results)

        # Ensure required columns exist
        if 'yoga_name' in df.columns and 'Type' not in df.columns:
            df['Type'] = df['yoga_name'].apply(self.categorize_yoga)

        # Format time columns
        time_columns = ['start_time', 'end_time', 'Start Time', 'End Time']
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M')

        # Rename columns for better display
        column_renames = {
            'yoga_name': 'Yoga Name',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'participating_planets': 'Planets',
            'description': 'Description',
            'strength': 'Strength',
            'is_active': 'Active'
        }

        df = df.rename(columns={k: v for k, v in column_renames.items() if k in df.columns})

        # Reorder columns for better display
        preferred_order = [
            'Yoga Name', 'Type', 'Start Time', 'End Time', 'Duration',
            'Planets', 'Strength', 'Active', 'Description'
        ]

        # Keep only columns that exist
        ordered_columns = [col for col in preferred_order if col in df.columns]

        # Add any remaining columns
        for col in df.columns:
            if col not in ordered_columns:
                ordered_columns.append(col)

        return df[ordered_columns]

    def format_yoga_periods(self, yoga_periods: List[Dict]) -> pd.DataFrame:
        """
        Format yoga periods for timeline display.

        Args:
            yoga_periods: List of yoga period dictionaries

        Returns:
            Formatted DataFrame
        """
        # Create base DataFrame
        df = pd.DataFrame(yoga_periods)

        # Add type column if not present
        if 'type' not in df.columns and 'yoga_name' in df.columns:
            df['type'] = df['yoga_name'].apply(self.categorize_yoga)

        # Format time columns
        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'])
        if 'end_time' in df.columns:
            df['end_time'] = pd.to_datetime(df['end_time'])

        # Calculate duration if not provided
        if 'duration' not in df.columns and 'start_time' in df.columns and 'end_time' in df.columns:
            df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600  # hours
            df['duration'] = df['duration'].round(1).astype(str) + ' hours'

        # Rename columns for better display
        column_renames = {
            'yoga_name': 'Yoga Name',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'type': 'Type',
            'duration': 'Duration',
            'planets': 'Planets',
            'description': 'Description'
        }

        df = df.rename(columns={k: v for k, v in column_renames.items() if k in df.columns})

        return df

    def summarize_yogas(self, yoga_results: List[Dict]) -> Dict:
        """
        Generate summary statistics for yoga results.

        Args:
            yoga_results: List of yoga result dictionaries

        Returns:
            Dictionary with summary statistics
        """
        # Count yogas by type
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for result in yoga_results:
            yoga_name = result.get('yoga_name', '')
            if not yoga_name:
                continue

            yoga_type = self.categorize_yoga(yoga_name)
            if yoga_type == "Positive":
                positive_count += 1
            elif yoga_type == "Negative":
                negative_count += 1
            else:
                neutral_count += 1

        # Calculate total and percentages
        total_count = positive_count + negative_count + neutral_count
        if total_count > 0:
            positive_pct = round(positive_count / total_count * 100, 1)
            negative_pct = round(negative_count / total_count * 100, 1)
            neutral_pct = round(neutral_count / total_count * 100, 1)
        else:
            positive_pct = negative_pct = neutral_pct = 0.0

        return {
            'total_yogas': total_count,
            'positive_yogas': positive_count,
            'negative_yogas': negative_count,
            'neutral_yogas': neutral_count,
            'positive_percentage': positive_pct,
            'negative_percentage': negative_pct,
            'neutral_percentage': neutral_pct
        }

    def format_yoga_summary(self, summary: Dict) -> pd.DataFrame:
        """
        Format yoga summary as a DataFrame.

        Args:
            summary: Dictionary with summary statistics

        Returns:
            Formatted DataFrame
        """
        # Create summary DataFrame
        data = {
            'Category': ['Positive Yogas', 'Negative Yogas', 'Neutral Yogas', 'Total'],
            'Count': [
                summary['positive_yogas'],
                summary['negative_yogas'],
                summary['neutral_yogas'],
                summary['total_yogas']
            ],
            'Percentage': [
                f"{summary['positive_percentage']}%",
                f"{summary['negative_percentage']}%",
                f"{summary['neutral_percentage']}%",
                '100.0%'
            ]
        }

        return pd.DataFrame(data)

    def get_most_significant_yogas(self, yoga_results: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        Get the most significant yogas based on duration and strength.

        Args:
            yoga_results: List of yoga result dictionaries
            top_n: Number of top yogas to return

        Returns:
            List of top yoga results
        """
        # Calculate significance score for each yoga
        scored_results = []

        for result in yoga_results:
            # Get duration in hours
            start_time = result.get('start_time')
            end_time = result.get('end_time')

            if not start_time or not end_time or end_time == 'Ongoing':
                # Skip if missing time data
                continue

            # Parse times
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            if isinstance(end_time, str) and end_time != 'Ongoing':
                end_time = pd.to_datetime(end_time)

            # Calculate duration in hours
            if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                duration = (end_time - start_time).total_seconds() / 3600
            else:
                duration = 0

            # Get strength (default to 1.0 if not available)
            strength = result.get('strength', 1.0)
            if isinstance(strength, str) and '%' in strength:
                strength = float(strength.strip('%')) / 100

            # Calculate score: duration * strength
            score = duration * strength

            # Add to scored results
            scored_results.append((score, result))

        # Sort by score in descending order
        scored_results.sort(reverse=True)

        # Return top N results
        return [result for _, result in scored_results[:top_n]]