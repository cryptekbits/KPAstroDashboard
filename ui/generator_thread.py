"""
Thread for generating KP Astrology data in the background.
"""

import logging
import traceback
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd

from data_generators.kp_data_generator import KPDataGenerator


class GeneratorThread(QThread):
    """
    Thread for generating data without freezing the UI.
    """
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, location, date, time, sheets_to_generate, output_file,
                 aspect_planets, yoga_settings=None, selected_date=None, config_settings=None):
        """
        Initialize the generator thread.

        Parameters:
        -----------
        location : dict
            Dictionary with location information (name, latitude, longitude, timezone)
        date : QDate
            The main date for calculations
        time : QTime
            The main time for calculations
        sheets_to_generate : list
            List of sheet names to generate
        output_file : str
            Path to the output Excel file
        aspect_planets : list
            List of planets to include in aspect calculations
        yoga_settings : dict, optional
            Settings for yoga calculations (start_date, end_date, time_interval)
        selected_date : QDate, optional
            The selected date from the main date picker (used for 1-day yoga calculations)
        config_settings : dict, optional
            Configuration settings from the configuration tab
        """
        super().__init__()
        self.location = location
        self.date = date
        self.time = time
        self.sheets_to_generate = sheets_to_generate
        self.output_file = output_file
        self.aspect_planets = aspect_planets
        self.yoga_settings = yoga_settings
        self.selected_date = selected_date
        self.config_settings = config_settings or {}

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
            generator.aspect_calculator.set_selected_planets(self.aspect_planets)

            # Convert QDate and QTime to Python datetime
            py_date = datetime(
                self.date.year(),
                self.date.month(),
                self.date.day(),
                self.time.hour(),
                self.time.minute(),
                self.time.second()
            )
            
            # Define end date time (11:55 PM on the same day)
            end_datetime = datetime(
                self.date.year(),
                self.date.month(),
                self.date.day(),
                23, 55, 0
            )

            results = {}

            # Planet positions sheet
            if "Planet Positions" in self.sheets_to_generate:
                self.progress_signal.emit(10, "Generating Planet Positions...")
                
                # Get planet positions data
                planet_positions_df = generator.get_planet_positions(py_date)
                
                # Apply configuration settings if available
                if self.config_settings and "planet_pos" in self.config_settings:
                    planet_pos_config = self.config_settings["planet_pos"]
                    
                    # Filter columns based on configuration
                    if "columns" in planet_pos_config:
                        columns_to_keep = ["Planet"] + [col for col, enabled in 
                                                      planet_pos_config["columns"].items() 
                                                      if enabled]
                        # Keep only the selected columns
                        planet_positions_df = planet_positions_df[
                            [col for col in planet_positions_df.columns if col in columns_to_keep]
                        ]
                    
                    # Filter planets based on configuration
                    if "planets" in planet_pos_config:
                        planets_to_keep = [planet for planet, enabled in 
                                          planet_pos_config["planets"].items() 
                                          if enabled]
                        # Keep only the selected planets
                        planet_positions_df = planet_positions_df[
                            planet_positions_df["Planet"].isin(planets_to_keep)
                        ]
                
                results["Planet Positions"] = planet_positions_df

            # Hora timing sheet
            if "Hora Timing" in self.sheets_to_generate:
                self.progress_signal.emit(15, "Generating Hora Timing...")
                
                # Get hora timing data
                hora_df = generator.get_hora_timings(py_date, end_datetime)
                
                # Apply configuration settings if available
                if self.config_settings and "hora" in self.config_settings:
                    hora_config = self.config_settings["hora"]
                    
                    # Filter columns based on configuration
                    if "columns" in hora_config:
                        columns_to_keep = [col for col, enabled in 
                                          hora_config["columns"].items() 
                                          if enabled]
                        # Keep only the selected columns
                        hora_df = hora_df[
                            [col for col in hora_df.columns if col in columns_to_keep]
                        ]
                
                results["Hora Timing"] = hora_df

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
                    
                    # Get planet transition data
                    planet_df = generator.get_planet_transitions(
                        planet, py_date, end_datetime
                    )
                    
                    # Apply configuration settings if available
                    if self.config_settings and "transit" in self.config_settings:
                        transit_config = self.config_settings["transit"]
                        
                        # Filter columns based on configuration
                        if "columns" in transit_config:
                            columns_to_keep = [col for col, enabled in 
                                              transit_config["columns"].items() 
                                              if enabled]
                            # Keep only the selected columns
                            planet_df = planet_df[
                                [col for col in planet_df.columns if col in columns_to_keep]
                            ]
                    
                    results[planet] = planet_df
                    current_progress += transition_progress_per_item
                    self.progress_signal.emit(current_progress, f"Completed {planet} data")

            # Calculate Yogas if included
            if "Yogas" in self.sheets_to_generate and self.yoga_settings:
                self.progress_signal.emit(current_progress, "Calculating Yogas...")

                yoga_start_date = self.yoga_settings["start_date"]
                yoga_end_date = self.yoga_settings["end_date"]
                
                # Get enabled yoga types if specified
                enabled_yoga_types = self.yoga_settings.get("enabled_yoga_types", [])

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
                
                # Filter yogas by enabled types if specified
                if enabled_yoga_types:
                    yoga_df = yoga_df[yoga_df["Yoga"].isin(enabled_yoga_types)]

                # If this is a 1-day calculation, filter to show only yogas active on the selected day
                if self.yoga_settings.get("is_one_day", False) and self.selected_date:
                    # Get the selected day
                    selected_date = self.selected_date
                    
                    # Convert selected date to string format used in the DataFrame
                    selected_date_str = selected_date.toString("dd/MM/yy")
                    
                    # Filter yogas that are active during the selected day
                    # A yoga is active on the selected day if:
                    # 1. It starts on or before the selected day AND
                    # 2. It ends on or after the selected day
                    filtered_yogas = []
                    
                    for _, yoga in yoga_df.iterrows():
                        # Parse dates for comparison
                        start_date = datetime.strptime(yoga["Start Date"], "%d/%m/%y").date()
                        end_date = datetime.strptime(yoga["End Date"], "%d/%m/%y").date()
                        
                        # Convert selected_date to datetime.date for comparison
                        py_selected_date = selected_date.toPyDate()
                        
                        # Check if the yoga is active on the selected day
                        if start_date <= py_selected_date and end_date >= py_selected_date:
                            filtered_yogas.append(yoga)
                    
                    # Create a new DataFrame with only the filtered yogas
                    if filtered_yogas:
                        yoga_df = pd.DataFrame(filtered_yogas)
                    else:
                        # If no yogas are active on the selected day, create an empty DataFrame with the same columns
                        yoga_df = pd.DataFrame(columns=yoga_df.columns)
                    
                    self.progress_signal.emit(
                        int(current_progress + 5),
                        f"Found {len(yoga_df)} yogas active on {selected_date_str}"
                    )
                
                # Apply configuration settings if available
                if self.config_settings and "yoga" in self.config_settings:
                    yoga_config = self.config_settings["yoga"]
                    
                    # Debug: Print column names before filtering
                    print("Yoga DataFrame columns before filtering:", yoga_df.columns.tolist())
                    
                    # Filter columns based on configuration
                    if "columns" in yoga_config:
                        columns_to_keep = [col for col, enabled in 
                                          yoga_config["columns"].items() 
                                          if enabled]
                        
                        # Debug: Print columns to keep
                        print("Columns to keep:", columns_to_keep)
                        
                        # Map column names from config to actual column names in DataFrame
                        column_mapping = {
                            "Start Date": "Start Date",
                            "Start Time": "Start Time",
                            "End Date": "End Date",
                            "End Time": "End Time",
                            "Yoga": "Yoga",
                            "Planets": "Planets",
                            "Nature": "Nature",
                            "Description": "Description"
                        }
                        
                        # Debug: Print column mapping
                        print("Column mapping:", column_mapping)
                        
                        # Keep only the selected columns
                        columns_to_keep_mapped = [column_mapping.get(col, col) for col in columns_to_keep]
                        
                        # Debug: Print columns to keep after mapping
                        print("Columns to keep after mapping:", columns_to_keep_mapped)
                        
                        # Debug: Print columns that exist in the DataFrame
                        print("Columns that exist in the DataFrame:", [col for col in columns_to_keep_mapped if col in yoga_df.columns])
                        
                        yoga_df = yoga_df[
                            [col for col in yoga_df.columns if col in columns_to_keep_mapped]
                        ]
                        
                        # Debug: Print column names after filtering
                        print("Yoga DataFrame columns after filtering:", yoga_df.columns.tolist())

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