"""
Positive (beneficial) yogas in KP Astrology.
"""
from typing import Dict, List, Optional
import math
from .yoga_base import Yoga, YogaType, YogaRegistry


@YogaRegistry.register
class BudhaAdityaYoga(Yoga):
    """Mercury and Sun conjunction yoga - intellectual brilliance."""

    def __init__(self):
        super().__init__(
            name="Budha-Aditya Yoga",
            description="Mercury and Sun in same sign. Grants intelligence, education, communication skills.",
            yoga_type=YogaType.POSITIVE,
            required_planets=["Sun", "Mercury"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Mercury and Sun are in the same sign."""
        sun_sign = None
        mercury_sign = None

        for planet in planets_data:
            if planet.Object == "Sun":
                sun_sign = planet.Rasi
            elif planet.Object == "Mercury":
                mercury_sign = planet.Rasi

        return sun_sign and mercury_sign and sun_sign == mercury_sign


@YogaRegistry.register
class GajaKesariYoga(Yoga):
    """Jupiter and Moon in quadrant from each other - success and fame."""

    def __init__(self):
        super().__init__(
            name="Gaja-Kesari Yoga",
            description="Jupiter and Moon in quadrant/kendra from each other. Grants success, fame, and prosperity.",
            yoga_type=YogaType.POSITIVE,
            required_planets=["Moon", "Jupiter"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Jupiter and Moon are in quadrant from each other."""
        moon_pos = None
        jupiter_pos = None

        for planet in planets_data:
            if planet.Object == "Moon":
                moon_pos = planet.LonDecDeg
            elif planet.Object == "Jupiter":
                jupiter_pos = planet.LonDecDeg

        if moon_pos is not None and jupiter_pos is not None:
            angle = abs(moon_pos - jupiter_pos)
            if angle > 180:
                angle = 360 - angle

            # Check for quadrant positions (90° multiples with orb)
            return any(abs(angle - quad) <= 10 for quad in [0, 90, 180, 270])

        return False


@YogaRegistry.register
class RajaYoga(Yoga):
    """Lord of trine and kendra conjunct - power and authority."""

    def __init__(self):
        super().__init__(
            name="Raja Yoga",
            description="Lords of trine (1,5,9) and kendra (1,4,7,10) houses conjunct or aspect each other. Grants power, authority, success.",
            yoga_type=YogaType.POSITIVE,
            required_planets=[]  # Depends on house lords
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if lords of trine and kendra houses are conjunct or aspect each other."""
        # Find house lordships
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # Trine and kendra houses
        trine_houses = [1, 5, 9]
        kendra_houses = [1, 4, 7, 10]

        # Get lords of these houses
        trine_lords = [house_lords.get(h) for h in trine_houses if house_lords.get(h)]
        kendra_lords = [house_lords.get(h) for h in kendra_houses if house_lords.get(h)]

        # Check for conjunction or aspect between any trine lord and any kendra lord
        for trine_lord in trine_lords:
            for kendra_lord in kendra_lords:
                if trine_lord and kendra_lord and trine_lord != kendra_lord:
                    if (self._are_planets_conjunct(trine_lord, kendra_lord, planets_data) or
                            self._are_planets_in_aspect(trine_lord, kendra_lord, planets_data)):
                        return True

        return False

    def _get_house_lord(self, house_num: int, planets_data: List) -> Optional[str]:
        """Find the lord of a specific house."""
        # Find the sign in the house
        house_sign = None
        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr == house_num:
                house_sign = planet.Rasi
                break

        if not house_sign:
            return None

        # Map signs to their lords
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }

        return sign_lords.get(house_sign)

    def _are_planets_conjunct(self, planet1: str, planet2: str, planets_data: List) -> bool:
        """Check if two planets are in the same sign."""
        planet1_sign = None
        planet2_sign = None

        for planet in planets_data:
            if planet.Object == planet1:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2:
                planet2_sign = planet.Rasi

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_planets_in_aspect(self, planet1: str, planet2: str, planets_data: List) -> bool:
        """Check if two planets aspect each other."""
        planet1_pos = None
        planet2_pos = None

        for planet in planets_data:
            if planet.Object == planet1:
                planet1_pos = planet.LonDecDeg
            elif planet.Object == planet2:
                planet2_pos = planet.LonDecDeg

        if not planet1_pos or not planet2_pos:
            return False

        # Calculate angle between planets
        angle = abs(planet1_pos - planet2_pos)
        if angle > 180:
            angle = 360 - angle

        # Check standard aspects with appropriate orbs
        aspects = {0: 8, 60: 6, 90: 8, 120: 8, 180: 10}
        return any(abs(angle - asp) <= orb for asp, orb in aspects.items())


@YogaRegistry.register
class DhanaYoga(Yoga):
    """Lords of 2nd and 11th houses conjunct - wealth."""

    def __init__(self):
        super().__init__(
            name="Dhana Yoga",
            description="Lords of 2nd and 11th houses conjunct or exchange. Brings wealth and financial prosperity.",
            yoga_type=YogaType.POSITIVE,
            required_planets=[]  # Depends on house lords
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if lords of 2nd and 11th houses are conjunct or in exchange."""
        # Find house lords
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # Get 2nd and 11th house lords
        lord_2 = house_lords.get(2)
        lord_11 = house_lords.get(11)

        if not lord_2 or not lord_11:
            return False

        # Check if they are conjunct or in exchange
        return (self._are_planets_conjunct(lord_2, lord_11, planets_data) or
                self._are_planets_in_exchange(lord_2, lord_11, planets_data))

    def _get_house_lord(self, house_num: int, planets_data: List) -> Optional[str]:
        """Find the lord of a specific house."""
        # Find the sign in the house
        house_sign = None
        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr == house_num:
                house_sign = planet.Rasi
                break

        if not house_sign:
            return None

        # Map signs to their lords
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }

        return sign_lords.get(house_sign)

    def _are_planets_conjunct(self, planet1: str, planet2: str, planets_data: List) -> bool:
        """Check if two planets are in the same sign."""
        planet1_sign = None
        planet2_sign = None

        for planet in planets_data:
            if planet.Object == planet1:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2:
                planet2_sign = planet.Rasi

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_planets_in_exchange(self, planet1: str, planet2: str, planets_data: List) -> bool:
        """Check if two planets are in exchange (each in the other's sign)."""
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

        # Get current signs
        planet1_sign = None
        planet2_sign = None

        for planet in planets_data:
            if planet.Object == planet1:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2:
                planet2_sign = planet.Rasi

        if not planet1_sign or not planet2_sign:
            return False

        # Check if each planet is in the other's sign
        return (planet1_sign in planet_signs.get(planet2, []) and
                planet2_sign in planet_signs.get(planet1, []))


@YogaRegistry.register
class MahapurushaYoga(Yoga):
    """Base class for the five Pancha Mahapurusha Yogas."""

    def __init__(self, planet, name_suffix):
        planet_descriptions = {
            "Mars": "courage, strength, leadership",
            "Mercury": "intelligence, communication skills",
            "Jupiter": "wisdom, knowledge, spirituality",
            "Venus": "luxury, artistic talents, comfort",
            "Saturn": "discipline, endurance, practical wisdom"
        }

        super().__init__(
            name=f"{name_suffix} Yoga",
            description=f"{planet} in own sign or exaltation in a kendra house. Grants {planet_descriptions.get(planet, '')}.",
            yoga_type=YogaType.POSITIVE,
            required_planets=[planet]
        )
        self.planet = planet

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if the specific planet is in own sign or exalted in kendra."""
        own_signs = {
            "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"],
            "Saturn": ["Capricorn", "Aquarius"]
        }

        exaltation = {
            "Mars": "Capricorn",
            "Mercury": "Virgo",
            "Jupiter": "Cancer",
            "Venus": "Pisces",
            "Saturn": "Libra"
        }

        kendra_houses = [1, 4, 7, 10]

        for planet in planets_data:
            if planet.Object == self.planet:
                # Check if in kendra
                if planet.HouseNr in kendra_houses:
                    # Check if in own sign or exaltation
                    in_own_sign = planet.Rasi in own_signs.get(self.planet, [])
                    in_exaltation = planet.Rasi == exaltation.get(self.planet)

                    return in_own_sign or in_exaltation

        return False


@YogaRegistry.register
class RuchakaYoga(MahapurushaYoga):
    """Mars Mahapurusha Yoga - leadership and courage."""

    def __init__(self):
        super().__init__("Mars", "Ruchaka")


@YogaRegistry.register
class BhadraYoga(MahapurushaYoga):
    """Mercury Mahapurusha Yoga - intelligence and communication."""

    def __init__(self):
        super().__init__("Mercury", "Bhadra")


@YogaRegistry.register
class HamsaYoga(MahapurushaYoga):
    """Jupiter Mahapurusha Yoga - wisdom and spirituality."""

    def __init__(self):
        super().__init__("Jupiter", "Hamsa")


@YogaRegistry.register
class MalavyaYoga(MahapurushaYoga):
    """Venus Mahapurusha Yoga - luxury and comfort."""

    def __init__(self):
        super().__init__("Venus", "Malavya")


@YogaRegistry.register
class SasaYoga(MahapurushaYoga):
    """Saturn Mahapurusha Yoga - discipline and endurance."""

    def __init__(self):
        super().__init__("Saturn", "Sasa")


@YogaRegistry.register
class AmalaYoga(Yoga):
    """10th house from Moon with no malefics - success and reputation."""

    def __init__(self):
        super().__init__(
            name="Amala Yoga",
            description="10th house from Moon has no malefic planets. Grants pure reputation, success, and good name.",
            yoga_type=YogaType.POSITIVE,
            required_planets=["Moon"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if 10th house from Moon has no malefics."""
        # Find Moon's house position
        moon_house = None
        for planet in planets_data:
            if planet.Object == "Moon":
                moon_house = planet.HouseNr
                break

        if not moon_house:
            return False

        # Calculate 10th house from Moon
        tenth_from_moon = (moon_house + 9) % 12
        if tenth_from_moon == 0:
            tenth_from_moon = 12

        # List of malefic planets
        malefics = ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]

        # Check if any malefic is in the 10th from Moon
        for planet in planets_data:
            if planet.Object in malefics and planet.HouseNr == tenth_from_moon:
                return False

        return True


@YogaRegistry.register
class ChamundaYoga(Yoga):
    """Jupiter, Venus and Mercury in kendras - grace and prosperity."""

    def __init__(self):
        super().__init__(
            name="Chamunda Yoga",
            description="Jupiter, Venus and Mercury in kendras. Grants divine grace, prosperity, and success.",
            yoga_type=YogaType.POSITIVE,
            required_planets=["Jupiter", "Venus", "Mercury"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Jupiter, Venus and Mercury are in kendra houses."""
        kendra_houses = [1, 4, 7, 10]
        planets_in_kendra = {"Jupiter": False, "Venus": False, "Mercury": False}

        for planet in planets_data:
            if planet.Object in planets_in_kendra and planet.HouseNr in kendra_houses:
                planets_in_kendra[planet.Object] = True

        # All three benefics must be in kendras
        return all(planets_in_kendra.values())