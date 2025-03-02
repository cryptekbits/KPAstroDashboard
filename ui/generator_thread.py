"""
Thread for generating KP Astrology data in the background.
"""

import logging
import traceback
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

from data_generators.kp_data_generator import KPDataGenerator


class GeneratorThread(QThread):
    """
    Thread for generating data without freezing the UI.
    """
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, location, start_datetime, sheets_to_generate, selected_aspects,
                 aspect_planets, yoga_settings=None):
        """
        Initialize the generator thread.

        Parameters:
        -----------
        location : str
            The location for calculations
        start_datetime : datetime
            The main date and time for calculations
        sheets_to_generate : list
            List of sheet names to generate
        selected_aspects : list
            List of aspect angles to calculate
        aspect_planets : list
            List of planets to include in aspect calculations
        yoga_settings : dict, optional
            Settings for yoga calculations including date range
        """
        super().__init__()
        self.location = location
        self.start_datetime = start_datetime
        self.sheets_to_generate = sheets_to_generate
        self.selected_aspects = selected_aspects
        self.aspect_planets = aspect_planets
        self.yoga_settings = yoga_settings

    def run(self):
        try:
            # Locations dictionary - can be expanded with more locations
            locations = {
                "Mumbai": {"latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
                "Delhi": {"latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "Chennai": {"latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata"},
                "Kolkata": {"latitude": 22.5726, "longitude": 88.3639, "timezone": "Asia/Kolkata"},
                "New York": {"latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
                "London": {"latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
            }

            location_data = locations.get(self.location)
            if not location_data:
                self.error_signal.emit(f"Location {self.location} not found!")
                return

            self.progress_signal.emit(5, "Initializing data generator...")

            # Create data generator
            generator = KPDataGenerator(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                timezone=location_data["timezone"],
                ayanamsa="Krishnamurti",
                house_system="Placidus"
            )

            # Set the selected aspects and aspect planets in the generator
            generator.aspect_calculator.set_selected_aspects(self.selected_aspects)
            generator.aspect_calculator.set_selected_planets(self.aspect_planets)

            # Define end date time (11:55 PM on the same day)
            end_datetime = self.start_datetime.replace(hour=23, minute=55, second=0)

            results = {}

            # Planet positions sheet
            if "Planet Positions" in self.sheets_to_generate:
                self.progress_signal.emit(10, "Generating Planet Positions...")
                results["Planet Positions"] = generator.get_planet_positions(self.start_datetime)

            # Hora timing sheet
            if "Hora Timing" in self.sheets_to_generate:
                self.progress_signal.emit(15, "Generating Hora Timing...")
                results["Hora Timing"] = generator.get_hora_timings(self.start_datetime, end_datetime)

            # Planets data
            planets = [
                "Moon", "Ascendant", "Sun", "Mercury", "Venus",
                "Mars", "Jupiter", "Saturn", "Rahu", "Ketu",
                "Uranus", "Neptune"
            ]

            # Calculate progress distribution for planet transitions
            total_transition_items = sum(1 for p in planets if p in self.sheets_to_generate)
            transition_progress_per_item = 40 / max(total_transition_items, 1)  # Avoid division by zero
            current_progress = 20

            # Process each planet transition
            for planet in planets:
                if planet in self.sheets_to_generate:
                    self.progress_signal.emit(current_progress, f"Generating {planet} data...")
                    results[planet] = generator.get_planet_transitions(
                        planet, self.start_datetime, end_datetime
                    )
                    current_progress += transition_progress_per_item
                    self.progress_signal.emit(current_progress, f"Completed {planet} data")

            # Calculate Yogas if included
            if "Yogas" in self.sheets_to_generate and self.yoga_settings:
                self.progress_signal.emit(current_progress, "Calculating Yogas...")

                yoga_start_date = self.yoga_settings["start_date"]
                yoga_end_date = self.yoga_settings["end_date"]

                # Define a progress callback for yoga calculations
                def yoga_progress_callback(current, total, message):
                    # Calculate percentage based on current/total
                    if total > 0:
                        progress_percent = current / total * 30  # 30% of progress bar for yogas
                        self.progress_signal.emit(
                            int(current_progress + progress_percent),
                            message
                        )

                # Calculate yogas for the date range
                yoga_df = generator.calculate_yogas_for_date_range(
                    yoga_start_date,
                    yoga_end_date,
                    progress_callback=yoga_progress_callback,
                    time_interval=self.yoga_settings.get("time_interval", 1)
                )

                # Store the yoga data in results
                results["Yogas"] = yoga_df
                current_progress += 30

            self.progress_signal.emit(95, "Finalizing results...")
            self.finished_signal.emit(results)
            self.progress_signal.emit(100, "Complete!")

        except Exception as e:
            error_msg = f"Error during data generation: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.error_signal.emit(error_msg) 