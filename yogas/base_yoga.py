class BaseYoga:
    def __init__(self):
        """Initialize the base yoga class."""
        pass
    
    def _get_house_lord(self, house_num, planets_data):
        """Find the lord of a specific house"""
        # First, find the sign in the house
        house_sign = None
        for planet in planets_
            if hasattr(planet, 'Object') and planet.Object.startswith('House') and getattr(planet, 'HouseNr',
                                                                                           None) == house_num:
                house_sign = planet.Rasi
                break

        if not house_sign:
            return None

        # Map signs to their lords
        sign_lords = {
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

        return sign_lords.get(house_sign)

    def _are_planets_conjunct(self, planet1_name, planet2_name, planets_data):
        """Check if two planets are in conjunction (same sign)"""
        if not planet1_name or not planet2_name:
            return False

        planet1_sign = None
        planet2_sign = None

        for planet in planets_
            if planet.Object == planet1_name:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2_name:
                planet2_sign = planet.Rasi

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_specific_planets_conjunct(self, planet1_name, planet2_name, planets_data):
        """Check if two specific planets are in conjunction (same sign)"""
        planet1_sign = None
        planet2_sign = None

        for planet in planets_
            if planet.Object == planet1_name:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2_name:
                planet2_sign = planet.Rasi

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_planets_in_exchange(self, planet1_name, planet2_name, planets_data):
        """Check if two planets are in an exchange (each in the other's sign)"""
        if not planet1_name or not planet2_name:
            return False

        # First get planet signs
        planet1_sign = None
        planet2_sign = None

        for planet in planets_data:
            if planet.Object == planet1_name:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2_name:
                planet2_sign = planet.Rasi

        if not planet1_sign or not planet2_sign:
            return False

        # Map planets to their own signs
        planet_signs = {
            "Sun": ["Leo"],
            "Moon": ["Cancer"],
            "Mercury": ["Gemini", "Virgo"],
            "Venus": ["Taurus", "Libra"],
            "Mars": ["Aries", "Scorpio"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Saturn": ["Capricorn", "Aquarius"]
        }

        # Check if each planet is in the other's sign
        return planet1_sign in planet_signs.get(planet2_name, []) and planet2_sign in planet_signs.get(planet1_name, [])

    def _are_planets_in_aspect(self, planet1_name, planet2_name, planets_data):
        """Check if two planets aspect each other"""
        planet1_data = None
        planet2_data = None

        for planet in planets_
            if planet.Object == planet1_name:
                planet1_data = planet
            elif planet.Object == planet2_name:
                planet2_data = planet

        if not planet1_data or not planet2_
            return False

        # Calculate the difference in degrees
        angle = abs(planet1_data.LonDecDeg - planet2_data.LonDecDeg)
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
        """Check if a planet is aspecting a particular house"""
        # Find house longitude
        house_lon = None
        for obj in planets_
            if hasattr(obj, 'Object') and obj.Object == f"House{house_num}":
                house_lon = obj.LonDecDeg
                break

        if house_lon is None:
            return False

        # Calculate the difference in degrees
        angle = abs(planet.LonDecDeg - house_lon)
        if angle > 180:
            angle = 360 - angle

        # Check standard aspects (conjunction, opposition, trine, square, sextile)
        standard_aspects = [0, 60, 90, 120, 180]
        orbs = {0: 8, 60: 6, 90: 8, 120: 8, 180: 10}

        for aspect in standard_aspects:
            if abs(angle - aspect) <= orbs[aspect]:
                return True

        return False
