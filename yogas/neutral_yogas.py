"""
Neutral yogas in KP Astrology - combinations with mixed or context-dependent effects.
"""
from typing import Dict, List, Optional
import math
from .yoga_base import Yoga, YogaType, YogaRegistry


@YogaRegistry.register
class ParivartanaYoga(Yoga):
    """Exchange of signs between two planets - mixed effects based on planets involved."""

    def __init__(self):
        super().__init__(
            name="Parivartana Yoga",
            description="Exchange of signs between two planets. Effects depend on the planets involved and houses they rule.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=[]  # Depends on which planets exchange
        )
        self.exchanging_planets = []

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if any two planets are exchanging signs."""
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

        # Tracking planets and their current signs
        current_signs = {}
        for planet in planets_data:
            if planet.Object in planet_signs and hasattr(planet, 'Rasi'):
                current_signs[planet.Object] = planet.Rasi

        # Check for exchanges
        self.exchanging_planets = []
        for planet1, sign1 in current_signs.items():
            for planet2, sign2 in current_signs.items():
                if planet1 != planet2:  # Different planets
                    # Planet1 is in a sign ruled by Planet2, and Planet2 is in a sign ruled by Planet1
                    if sign1 in planet_signs.get(planet2, []) and sign2 in planet_signs.get(planet1, []):
                        self.exchanging_planets = [planet1, planet2]
                        return True

        return False

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """Get planets participating in the exchange."""
        if not self.exchanging_planets:
            # Recheck to populate exchanging_planets if needed
            self.check_yoga(chart_data, planets_data)

        participating_planets = []
        for planet in planets_data:
            if planet.Object in self.exchanging_planets:
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })

        return participating_planets


@YogaRegistry.register
class ShubhaKartariYoga(Yoga):
    """Planet hemmed between benefics - protection and support."""

    def __init__(self):
        super().__init__(
            name="Shubha-Kartari Yoga",
            description="A planet hemmed between benefics. Provides protection and support to the planet's significations.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=[]  # Any planet can be hemmed
        )
        self.central_planet = None

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if any planet is hemmed between benefics."""
        # Define benefics
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        # Get positions of all planets
        planet_positions = {}
        for planet in planets_data:
            if hasattr(planet, 'LonDecDeg'):
                planet_positions[planet.Object] = planet.LonDecDeg

        # Get positions of benefics
        benefic_positions = {p: pos for p, pos in planet_positions.items() if p in benefics}

        # Check each planet to see if it's hemmed between benefics
        for planet, position in planet_positions.items():
            if planet in benefics:
                continue  # Skip checking benefics themselves

            # Look for benefics on both sides
            has_benefic_before = False
            has_benefic_after = False

            for benefic, b_position in benefic_positions.items():
                angle = (position - b_position) % 360
                if 0 < angle < 180:
                    has_benefic_before = True
                elif 180 < angle < 360:
                    has_benefic_after = True

            if has_benefic_before and has_benefic_after:
                self.central_planet = planet
                return True

        return False

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """Get planets participating in the yoga."""
        if not self.central_planet:
            # Recheck to populate central_planet if needed
            self.check_yoga(chart_data, planets_data)

        participating_planets = []

        # Find the central planet and its details
        for planet in planets_data:
            if planet.Object == self.central_planet:
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })
                break

        # Find the benefics hemming this planet
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        for planet in planets_data:
            if planet.Object in benefics:
                # Simplified - we'd need to actually check if this benefic is hemming
                # For now, just add all benefics
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })

        return participating_planets


@YogaRegistry.register
class ChandraMangalaYoga(Yoga):
    """Moon and Mars conjunction - emotional intensity and drive."""

    def __init__(self):
        super().__init__(
            name="Chandra-Mangala Yoga",
            description="Conjunction of Moon and Mars. Creates emotional intensity, drive, and sometimes volatility.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=["Moon", "Mars"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if Moon and Mars are in conjunction."""
        moon_sign = None
        mars_sign = None

        for planet in planets_data:
            if planet.Object == "Moon":
                moon_sign = planet.Rasi
            elif planet.Object == "Mars":
                mars_sign = planet.Rasi

        return moon_sign and mars_sign and moon_sign == mars_sign


@YogaRegistry.register
class AdhiYoga(Yoga):
    """Benefics in 6th, 7th, and 8th from Moon - prosperity but also challenges."""

    def __init__(self):
        super().__init__(
            name="Adhi Yoga",
            description="Benefics in 6th, 7th, and 8th from Moon. Grants prosperity but may come with challenges.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=["Moon", "Jupiter", "Venus", "Mercury"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if benefics are in 6th, 7th, and 8th from Moon."""
        # Find Moon's house
        moon_house = None
        for planet in planets_data:
            if planet.Object == "Moon":
                moon_house = planet.HouseNr
                break

        if not moon_house:
            return False

        # Calculate 6th, 7th, and 8th houses from Moon
        houses_needed = [
            (moon_house + 5) % 12 or 12,  # 6th from Moon
            (moon_house + 6) % 12 or 12,  # 7th from Moon
            (moon_house + 7) % 12 or 12  # 8th from Moon
        ]

        # List of benefics
        benefics = ["Jupiter", "Venus", "Mercury"]

        # Check if benefics occupy the required houses
        benefic_houses = []
        for planet in planets_data:
            if planet.Object in benefics:
                benefic_houses.append(planet.HouseNr)

        # Check if at least one benefic is in each of these houses
        return all(any(house == needed for house in benefic_houses) for needed in houses_needed)

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """Get planets participating in Adhi Yoga."""
        moon_house = None
        participating_planets = []

        # Find Moon
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

        # Calculate 6th, 7th, and 8th houses from Moon
        houses_needed = [
            (moon_house + 5) % 12 or 12,  # 6th from Moon
            (moon_house + 6) % 12 or 12,  # 7th from Moon
            (moon_house + 7) % 12 or 12  # 8th from Moon
        ]

        # List of benefics
        benefics = ["Jupiter", "Venus", "Mercury"]

        # Find benefics in these houses
        for planet in planets_data:
            if planet.Object in benefics and planet.HouseNr in houses_needed:
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })

        return participating_planets


@YogaRegistry.register
class NabhashYoga(Yoga):
    """Base class for Nabhash yogas - planetary patterns."""

    def __init__(self, name, description):
        super().__init__(
            name=name,
            description=description,
            yoga_type=YogaType.NEUTRAL,
            required_planets=[]  # Depends on the specific pattern
        )


@YogaRegistry.register
class MalaYoga(NabhashYoga):
    """Planets in consecutive houses - chain of events."""

    def __init__(self):
        super().__init__(
            name="Mala Yoga",
            description="Planets in 7 or more consecutive houses. Creates a chain of events and interwoven destiny.",
            yoga_type=YogaType.NEUTRAL
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if planets are in 7 or more consecutive houses."""
        # Create a dictionary to track which houses are occupied
        houses_occupied = {i: False for i in range(1, 13)}

        # Mark occupied houses
        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr:
                houses_occupied[planet.HouseNr] = True

        # Convert to list for easier processing
        occupied_list = [houses_occupied[i] for i in range(1, 13)]

        # Add the first element to the end to handle wrapping
        occupied_list.append(occupied_list[0])

        # Find longest sequence of consecutive houses
        max_consecutive = 0
        current_consecutive = 0

        for occupied in occupied_list:
            if occupied:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive >= 7


@YogaRegistry.register
class GadaYoga(NabhashYoga):
    """Planets in alternate houses - inconsistency."""

    def __init__(self):
        super().__init__(
            name="Gada Yoga",
            description="Planets in alternate houses. Creates inconsistency in life pattern and experiences.",
            yoga_type=YogaType.NEUTRAL
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if planets are in a pattern of alternate houses."""
        # Create a dictionary to track which houses are occupied
        houses_occupied = {i: False for i in range(1, 13)}

        # Mark occupied houses
        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr:
                houses_occupied[planet.HouseNr] = True

        # Check for alternating pattern
        has_alternating_pattern = False

        # Check from each potential starting point
        for start in range(1, 13, 2):  # Start with odd houses
            alternating = True
            for i in range(start, start + 12, 2):
                house = ((i - 1) % 12) + 1
                if not houses_occupied[house]:
                    alternating = False
                    break

            if alternating:
                has_alternating_pattern = True
                break

        # Check even houses too
        for start in range(2, 13, 2):  # Start with even houses
            alternating = True
            for i in range(start, start + 12, 2):
                house = ((i - 1) % 12) + 1
                if not houses_occupied[house]:
                    alternating = False
                    break

            if alternating:
                has_alternating_pattern = True
                break

        return has_alternating_pattern


@YogaRegistry.register
class SarpaYoga(NabhashYoga):
    """Planets in 1, 2, 3, 4, 5, 6 or 7, 8, 9, 10, 11, 12 houses - serpentine path."""

    def __init__(self):
        super().__init__(
            name="Sarpa Yoga",
            description="Planets in 1-6 or 7-12 houses only. Creates a serpentine path in life with major changes.",
            yoga_type=YogaType.NEUTRAL
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if planets are confined to houses 1-6 or 7-12."""
        # Track which houses have planets
        houses_with_planets = set()

        for planet in planets_data:
            if hasattr(planet, 'HouseNr') and planet.HouseNr:
                houses_with_planets.add(planet.HouseNr)

        # Check if all planets are in houses 1-6
        if all(house <= 6 for house in houses_with_planets):
            return True

        # Check if all planets are in houses 7-12
        if all(house >= 7 for house in houses_with_planets):
            return True

        return False


@YogaRegistry.register
class UbhayachariYoga(Yoga):
    """Planets flanking Sun and Moon - balance of solar and lunar energies."""

    def __init__(self):
        super().__init__(
            name="Ubhayachari Yoga",
            description="Planets on both sides of Sun and Moon. Creates balance between solar and lunar energies.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=["Sun", "Moon"]
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if planets flank both Sun and Moon."""
        sun_pos = None
        moon_pos = None

        # Get Sun and Moon positions
        for planet in planets_data:
            if planet.Object == "Sun":
                sun_pos = planet.LonDecDeg
            elif planet.Object == "Moon":
                moon_pos = planet.LonDecDeg

        if sun_pos is None or moon_pos is None:
            return False

        # Check if both luminaries have planets flanking them
        sun_has_flanking = self._has_flanking_planets(sun_pos, planets_data)
        moon_has_flanking = self._has_flanking_planets(moon_pos, planets_data)

        return sun_has_flanking and moon_has_flanking

    def _has_flanking_planets(self, center_pos: float, planets_data: List) -> bool:
        """Check if a position has planets on both sides within a certain arc."""
        has_planet_before = False
        has_planet_after = False

        # Look for planets within 60° on either side
        for planet in planets_data:
            if planet.Object in ["Sun", "Moon"]:
                continue  # Skip the luminaries

            angle = (planet.LonDecDeg - center_pos) % 360

            if 0 < angle < 60:
                has_planet_after = True
            elif 300 < angle < 360:
                has_planet_before = True

        return has_planet_before and has_planet_after


@YogaRegistry.register
class DurdhuraYoga(Yoga):
    """Malefics in angles, and benefics in trines - mixed influences."""

    def __init__(self):
        super().__init__(
            name="Durdhura Yoga",
            description="Malefics in angles (1,4,7,10) and benefics in trines (1,5,9). Creates a mix of challenging exterior and supportive interior.",
            yoga_type=YogaType.NEUTRAL,
            required_planets=[]  # Depends on planet arrangements
        )

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """Check if malefics are in angles and benefics are in trines."""
        # Define malefics and benefics
        malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        # Define angular and trine houses
        angles = [1, 4, 7, 10]
        trines = [1, 5, 9]

        # Track houses occupied by malefics and benefics
        malefic_houses = set()
        benefic_houses = set()

        for planet in planets_data:
            if planet.Object in malefics and planet.HouseNr:
                malefic_houses.add(planet.HouseNr)
            elif planet.Object in benefics and planet.HouseNr:
                benefic_houses.add(planet.HouseNr)

        # Check if any malefic is in an angle and any benefic is in a trine
        has_malefic_in_angle = any(house in angles for house in malefic_houses)
        has_benefic_in_trine = any(house in trines for house in benefic_houses)

        return has_malefic_in_angle and has_benefic_in_trine