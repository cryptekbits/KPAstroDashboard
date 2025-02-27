from datetime import datetime
from flatlib.chart import Chart
import math


class AspectCalculator:
    def __init__(self):
        # Planet name mapping for aspect display
        self.planet_short_names = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mer",
            "Venus": "Ven",
            "Mars": "Mars",
            "Jupiter": "Jup",
            "Saturn": "Sat",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
            "Uranus": "Ura",
            "Neptune": "Nep",
            "Pluto": "Plu",
            "North Node": "Rahu",
            "South Node": "Ketu",
            "Asc": "Asc"
        }

        # Major aspects with their orbs
        self.major_aspects = {
            0: {"name": "Conjunction", "orb": 8, "symbol": "☌"},
            30: {"name": "Semi-Sextile", "orb": 2, "symbol": "⚺"},
            60: {"name": "Sextile", "orb": 6, "symbol": "⚹"},
            90: {"name": "Square", "orb": 8, "symbol": "□"},
            120: {"name": "Trine", "orb": 8, "symbol": "△"},
            150: {"name": "Quincunx", "orb": 4, "symbol": "⚻"},
            180: {"name": "Opposition", "orb": 10, "symbol": "☍"}
        }

        # Set default selected aspects (0, 90, 180)
        self.selected_aspects = [0, 90, 180]

        # Set default selected planets
        self.selected_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu",
                                 "Ascendant"]

        # Yoga definitions
        self.yogas = [
            {"name": "Budha-Aditya Yoga", "condition": self._check_budha_aditya},
            {"name": "Gaja-Kesari Yoga", "condition": self._check_gaja_kesari},
            {"name": "Vish Yoga", "condition": self._check_vish_yoga},
            {"name": "Neech Bhanga Raja Yoga", "condition": self._check_neech_bhanga}
        ]

    def set_selected_aspects(self, aspects):
        """Set the aspects to be calculated"""
        self.selected_aspects = aspects

    def set_selected_planets(self, planets):
        """Set the planets to calculate aspects for"""
        self.selected_planets = planets

    def calculate_aspects(self, chart, planets_data):
        """Calculate important aspects between planets"""
        aspects = []
        planet_positions = {}
        planet_retrograde = {}

        # Extract planet positions and retrograde status
        for planet in planets_data:
            name = planet.Object

            # Get the display name for this planet (to check against selected_planets)
            display_name = name
            if name == "North Node":
                display_name = "Rahu"
            elif name == "South Node":
                display_name = "Ketu"
            elif name == "Asc":
                display_name = "Ascendant"

            # Skip planets that aren't in our selected list
            if display_name not in self.selected_planets:
                continue

            planet_positions[name] = planet.LonDecDeg
            planet_retrograde[name] = planet.isRetroGrade

        # Get planet pairs and check aspects
        planet_keys = list(planet_positions.keys())

        for i in range(len(planet_keys)):
            for j in range(i + 1, len(planet_keys)):
                p1 = planet_keys[i]
                p2 = planet_keys[j]

                # Calculate the angular distance
                degree_diff = abs(planet_positions[p1] - planet_positions[p2])
                if degree_diff > 180:
                    degree_diff = 360 - degree_diff

                # Check if it's one of our selected aspects
                for angle in self.selected_aspects:
                    aspect_info = self.major_aspects.get(angle)
                    if not aspect_info:
                        continue

                    orb = aspect_info["orb"]
                    if abs(degree_diff - angle) <= orb:
                        # Format retrograde status
                        p1_name = self.planet_short_names.get(p1, p1)
                        p2_name = self.planet_short_names.get(p2, p2)

                        if planet_retrograde.get(p1):
                            p1_name += "(Ret.)"
                        if planet_retrograde.get(p2):
                            p2_name += "(Ret.)"

                        # Calculate exact orb
                        exact_orb = round(abs(degree_diff - angle), 1)

                        # Add the aspect with the symbol
                        aspects.append(f"{p1_name} {aspect_info['symbol']} {p2_name} ({exact_orb}° orb)")
                        break

        return aspects

    def calculate_yogas(self, chart, planets_data):
        """Calculate important Vedic yogas"""
        yogas = []

        for yoga in self.yogas:
            if yoga["condition"](chart, planets_data):
                yogas.append(yoga["name"])

        return yogas

    def check_retrograde_changes(self, previous_data, current_data):
        """Check if any planet changed retrograde status"""
        if not previous_data:
            return []

        changes = []
        for planet in current_data:
            # Get the display name for this planet
            display_name = planet.Object
            if display_name == "North Node":
                display_name = "Rahu"
            elif display_name == "South Node":
                display_name = "Ketu"
            elif display_name == "Asc":
                display_name = "Ascendant"

            # Skip planets that aren't in our selected list
            if display_name not in self.selected_planets:
                continue

            # Look for the same planet in previous data
            for prev_planet in previous_data:
                if planet.Object == prev_planet.Object:
                    # Check if retrograde status changed
                    if planet.isRetroGrade != prev_planet.isRetroGrade:
                        status = "Retrograde" if planet.isRetroGrade else "Direct"
                        planet_name = self.planet_short_names.get(planet.Object, planet.Object)
                        changes.append(f"{planet_name} turned {status}")

        return changes

    def check_sign_changes(self, previous_data, current_data):
        """Check if any planet changed signs"""
        if not previous_data:
            return []

        changes = []
        for planet in current_data:
            # Get the display name for this planet
            display_name = planet.Object
            if display_name == "North Node":
                display_name = "Rahu"
            elif display_name == "South Node":
                display_name = "Ketu"
            elif display_name == "Asc":
                display_name = "Ascendant"

            # Skip planets that aren't in our selected list
            if display_name not in self.selected_planets:
                continue

            # Look for the same planet in previous data
            for prev_planet in previous_data:
                if planet.Object == prev_planet.Object:
                    # Check if sign changed
                    if planet.Rasi != prev_planet.Rasi:
                        planet_name = self.planet_short_names.get(planet.Object, planet.Object)
                        changes.append(f"{planet_name} entered {planet.Rasi}")

        return changes

    def check_nakshatra_changes(self, previous_data, current_data):
        """Check if any planet changed nakshatras"""
        if not previous_data:
            return []

        changes = []
        for planet in current_data:
            # Get the display name for this planet
            display_name = planet.Object
            if display_name == "North Node":
                display_name = "Rahu"
            elif display_name == "South Node":
                display_name = "Ketu"
            elif display_name == "Asc":
                display_name = "Ascendant"

            # Skip planets that aren't in our selected list
            if display_name not in self.selected_planets:
                continue

            # Look for the same planet in previous data
            for prev_planet in previous_data:
                if planet.Object == prev_planet.Object:
                    # Check if nakshatra changed
                    if planet.Nakshatra != prev_planet.Nakshatra:
                        planet_name = self.planet_short_names.get(planet.Object, planet.Object)
                        changes.append(f"{planet_name} entered {planet.Nakshatra} nakshatra")

        return changes

    def get_important_events(self, previous_data, current_data, chart):
        """Get all important events between the previous and current time"""
        events = []

        # Check for aspects
        aspects = self.calculate_aspects(chart, current_data)
        if aspects:
            events.extend(aspects)

        # Check for yogas
        yogas = self.calculate_yogas(chart, current_data)
        if yogas:
            events.extend(yogas)

        # Check for retrograde changes
        retro_changes = self.check_retrograde_changes(previous_data, current_data)
        if retro_changes:
            events.extend(retro_changes)

        return events

    # Yoga condition check methods
    def _check_budha_aditya(self, chart, planets_data):
        """Check for Budha-Aditya Yoga (Mercury and Sun in same sign)"""
        sun_sign = None
        mercury_sign = None

        for planet in planets_data:
            if planet.Object == "Sun":
                sun_sign = planet.Rasi
            elif planet.Object == "Mercury":
                mercury_sign = planet.Rasi

        return sun_sign and mercury_sign and sun_sign == mercury_sign

    def _check_gaja_kesari(self, chart, planets_data):
        """Check for Gaja-Kesari Yoga (Jupiter and Moon in quadrant from each other)"""
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

            # Check for quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            return abs(angle - 90) <= 10 or abs(angle - 270) <= 10

        return False

    def _check_vish_yoga(self, chart, planets_data):
        """Check for Vish Yoga (Malefics in 6, 8, 12 houses from Moon)"""
        moon_house = None
        malefic_houses = []

        for planet in planets_data:
            if planet.Object == "Moon":
                moon_house = planet.HouseNr
            elif planet.Object in ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "North Node", "South Node"]:
                if planet.HouseNr:
                    malefic_houses.append(planet.HouseNr)

        if moon_house:
            vish_houses = [(moon_house + 5) % 12 + 1, (moon_house + 7) % 12 + 1, (moon_house + 11) % 12 + 1]
            return any(house in vish_houses for house in malefic_houses)

        return False

    def _check_neech_bhanga(self, chart, planets_data):
        """Check for Neech Bhanga Raja Yoga (Debilitated planet with cancellation)"""
        # Debilitation signs
        debilitation = {
            "Sun": "Libra",
            "Moon": "Scorpio",
            "Mercury": "Pisces",
            "Venus": "Virgo",
            "Mars": "Cancer",
            "Jupiter": "Capricorn",
            "Saturn": "Aries"
        }

        # Lords of debilitation signs
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

        # Check if any planet is in debilitation and if its lord is well-placed
        for planet in planets_data:
            name = planet.Object
            if name in debilitation and planet.Rasi == debilitation[name]:
                # Planet is debilitated
                lord_of_sign = sign_lords[planet.Rasi]

                # Check if lord is exalted or in a good house
                for other_planet in planets_data:
                    if other_planet.Object == lord_of_sign:
                        # If lord is in a kendra (1, 4, 7, 10) or trikona (1, 5, 9) house
                        good_houses = [1, 4, 5, 7, 9, 10]
                        if other_planet.HouseNr in good_houses:
                            return True

        return False