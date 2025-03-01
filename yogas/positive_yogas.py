from .base_yoga import BaseYoga


class PositiveYogas(BaseYoga):
    """
    Class for calculating positive yogas (auspicious combinations).
    Includes Excellent and Good yogas as defined in the metadata.
    """

    def __init__(self):
        """Initialize the positive yogas calculator."""
        super().__init__()

    def check_budha_aditya(self, chart, planets_data):
        """
        Check for Budha-Aditya Yoga (Mercury and Sun in same sign).

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        dict or None
            Yoga information if present, None otherwise
        """
        sun_data = self._get_planet_by_name("Sun", planets_data)
        mercury_data = self._get_planet_by_name("Mercury", planets_data)

        if sun_data and mercury_data and sun_data['Rasi'] == mercury_data['Rasi']:
            planets_info = [
                self._format_planet_info(sun_data),
                self._format_planet_info(mercury_data)
            ]
            return self.create_yoga_result("Budha-Aditya Yoga", planets_info)
        return None

    def check_gaja_kesari(self, chart, planets_data):
        """
        Check for Gaja-Kesari Yoga (Jupiter and Moon in quadrant from each other).

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        dict or None
            Yoga information if present, None otherwise
        """
        moon_data = self._get_planet_by_name("Moon", planets_data)
        jupiter_data = self._get_planet_by_name("Jupiter", planets_data)

        if moon_data is not None and jupiter_data is not None:
            angle = abs(moon_data['LonDecDeg'] - jupiter_data['LonDecDeg'])
            if angle > 180:
                angle = 360 - angle

            # Check for quadrant (approximately 90° or 270° with 10° orb)
            if abs(angle - 90) <= 10 or abs(angle - 270) <= 10:
                planets_info = [
                    self._format_planet_info(moon_data),
                    self._format_planet_info(jupiter_data)
                ]
                return self.create_yoga_result("Gaja-Kesari Yoga", planets_info)

        return None

    def check_neech_bhanga(self, chart, planets_data):
        """
        Check for Neech Bhanga Raja Yoga (Debilitated planet with cancellation).

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        dict or None
            Yoga information if present, None otherwise
        """
        # Check if any planet is in debilitation and if its lord is well-placed
        for planet_data in self._iter_planets(planets_data):
            name = planet_data['Object']
            # Skip nodes, Uranus, Neptune, etc.
            if name not in self.debilitation_signs:
                continue

            if self._is_planet_debilitated(name, planet_data['Rasi']):
                # Planet is debilitated
                lord_of_sign = self.sign_lords[planet_data['Rasi']]
                lord_data = self._get_planet_by_name(lord_of_sign, planets_data)

                if lord_data:
                    # If lord is in a kendra (1, 4, 7, 10) or trikona (1, 5, 9) house
                    good_houses = self.kendra_houses + self.trikona_houses
                    if lord_data['HouseNr'] in good_houses:
                        planets_info = [
                            self._format_planet_info(planet_data),
                            self._format_planet_info(lord_data)
                        ]
                        return self.create_yoga_result("Neech Bhanga Raja Yoga", planets_info)

        return None

    def check_pancha_mahapurusha_yoga(self, chart, planets_data):
        """
        Check for Pancha Mahapurusha Yogas (five great person yogas).

        - Ruchaka: Mars in own sign or exalted in kendra
        - Bhadra: Mercury in own sign or exalted in kendra
        - Hamsa: Jupiter in own sign or exalted in kendra
        - Malavya: Venus in own sign or exalted in kendra
        - Sasa: Saturn in own sign or exalted in kendra

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        list
            List of yoga dictionaries
        """
        active_yogas = []

        # Check each planet
        for planet_data in self._iter_planets(planets_data):
            planet_name = planet_data['Object']

            # Only check the five planets involved in Pancha Mahapurusha Yoga
            if planet_name not in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                continue

            # Check if planet is in own sign or exalted
            in_own_sign = self._is_planet_in_own_sign(planet_name, planet_data['Rasi'])
            in_exalted = self._is_planet_exalted(planet_name, planet_data['Rasi'])

            # Check if in kendra house
            in_kendra = self._is_in_kendra(planet_data['HouseNr'])

            if (in_own_sign or in_exalted) and in_kendra:
                planets_info = [self._format_planet_info(planet_data)]

                if planet_name == "Mars":
                    active_yogas.append(self.create_yoga_result("Ruchaka Yoga", planets_info))
                elif planet_name == "Mercury":
                    active_yogas.append(self.create_yoga_result("Bhadra Yoga", planets_info))
                elif planet_name == "Jupiter":
                    active_yogas.append(self.create_yoga_result("Hamsa Yoga", planets_info))
                elif planet_name == "Venus":
                    active_yogas.append(self.create_yoga_result("Malavya Yoga", planets_info))
                elif planet_name == "Saturn":
                    active_yogas.append(self.create_yoga_result("Sasa Yoga", planets_info))

        return active_yogas

    def check_dhana_yogas(self, chart, planets_data):
        """
        Check for Dhana Yogas (wealth-producing combinations).

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        list
            List of yoga dictionaries
        """
        active_yogas = []

        # Find lords of houses
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # 1. Lords of 5th and 9th houses together or in exchange
        if house_lords.get(5) and house_lords.get(9):
            lord5_data = self._get_planet_by_name(house_lords[5], planets_data)
            lord9_data = self._get_planet_by_name(house_lords[9], planets_data)

            if lord5_data and lord9_data:
                # Check for conjunction or exchange
                if self._are_planets_conjunct(house_lords[5], house_lords[9], planets_data) or \
                        self._are_planets_in_exchange(house_lords[5], house_lords[9], planets_data):
                    planets_info = [
                        f"{self._format_planet_info(lord5_data)} (Lord of 5th)",
                        f"{self._format_planet_info(lord9_data)} (Lord of 9th)"
                    ]
                    active_yogas.append(self.create_yoga_result("Lakshmi Yoga", planets_info))

        # 2. Lords of 2nd and 11th houses conjunct or in exchange
        if house_lords.get(2) and house_lords.get(11):
            lord2_data = self._get_planet_by_name(house_lords[2], planets_data)
            lord11_data = self._get_planet_by_name(house_lords[11], planets_data)

            if lord2_data and lord11_data:
                # Check for conjunction or exchange
                if self._are_planets_conjunct(house_lords[2], house_lords[11], planets_data) or \
                        self._are_planets_in_exchange(house_lords[2], house_lords[11], planets_data):
                    planets_info = [
                        f"{self._format_planet_info(lord2_data)} (Lord of 2nd)",
                        f"{self._format_planet_info(lord11_data)} (Lord of 11th)"
                    ]
                    active_yogas.append(self.create_yoga_result("Dhana Yoga", planets_info))

        # 3. Jupiter in 2nd or 5th or 11th house
        jupiter_data = self._get_planet_by_name("Jupiter", planets_data)
        if jupiter_data and jupiter_data['HouseNr'] in [2, 5, 11]:
            planets_info = [self._format_planet_info(jupiter_data)]
            active_yogas.append(self.create_yoga_result("Guru-Mangala Yoga", planets_info))

        # 4. Venus and Jupiter conjunction
        venus_data = self._get_planet_by_name("Venus", planets_data)
        if venus_data and jupiter_data and self._are_specific_planets_conjunct("Venus", "Jupiter", planets_data):
            planets_info = [
                self._format_planet_info(venus_data),
                self._format_planet_info(jupiter_data)
            ]
            active_yogas.append(self.create_yoga_result("Guru-Shukra Yoga", planets_info))

        return active_yogas

    def check_raja_yogas(self, chart, planets_data):
        """
        Check for Raja Yogas (combinations indicating power, status, and success).

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        list
            List of yoga dictionaries
        """
        active_yogas = []

        # Find houses lordships
        house_lords = {}
        for i in range(1, 13):
            house_lords[i] = self._get_house_lord(i, planets_data)

        # 1. Lords of trine houses (1,5,9) and kendra houses (1,4,7,10) conjunct
        trine_lords = [house_lords.get(i) for i in self.trikona_houses if house_lords.get(i)]
        kendra_lords = [house_lords.get(i) for i in self.kendra_houses if house_lords.get(i)]

        for trine_lord in trine_lords:
            for kendra_lord in kendra_lords:
                if trine_lord and kendra_lord and trine_lord != kendra_lord:
                    trine_lord_data = self._get_planet_by_name(trine_lord, planets_data)
                    kendra_lord_data = self._get_planet_by_name(kendra_lord, planets_data)

                    if trine_lord_data and kendra_lord_data and self._are_planets_conjunct(trine_lord, kendra_lord,
                                                                                           planets_data):
                        trine_house = next((h for h in self.trikona_houses if house_lords.get(h) == trine_lord), None)
                        kendra_house = next((h for h in self.kendra_houses if house_lords.get(h) == kendra_lord), None)

                        planets_info = [
                            f"{self._format_planet_info(trine_lord_data)} (Lord of {trine_house})",
                            f"{self._format_planet_info(kendra_lord_data)} (Lord of {kendra_house})"
                        ]
                        active_yogas.append(self.create_yoga_result("Raja Yoga", planets_info))

        # 2. Gajakesari Yoga - Moon and Jupiter in kendra from each other
        moon_data = self._get_planet_by_name("Moon", planets_data)
        jupiter_data = self._get_planet_by_name("Jupiter", planets_data)

        if moon_data and jupiter_data:
            angle = abs(moon_data['LonDecDeg'] - jupiter_data['LonDecDeg'])
            if angle > 180:
                angle = 360 - angle

            # Check if they're in quadrant (90°, 180°, 270° with orb)
            if abs(angle - 90) <= 10 or abs(angle - 180) <= 10 or abs(angle - 270) <= 10:
                planets_info = [
                    self._format_planet_info(moon_data),
                    self._format_planet_info(jupiter_data)
                ]
                active_yogas.append(self.create_yoga_result("Gajakesari Yoga", planets_info))

        # 3. Sun in 10th house with Jupiter or Venus aspect
        sun_data = self._get_planet_by_name("Sun", planets_data)
        if sun_data and sun_data['HouseNr'] == 10:
            # Check for Jupiter or Venus aspect to Sun
            for planet_name in ["Jupiter", "Venus"]:
                planet_data = self._get_planet_by_name(planet_name, planets_data)
                if planet_data and self._are_planets_in_aspect(planet_name, "Sun", planets_data):
                    planets_info = [
                        f"{self._format_planet_info(sun_data)} (10th House)",
                        f"{self._format_planet_info(planet_data)} (Aspecting Sun)"
                    ]
                    active_yogas.append(self.create_yoga_result("Amala Yoga", planets_info))
                    break  # Only need one instance of the yoga

        return active_yogas

    def get_all_positive_yogas(self, chart, planets_data):
        """
        Get all positive yogas present in the chart.

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : DataFrame or list
            Planetary position data

        Returns:
        --------
        list
            List of yoga dictionaries
        """
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