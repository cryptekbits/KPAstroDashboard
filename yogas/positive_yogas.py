from .base_yoga import BaseYoga


class PositiveYogas(BaseYoga):
    def __init__(self):
        super().__init__()

    def check_budha_aditya(self, chart, planets_data):
        """Check for Budha-Aditya Yoga (Mercury and Sun in same sign)"""
        sun_data = None
        mercury_data = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Sun":
                sun_data = planet
            elif planet['Object'] == "Mercury":
                mercury_data = planet

        if sun_data and mercury_data and sun_data['Rasi'] == mercury_data['Rasi']:
            planets_info = [
                f"Sun ({sun_data['Rasi']} {sun_data['LonDecDeg']:.2f}°)",
                f"Mercury ({mercury_data['Rasi']} {mercury_data['LonDecDeg']:.2f}°)"
            ]
            return {"name": "Budha-Aditya Yoga", "planets_info": planets_info}
        return None

    def check_gaja_kesari(self, chart, planets_data):
        """Check for Gaja-Kesari Yoga (Jupiter and Moon in quadrant from each other)"""
        moon_data = None
        jupiter_data = None

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                moon_data = planet
            elif planet['Object'] == "Jupiter":
                jupiter_data = planet

        if moon_data is not None and jupiter_data is not None:
            angle = abs(moon_data['LonDecDeg'] - jupiter_data['LonDecDeg'])
            if angle > 180:
                angle = 360 - angle

            # Check for quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            if abs(angle - 90) <= 10 or abs(angle - 270) <= 10:
                planets_info = [
                    f"Moon ({moon_data['Rasi']} {moon_data['LonDecDeg']:.2f}°)",
                    f"Jupiter ({jupiter_data['Rasi']} {jupiter_data['LonDecDeg']:.2f}°)"
                ]
                return {"name": "Gaja-Kesari Yoga", "planets_info": planets_info}

        return None

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
        for planet_data in self._iter_planets(planets_data):
            name = planet_data['Object']
            if name in debilitation and planet_data['Rasi'] == debilitation[name]:
                # Planet is debilitated
                lord_of_sign = sign_lords[planet_data['Rasi']]
                lord_data = None

                # Check if lord is exalted or in a good house
                for other_planet in self._iter_planets(planets_data):
                    if other_planet['Object'] == lord_of_sign:
                        lord_data = other_planet
                        # If lord is in a kendra (1, 4, 7, 10) or trikona (1, 5, 9) house
                        good_houses = [1, 4, 5, 7, 9, 10]
                        if other_planet['HouseNr'] in good_houses:
                            planets_info = [
                                f"{name} ({planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)",
                                f"{lord_of_sign} ({lord_data['Rasi']} {lord_data['LonDecDeg']:.2f}°)"
                            ]
                            return {"name": "Neech Bhanga Raja Yoga", "planets_info": planets_info}

        return None

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
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] in own_signs:
                # Check if planet is in own sign or exalted
                in_own_sign = planet_data['Rasi'] in own_signs[planet_data['Object']]
                in_exalted = planet_data['Rasi'] == exalted_signs[planet_data['Object']]

                # Check if in kendra house
                in_kendra = planet_data['HouseNr'] in kendras

                if (in_own_sign or in_exalted) and in_kendra:
                    planet_info = f"{planet_data['Object']} ({planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)"
                    
                    if planet_data['Object'] == "Mars":
                        active_yogas.append({"name": "Ruchaka Yoga", "planets_info": [planet_info]})
                    elif planet_data['Object'] == "Mercury":
                        active_yogas.append({"name": "Bhadra Yoga", "planets_info": [planet_info]})
                    elif planet_data['Object'] == "Jupiter":
                        active_yogas.append({"name": "Hamsa Yoga", "planets_info": [planet_info]})
                    elif planet_data['Object'] == "Venus":
                        active_yogas.append({"name": "Malavya Yoga", "planets_info": [planet_info]})
                    elif planet_data['Object'] == "Saturn":
                        active_yogas.append({"name": "Sasa Yoga", "planets_info": [planet_info]})

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

        # Get planet data for lookup
        planet_data_map = {}
        for planet_data in self._iter_planets(planets_data):
            planet_data_map[planet_data['Object']] = planet_data

        # 1. Lords of 5th and 9th houses together or in exchange
        if house_lords.get(5) and house_lords.get(9):
            lord5_data = planet_data_map.get(house_lords[5])
            lord9_data = planet_data_map.get(house_lords[9])
            
            if lord5_data and lord9_data:
                if self._are_planets_conjunct(house_lords.get(5), house_lords.get(9), planets_data) or \
                        self._are_planets_in_exchange(house_lords.get(5), house_lords.get(9), planets_data):
                    planets_info = [
                        f"{house_lords[5]} (Lord of 5th, {lord5_data['Rasi']} {lord5_data['LonDecDeg']:.2f}°)",
                        f"{house_lords[9]} (Lord of 9th, {lord9_data['Rasi']} {lord9_data['LonDecDeg']:.2f}°)"
                    ]
                    active_yogas.append({"name": "Lakshmi Yoga", "planets_info": planets_info})

        # 2. Lords of 2nd and 11th houses conjunct or in exchange
        if house_lords.get(2) and house_lords.get(11):
            lord2_data = planet_data_map.get(house_lords[2])
            lord11_data = planet_data_map.get(house_lords[11])
            
            if lord2_data and lord11_data:
                if self._are_planets_conjunct(house_lords.get(2), house_lords.get(11), planets_data) or \
                        self._are_planets_in_exchange(house_lords.get(2), house_lords.get(11), planets_data):
                    planets_info = [
                        f"{house_lords[2]} (Lord of 2nd, {lord2_data['Rasi']} {lord2_data['LonDecDeg']:.2f}°)",
                        f"{house_lords[11]} (Lord of 11th, {lord11_data['Rasi']} {lord11_data['LonDecDeg']:.2f}°)"
                    ]
                    active_yogas.append({"name": "Dhana Yoga", "planets_info": planets_info})

        # 3. Jupiter in 2nd or 5th or 11th house
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] == "Jupiter" and planet_data['HouseNr'] in [2, 5, 11]:
                planets_info = [
                    f"Jupiter (House {planet_data['HouseNr']}, {planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)"
                ]
                active_yogas.append({"name": "Guru-Mangala Yoga", "planets_info": planets_info})
                break

        # 4. Venus and Jupiter conjunction
        venus_data = planet_data_map.get("Venus")
        jupiter_data = planet_data_map.get("Jupiter")
        
        if venus_data and jupiter_data and self._are_specific_planets_conjunct("Venus", "Jupiter", planets_data):
            planets_info = [
                f"Venus ({venus_data['Rasi']} {venus_data['LonDecDeg']:.2f}°)",
                f"Jupiter ({jupiter_data['Rasi']} {jupiter_data['LonDecDeg']:.2f}°)"
            ]
            active_yogas.append({"name": "Guru-Shukra Yoga", "planets_info": planets_info})

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

        # Get planet data for lookup
        planet_data_map = {}
        for planet_data in self._iter_planets(planets_data):
            planet_data_map[planet_data['Object']] = planet_data

        # 1. Lords of trine houses (1,5,9) and kendra houses (1,4,7,10) conjunct
        trine_lords = [house_lords.get(1), house_lords.get(5), house_lords.get(9)]
        kendra_lords = [house_lords.get(1), house_lords.get(4), house_lords.get(7), house_lords.get(10)]

        for trine_lord in trine_lords:
            for kendra_lord in kendra_lords:
                if trine_lord and kendra_lord and trine_lord != kendra_lord:
                    trine_lord_data = planet_data_map.get(trine_lord)
                    kendra_lord_data = planet_data_map.get(kendra_lord)
                    
                    if trine_lord_data and kendra_lord_data and self._are_planets_conjunct(trine_lord, kendra_lord, planets_data):
                        planets_info = [
                            f"{trine_lord} (Trine Lord, {trine_lord_data['Rasi']} {trine_lord_data['LonDecDeg']:.2f}°)",
                            f"{kendra_lord} (Kendra Lord, {kendra_lord_data['Rasi']} {kendra_lord_data['LonDecDeg']:.2f}°)"
                        ]
                        active_yogas.append({"name": "Raja Yoga", "planets_info": planets_info})

        # 2. Gajakesari Yoga - Moon and Jupiter in kendra from each other
        moon_data = planet_data_map.get("Moon")
        jupiter_data = planet_data_map.get("Jupiter")

        if moon_data and jupiter_data:
            angle = abs(moon_data['LonDecDeg'] - jupiter_data['LonDecDeg'])
            if angle > 180:
                angle = 360 - angle

            # Check if they're in quadrant (1, 4, 7, 10 houses - approximately 90° multiples)
            if abs(angle - 90) <= 10 or abs(angle - 180) <= 10 or abs(angle - 270) <= 10:
                planets_info = [
                    f"Moon ({moon_data['Rasi']} {moon_data['LonDecDeg']:.2f}°)",
                    f"Jupiter ({jupiter_data['Rasi']} {jupiter_data['LonDecDeg']:.2f}°)"
                ]
                active_yogas.append({"name": "Gajakesari Yoga", "planets_info": planets_info})

        # 3. Sun in 10th house with Jupiter or Venus aspect
        sun_in_10th = False
        sun_data = None
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] == "Sun" and planet_data['HouseNr'] == 10:
                sun_in_10th = True
                sun_data = planet_data
                break

        if sun_in_10th and sun_data:
            # Check for Jupiter or Venus aspect to the 10th house
            for planet_data in self._iter_planets(planets_data):
                if (planet_data['Object'] == "Jupiter" or planet_data['Object'] == "Venus") and \
                        self._is_planet_aspecting_house(planet_data, 10, planets_data):
                    planets_info = [
                        f"Sun (10th House, {sun_data['Rasi']} {sun_data['LonDecDeg']:.2f}°)",
                        f"{planet_data['Object']} (Aspecting 10th, {planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)"
                    ]
                    active_yogas.append({"name": "Amala Yoga", "planets_info": planets_info})
                    break

        return active_yogas

    def get_all_positive_yogas(self, chart, planets_data):
        """Get all positive yogas present in the chart"""
        yogas = []

        # Individual yoga checks
        budha_aditya = self.check_budha_aditya(chart, planets_data)
        if budha_aditya:
            yogas.append(budha_aditya)

        gaja_kesari = self.check_gaja_kesari(chart, planets_data)
        if gaja_kesari:
            yogas.append(gaja_kesari)

        neech_bhanga = self.check_neech_bhanga(chart, planets_data)
        if neech_bhanga:
            yogas.append(neech_bhanga)

        # Collection yoga checks
        yogas.extend(self.check_pancha_mahapurusha_yoga(chart, planets_data))
        yogas.extend(self.check_dhana_yogas(chart, planets_data))
        yogas.extend(self.check_raja_yogas(chart, planets_data))

        return yogas
