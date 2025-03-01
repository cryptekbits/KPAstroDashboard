from .base_yoga import BaseYoga


class PositiveYogas(BaseYoga):
    def __init__(self):
        super().__init__()

    def check_budha_aditya(self, chart, planets_data):
        """Check for Budha-Aditya Yoga (Mercury and Sun in same sign)"""
        sun_sign = None
        mercury_sign = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Sun":
                sun_sign = planet['Rasi']
            elif planet['Object'] == "Mercury":
                mercury_sign = planet['Rasi']

        return sun_sign and mercury_sign and sun_sign == mercury_sign

    def check_gaja_kesari(self, chart, planets_data):
        """Check for Gaja-Kesari Yoga (Jupiter and Moon in quadrant from each other)"""
        moon_pos = None
        jupiter_pos = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                moon_pos = planet['LonDecDeg']
            elif planet['Object'] == "Jupiter":
                jupiter_pos = planet['LonDecDeg']

        if moon_pos is not None and jupiter_pos is not None:
            angle = abs(moon_pos - jupiter_pos)
            if angle > 180:
                angle = 360 - angle

            # Check for quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            return abs(angle - 90) <= 10 or abs(angle - 270) <= 10

        return False

    def check_neech_bhanga(self, chart, planets_data):
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
        for planet in self._iter_planets(planets_data):
            name = planet['Object']
            if name in debilitation and planet['Rasi'] == debilitation[name]:
                # Planet is debilitated
                lord_of_sign = sign_lords[planet['Rasi']]

                # Check if lord is exalted or in a good house
                for other_planet in self._iter_planets(planets_data):
                    if other_planet['Object'] == lord_of_sign:
                        # If lord is in a kendra (1, 4, 7, 10) or trikona (1, 5, 9) house
                        good_houses = [1, 4, 5, 7, 9, 10]
                        if other_planet['HouseNr'] in good_houses:
                            return True

        return False

    def check_pancha_mahapurusha_yoga(self, chart, planets_data):
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
        for planet in self._iter_planets(planets_data):
            if planet['Object'] in own_signs:
                # Check if planet is in own sign or exalted
                in_own_sign = planet['Rasi'] in own_signs[planet['Object']]
                in_exalted = planet['Rasi'] == exalted_signs[planet['Object']]

                # Check if in kendra house
                in_kendra = planet['HouseNr'] in kendras

                if (in_own_sign or in_exalted) and in_kendra:
                    if planet['Object'] == "Mars":
                        active_yogas.append("Ruchaka Yoga")
                    elif planet['Object'] == "Mercury":
                        active_yogas.append("Bhadra Yoga")
                    elif planet['Object'] == "Jupiter":
                        active_yogas.append("Hamsa Yoga")
                    elif planet['Object'] == "Venus":
                        active_yogas.append("Malavya Yoga")
                    elif planet['Object'] == "Saturn":
                        active_yogas.append("Sasa Yoga")

        return active_yogas

    def check_dhana_yogas(self, chart, planets_data):
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
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Jupiter" and planet['HouseNr'] in [2, 5, 11]:
                active_yogas.append("Guru-Mangala Yoga")
                break

        # 4. Venus and Jupiter conjunction
        if self._are_specific_planets_conjunct("Venus", "Jupiter", planets_data):
            active_yogas.append("Guru-Shukra Yoga")

        return active_yogas

    def check_raja_yogas(self, chart, planets_data):
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

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                moon_pos = planet['LonDecDeg']
            elif planet['Object'] == "Jupiter":
                jupiter_pos = planet['LonDecDeg']

        if moon_pos is not None and jupiter_pos is not None:
            angle = abs(moon_pos - jupiter_pos)
            if angle > 180:
                angle = 360 - angle

            # Check if they're in quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            if abs(angle - 90) <= 10 or abs(angle - 180) <= 10 or abs(angle - 270) <= 10:
                active_yogas.append("Gajakesari Yoga")

        # 3. Sun in 10th house with Jupiter or Venus aspect
        sun_in_10th = False
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Sun" and planet['HouseNr'] == 10:
                sun_in_10th = True
                break

        if sun_in_10th:
            # Check for Jupiter or Venus aspect to the 10th house
            for planet in self._iter_planets(planets_data):
                if (planet['Object'] == "Jupiter" or planet['Object'] == "Venus") and \
                        self._is_planet_aspecting_house(planet, 10, planets_data):
                    active_yogas.append("Amala Yoga")
                    break

        return active_yogas

    def get_all_positive_yogas(self, chart, planets_data):
        """Get all positive yogas present in the chart"""
        yogas = []

        # Individual yoga checks
        if self.check_budha_aditya(chart, planets_data):
            yogas.append("Budha-Aditya Yoga")

        if self.check_gaja_kesari(chart, planets_data):
            yogas.append("Gaja-Kesari Yoga")

        if self.check_neech_bhanga(chart, planets_data):
            yogas.append("Neech Bhanga Raja Yoga")

        # Collection yoga checks
        yogas.extend(self.check_pancha_mahapurusha_yoga(chart, planets_data))
        yogas.extend(self.check_dhana_yogas(chart, planets_data))
        yogas.extend(self.check_raja_yogas(chart, planets_data))

        return yogas
