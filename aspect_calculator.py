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
                        aspects.append(f"{p1_name} {aspect_info['symbol']} {p2_name} ({aspect_info['name']}) - {angle}°")
                        break

        return aspects

    def calculate_yogas(self, chart, planets_data):
        """Calculate important Vedic yogas"""
        yogas = []

        # Check existing yogas
        if self._check_budha_aditya(chart, planets_data):
            yogas.append("Budha-Aditya Yoga")

        if self._check_gaja_kesari(chart, planets_data):
            yogas.append("Gaja-Kesari Yoga")

        if self._check_vish_yoga(chart, planets_data):
            yogas.append("Vish Yoga")

        if self._check_neech_bhanga(chart, planets_data):
            yogas.append("Neech Bhanga Raja Yoga")

        # Add new yogas
        mahapurusha_yogas = self._check_pancha_mahapurusha_yoga(chart, planets_data)
        if mahapurusha_yogas:
            yogas.extend(mahapurusha_yogas)

        dhana_yogas = self._check_dhana_yogas(chart, planets_data)
        if dhana_yogas:
            yogas.extend(dhana_yogas)

        kala_sarpa = self._check_kala_sarpa_yoga(chart, planets_data)
        if kala_sarpa:
            yogas.append(kala_sarpa)

        raja_yogas = self._check_raja_yogas(chart, planets_data)
        if raja_yogas:
            yogas.extend(raja_yogas)

        graha_malika = self._check_graha_malika_yoga(chart, planets_data)
        if graha_malika:
            yogas.append(graha_malika)

        negative_yogas = self._check_negative_yogas(chart, planets_data)
        if negative_yogas:
            yogas.extend(negative_yogas)

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

    def _check_pancha_mahapurusha_yoga(self, chart, planets_data):
        """
        Check for Pancha Mahapurusha Yogas (five great person yogas).

        - Ruchaka: Mars in own sign (Aries/Scorpio) or exalted (Capricorn) in kendra (1,4,7,10)
        - Bhadra: Mercury in own sign (Gemini/Virgo) or exalted (Virgo) in kendra
        - Hamsa: Jupiter in own sign (Sagittarius/Pisces) or exalted (Cancer) in kendra
        - Malavya: Venus in own sign (Taurus/Libra) or exalted (Pisces) in kendra
        - Sasa: Saturn in own sign (Capricorn/Aquarius) or exalted (Libra) in kendra
        """
        active_yogas = []

        # Own signs and exaltation signs for planets
        own_signs = {
            "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"],
            "Saturn": ["Capricorn", "Aquarius"]
        }

        exalted_signs = {
            "Mars": "Capricorn",
            "Mercury": "Virgo",
            "Jupiter": "Cancer",
            "Venus": "Pisces",
            "Saturn": "Libra"
        }

        # Kendra houses (1, 4, 7, 10)
        kendras = [1, 4, 7, 10]

        # Check each planet
        for planet in planets_data:
            if planet.Object in own_signs:
                # Check if planet is in own sign or exalted
                in_own_sign = planet.Rasi in own_signs[planet.Object]
                in_exalted = planet.Rasi == exalted_signs[planet.Object]

                # Check if in kendra house
                in_kendra = planet.HouseNr in kendras

                if (in_own_sign or in_exalted) and in_kendra:
                    if planet.Object == "Mars":
                        active_yogas.append("Ruchaka Yoga")
                    elif planet.Object == "Mercury":
                        active_yogas.append("Bhadra Yoga")
                    elif planet.Object == "Jupiter":
                        active_yogas.append("Hamsa Yoga")
                    elif planet.Object == "Venus":
                        active_yogas.append("Malavya Yoga")
                    elif planet.Object == "Saturn":
                        active_yogas.append("Sasa Yoga")

        return active_yogas

    def _check_dhana_yogas(self, chart, planets_data):
        """
        Check for Dhana Yogas (wealth-producing combinations)
        """
        active_yogas = []

        # Find lords of houses
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # Check specific house combinations

        # 1. Lords of 5th and 9th houses together or in exchange
        if self._are_planets_conjunct(house_lords.get(5), house_lords.get(9), planets_data) or \
                self._are_planets_in_exchange(house_lords.get(5), house_lords.get(9), planets_data):
            active_yogas.append("Lakshmi Yoga")

        # 2. Lords of 2nd and 11th houses conjunct or in exchange
        if self._are_planets_conjunct(house_lords.get(2), house_lords.get(11), planets_data) or \
                self._are_planets_in_exchange(house_lords.get(2), house_lords.get(11), planets_data):
            active_yogas.append("Dhana Yoga")

        # 3. Jupiter in 2nd or 5th or 11th house
        for planet in planets_data:
            if planet.Object == "Jupiter" and planet.HouseNr in [2, 5, 11]:
                active_yogas.append("Guru-Mangala Yoga")
                break

        # 4. Venus and Jupiter conjunction
        if self._are_specific_planets_conjunct("Venus", "Jupiter", planets_data):
            active_yogas.append("Guru-Shukra Yoga")

        return active_yogas

    def _check_kala_sarpa_yoga(self, chart, planets_data):
        """
        Check for Kala Sarpa Yoga (all planets between Rahu and Ketu)
        """
        rahu_lon = None
        ketu_lon = None

        for planet in planets_data:
            if planet.Object == "North Node" or planet.Object == "Rahu":
                rahu_lon = planet.LonDecDeg
            elif planet.Object == "South Node" or planet.Object == "Ketu":
                ketu_lon = planet.LonDecDeg

        if rahu_lon is None or ketu_lon is None:
            return False

        # Define arc from Rahu to Ketu
        if rahu_lon < ketu_lon:
            # If Rahu is earlier in the zodiac than Ketu
            rahu_ketu_arc = [rahu_lon, ketu_lon]
        else:
            # If Rahu is later in the zodiac than Ketu
            rahu_ketu_arc = [rahu_lon, ketu_lon + 360]

        # Check if all planets are in this arc
        all_in_arc = True
        for planet in planets_data:
            if planet.Object in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                lon = planet.LonDecDeg
                if rahu_lon < ketu_lon and (lon < rahu_lon or lon > ketu_lon):
                    all_in_arc = False
                    break
                elif rahu_lon > ketu_lon and (lon > ketu_lon and lon < rahu_lon):
                    all_in_arc = False
                    break

        return "Kala Sarpa Yoga" if all_in_arc else None

    def _check_raja_yogas(self, chart, planets_data):
        """
        Check for Raja Yogas (combinations indicating power, status, and success)
        """
        active_yogas = []

        # Find houses lordships
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # 1. Lords of trine houses (1,5,9) and kendra houses (1,4,7,10) conjunct
        trine_lords = [house_lords.get(1), house_lords.get(5), house_lords.get(9)]
        kendra_lords = [house_lords.get(1), house_lords.get(4), house_lords.get(7), house_lords.get(10)]

        for trine_lord in trine_lords:
            for kendra_lord in kendra_lords:
                if trine_lord and kendra_lord and trine_lord != kendra_lord:
                    if self._are_planets_conjunct(trine_lord, kendra_lord, planets_data):
                        active_yogas.append("Raja Yoga")

        # 2. Gajakesari Yoga - Moon and Jupiter in kendra from each other
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

            # Check if they're in quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            if abs(angle - 90) <= 10 or abs(angle - 180) <= 10 or abs(angle - 270) <= 10:
                active_yogas.append("Gajakesari Yoga")

        # 3. Sun in 10th house with Jupiter or Venus aspect
        sun_in_10th = False
        for planet in planets_data:
            if planet.Object == "Sun" and planet.HouseNr == 10:
                sun_in_10th = True
                break

        if sun_in_10th:
            # Check for Jupiter or Venus aspect to the 10th house
            for planet in planets_data:
                if (planet.Object == "Jupiter" or planet.Object == "Venus") and \
                        self._is_planet_aspecting_house(planet, 10, planets_data):
                    active_yogas.append("Amala Yoga")
                    break

        return active_yogas

    def _check_graha_malika_yoga(self, chart, planets_data):
        """
        Check for Graha Malika Yoga (chain of planets in consecutive houses)
        """
        # Create a dictionary to track which planets are in which houses
        houses_occupied = {i: [] for i in range(1, 13)}

        # Only use the main planets for this yoga
        main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        for planet in planets_data:
            if planet.Object in main_planets and planet.HouseNr:
                houses_occupied[planet.HouseNr].append(planet.Object)

        # Check for consecutive houses with planets
        consecutive_count = 0
        max_consecutive = 0
        for i in range(1, 13):
            if houses_occupied[i]:
                consecutive_count += 1
            else:
                consecutive_count = 0
            max_consecutive = max(max_consecutive, consecutive_count)

        # Check first house after 12th to handle wrapping around the chart
        if houses_occupied[1] and consecutive_count > 0:
            # Count how many houses going backward from 12 are occupied
            back_count = 0
            for i in range(12, 0, -1):
                if houses_occupied[i]:
                    back_count += 1
                else:
                    break

            if back_count > 0:
                # Adjust max consecutive to account for wrapping
                max_consecutive = max(max_consecutive, consecutive_count + back_count)

        # Need at least 5 consecutive houses with planets for Graha Malika Yoga
        return "Graha Malika Yoga" if max_consecutive >= 5 else None

    def _check_negative_yogas(self, chart, planets_data):
        """
        Check for negative yogas (challenging combinations)
        """
        negative_yogas = []

        # 1. Angarak Yoga - Mars in 1st, 4th, 7th, 8th, or 12th house
        for planet in planets_data:
            if planet.Object == "Mars" and planet.HouseNr in [1, 4, 7, 8, 12]:
                negative_yogas.append("Angarak Yoga")
                break

        # 2. Guru Chandala Yoga - Rahu and Jupiter conjunction
        if self._are_specific_planets_conjunct("Jupiter", "Rahu", planets_data) or \
                self._are_specific_planets_conjunct("Jupiter", "North Node", planets_data):
            negative_yogas.append("Guru Chandala Yoga")

        # 3. Graha Yuddha (Planetary War) - Two planets in close conjunction within 1 degree
        for i, planet1 in enumerate(planets_data):
            if planet1.Object not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                continue

            for j, planet2 in enumerate(planets_data[i + 1:]):
                if planet2.Object not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                    continue

                # Calculate separation angle
                angle = abs(planet1.LonDecDeg - planet2.LonDecDeg)
                if angle > 180:
                    angle = 360 - angle

                if angle < 1:
                    negative_yogas.append(f"Graha Yuddha ({planet1.Object}-{planet2.Object})")

        # 4. Kemadruma Yoga - Moon with no planets in 2nd, 12th, or its own sign and no aspects
        moon_data = None
        for planet in planets_data:
            if planet.Object == "Moon":
                moon_data = planet
                break

        if moon_data:
            # Find Moon's house
            moon_house = moon_data.HouseNr

            # Check if planets occupy 2nd from Moon, 12th from Moon, or same sign as Moon
            has_supporting_planet = False

            # Calculate 2nd and 12th houses from Moon
            second_from_moon = moon_house % 12 + 1
            twelfth_from_moon = (moon_house - 2) % 12 + 1

            for planet in planets_data:
                if planet.Object == "Moon":
                    continue

                # Check if planet is in 2nd or 12th from Moon
                if planet.HouseNr in [second_from_moon, twelfth_from_moon]:
                    has_supporting_planet = True
                    break

                # Check if planet is in same sign as Moon
                if planet.Rasi == moon_data.Rasi:
                    has_supporting_planet = True
                    break

                # Check if planet is aspecting Moon (simplified check)
                if self._are_planets_in_aspect(planet.Object, "Moon", planets_data):
                    has_supporting_planet = True
                    break

            if not has_supporting_planet:
                negative_yogas.append("Kemadruma Yoga")

        return negative_yogas

    # Helper methods for yoga checks
    def _get_house_lord(self, house_num, planets_data):
        """Find the lord of a specific house"""
        # First, find the sign in the house
        house_sign = None
        for planet in planets_data:
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

        for planet in planets_data:
            if planet.Object == planet1_name:
                planet1_sign = planet.Rasi
            elif planet.Object == planet2_name:
                planet2_sign = planet.Rasi

        return planet1_sign and planet2_sign and planet1_sign == planet2_sign

    def _are_specific_planets_conjunct(self, planet1_name, planet2_name, planets_data):
        """Check if two specific planets are in conjunction (same sign)"""
        planet1_sign = None
        planet2_sign = None

        for planet in planets_data:
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

        for planet in planets_data:
            if planet.Object == planet1_name:
                planet1_data = planet
            elif planet.Object == planet2_name:
                planet2_data = planet

        if not planet1_data or not planet2_data:
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
        for obj in planets_data:
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