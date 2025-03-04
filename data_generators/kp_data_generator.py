from datetime import datetime, timedelta
import pytz
import pandas as pd
import concurrent.futures
import threading

from astro_engine.core import VedicHoroscopeData
from astro_engine.utils import dms_to_decdeg
from calculations.aspect_calculator import AspectCalculator
from calculations.hora_calculator import HoraCalculator
from calculations.position_calculator import PlanetPositionCalculator
from calculations.transit_calculator import TransitCalculator
from calculations.planetary_strength_calculator import PlanetaryStrengthCalculator


class KPDataGenerator:
    """
    Class for generating KP (Krishnamurti Paddhati) astrological data.
    Handles planetary positions, hora timings, transits, and yogas.
    """

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
        print(f"Initializing KP Data Generator with: lat={latitude}, lon={longitude}, tz={timezone}")
        print(f"Using ayanamsa: {ayanamsa}, house system: {house_system}")

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

        # Initialize the specialized calculators
        self.position_calculator = PlanetPositionCalculator(
            latitude, longitude, timezone, ayanamsa, house_system
        )
        self.hora_calculator = HoraCalculator(
            latitude, longitude, timezone
        )
        self.transit_calculator = TransitCalculator(
            latitude, longitude, timezone, self.position_calculator, ayanamsa, house_system
        )

        # Initialize aspect calculator
        self.aspect_calculator = AspectCalculator()
        
        # Initialize planetary strength calculator
        self.strength_calculator = PlanetaryStrengthCalculator(
            self.position_calculator
        )

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
        return self.position_calculator.create_chart_data(dt)

    def format_position(self, planet):
        """
        Format planet position consistently as degrees within sign.

        Parameters:
        -----------
        planet : object
            The planet object with position data

        Returns:
        --------
        str
            A formatted string representing the planet's position
        """
        return self.position_calculator.format_position(planet)

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
        print(f"Getting planet positions for {dt}")
        planet_positions_df = self.position_calculator.get_planet_positions(dt)
        
        # Add planetary strength calculations
        planet_positions_df = self.strength_calculator.add_planetary_strengths(planet_positions_df)
        
        # Add metadata for conditional formatting
        bala_columns = [col for col in planet_positions_df.columns if any(bala in col for bala in ["Digbala", "Sthanabala", "Shadbala"])]
        
        # Get ranges for each bala
        bala_ranges = self.strength_calculator.get_bala_ranges()
        
        # Add conditional formatting metadata
        for col in bala_columns:
            # Extract the bala type from the column name
            bala_type = col.split(" ")[0]
            
            # Set min and max values for conditional formatting
            min_val = bala_ranges[bala_type]["min"]
            max_val = bala_ranges[bala_type]["max"]
            
            # Add metadata for conditional formatting
            planet_positions_df.attrs[f"{col}_format"] = {
                "type": "gradient",
                "min": min_val,
                "max": max_val,
                "min_color": "red",
                "max_color": "green"
            }
        
        return planet_positions_df

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
        return self.hora_calculator.get_sunrise_with_ephem(date, latitude, longitude)

    def get_hora_timings(self, start_dt, end_dt):
        """
        Get accurate Hora timings based on sunrise/sunset for the given date range.
        Properly handles timezone conversions.

        Parameters:
        -----------
        start_dt : datetime
            The start datetime
        end_dt : datetime
            The end datetime

        Returns:
        --------
        pandas.DataFrame
            DataFrame with hora timing information
        """
        print(f"Getting hora timings from {start_dt} to {end_dt}")
        return self.hora_calculator.get_hora_timings(start_dt, end_dt)

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
        print(f"Getting transitions for {planet_name} from {start_dt} to {end_dt}")
        return self.transit_calculator.get_planet_transitions(planet_name, start_dt, end_dt, check_interval_minutes)

    def calculate_yogas(self, chart, planets_data):
        """
        Calculate all yogas (auspicious and inauspicious planetary combinations) for the given chart.

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : pandas.DataFrame with planet positions

        Returns:
        --------
        list
            List of yoga dictionaries containing yoga information
        """
        # Use the aspect calculator to calculate yogas
        return self.aspect_calculator.calculate_yogas(chart, planets_data)

    def calculate_yogas_for_date_range(self, start_date, end_date, progress_callback=None, time_interval=1, max_workers=4):
        """
        Calculate yogas for a date range and track when each yoga starts and ends.

        Parameters:
        -----------
        start_date : datetime
            The start date for yoga calculation
        end_date : datetime
            The end date for yoga calculation
        progress_callback : function, optional
            Callback function to report progress (receives current_progress, total, message)
        time_interval : float, optional
            Time interval in hours between yoga calculations (default: 1)
            Can be fractional for minute-level precision (e.g., 1/60 for 1 minute)
        max_workers : int, optional
            Maximum number of worker threads to use for parallel processing

        Returns:
        --------
        pandas.DataFrame
            DataFrame with yoga information including start and end times
        """
        print(f"Calculating yogas from {start_date.date()} to {end_date.date()} with {time_interval*60:.0f} minute intervals")

        # Prepare for parallel processing
        # Split the date range into chunks for different threads
        total_time = (end_date - start_date).total_seconds()
        chunk_size = timedelta(seconds=total_time / max_workers)
        
        # Create date chunks for parallel processing
        date_chunks = []
        chunk_start = start_date
        while chunk_start < end_date:
            chunk_end = min(chunk_start + chunk_size, end_date)
            date_chunks.append((chunk_start, chunk_end))
            chunk_start = chunk_end

        # Progress tracking with thread safety
        progress_lock = threading.Lock()
        hours_to_check = (end_date - start_date).total_seconds() / 3600
        total_checks = hours_to_check / time_interval + 1
        checks_done = 0
        
        def track_progress(increment):
            nonlocal checks_done
            with progress_lock:
                checks_done += increment
                if progress_callback:
                    progress_callback(checks_done, total_checks, 
                                     f"Processed {checks_done}/{total_checks:.0f} time points")

        # Track the active yogas by their unique signature
        active_yogas = {}
        active_yogas_lock = threading.Lock()
        
        # Define a cooldown period (in minutes) to prevent the same yoga from being reported multiple times
        # This is the minimum duration a yoga must have
        cooldown_minutes = max(5, int(time_interval * 60))
        
        # Function to process a chunk of dates and identify yoga transitions
        def process_date_chunk(chunk_start, chunk_end):
            local_yogas = []
            current_date = chunk_start.replace(hour=0, minute=0, second=0, microsecond=0)
            if current_date < chunk_start:
                current_date = chunk_start
                
            end_point = chunk_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            if end_point > chunk_end:
                end_point = chunk_end
                
            # Initialize the active yogas set for this chunk
            local_active_yogas = {}
            # Track when each yoga was last seen to implement cooldown
            yoga_last_seen = {}
            chunk_checks_done = 0
            
            while current_date <= end_point:
                try:
                    # Generate chart data for this date
                    chart_data = self.create_chart_data(current_date)
                    chart = chart_data.generate_chart()

                    # Get planetary positions
                    planets_data = chart_data.get_planets_data_from_chart(chart)

                    # Calculate yogas for this date/time
                    current_yogas = self.calculate_yogas(chart, planets_data)
                    
                    # Build a set of current yoga signatures with more detailed information
                    current_yoga_set = set()
                    for yoga in current_yogas:
                        # Create a more detailed key that includes the yoga name and planets involved
                        yoga_key = (yoga["name"], tuple(sorted(yoga["planets_info"])))
                        current_yoga_set.add(yoga_key)
                    
                    # Check for yogas that have started
                    for yoga in current_yogas:
                        yoga_key = (yoga["name"], tuple(sorted(yoga["planets_info"])))
                        
                        # Update the last seen time for this yoga
                        yoga_last_seen[yoga_key] = current_date
                        
                        if yoga_key not in local_active_yogas:
                            # Check if this yoga is in cooldown period from a previous occurrence
                            should_record = True
                            for existing_key, existing_entry in local_active_yogas.items():
                                # If it's the same yoga name but different planets, check the end time
                                if (existing_key[0] == yoga_key[0] and 
                                    existing_entry["End Date"] and 
                                    existing_entry["End Time"]):
                                    # Convert end date/time to datetime for comparison
                                    try:
                                        end_dt_str = f"{existing_entry['End Date']} {existing_entry['End Time']}"
                                        end_dt = datetime.strptime(end_dt_str, "%d/%m/%y %I:%M %p")
                                        # Add timezone info if needed
                                        if current_date.tzinfo:
                                            end_dt = end_dt.replace(tzinfo=current_date.tzinfo)
                                        
                                        # If the current time is within cooldown period of the previous end time
                                        if (current_date - end_dt).total_seconds() < cooldown_minutes * 60:
                                            should_record = False
                                            break
                                    except ValueError:
                                        # If date parsing fails, continue with recording
                                        pass
                            
                            if should_record:
                                # New yoga has started - record it
                                yoga_entry = {
                                    "Start Date": current_date.strftime("%d/%m/%y"),
                                    "Start Time": current_date.strftime("%I:%M %p"),
                                    "End Date": "",  # Will be filled later
                                    "End Time": "",  # Will be filled later
                                    "Yoga": yoga["name"],
                                    "Planets": self._format_planets_for_excel(yoga["planets_info"]),
                                    "Nature": yoga.get("nature", "Neutral"),
                                    "Description": yoga.get("description", ""),
                                    "Raw Time": current_date,  # For sorting & processing, will be removed later
                                    "Active": True,
                                    "Chunk": f"{chunk_start}-{chunk_end}"  # For debugging
                                }
                                local_active_yogas[yoga_key] = yoga_entry
                    
                    # Check for yogas that have ended
                    ended_yogas = []
                    for yoga_key, yoga_entry in list(local_active_yogas.items()):
                        if yoga_key not in current_yoga_set and yoga_entry["Active"]:
                            # Check if the yoga has been active for at least the cooldown period
                            start_dt_str = f"{yoga_entry['Start Date']} {yoga_entry['Start Time']}"
                            try:
                                start_dt = datetime.strptime(start_dt_str, "%d/%m/%y %I:%M %p")
                                # Add timezone info if needed
                                if current_date.tzinfo:
                                    start_dt = start_dt.replace(tzinfo=current_date.tzinfo)
                                
                                # Only end the yoga if it has been active for at least the cooldown period
                                duration_minutes = (current_date - start_dt).total_seconds() / 60
                                if duration_minutes >= cooldown_minutes:
                                    # Yoga has ended
                                    yoga_entry["End Date"] = current_date.strftime("%d/%m/%y")
                                    yoga_entry["End Time"] = current_date.strftime("%I:%M %p")
                                    yoga_entry["Active"] = False
                                    ended_yogas.append(yoga_entry)
                                    # Remove from active yogas
                                    del local_active_yogas[yoga_key]
                                else:
                                    # If the yoga hasn't been active long enough, check if it's been gone for too long
                                    time_since_last_seen = (current_date - yoga_last_seen.get(yoga_key, start_dt)).total_seconds() / 60
                                    if time_since_last_seen > 2 * time_interval * 60:  # If not seen for 2 intervals
                                        # Force end the yoga
                                        yoga_entry["End Date"] = yoga_last_seen.get(yoga_key, current_date).strftime("%d/%m/%y")
                                        yoga_entry["End Time"] = yoga_last_seen.get(yoga_key, current_date).strftime("%I:%M %p")
                                        yoga_entry["Active"] = False
                                        ended_yogas.append(yoga_entry)
                                        # Remove from active yogas
                                        del local_active_yogas[yoga_key]
                            except ValueError:
                                # If date parsing fails, end the yoga at current time
                                yoga_entry["End Date"] = current_date.strftime("%d/%m/%y")
                                yoga_entry["End Time"] = current_date.strftime("%I:%M %p")
                                yoga_entry["Active"] = False
                                ended_yogas.append(yoga_entry)
                                # Remove from active yogas
                                del local_active_yogas[yoga_key]
                    
                    # Add ended yogas to the result list
                    local_yogas.extend(ended_yogas)
                    
                except Exception as e:
                    print(f"Error calculating yogas for {current_date}: {str(e)}")

                # Convert time_interval from hours to timedelta
                # This handles fractional hours (e.g., 1/60 for 1 minute)
                hours = int(time_interval)
                minutes = int((time_interval - hours) * 60)
                current_date += timedelta(hours=hours, minutes=minutes)
                chunk_checks_done += 1
                
                # Update progress occasionally
                if chunk_checks_done % 10 == 0:
                    track_progress(10)
            
            # Handle any yogas still active at the end of the chunk
            for yoga_key, yoga_entry in local_active_yogas.items():
                if yoga_entry["Active"]:
                    # For yogas at chunk boundaries, we don't know if they end 
                    # until we merge results - mark them specially
                    if chunk_end < end_date:
                        yoga_entry["End Date"] = "PENDING"
                        yoga_entry["End Time"] = "PENDING"
                    else:
                        # For the last chunk, use the end date of our calculation
                        yoga_entry["End Date"] = end_point.strftime("%d/%m/%y")
                        yoga_entry["End Time"] = end_point.strftime("%I:%M %p") 
                    local_yogas.append(yoga_entry)
            
            # Update progress for any remaining checks
            if chunk_checks_done % 10 != 0:
                track_progress(chunk_checks_done % 10)
            
            return local_yogas
        
        # Process chunks in parallel
        all_yogas = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {
                executor.submit(process_date_chunk, chunk[0], chunk[1]): chunk 
                for chunk in date_chunks
            }
            
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    chunk_yogas = future.result()
                    all_yogas.extend(chunk_yogas)
                except Exception as e:
                    print(f"Error processing chunk {chunk}: {str(e)}")
        
        # Now merge results and resolve any PENDING end dates
        # Sort yogas by start time
        all_yogas.sort(key=lambda y: y["Raw Time"])
        
        # Process any yogas with PENDING end dates
        yoga_continuations = {}
        for i, yoga in enumerate(all_yogas):
            if yoga["End Date"] == "PENDING":
                yoga_key = (yoga["Yoga"], yoga["Planets"])
                yoga_continuations[yoga_key] = i
        
        # Second pass to resolve continuations
        for i, yoga in enumerate(all_yogas):
            yoga_key = (yoga["Yoga"], yoga["Planets"])
            if yoga_key in yoga_continuations and yoga_continuations[yoga_key] != i:
                # This is a continuation of a previous yoga
                previous_idx = yoga_continuations[yoga_key]
                # Copy the end date/time from this yoga to the previous one
                all_yogas[previous_idx]["End Date"] = yoga["End Date"]
                all_yogas[previous_idx]["End Time"] = yoga["End Time"]
                # Mark this yoga for removal (it's a duplicate)
                yoga["To_Remove"] = True
        
        # Additional pass to merge yogas of the same type that are close together
        # This helps prevent the same yoga from appearing multiple times with small gaps
        merge_window_minutes = cooldown_minutes * 2
        i = 0
        while i < len(all_yogas) - 1:
            current = all_yogas[i]
            if current.get("To_Remove", False):
                i += 1
                continue
                
            # Look ahead for yogas of the same name that start soon after this one ends
            j = i + 1
            while j < len(all_yogas):
                next_yoga = all_yogas[j]
                if next_yoga.get("To_Remove", False) or current["Yoga"] != next_yoga["Yoga"]:
                    j += 1
                    continue
                
                # Check if the next yoga starts soon after this one ends
                try:
                    current_end = datetime.strptime(f"{current['End Date']} {current['End Time']}", "%d/%m/%y %I:%M %p")
                    next_start = datetime.strptime(f"{next_yoga['Start Date']} {next_yoga['Start Time']}", "%d/%m/%y %I:%M %p")
                    
                    # If the gap is small, merge them
                    gap_minutes = (next_start - current_end).total_seconds() / 60
                    if gap_minutes <= merge_window_minutes:
                        # Extend the current yoga to the end of the next one
                        current["End Date"] = next_yoga["End Date"]
                        current["End Time"] = next_yoga["End Time"]
                        # Mark the next yoga for removal
                        next_yoga["To_Remove"] = True
                        # Continue looking for more yogas to merge
                        j += 1
                    else:
                        # Gap too large, stop looking
                        break
                except ValueError:
                    # Date parsing error, skip this comparison
                    j += 1
            
            i += 1
        
        # Final pass to handle overlapping yoga periods of the same type
        # Convert all dates to datetime objects for easier comparison
        for yoga in all_yogas:
            if yoga.get("To_Remove", False):
                continue
                
            try:
                yoga["StartDT"] = datetime.strptime(f"{yoga['Start Date']} {yoga['Start Time']}", "%d/%m/%y %I:%M %p")
                # Handle PENDING end dates
                if yoga["End Date"] == "PENDING":
                    yoga["EndDT"] = datetime.max  # Use max datetime as a placeholder
                else:
                    yoga["EndDT"] = datetime.strptime(f"{yoga['End Date']} {yoga['End Time']}", "%d/%m/%y %I:%M %p")
            except ValueError as e:
                # Skip if date parsing fails
                print(f"Date parsing error: {e} for yoga {yoga['Yoga']}")
                continue
        
        # Sort by start time for the overlap check
        all_yogas.sort(key=lambda y: y.get("StartDT", datetime.max))
        
        # Check for overlaps
        i = 0
        while i < len(all_yogas):
            current = all_yogas[i]
            if current.get("To_Remove", False) or "StartDT" not in current or "EndDT" not in current:
                i += 1
                continue
                
            # Look for overlapping periods
            j = i + 1
            while j < len(all_yogas):
                next_yoga = all_yogas[j]
                if (next_yoga.get("To_Remove", False) or 
                    "StartDT" not in next_yoga or 
                    "EndDT" not in next_yoga or
                    current["Yoga"] != next_yoga["Yoga"]):
                    j += 1
                    continue
                
                # Check for overlap
                if next_yoga["StartDT"] <= current["EndDT"]:
                    # Periods overlap, merge them
                    # Take the earlier start time
                    if next_yoga["StartDT"] < current["StartDT"]:
                        current["Start Date"] = next_yoga["Start Date"]
                        current["Start Time"] = next_yoga["Start Time"]
                        current["StartDT"] = next_yoga["StartDT"]
                    
                    # Take the later end time
                    if next_yoga["EndDT"] > current["EndDT"]:
                        current["End Date"] = next_yoga["End Date"]
                        current["End Time"] = next_yoga["End Time"]
                        current["EndDT"] = next_yoga["EndDT"]
                    
                    # Mark the next yoga for removal
                    next_yoga["To_Remove"] = True
                    # Continue checking with the merged period
                    j += 1
                else:
                    # No overlap, move to next yoga
                    j += 1
            
            i += 1
        
        # Remove duplicates and temporary fields
        final_yogas = []
        for yoga in all_yogas:
            if not yoga.get("To_Remove", False):
                # Remove temporary fields
                yoga.pop("Raw Time", None)
                yoga.pop("Active", None)
                yoga.pop("Chunk", None)
                yoga.pop("To_Remove", None)
                yoga.pop("StartDT", None)
                yoga.pop("EndDT", None)
                
                # Handle any remaining PENDING entries
                if yoga["End Date"] == "PENDING":
                    yoga["End Date"] = end_date.strftime("%d/%m/%y")
                    yoga["End Time"] = end_date.strftime("%I:%M %p")
                
                final_yogas.append(yoga)

        # Convert the list to a DataFrame
        if not final_yogas:
            # Return empty DataFrame with expected columns if no yogas found
            return pd.DataFrame(columns=[
                "Start Date", "Start Time", "End Date", "End Time", 
                "Yoga", "Planets", "Nature", "Description"
            ])

        df = pd.DataFrame(final_yogas)

        # Ensure all required columns are present
        required_columns = ["Start Date", "Start Time", "End Date", "End Time", 
                           "Yoga", "Planets", "Nature", "Description"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""  # Add empty column if missing

        # Sort by start date and time
        df = df.sort_values(["Start Date", "Start Time"])

        print(f"Found {len(df)} unique yoga periods in the date range")
        return df

    def _format_planets_for_excel(self, planets_info):
        """
        Format planet information for display in Excel.

        Parameters:
        -----------
        planets_info : list
            List of planet information strings

        Returns:
        --------
        str
            Formatted planet information
        """
        return "\n".join(planets_info)