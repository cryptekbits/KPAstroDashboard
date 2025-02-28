"""
Negative (challenging) yogas in KP Astrology.
"""
from typing import Dict, List, Optional
import math
from yoga_base import Yoga, YogaType, YogaRegistry


@YogaRegistry.register
class KalaSarpaYoga(Yoga):
    """All planets between Rahu and Ketu - obstacles and delays."""

    def __init__(self):
        super().__init__(
            name="Kala Sarpa Yoga",
            description="All planets between Rahu and Ketu. Creates obstacles, delays, and karmic challenges.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Rahu", "Ketu"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if all planets are between Rahu and Ketu."""
        rahu_lon = None
        ketu_lon = None

        for planet in planets_data:
            if planet.Object == "North Node" or planet.Object == "Rahu":
                rahu_lon = planet.LonDecDeg
            elif planet.Object == "South Node" or planet.Object == "Ketu":
                ketu_lon = planet.LonDecDeg

        if rahu_lon is None or ketu_lon is None:
            return False

        # Define the arc from Rahu to Ketu
        if rahu_lon < ketu_lon:
            # If Rahu is earlier in the zodiac than Ketu
            arc_start = rahu_lon
            arc_end = ketu_lon
        else:
            # If Rahu is later in the zodiac than Ketu
            arc_start = rahu_lon
            arc_end = ketu_lon + 360

        # Check if all planets are in this arc
        all_in_arc = True
        main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        for planet in planets_data:
            if planet.Object in main_planets:
                lon = planet.LonDecDeg
                if rahu_lon < ketu_lon and (lon < rahu_lon or lon > ketu_lon):
                    all_in_arc = False
                    break
                elif rahu_lon > ketu_lon and (lon > ketu_lon % 360 and lon < rahu_lon):
                    all_in_arc = False
                    break

        return all_in_arc


@YogaRegistry.register
class VishYoga(Yoga):
    """Malefics in 6, 8, 12 houses from Moon - stress and suffering."""

    def __init__(self):
        super().__init__(
            name="Vish Yoga",
            description="Malefics in 6th, 8th, 12th houses from Moon. Creates stress, suffering, and negative life events.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Moon", "Sun", "Mars", "Saturn", "Rahu", "Ketu"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if malefics are in 6th, 8th, or 12th house from Moon."""
        moon_house = None
        malefic_houses = []

        for planet in planets_data:
            if planet.Object == "Moon":
                moon_house = planet.HouseNr
            elif planet.Object in ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "North Node", "South Node"]:
                if planet.HouseNr:
                    malefic_houses.append(planet.HouseNr)

        if not moon_house:
            return False

        # Calculate 6th, 8th, and 12th houses from Moon
        vish_houses = [
            (moon_house + 5) % 12 or 12,  # 6th from Moon
            (moon_house + 7) % 12 or 12,  # 8th from Moon
            (moon_house + 11) % 12 or 12  # 12th from Moon
        ]

        # Check if any malefic is in these houses
        return any(house in vish_houses for house in malefic_houses)

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """Get planets participating in Vish Yoga."""
        moon_house = None
        participating_planets = []

        for planet in planets_data:
            if planet.Object == "Moon":
                moon_house = planet.HouseNr
                participating_planets.append({
                    "name": "Moon",
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })
                break

        if not moon_house:
            return participating_planets

        # Calculate 6th, 8th, and 12th houses from Moon
        vish_houses = [
            (moon_house + 5) % 12 or 12,  # 6th from Moon
            (moon_house + 7) % 12 or 12,  # 8th from Moon
            (moon_house + 11) % 12 or 12  # 12th from Moon
        ]

        # Find malefics in these houses
        for planet in planets_data:
            if (planet.Object in ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "North Node", "South Node"]
                    and planet.HouseNr in vish_houses):
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })

        return participating_planets


@YogaRegistry.register
class AngarakYoga(Yoga):
    """Mars in 1, 4, 7, 8, 12 houses - aggression and conflicts."""

    def __init__(self):
        super().__init__(
            name="Angarak Yoga",
            description="Mars in 1st, 4th, 7th, 8th, or 12th house. Creates aggression, conflicts, and physical challenges.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Mars"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Mars is in 1st, 4th, 7th, 8th, or 12th house."""
        critical_houses = [1, 4, 7, 8, 12]

        for planet in planets_data:
            if planet.Object == "Mars" and planet.HouseNr in critical_houses:
                return True

        return False


@YogaRegistry.register
class GuruChandalaYoga(Yoga):
    """Jupiter and Rahu conjunction - false knowledge and deception."""

    def __init__(self):
        super().__init__(
            name="Guru Chandala Yoga",
            description="Jupiter and Rahu in conjunction. Creates false knowledge, spiritual deception, and confusion.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Jupiter", "Rahu"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Jupiter and Rahu are in conjunction."""
        jupiter_sign = None
        rahu_sign = None

        for planet in planets_data:
            if planet.Object == "Jupiter":
                jupiter_sign = planet.Rasi
            elif planet.Object == "North Node" or planet.Object == "Rahu":
                rahu_sign = planet.Rasi

        return jupiter_sign and rahu_sign and jupiter_sign == rahu_sign


@YogaRegistry.register
class GrahaYuddhaYoga(Yoga):
    """Two planets in close conjunction - conflict and struggle."""

    def __init__(self):
        super().__init__(
            name="Graha Yuddha",
            description="Two planets in close conjunction within 1 degree. Creates conflict, struggle, and energy blockage.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=[]  # Depends on which planets are in war
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if any two planets are in close conjunction (within 1 degree)."""
        main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        # Check each planet pair
        for i, planet1 in enumerate(planets_data):
            if planet1.Object not in main_planets:
                continue

            for j, planet2 in enumerate(planets_data[i + 1:], i + 1):
                if planet2.Object not in main_planets:
                    continue

                # Calculate angular separation
                angle = abs(planet1.LonDecDeg - planet2.LonDecDeg)
                if angle > 180:
                    angle = 360 - angle

                # Check if within 1 degree
                if angle < 1:
                    self.war_planets = [planet1.Object, planet2.Object]  # Store the planets in war
                    return True

        return False

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """Get planets participating in Graha Yuddha."""
        if not hasattr(self, 'war_planets') or not self.war_planets:
            # Re-check the yoga to identify the planets
            self.check_yoga(chart_data, planets_data)

        participating_planets = []

        # If we have identified planets in war
        if hasattr(self, 'war_planets') and self.war_planets:
            for planet in planets_data:
                if planet.Object in self.war_planets:
                    participating_planets.append({
                        "name": planet.Object,
                        "house": planet.HouseNr,
                        "sign": planet.Rasi
                    })

        return participating_planets


@YogaRegistry.register
class KemadrumaYoga(Yoga):
    """Moon with no beneficial conjunctions or aspects - poverty and hardship."""

    def __init__(self):
        super().__init__(
            name="Kemadruma Yoga",
            description="Moon with no planets in adjacent houses or aspects. Creates poverty, lack of resources, and mental stress.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Moon"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Moon has no planets in 2nd/12th houses, same sign, or aspects."""
        moon_data = None
        for planet in planets_data:
            if planet.Object == "Moon":
                moon_data = planet
                break

        if not moon_data:
            return False

        # Find Moon's house and sign
        moon_house = moon_data.HouseNr
        moon_sign = moon_data.Rasi

        # Calculate 2nd and 12th houses from Moon
        second_from_moon = moon_house % 12 + 1
        twelfth_from_moon = (moon_house - 2) % 12 + 1
        if twelfth_from_moon == 0:
            twelfth_from_moon = 12

        # Check if any planet is in 2nd or 12th from Moon, in same sign as Moon, or aspects Moon
        for planet in planets_data:
            if planet.Object == "Moon":
                continue

            # Check if planet is in 2nd or 12th from Moon
            if planet.HouseNr in [second_from_moon, twelfth_from_moon]:
                return False

            # Check if planet is in same sign as Moon
            if planet.Rasi == moon_sign:
                return False

            # Check if planet aspects Moon (simplified check - just check standard aspects)
            if self._are_planets_in_aspect(planet, moon_data):
                return False

        return True

    def _are_planets_in_aspect(self, planet1, planet2) -> bool:
        """Check if two planets are in standard aspect to each other."""
        if not planet1 or not planet2:
            return False

        # Calculate angle between planets
        angle = abs(planet1.LonDecDeg - planet2.LonDecDeg)
        if angle > 180:
            angle = 360 - angle

        # Check standard aspects with appropriate orbs
        standard_aspects = [0, 60, 90, 120, 180]
        aspect_orbs = {0: 8, 60: 6, 90: 8, 120: 8, 180: 10}

        for aspect in standard_aspects:
            if abs(angle - aspect) <= aspect_orbs[aspect]:
                return True

        return False


@YogaRegistry.register
class ShakatYoga(Yoga):
    """Moon in 6th, 8th, or 12th from Jupiter - emotional challenges."""

    def __init__(self):
        super().__init__(
            name="Shakat Yoga",
            description="Moon in 6th, 8th, or 12th house from Jupiter. Creates emotional challenges, lack of luck, and life obstacles.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=["Moon", "Jupiter"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Moon is in 6th, 8th, or 12th house from Jupiter."""
        jupiter_house = None
        moon_house = None

        for planet in planets_data:
            if planet.Object == "Jupiter":
                jupiter_house = planet.HouseNr
            elif planet.Object == "Moon":
                moon_house = planet.HouseNr

        if not jupiter_house or not moon_house:
            return False

        # Calculate 6th, 8th, and 12th houses from Jupiter
        shakat_houses = [
            (jupiter_house + 5) % 12 or 12,  # 6th from Jupiter
            (jupiter_house + 7) % 12 or 12,  # 8th from Jupiter
            (jupiter_house + 11) % 12 or 12  # 12th from Jupiter
        ]

        return moon_house in shakat_houses


@YogaRegistry.register
class DaridraYoga(Yoga):
    """Fifth house lord in 6th, 8th, or 12th house - poverty and struggle."""

    def __init__(self):
        super().__init__(
            name="Daridra Yoga",
            description="Lord of 5th house in 6th, 8th, or 12th house. Creates poverty, financial struggles, and bad luck.",
            yoga_type=YogaType.NEGATIVE,
            required_planets=[]  # Depends on 5th house lord
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if 5th house lord is in 6th, 8th, or 12th house."""
        # Find 5th house sign
        fifth_house_sign = None
        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr == 5:
                fifth_house_sign = planet.Rasi
                break

        if not fifth_house_sign:
            return False

        # Map signs to their lords
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }

        fifth_lord = sign_lords.get(fifth_house_sign)
        if not fifth_lord:
            return False

        # Check where 5th lord is placed
        dusthana_houses = [6, 8, 12]  # Houses of difficulty
        for planet in planets_data:
            if planet.Object == fifth_lord and planet.HouseNr in dusthana_houses:
                return True

        return False