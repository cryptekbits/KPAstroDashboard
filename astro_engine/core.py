"""
Core functionality for Vedic astrology calculations.

This module provides the main class for generating and analyzing
Vedic horoscope data according to the Krishnamurti Paddhati (KP) system.
"""

import pandas as pd
import polars as pl
import collections
from geopy.geocoders import Nominatim
import re
try:
    # First try to import from our local copy
    from lib.flatlib import const, aspects
    from lib.flatlib.chart import Chart
    from lib.flatlib.datetime import Datetime
    from lib.flatlib.geopos import GeoPos
    from lib.flatlib.object import GenericObject
except ImportError:
    # Fall back to the installed version if the local copy isn't available
    from flatlib import const, aspects
    from flatlib.chart import Chart
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.object import GenericObject

from .utils import dms_to_decdeg, clean_select_objects_split_str

# Global Constants
ROMAN_HOUSE_NUMBERS = {
    'House1': 'I', 'House2': 'II', 'House3': 'III', 'House4': 'IV', 
    'House5': 'V', 'House6': 'VI', 'House7': 'VII', 'House8': 'VIII', 
    'House9': 'IX', 'House10': 'X', 'House11': 'XI', 'House12': 'XII'
}

RASHIS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 
    'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Lords of the 12 Zodiac Signs
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", 
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]          

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashīrsha', 'Ardra', 
    'Punarvasu', 'Pushya', 'Āshleshā', 'Maghā', 'PūrvaPhalgunī', 'UttaraPhalgunī', 
    'Hasta', 'Chitra', 'Svati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 
    'PurvaAshadha', 'UttaraAshadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 
    'PurvaBhādrapadā', 'UttaraBhādrapadā', 'Revati'
]

AYANAMSA_MAPPING = {
    "Lahiri": const.AY_LAHIRI,
    "Lahiri_1940": const.AY_LAHIRI_1940, 
    "Lahiri_VP285": const.AY_LAHIRI_VP285,
    "Lahiri_ICRC": const.AY_LAHIRI_ICRC,
    "Raman": const.AY_RAMAN,
    "Krishnamurti": const.AY_KRISHNAMURTI,
    "Krishnamurti_Senthilathiban": const.AY_KRISHNAMURTI_SENTHILATHIBAN,
}

HOUSE_SYSTEM_MAPPING = {
    "Placidus": const.HOUSES_PLACIDUS,
    "Equal": const.HOUSES_EQUAL,
    "Equal 2": const.HOUSES_EQUAL_2,
    "Whole Sign": const.HOUSES_WHOLE_SIGN,
}

ASPECT_MAPPING = {
    const.NO_ASPECT: "No Aspect",
    const.CONJUNCTION: "Conjunction",
    const.SEXTILE: "Sextile",
    const.SQUARE: "Square",
    const.TRINE: "Trine",
    const.OPPOSITION: "Opposition", 
    const.SEMISEXTILE: "Semi Sextile",
    const.SEMIQUINTILE: "Semi Quintile",
    const.SEMISQUARE: "Semi Square",
    const.QUINTILE: "Quintile", 
    const.SESQUIQUINTILE: "Sesqui Quintile",
    const.SESQUISQUARE: "Sesqui Square",
    const.BIQUINTILE: "Bi Quintile",
    const.QUINCUNX: "Quincunx",
}

# Columns names for NamedTuple Collections / Final Output DataFrames
HOUSES_TABLE_COLS = [
    "Object", "HouseNr", "Rasi", "LonDecDeg", "SignLonDMS", "SignLonDecDeg", "DegSize",
    "Nakshatra", "RasiLord", "NakshatraLord", "SubLord", "SubSubLord"
]

PLANETS_TABLE_COLS = [
    "Object", "Rasi", "isRetroGrade", "LonDecDeg", "SignLonDMS", "SignLonDecDeg", "LatDMS",
    "Nakshatra", "RasiLord", "NakshatraLord", "SubLord", "SubSubLord", "HouseNr"
]

# Add fallback values for AY_LAHIRI constants if they're not defined in flatlib.const
if not hasattr(const, 'AY_LAHIRI'):
    const.AY_LAHIRI = "Ayanamsa Lahiri"
if not hasattr(const, 'AY_LAHIRI_1940'):
    const.AY_LAHIRI_1940 = "Ayanamsa Lahiri 1940" 
if not hasattr(const, 'AY_LAHIRI_VP285'):
    const.AY_LAHIRI_VP285 = "Ayanamsa Lahiri VP285"
if not hasattr(const, 'AY_LAHIRI_ICRC'):
    const.AY_LAHIRI_ICRC = "Ayanamsa Lahiri ICRC"
if not hasattr(const, 'AY_RAMAN'):
    const.AY_RAMAN = "Ayanamsa Raman"
if not hasattr(const, 'AY_KRISHNAMURTI'):
    const.AY_KRISHNAMURTI = "Ayanamsa Krishnamurti"
if not hasattr(const, 'AY_KRISHNAMURTI_SENTHILATHIBAN'):
    const.AY_KRISHNAMURTI_SENTHILATHIBAN = "Ayanamsa Krishnamurti VP291"

class VedicHoroscopeData:
    """
    Generates Planetary and House Positions Data for a time and place input.
    
    This class provides methods to calculate and analyze astrological data
    according to the Krishnamurti Paddhati (KP) system of Vedic astrology.
    """
    
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, second: int, utc: str, 
                 latitude: float, longitude: float, ayanamsa: str = "Lahiri", house_system: str = "Equal"):
        """
        Initialize the VedicHoroscopeData object.

        Args:
            year (int): Birth Year
            month (int): Birth Month
            day (int): Birth Day
            hour (int): Birth Hour
            minute (int): Birth Minute
            second (int): Birth Second
            utc (str): Country UTC offset (e.g., '+5:30')
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            ayanamsa (str, optional): Ayanamsa system to use. Defaults to "Lahiri".
            house_system (str, optional): House system to use. Defaults to "Equal".
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.utc = utc
        self.latitude = latitude
        self.longitude = longitude
        self.ayanamsa = ayanamsa
        self.house_system = house_system
    
    def get_ayanamsa(self):
        """
        Return an Ayanamsa System from flatlib.sidereal library, based on user input.
        
        Returns:
            str: The ayanamsa system code.
        """
        return AYANAMSA_MAPPING.get(self.ayanamsa, None)
    
    def get_house_system(self):
        """
        Return a House System from flatlib.sidereal library, based on user input.
        
        Returns:
            str: The house system code.
        """
        return HOUSE_SYSTEM_MAPPING.get(self.house_system, None)

    def generate_chart(self):
        """
        Generate a `flatlib.Chart` object for the given time and location data.
        
        Returns:
            Chart: A flatlib Chart object.
        """
        date = Datetime([self.year, self.month, self.day], ["+", self.hour, self.minute, self.second], self.utc)
        geopos = GeoPos(self.latitude, self.longitude)
        chart = Chart(date, geopos, IDs=const.LIST_OBJECTS, hsys=self.get_house_system(), mode=self.get_ayanamsa())
        return chart

    def get_planetary_aspects(self, chart: Chart):
        """
        Calculate the aspects between planets in the chart.
        
        Args:
            chart (Chart): The chart to analyze.
            
        Returns:
            list: A list of dictionaries containing aspect information.
        """
        planets = [
            const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN,
            const.URANUS, const.NEPTUNE, const.PLUTO, const.NORTH_NODE, const.SOUTH_NODE
        ]
        aspects_dict = []

        for p1 in planets:
            for p2 in planets:
                if p1 != p2:
                    obj1 = chart.get(p1)
                    obj2 = chart.get(p2)
                    aspect = aspects.getAspect(obj1, obj2, const.ALL_ASPECTS)
                    # Replace North and South nodes with conventional names
                    p1_new = p1.replace("North Node", "Rahu").replace("South Node", "Ketu")
                    p2_new = p2.replace("North Node", "Rahu").replace("South Node", "Ketu")
                    if aspect.exists():
                        aspect_type = ASPECT_MAPPING[int(aspect.type)]
                        aspect_orb = round(aspect.orb, 3)
                        aspects_dict.append({
                            "P1": p1_new,
                            "P2": p2_new,
                            "AspectType": aspect_type,
                            "AspectDeg": aspect.type,
                            "AspectOrb": aspect_orb
                        })

        return aspects_dict

    def get_ascendant_data(self, asc_data: GenericObject, PlanetsDataCollection: collections.namedtuple):
        """
        Generate Ascendant Data and return it in the format of the PlanetsDataCollection Named Tuple.
        
        Args:
            asc_data (GenericObject): The ascendant data from the chart.
            PlanetsDataCollection (collections.namedtuple): The namedtuple class to use for the result.
            
        Returns:
            collections.namedtuple: The ascendant data in the PlanetsDataCollection format.
        """
        asc_chart_data = clean_select_objects_split_str(str(asc_data))
        asc_rl_nl_sl_data = self.get_rl_nl_sl_data(deg=asc_data.lon)
        
        # Create a dictionary with None values for all fields
        data_dict = {field: None for field in PlanetsDataCollection._fields}
        
        # Update the specific fields with the ascendant data
        data_dict["Object"] = asc_chart_data[0]
        data_dict["Rasi"] = asc_chart_data[1]
        data_dict["SignLonDMS"] = asc_chart_data[2]
        data_dict["Nakshatra"] = asc_rl_nl_sl_data.get("Nakshatra", None)
        data_dict["RasiLord"] = asc_rl_nl_sl_data.get("RasiLord", None)
        data_dict["SubLord"] = asc_rl_nl_sl_data.get("SubLord", None)
        data_dict["SubSubLord"] = asc_rl_nl_sl_data.get("SubSubLord", None)
        data_dict["NakshatraLord"] = asc_rl_nl_sl_data.get("NakshatraLord", None)
        data_dict["isRetroGrade"] = None
        data_dict["LonDecDeg"] = round(asc_data.lon, 3)
        data_dict["SignLonDecDeg"] = dms_to_decdeg(asc_chart_data[2])
        data_dict["LatDMS"] = None
        data_dict["HouseNr"] = 1

        # Return a new PlanetsDataCollection instance with the data
        return PlanetsDataCollection(**data_dict)

    def get_rl_nl_sl_data(self, deg: float):
        """
        Return the Rashi (Sign) Lord, Nakshatra, Nakshatra Pada, Nakshatra Lord, Sub Lord and Sub Sub Lord 
        corresponding to the given degree.
        
        Args:
            deg (float): The degree in the zodiac.
            
        Returns:
            dict: A dictionary containing the astrological data.
        """
        duration = [7, 20, 6, 10, 7, 18, 16, 19, 17]
        lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        star_lords = lords * 3  # lords for the 27 Nakshatras

        # Compute Sign lords
        sign_deg = deg % 360  # Normalize degree to [0, 360)
        sign_index = int(sign_deg // 30)  # Each zodiac sign is 30 degrees
        
        # Compute Nakshatra details
        nakshatra_deg = sign_deg % 13.332  # Each nakshatra is 13.332 degrees
        nakshatra_index = int(sign_deg // 13.332)  # Find the nakshatra index
        pada = int((nakshatra_deg % 13.332) // 3.325) + 1  # Each pada is 3.325 degrees

        # Ensure nakshatra_index is within bounds
        nakshatra_index = nakshatra_index % len(NAKSHATRAS)        

        # Compute SubLords
        deg = deg - 120 * int(deg / 120)
        degcum = 0
        i = 0

        while i < 9:
            deg_nl = 360 / 27
            j = i
            while True:
                deg_sl = deg_nl * duration[j] / 120
                k = j
                while True:
                    deg_ss = deg_sl * duration[k] / 120
                    degcum += deg_ss
                    if degcum >= deg:
                        return {
                            "Nakshatra": NAKSHATRAS[nakshatra_index],
                            "Pada": pada, 
                            "NakshatraLord": star_lords[nakshatra_index],
                            "RasiLord": SIGN_LORDS[sign_index], 
                            "SubLord": lords[j],
                            "SubSubLord": lords[k]
                        }
                    k = (k + 1) % 9
                    if k == j:
                        break
                j = (j + 1) % 9
                if j == i:
                    break
            i += 1
        
        # This should not happen, but return a default value just in case
        return {
            "Nakshatra": None,
            "Pada": None,
            "NakshatraLord": None,
            "RasiLord": None,
            "SubLord": None,
            "SubSubLord": None
        }

    def get_planets_data_from_chart(self, chart: Chart, new_houses_chart: Chart = None):
        """
        Generate the planets data table given a `flatlib.Chart` object.
        
        Args:
            chart (Chart): flatlib Chart object using which planetary positions have to be generated.
            new_houses_chart (Chart, optional): flatlib Chart Object using which new house numbers have to be
                                              computed, typically used along with KP Horary Method.
                                              
        Returns:
            list: A list of PlanetsData namedtuples.
        """
        PlanetsData = collections.namedtuple("PlanetsData", PLANETS_TABLE_COLS)

        # Get the house each planet is in
        planet_in_house = self.get_planet_in_house(planets_chart=chart, houses_chart=new_houses_chart) if new_houses_chart \
                        else self.get_planet_in_house(planets_chart=chart, houses_chart=chart)

        # Get Ascendant Data
        ascendant_data = self.get_ascendant_data(asc_data=chart.get(const.ASC), PlanetsDataCollection=PlanetsData)

        planets_data = []
        planets_data.append(ascendant_data)
        
        for planet in chart.objects:
            planet_obj = clean_select_objects_split_str(str(planet))
            planet_name, planet_lon_deg, planet_lat_deg = planet_obj[0], planet_obj[2], planet_obj[3]

            # Get additional details like Nakshatra, RL, NL, SL details
            rl_nl_sl_data = self.get_rl_nl_sl_data(deg=planet.lon)
            planet_star = rl_nl_sl_data.get("Nakshatra", None)
            planet_rasi_lord = rl_nl_sl_data.get("RasiLord", None)
            planet_star_lord = rl_nl_sl_data.get("NakshatraLord", None)
            planet_sub_lord = rl_nl_sl_data.get("SubLord", None)
            planet_ss_lord = rl_nl_sl_data.get("SubSubLord", None)

            # Get the house the planet is in
            planet_house = planet_in_house.get(planet_name, None)

            # Append data to NamedTuple Collection
            planets_data.append(PlanetsData(
                planet_name, planet.sign, planet.isRetrograde(), round(planet.lon, 3), 
                planet_lon_deg, round(planet.signlon, 3), planet_lat_deg, planet_star, 
                planet_rasi_lord, planet_star_lord, planet_sub_lord, planet_ss_lord, planet_house
            ))
            
        return planets_data

    def get_houses_data_from_chart(self, chart: Chart):
        """
        Generate the houses data table given a `flatlib.Chart` object.
        
        Args:
            chart (Chart): The chart to analyze.
            
        Returns:
            list: A list of HousesData namedtuples.
        """
        HousesData = collections.namedtuple("HousesData", HOUSES_TABLE_COLS)  # Create NamedTuple Collection to store data
        houses_data = []
        
        for house in chart.houses:    
            house_obj = str(house).strip('<').strip('>').split()
            house_name, house_lon_deg, house_size = house_obj[0], house_obj[2], round(float(house_obj[3]), 3)
            house_nr = int(house_name.strip("House"))
            house_roman_nr = ROMAN_HOUSE_NUMBERS.get(house_name)

            # Get additional details like Nakshatra, RL, NL, SL details
            rl_nl_sl_data = self.get_rl_nl_sl_data(deg=house.lon)
            house_star = rl_nl_sl_data.get("Nakshatra", None)
            house_rasi_lord = rl_nl_sl_data.get("RasiLord", None)
            house_star_lord = rl_nl_sl_data.get("NakshatraLord", None)
            house_sub_lord = rl_nl_sl_data.get("SubLord", None)
            house_ss_lord = rl_nl_sl_data.get("SubSubLord", None)

            # Append data to NamedTuple Collection
            houses_data.append(HousesData(
                house_name, house_roman_nr, house.sign, round(house.lon, 3), 
                house_lon_deg, round(house.signlon, 3), house_size, house_star, 
                house_rasi_lord, house_star_lord, house_sub_lord, house_ss_lord
            ))
            
        return houses_data

    def get_consolidated_chart_data(self, planets_data: collections.namedtuple, houses_data: collections.namedtuple, 
                                    return_style: str = None):
        """
        Consolidate planets and houses data into a single DataFrame.
        
        Args:
            planets_data (collections.namedtuple): The planets data.
            houses_data (collections.namedtuple): The houses data.
            return_style (str, optional): The style of the returned data. Defaults to None.
            
        Returns:
            polars.DataFrame: The consolidated chart data.
        """
        # Convert NamedTuple Collections to DataFrames
        planets_df = pl.DataFrame(planets_data)
        houses_df = pl.DataFrame(houses_data)
        
        # Rename columns for clarity
        planets_df = planets_df.rename({"Object": "Planet", "HouseNr": "House"})
        houses_df = houses_df.rename({"Object": "House", "HouseNr": "HouseRoman"})
        
        # Select relevant columns
        planets_df = planets_df.select([
            "Planet", "Rasi", "House", "isRetroGrade", "LonDecDeg", "SignLonDMS", "SignLonDecDeg",
            "Nakshatra", "RasiLord", "NakshatraLord", "SubLord", "SubSubLord"
        ])
        
        houses_df = houses_df.select([
            "House", "HouseRoman", "Rasi", "LonDecDeg", "SignLonDMS", "SignLonDecDeg", "DegSize",
            "Nakshatra", "RasiLord", "NakshatraLord", "SubLord", "SubSubLord"
        ])
        
        if return_style == "rasi_wise":
            return self.get_consolidated_chart_data_rasi_wise(planets_df)
        else:
            return {"planets": planets_df, "houses": houses_df}

    def get_consolidated_chart_data_rasi_wise(self, df: pl.DataFrame):
        """
        Organize chart data by Rasi (zodiac sign).
        
        Args:
            df (polars.DataFrame): The planets DataFrame.
            
        Returns:
            dict: A dictionary with data organized by Rasi.
        """
        rasi_wise_data = {}
        
        for rasi in RASHIS:
            rasi_planets = df.filter(pl.col("Rasi") == rasi)
            if rasi_planets.height > 0:
                rasi_wise_data[rasi] = {
                    "planets": rasi_planets.to_dicts(),
                    "rasi_lord": SIGN_LORDS[RASHIS.index(rasi)]
                }
            else:
                rasi_wise_data[rasi] = {
                    "planets": [],
                    "rasi_lord": SIGN_LORDS[RASHIS.index(rasi)]
                }
                
        return rasi_wise_data

    def get_planet_in_house(self, houses_chart: Chart, planets_chart: Chart = None):
        """
        Determine which house each planet is in.
        
        Args:
            houses_chart (Chart): The chart with house data.
            planets_chart (Chart, optional): The chart with planet data. Defaults to None.
            
        Returns:
            dict: A dictionary mapping planet names to house numbers.
        """
        if planets_chart is None:
            planets_chart = houses_chart
            
        # Get house cusps
        house_cusps = []
        for house in houses_chart.houses:
            house_cusps.append(house.lon)
            
        # Get planet positions
        planet_positions = {}
        for planet in planets_chart.objects:
            planet_obj = clean_select_objects_split_str(str(planet))
            planet_name = planet_obj[0]
            planet_positions[planet_name] = planet.lon
            
        # Determine which house each planet is in
        planet_in_house = {}
        
        for planet_name, planet_lon in planet_positions.items():
            for i in range(12):
                house_nr = i + 1
                next_house_nr = (i + 1) % 12 + 1
                
                house_cusp = house_cusps[i]
                next_house_cusp = house_cusps[next_house_nr - 1]
                
                # Handle the case where the next house cusp is in the next zodiac cycle
                if next_house_cusp < house_cusp:
                    next_house_cusp += 360
                    
                # Handle the case where the planet is in the next zodiac cycle
                planet_lon_adj = planet_lon
                if planet_lon < house_cusp:
                    planet_lon_adj += 360
                    
                if house_cusp <= planet_lon_adj < next_house_cusp:
                    planet_in_house[planet_name] = house_nr
                    break
                    
        return planet_in_house

    def get_unique_house_nrs_for_rasi_lord(self, planets_df: pl.DataFrame, planet_name: str):
        """
        Get the unique house numbers for a given Rasi lord.
        
        Args:
            planets_df (polars.DataFrame): The planets DataFrame.
            planet_name (str): The name of the planet.
            
        Returns:
            list: A list of unique house numbers.
        """
        # Filter planets DataFrame to get rows where RasiLord matches the given planet_name
        filtered_df = planets_df.filter(pl.col("RasiLord") == planet_name)
        
        # Get unique house numbers
        unique_houses = filtered_df.select("House").unique().to_series().to_list()
        
        # Sort the house numbers
        unique_houses.sort()
        
        return unique_houses

    def get_planet_wise_significators(self, planets_data: collections.namedtuple, houses_data: collections.namedtuple):
        """
        Calculate planet-wise significators.
        
        Args:
            planets_data (collections.namedtuple): The planets data.
            houses_data (collections.namedtuple): The houses data.
            
        Returns:
            dict: A dictionary of planet-wise significators.
        """
        planets_df = pl.DataFrame(planets_data)
        houses_df = pl.DataFrame(houses_data)
        
        # Rename columns for clarity
        planets_df = planets_df.rename({"Object": "Planet", "HouseNr": "House"})
        
        planet_wise_significators = {}
        
        for planet_row in planets_df.iter_rows(named=True):
            planet_name = planet_row["Planet"]
            
            # Skip the Ascendant
            if planet_name == "Asc":
                continue
                
            # Get the house the planet is in (Star Position)
            star_position = planet_row["House"]
            
            # Get the houses owned by the planet (as a Rasi Lord)
            owned_houses = self.get_unique_house_nrs_for_rasi_lord(planets_df, planet_name)
            
            # Get the houses where the planet is a Nakshatra Lord
            nakshatra_lord_houses = planets_df.filter(pl.col("NakshatraLord") == planet_name).select("House").unique().to_series().to_list()
            
            # Get the houses where the planet is a Sub Lord
            sub_lord_houses = planets_df.filter(pl.col("SubLord") == planet_name).select("House").unique().to_series().to_list()
            
            planet_wise_significators[planet_name] = {
                "star_position": star_position,
                "owned_houses": owned_houses,
                "nakshatra_lord_houses": nakshatra_lord_houses,
                "sub_lord_houses": sub_lord_houses
            }
            
        return planet_wise_significators

    def get_house_wise_significators(self, planets_data: collections.namedtuple, houses_data: collections.namedtuple):
        """
        Calculate house-wise significators.
        
        Args:
            planets_data (collections.namedtuple): The planets data.
            houses_data (collections.namedtuple): The houses data.
            
        Returns:
            dict: A dictionary of house-wise significators.
        """
        planets_df = pl.DataFrame(planets_data)
        houses_df = pl.DataFrame(houses_data)
        
        # Rename columns for clarity
        planets_df = planets_df.rename({"Object": "Planet", "HouseNr": "House"})
        houses_df = houses_df.rename({"Object": "House", "HouseNr": "HouseRoman"})
        
        house_wise_significators = {}
        
        for house_row in houses_df.iter_rows(named=True):
            house_name = house_row["House"]
            house_nr = int(house_name.replace("House", ""))
            
            # Get the planets in this house
            planets_in_house = planets_df.filter(pl.col("House") == house_nr).select("Planet").to_series().to_list()
            
            # Get the Rasi Lord of this house
            rasi_lord = house_row["RasiLord"]
            
            # Get the Nakshatra Lord of this house
            nakshatra_lord = house_row["NakshatraLord"]
            
            # Get the Sub Lord of this house
            sub_lord = house_row["SubLord"]
            
            house_wise_significators[house_name] = {
                "planets_in_house": planets_in_house,
                "rasi_lord": rasi_lord,
                "nakshatra_lord": nakshatra_lord,
                "sub_lord": sub_lord
            }
            
        return house_wise_significators

    def compute_vimshottari_dasa(self, chart: Chart):
        """
        Compute the Vimshottari Dasa periods.
        
        Args:
            chart (Chart): The chart to analyze.
            
        Returns:
            dict: A dictionary of Vimshottari Dasa periods.
        """
        # This is a placeholder for the Vimshottari Dasa calculation
        # The actual implementation would be more complex
        return {"message": "Vimshottari Dasa calculation not implemented yet"} 