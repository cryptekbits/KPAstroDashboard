class BaseYoga:
    """
    Base class for all yoga calculations.
    Provides common utilities and interfaces for yoga detection and formatting.
    """

    def __init__(self):
        """Initialize the base yoga class."""
        # Map signs to their lords
        self.sign_lords = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter"
        }

        # Exaltation signs for planets
        self.exalted_signs = {
            "Sun": "Aries",
            "Moon": "Taurus",
            "Mercury": "Virgo",
            "Venus": "Pisces",
            "Mars": "Capricorn",
            "Jupiter": "Cancer",
            "Saturn": "Libra"
        }

        # Debilitation signs for planets
        self.debilitation_signs = {
            "Sun": "Libra",
            "Moon": "Scorpio",
            "Mercury": "Pisces",
            "Venus": "Virgo",
            "Mars": "Cancer",
            "Jupiter": "Capricorn",
            "Saturn": "Aries"
        }

        # Own signs for planets (moolatrikona and swakshetra)
        self.own_signs = {
            "Sun": ["Leo"],
            "Moon": ["Cancer"],
            "Mercury": ["Gemini", "Virgo"],
            "Venus": ["Taurus", "Libra"],
            "Mars": ["Aries", "Scorpio"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Saturn": ["Capricorn", "Aquarius"]
        }

        # Kendra (angle) houses
        self.kendra_houses = [1, 4, 7, 10]

        # Trikona (trine) houses
        self.trikona_houses = [1, 5, 9]

        # Dusthana (difficult) houses
        self.dusthana_houses = [6, 8, 12]

        # Malefic planets
        self.malefic_planets = ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "North Node", "South Node"]

        # Benefic planets
        self.benefic_planets = ["Moon", "Mercury", "Jupiter", "Venus"]

    def _iter_planets(self, planets_data):
        """
        Yield planets with consistent interface from either DataFrame or object list.

        Parameters:
        -----------
        planets_data : DataFrame or list
            Planetary position data

        Yields:
        -------
        dict
            Standardized planet data dictionary
        """
        if hasattr(planets_data, 'iterrows'):  # DataFrame case
            for _, row in planets_data.iterrows():
                yield {
                    'Object': row['Planet'],
                    'Rasi': row['Sign'],
                    'HouseNr': row['House'] if row['House'] != '-' else None,
                    'LonDecDeg': row.get('LonDecDeg', 0),
                    'isRetroGrade': row['Retrograde'] == 'Y',
                    'Nakshatra': row.get('Nakshatra', '')
                }
        else:  # Object case
            for planet in planets_data:
                yield {
                    'Object': planet.Object,
                    'Rasi': planet.Rasi,
                    'HouseNr': getattr(planet, 'HouseNr', None),
                    'LonDecDeg': getattr(planet, 'LonDecDeg', 0),
                    'isRetroGrade': getattr(planet, 'isRetroGrade', False),
                    'Nakshatra': getattr(planet, 'Nakshatra', '')
                }

    def _get_house_lord(self, house_num, planets_data):
        """
        Find the lord of a specific house.

        Parameters:
        -----------
        house_num : int
            House number (1-12)
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        str or None
            Name of the planet that rules the house, or None if not found
        """
        # First, find the sign in the house
        house_sign = None
        for planet in self._iter_planets(planets_data):
            if planet['Object'].startswith('House') and planet.get('HouseNr') == house_num:
                house_sign = planet['Rasi']
                break

        if not house_sign:
            return None

        return self.sign_lords.get(house_sign)

    def _are_planets_conjunct(self, planet1_name, planet2_name, planets_data):
        """
        Check if two planets are in conjunction (same sign).

        Parameters:
        -----------
        planet1_name : str
            Name of the first planet
        planet2_name : str
            Name of the second planet
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        bool
            True if planets are conjunct, False otherwise
        """
        if not planet1_name or not planet2_name:
            return False

        planet1_sign = None
        planet2_sign = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == planet1_name:
                planet1_sign = planet['Rasi']
            elif planet['Object'] == planet2_name:
                planet2_sign = planet['Rasi']

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_specific_planets_conjunct(self, planet1_name, planet2_name, planets_data):
        """
        Check if two specific planets are in conjunction (same sign).

        Parameters:
        -----------
        planet1_name : str
            Name of the first planet
        planet2_name : str
            Name of the second planet
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        bool
            True if planets are conjunct, False otherwise
        """
        planet1_sign = None
        planet2_sign = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == planet1_name:
                planet1_sign = planet['Rasi']
            elif planet['Object'] == planet2_name:
                planet2_sign = planet['Rasi']

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_planets_in_exchange(self, planet1_name, planet2_name, planets_data):
        """
        Check if two planets are in an exchange (each in the other's sign).

        Parameters:
        -----------
        planet1_name : str
            Name of the first planet
        planet2_name : str
            Name of the second planet
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        bool
            True if planets are in exchange, False otherwise
        """
        if not planet1_name or not planet2_name:
            return False

        # First get planet signs
        planet1_sign = None
        planet2_sign = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == planet1_name:
                planet1_sign = planet['Rasi']
            elif planet['Object'] == planet2_name:
                planet2_sign = planet['Rasi']

        if not planet1_sign or not planet2_sign:
            return False

        # Check if each planet is in the other's sign
        return planet1_sign in self.own_signs.get(planet2_name, []) and planet2_sign in self.own_signs.get(planet1_name,
                                                                                                           [])

    def _are_planets_in_aspect(self, planet1_name, planet2_name, planets_data):
        """
        Check if two planets aspect each other.

        Parameters:
        -----------
        planet1_name : str
            Name of the first planet
        planet2_name : str
            Name of the second planet
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        bool
            True if planets are in aspect, False otherwise
        """
        planet1_data = None
        planet2_data = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == planet1_name:
                planet1_data = planet
            elif planet['Object'] == planet2_name:
                planet2_data = planet

        if not planet1_data or not planet2_data:
            return False

        # Calculate the difference in degrees
        angle = abs(planet1_data['LonDecDeg'] - planet2_data['LonDecDeg'])
        if angle > 180:
            angle = 360 - angle

        # Check standard aspects (conjunction, opposition, trine, square, sextile)
        standard_aspects = [0, 60, 90, 120, 180]
        orbs = {0: 8, 60: 6, 90: 8, 120: 8, 180: 10}

        for aspect in standard_aspects:
            if abs(angle - aspect) <= orbs[aspect]:
                return True

        return False

    def _is_planet_aspecting_house(self, planet, house_num, planets_data):
        """
        Check if a planet is aspecting a particular house.

        Parameters:
        -----------
        planet : dict
            Planet data dictionary
        house_num : int
            House number (1-12)
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        bool
            True if the planet is aspecting the house, False otherwise
        """
        # Find house longitude
        house_lon = None
        for obj in self._iter_planets(planets_data):
            if obj['Object'] == f"House{house_num}":
                house_lon = obj['LonDecDeg']
                break

        if house_lon is None:
            return False

        # Calculate the difference in degrees
        angle = abs(planet['LonDecDeg'] - house_lon)
        if angle > 180:
            angle = 360 - angle

        # Check standard aspects (conjunction, opposition, trine, square, sextile)
        standard_aspects = [0, 60, 90, 120, 180]
        orbs = {0: 8, 60: 6, 90: 8, 120: 8, 180: 10}

        for aspect in standard_aspects:
            if abs(angle - aspect) <= orbs[aspect]:
                return True

        return False

    def _is_planet_in_own_sign(self, planet_name, sign):
        """
        Check if a planet is in its own sign.

        Parameters:
        -----------
        planet_name : str
            Name of the planet
        sign : str
            Sign to check

        Returns:
        --------
        bool
            True if the planet is in its own sign, False otherwise
        """
        return sign in self.own_signs.get(planet_name, [])

    def _is_planet_exalted(self, planet_name, sign):
        """
        Check if a planet is exalted in the given sign.

        Parameters:
        -----------
        planet_name : str
            Name of the planet
        sign : str
            Sign to check

        Returns:
        --------
        bool
            True if the planet is exalted, False otherwise
        """
        return self.exalted_signs.get(planet_name) == sign

    def _is_planet_debilitated(self, planet_name, sign):
        """
        Check if a planet is debilitated in the given sign.

        Parameters:
        -----------
        planet_name : str
            Name of the planet
        sign : str
            Sign to check

        Returns:
        --------
        bool
            True if the planet is debilitated, False otherwise
        """
        return self.debilitation_signs.get(planet_name) == sign

    def _is_in_kendra(self, house_num):
        """
        Check if a house is a kendra (angle) house.

        Parameters:
        -----------
        house_num : int
            House number to check

        Returns:
        --------
        bool
            True if the house is a kendra, False otherwise
        """
        return house_num in self.kendra_houses

    def _is_in_trikona(self, house_num):
        """
        Check if a house is a trikona (trine) house.

        Parameters:
        -----------
        house_num : int
            House number to check

        Returns:
        --------
        bool
            True if the house is a trikona, False otherwise
        """
        return house_num in self.trikona_houses

    def _is_in_dusthana(self, house_num):
        """
        Check if a house is a dusthana (difficult) house.

        Parameters:
        -----------
        house_num : int
            House number to check

        Returns:
        --------
        bool
            True if the house is a dusthana, False otherwise
        """
        return house_num in self.dusthana_houses

    def _format_planet_info(self, planet_data):
        """
        Format planet information for display in the result.

        Parameters:
        -----------
        planet_data : dict
            Planet data dictionary

        Returns:
        --------
        str
            Formatted planet information string
        """
        house_info = f"House {planet_data['HouseNr']}" if planet_data.get('HouseNr') else ""
        if house_info and planet_data.get('Rasi'):
            house_info += ", "

        return f"{planet_data['Object']} ({house_info}{planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)"

    def _get_planet_by_name(self, planet_name, planets_data):
        """
        Get planet data by name.

        Parameters:
        -----------
        planet_name : str
            Name of the planet
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        dict or None
            Planet data dictionary or None if not found
        """
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == planet_name:
                return planet
        return None

    def create_yoga_result(self, name, planets_info):
        """
        Create a standard yoga result dictionary.

        Parameters:
        -----------
        name : str
            Name of the yoga
        planets_info : list
            List of formatted planet information strings

        Returns:
        --------
        dict
            Yoga result dictionary
        """
        return {
            "name": name,
            "planets_info": planets_info
        }