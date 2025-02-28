"""
Core Vedic astrology calculations for the KP Astrology system.
This is a wrapper around flatlib's functionality with KP-specific enhancements.
"""
from typing import Dict, List, Optional, Tuple, Any, NamedTuple, Union
from datetime import datetime
import collections
import pandas as pd

# Import flatlib components
from flatlib import const, aspects
from flatlib.chart import Chart
from flatlib.geopos import GeoPos
from flatlib.datetime import Datetime, Date
from flatlib.object import GenericObject

# Import utility functions
from .utils import dms_to_decdeg, utc_offset_str_to_float

# Constants for ayanamsa systems
AYANAMSA_MAPPING = {
    "Lahiri": const.AY_LAHIRI,
    "Lahiri_1940": const.AY_LAHIRI_1940,
    "Lahiri_VP285": const.AY_LAHIRI_VP285,
    "Lahiri_ICRC": const.AY_LAHIRI_ICRC,
    "Raman": const.AY_RAMAN,
    "Krishnamurti": const.AY_KRISHNAMURTI,
    "Krishnamurti_Senthilathiban": const.AY_KRISHNAMURTI_SENTHILATHIBAN,
}

# Constants for house systems
HOUSE_SYSTEM_MAPPING = {
    "Placidus": const.HOUSES_PLACIDUS,
    "Equal": const.HOUSES_EQUAL,
    "Equal 2": const.HOUSES_EQUAL_2,
    "Whole Sign": const.HOUSES_WHOLE_SIGN,
}

# Constants for aspects
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

# Roman numerals for houses
ROMAN_HOUSE_NUMBERS = {
    'House1': 'I', 'House2': 'II', 'House3': 'III', 'House4': 'IV',
    'House5': 'V', 'House6': 'VI', 'House7': 'VII', 'House8': 'VIII',
    'House9': 'IX', 'House10': 'X', 'House11': 'XI', 'House12': 'XII'
}

# Zodiac signs
RASHIS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
    'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Lords of the 12 Zodiac Signs
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

# Nakshatras
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashīrsha', 'Ardra',
    'Punarvasu', 'Pushya', 'Āshleshā', 'Maghā', 'PūrvaPhalgunī', 'UttaraPhalgunī',
    'Hasta', 'Chitra', 'Svati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula',
    'PurvaAshadha', 'UttaraAshadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'PurvaBhādrapadā', 'UttaraBhādrapadā', 'Revati'
]

# Column names for data tables
PLANETS_TABLE_COLS = [
    "Object", "Rasi", "isRetroGrade", "LonDecDeg", "SignLonDMS", "SignLonDecDeg",
    "LatDMS", "Nakshatra", "RasiLord", "NakshatraLord", "SubLord",
    "SubSubLord", "HouseNr"
]

HOUSES_TABLE_COLS = [
    "Object", "HouseNr", "Rasi", "LonDecDeg", "SignLonDMS", "SignLonDecDeg",
    "DegSize", "Nakshatra", "RasiLord", "NakshatraLord", "SubLord", "SubSubLord"
]


class VedicChart:
    """Modern wrapper for Vedic/KP astrological chart calculations."""

    def __init__(self,
                 dt: datetime,
                 latitude: float,
                 longitude: float,
                 timezone_str: str = "UTC",
                 ayanamsa: str = "Krishnamurti",
                 house_system: str = "Placidus"):
        """
        Initialize the Vedic chart calculator.

        Args:
            dt: Date and time for the chart
            latitude: Latitude of location
            longitude: Longitude of location
            timezone_str: Timezone string
            ayanamsa: Ayanamsa system to use
            house_system: House system to use
        """
        self.dt = dt
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_str = timezone_str
        self.ayanamsa = ayanamsa
        self.house_system = house_system

        # Calculate UTC offset
        import pytz
        tz = pytz.timezone(timezone_str)
        offset = dt.astimezone(tz).strftime('%z')
        hours, minutes = int(offset[0:3]), int(offset[0] + offset[3:5])
        self.utc_offset = f"{'+' if hours >= 0 else ''}{hours}:{minutes:02d}"

        # Create the chart
        self.chart = self._generate_chart()

        # Calculate planet and house data
        self.planets_data = self._get_planets_data()
        self.houses_data = self._get_houses_data()

        print(f"VedicChart initialized for {dt} at {latitude}, {longitude}")

    def _get_ayanamsa(self) -> Optional[str]:
        """Get the flatlib ayanamsa constant from the name."""
        return AYANAMSA_MAPPING.get(self.ayanamsa, None)

    def _get_house_system(self) -> Optional[str]:
        """Get the flatlib house system constant from the name."""
        return HOUSE_SYSTEM_MAPPING.get(self.house_system, None)

    def _generate_chart(self) -> Chart:
        """Generate a flatlib Chart object for the given data."""
        date = Datetime(
            [self.dt.year, self.dt.month, self.dt.day],
            ["+", self.dt.hour, self.dt.minute, self.dt.second],
            self.utc_offset
        )
        geopos = GeoPos(self.latitude, self.longitude)
        chart = Chart(
            date,
            geopos,
            IDs=const.LIST_OBJECTS,
            hsys=self._get_house_system(),
            mode=self._get_ayanamsa()
        )
        return chart

    def _clean_object_string(self, input_str: str) -> List[str]:
        """Clean and parse object string from flatlib."""
        cleaned_str = (input_str.strip('<').strip('>')
                       .replace("North Node", "Rahu")
                       .replace("South Node", "Ketu")
                       .replace("Pars Fortuna", "Fortuna"))
        return cleaned_str.split()

    def _get_rl_nl_sl_data(self, deg: float) -> Dict[str, Any]:
        """
        Calculate Rashi Lord, Nakshatra, Nakshatra Lord, Sub Lord, and Sub-Sub Lord.

        Args:
            deg: Longitude in decimal degrees

        Returns:
            Dictionary with lord information
        """
        # KP sub-division duration for each planet
        duration = [7, 20, 6, 10, 7, 18, 16, 19, 17]

        # KP planet lords in sequence
        lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

        # Generate lords for all 27 nakshatras
        star_lords = lords * 3

        # Compute sign (rashi) information
        sign_deg = deg % 360  # Normalize degree to [0, 360)
        sign_index = int(sign_deg // 30)  # Each zodiac sign is 30 degrees

        # Compute Nakshatra details
        nakshatra_deg = 13.333333  # Each nakshatra is 13°20' (13.333... degrees)
        nakshatra_index = int(sign_deg // nakshatra_deg)  # Find the nakshatra index
        nakshatra_index = nakshatra_index % 27  # Ensure index is within bounds

        # Calculate pada (quarter of nakshatra)
        pada_deg = nakshatra_deg / 4  # Each pada is 3°20' (3.333... degrees)
        nakshatra_position = sign_deg % nakshatra_deg
        pada = int(nakshatra_position // pada_deg) + 1

        # Compute Sub and Sub-Sub Lords (KP approach)
        # This is a simplified version of the complex KP algorithm
        deg = deg - 120 * int(deg / 120)  # Normalize to 0-120 range for KP calculations
        degcum = 0
        i = 0

        while i < 9:
            deg_nl = 360 / 27  # Degree span of each nakshatra lord
            j = i
            while True:
                deg_sl = deg_nl * duration[j] / 120  # Degree span for sub-lord
                k = j
                while True:
                    deg_ss = deg_sl * duration[k] / 120  # Degree span for sub-sub-lord
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

        # Fallback in case of calculation issues
        return {
            "Nakshatra": NAKSHATRAS[nakshatra_index],
            "Pada": pada,
            "NakshatraLord": star_lords[nakshatra_index],
            "RasiLord": SIGN_LORDS[sign_index],
            "SubLord": "Unknown",
            "SubSubLord": "Unknown"
        }

    def _get_ascendant_data(self, asc_data: GenericObject, PlanetsDataCollection) -> NamedTuple:
        """
        Generate Ascendant data in the format of planets data.

        Args:
            asc_data: Ascendant object from chart
            PlanetsDataCollection: NamedTuple class for planets data

        Returns:
            NamedTuple instance with ascendant data
        """
        asc_chart_data = self._clean_object_string(str(asc_data))
        asc_rl_nl_sl_data = self._get_rl_nl_sl_data(deg=asc_data.lon)

        # Create a dictionary with None values for all fields
        data_dict = {field: None for field in PlanetsDataCollection._fields}

        # Update with ascendant data
        data_dict["Object"] = asc_chart_data[0]
        data_dict["Rasi"] = asc_data.sign
        data_dict["SignLonDMS"] = asc_chart_data[2]
        data_dict["Nakshatra"] = asc_rl_nl_sl_data.get("Nakshatra", None)
        data_dict["RasiLord"] = asc_rl_nl_sl_data.get("RasiLord", None)
        data_dict["SubLord"] = asc_rl_nl_sl_data.get("SubLord", None)
        data_dict["SubSubLord"] = asc_rl_nl_sl_data.get("SubSubLord", None)
        data_dict["NakshatraLord"] = asc_rl_nl_sl_data.get("NakshatraLord", None)
        data_dict["isRetroGrade"] = None
        data_dict["LonDecDeg"] = round(asc_data.lon, 3)
        data_dict["SignLonDecDeg"] = round(asc_data.signlon, 3)
        data_dict["LatDMS"] = None
        data_dict["HouseNr"] = 1

        return PlanetsDataCollection(**data_dict)

    def _get_planets_data(self) -> List[NamedTuple]:
        """
        Generate planetary position data.

        Returns:
            List of NamedTuple instances with planet data
        """
        # Create NamedTuple for storing planet data
        PlanetsData = collections.namedtuple("PlanetsData", PLANETS_TABLE_COLS)

        # Get planet-house relationships
        planet_in_house = self._get_planet_in_house()

        # Get Ascendant data
        ascendant_data = self._get_ascendant_data(
            asc_data=self.chart.get(const.ASC),
            PlanetsDataCollection=PlanetsData
        )

        # Process data for all planets
        planets_data = [ascendant_data]

        for planet in self.chart.objects:
            planet_obj = self._clean_object_string(str(planet))
            planet_name = planet_obj[0]
            planet_lon_deg = planet_obj[2] if len(planet_obj) > 2 else None
            planet_lat_deg = planet_obj[3] if len(planet_obj) > 3 else None

            # Get additional KP details
            rl_nl_sl_data = self._get_rl_nl_sl_data(deg=planet.lon)

            # Get the house the planet is in
            planet_house = planet_in_house.get(planet_name, None)

            # Add to data collection
            planets_data.append(PlanetsData(
                planet_name,
                planet.sign,
                planet.isRetrograde(),
                round(planet.lon, 3),
                planet_lon_deg,
                round(planet.signlon, 3),
                planet_lat_deg,
                rl_nl_sl_data.get("Nakshatra", None),
                rl_nl_sl_data.get("RasiLord", None),
                rl_nl_sl_data.get("NakshatraLord", None),
                rl_nl_sl_data.get("SubLord", None),
                rl_nl_sl_data.get("SubSubLord", None),
                planet_house
            ))

        return planets_data

    def _get_houses_data(self) -> List[NamedTuple]:
        """
        Generate house position data.

        Returns:
            List of NamedTuple instances with house data
        """
        # Create NamedTuple for storing house data
        HousesData = collections.namedtuple("HousesData", HOUSES_TABLE_COLS)

        # Process data for all houses
        houses_data = []

        for house in self.chart.houses:
            house_obj = str(house).strip('<').strip('>').split()

            house_name = house_obj[0]
            house_lon_deg = house_obj[2] if len(house_obj) > 2 else None
            house_size = round(float(house_obj[3]), 3) if len(house_obj) > 3 else None

            house_nr = int(house_name.strip("House"))
            house_roman_nr = ROMAN_HOUSE_NUMBERS.get(house_name)

            # Get additional KP details
            rl_nl_sl_data = self._get_rl_nl_sl_data(deg=house.lon)

            # Add to data collection
            houses_data.append(HousesData(
                house_roman_nr,
                house_nr,
                house.sign,
                round(house.lon, 3),
                house_lon_deg,
                round(house.signlon, 3),
                house_size,
                rl_nl_sl_data.get("Nakshatra", None),
                rl_nl_sl_data.get("RasiLord", None),
                rl_nl_sl_data.get("NakshatraLord", None),
                rl_nl_sl_data.get("SubLord", None),
                rl_nl_sl_data.get("SubSubLord", None)
            ))

        return houses_data

    def _get_planet_in_house(self) -> Dict[str, int]:
        """
        Determine which house each planet is in.

        Returns:
            Dictionary mapping planet names to house numbers
        """
        planet_in_house = {}

        # Get house cusps with their house numbers
        cusps = [(house.lon, int(house.id.replace('House', ''))) for house in self.chart.houses]

        # Sort by longitude
        cusps = sorted(cusps, key=lambda x: x[0])

        # Add the first cusp plus 360° as the end of the zodiac
        cusps.append((cusps[0][0] + 360, cusps[0][1]))

        for planet in self.chart.objects:
            planet_name = self._clean_object_string(str(planet))[0]
            planet_lon = planet.lon

            # Find the house
            house_found = False
            for i in range(len(cusps) - 1):
                if cusps[i][0] <= planet_lon < cusps[i + 1][0]:
                    planet_in_house[planet_name] = cusps[i][1]
                    house_found = True
                    break

            # Edge case: If we're very close to the 360° boundary
            if not house_found:
                # Try with normalized longitude
                norm_lon = planet_lon % 360
                for i in range(len(cusps) - 1):
                    if cusps[i][0] <= norm_lon < cusps[i + 1][0]:
                        planet_in_house[planet_name] = cusps[i][1]
                        house_found = True
                        break

            # Validate house number
            if planet_name in planet_in_house:
                house_nr = planet_in_house[planet_name]
                if house_nr < 1 or house_nr > 12:
                    # Fix invalid house number
                    print(f"Warning: Invalid house {house_nr} calculated for {planet_name}. Correcting.")
                    planet_in_house[planet_name] = ((house_nr - 1) % 12) + 1

        return planet_in_house

    def get_planetary_aspects(self) -> List[Dict]:
        """
        Get all planetary aspects in the chart.

        Returns:
            List of dictionaries with aspect information
        """
        planets = [
            const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER,
            const.VENUS, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
            const.NORTH_NODE, const.SOUTH_NODE
        ]

        aspects_dict = []

        for p1 in planets:
            for p2 in planets:
                if p1 != p2:
                    obj1 = self.chart.get(p1)
                    obj2 = self.chart.get(p2)
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

    def get_consolidated_chart_data(self, return_style: str = None) -> Union[Dict, List[Dict]]:
        """
        Create consolidated chart data where all objects are listed by rasi (sign).

        Args:
            return_style: If "dataframe_records", returns list of dictionaries,
                          otherwise returns dictionary grouped by rasi

        Returns:
            Consolidated chart data
        """
        import polars as pl

        # Construct DataFrames of planets and houses data
        req_cols = ["Rasi", "Object", "isRetroGrade", "LonDecDeg", "SignLonDMS", "SignLonDecDeg"]

        # Convert namedtuples to dictionaries
        planets_dict = [p._asdict() for p in self.planets_data]
        houses_dict = [h._asdict() for h in self.houses_data]

        # Create DataFrames
        planets_df = pl.DataFrame(planets_dict).select(req_cols)

        # Add isRetroGrade column to houses data (always False)
        houses_df = pl.DataFrame(houses_dict) \
            .with_columns(pl.lit(False).alias("isRetroGrade")) \
            .select(req_cols)

        # Create joined dataframe
        df_concat = pl.concat([houses_df, planets_df])

        # Group by 'Rasi' and aggregate
        result_df = df_concat.group_by('Rasi').agg([
            pl.col('Object').map_elements(list, return_dtype=pl.Object).alias('Object'),
            pl.col('isRetroGrade').map_elements(list, return_dtype=pl.Object).alias('isRetroGrade'),
            pl.col('LonDecDeg').map_elements(list, return_dtype=pl.Object).alias('LonDecDeg'),
            pl.col('SignLonDMS').map_elements(list, return_dtype=pl.Object).alias('SignLonDMS'),
            pl.col('SignLonDecDeg').map_elements(list, return_dtype=pl.Object).alias('SignLonDecDeg')
        ])

        # Sort by Rashi order
        result_df = result_df.with_columns(
            pl.col('Rasi').map_elements(lambda rasi: RASHIS.index(rasi)).alias('RashiOrder')
        )
        result_df = result_df.sort('RashiOrder').drop('RashiOrder')

        if return_style == "dataframe_records":
            return result_df.to_dicts()
        else:
            # Convert to dictionary grouped by Rasi
            return self._get_rasi_grouped_data(result_df)

    def _get_rasi_grouped_data(self, df) -> Dict:
        """
        Convert DataFrame to dictionary grouped by Rasi.

        Args:
            df: DataFrame with Rasi groups

        Returns:
            Dictionary with data grouped by Rasi
        """
        final_dict = {}
        columns = df.columns

        for row in df.iter_rows():
            rasi = row[columns.index('Rasi')]
            final_dict[rasi] = {}

            for obj, is_retrograde, lon_dd, lon_dms, sign_lon_dd in zip(
                    row[columns.index('Object')],
                    row[columns.index('isRetroGrade')],
                    row[columns.index('LonDecDeg')],
                    row[columns.index('SignLonDMS')],
                    row[columns.index('SignLonDecDeg')]
            ):
                final_dict[rasi][obj] = {
                    "is_Retrograde": is_retrograde,
                    "LonDecDeg": lon_dd,
                    "SignLonDMS": lon_dms,
                    "SignLonDecDeg": sign_lon_dd
                }

        return final_dict

    def get_planet_significators(self) -> List[Dict]:
        """
        Generate ABCD significator table for each planet.

        Returns:
            List of dictionaries with planet significator data
        """
        significators = []

        # Filter planets_data to remove objects like "Asc", "Chiron", "Syzygy", "Fortuna"
        planets = [p for p in self.planets_data if p.Object not in ["Asc", "Chiron", "Syzygy", "Fortuna"]]

        # Get house deposition for each planet
        planets_house = {p.Object: p.HouseNr for p in planets}

        for planet in planets:
            # A. House occupied by the star lord (Nakshatra Lord) of the planet
            significator_a = planets_house.get(planet.NakshatraLord, None)

            # B. House occupied by the planet itself
            significator_b = planet.HouseNr

            # C. House nrs where the star lord planet is also the rashi lord
            significator_c = [h.HouseNr for h in self.houses_data if h.RasiLord == planet.NakshatraLord]

            # D. House nrs where the planet itself is also the rashi lord
            significator_d = [h.HouseNr for h in self.houses_data if h.RasiLord == planet.Object]

            significators.append({
                "Planet": planet.Object,
                "A": significator_a,
                "B": significator_b,
                "C": significator_c,
                "D": significator_d
            })

        return significators

    def get_house_significators(self) -> List[Dict]:
        """
        Generate ABCD significator table for each house.

        Returns:
            List of dictionaries with house significator data
        """
        significators = []

        # Filter planets_data to remove objects like "Asc", "Chiron", "Syzygy", "Fortuna"
        planets = [p for p in self.planets_data if p.Object not in ["Asc", "Chiron", "Syzygy", "Fortuna"]]

        # Create mapping of planets to their star lords
        planet_to_star_lord = {p.Object: p.NakshatraLord for p in planets}

        for house in self.houses_data:
            # A. Planets in the star of occupants of that house
            # A1. Get all planets in this house
            occupant_house_planets = [p.Object for p in planets if p.HouseNr == house.HouseNr]

            # A2. Find planets whose star lord is one of the occupants
            significator_a = [p.Object for p in planets if p.NakshatraLord in occupant_house_planets]

            # B. Planets in that house
            significator_b = occupant_house_planets

            # C. Planets in the star of owners of that house
            significator_c = [p for p, lord in planet_to_star_lord.items() if lord == house.RasiLord]

            # D. Owner of that house
            significator_d = house.RasiLord

            significators.append({
                "House": house.Object,
                "A": significator_a,
                "B": significator_b,
                "C": significator_c,
                "D": significator_d
            })

        return significators

    def compute_vimshottari_dasa(self) -> Dict:
        """
        Compute Vimshottari Dasa periods.

        Returns:
            Dictionary with dasa information
        """
        from .utils import compute_new_date

        # Get the moon object
        moon = self.chart.get(const.MOON)

        # Moon's details
        moon_rl_nl_sl = self._get_rl_nl_sl_data(deg=moon.lon)
        moon_nakshatra = moon_rl_nl_sl["Nakshatra"]
        moon_nakshatra_lord = moon_rl_nl_sl["NakshatraLord"]

        # Define the sequence of Dasa periods and their lengths
        dasa_sequence = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        dasa_lengths = [7, 20, 6, 10, 7, 18, 16, 19, 17]

        # Find the starting point in the sequence
        start_index = dasa_sequence.index(moon_nakshatra_lord)

        # Reorder the sequence to start with Moon's nakshatra lord
        dasa_sequence = dasa_sequence[start_index:] + dasa_sequence[:start_index]
        dasa_lengths = dasa_lengths[start_index:] + dasa_lengths[:start_index]
        dasa_order = dict(zip(dasa_sequence, dasa_lengths))

        # Compute remaining portion of starting dasa
        typical_nakshatra_arc = 800  # degree-minutes (13°20')
        nakshatra_start = NAKSHATRAS.index(moon_nakshatra) * typical_nakshatra_arc
        moon_lon_mins = round(moon.lon * 60, 2)  # Convert to minutes
        elapsed_moon_mins = moon_lon_mins - nakshatra_start
        remaining_arc_mins = typical_nakshatra_arc - elapsed_moon_mins

        # Calculate starting dasa duration
        starting_dasa_duration = dasa_order[moon_nakshatra_lord]
        start_dasa_remaining_duration = (starting_dasa_duration / typical_nakshatra_arc) * remaining_arc_mins
        start_dasa_elapsed_duration = starting_dasa_duration - start_dasa_remaining_duration

        # Compute dasa periods
        vimshottari_dasa = {}

        # Convert datetime to tuple for calculation
        chart_date = (
            self.dt.year, self.dt.month, self.dt.day,
            self.dt.hour, self.dt.minute
        )

        # Calculate dasa start date (going backward from birth time)
        dasa_start_date = compute_new_date(
            start_date=chart_date,
            diff_value=start_dasa_elapsed_duration,
            direction="backward"
        )

        # Generate all dasa periods
        for i in range(len(dasa_sequence)):
            dasa = dasa_sequence[i]
            dasa_length = dasa_lengths[i]

            # Calculate dasa end date
            dasa_end_date = compute_new_date(
                start_date=tuple(dasa_start_date.timetuple())[:5],
                diff_value=dasa_length,
                direction="forward"
            )

            # Format dates
            start_str = dasa_start_date.strftime("%d-%m-%Y")
            end_str = dasa_end_date.strftime("%d-%m-%Y")

            # Initialize dasa entry
            vimshottari_dasa[dasa] = {
                'start': start_str,
                'end': end_str,
                'bhuktis': {}
            }

            # Calculate bhuktis (sub-periods)
            bhukti_start_date = dasa_start_date

            # Reorder sequence for bhuktis
            bhukti_start_index = dasa_sequence.index(dasa)
            bhukti_sequence = dasa_sequence[bhukti_start_index:] + dasa_sequence[:bhukti_start_index]
            bhukti_lengths = dasa_lengths[bhukti_start_index:] + dasa_lengths[:bhukti_start_index]

            for j in range(len(bhukti_sequence)):
                bhukti = bhukti_sequence[j]

                # Calculate bhukti length (proportional to dasa length)
                bhukti_length = dasa_length * bhukti_lengths[j] / 120

                # Calculate bhukti end date
                bhukti_end_date = compute_new_date(
                    start_date=tuple(bhukti_start_date.timetuple())[:5],
                    diff_value=bhukti_length,
                    direction="forward"
                )

                # Format dates
                bhukti_start_str = bhukti_start_date.strftime("%d-%m-%Y")
                bhukti_end_str = bhukti_end_date.strftime("%d-%m-%Y")

                # Add bhukti entry
                vimshottari_dasa[dasa]['bhuktis'][bhukti] = {
                    'start': bhukti_start_str,
                    'end': bhukti_end_str
                }

                bhukti_start_date = bhukti_end_date

            dasa_start_date = dasa_end_date

        return vimshottari_dasa

    def to_dataframe(self) -> Dict[str, pd.DataFrame]:
        """
        Convert chart data to pandas DataFrames.

        Returns:
            Dictionary of DataFrames
        """
        # Convert planets data
        planets_df = pd.DataFrame([p._asdict() for p in self.planets_data])

        # Convert houses data
        houses_df = pd.DataFrame([h._asdict() for h in self.houses_data])

        # Get aspects
        aspects = self.get_planetary_aspects()
        aspects_df = pd.DataFrame(aspects)

        # Get significators
        planet_sig = self.get_planet_significators()
        planet_sig_df = pd.DataFrame(planet_sig)

        house_sig = self.get_house_significators()
        house_sig_df = pd.DataFrame(house_sig)

        # Return all data
        return {
            "planets": planets_df,
            "houses": houses_df,
            "aspects": aspects_df,
            "planet_significators": planet_sig_df,
            "house_significators": house_sig_df
        }