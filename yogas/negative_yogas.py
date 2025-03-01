from .base_yoga import BaseYoga


class NegativeYogas(BaseYoga):
    """
    Class for calculating negative yogas (inauspicious combinations).
    Includes Bad and Worst yogas as defined in the metadata.
    """

    def __init__(self):
        """Initialize the negative yogas calculator."""
        super().__init__()

    def check_vish_yoga(self, chart, planets_data):
        """
        Check for Vish Yoga (Malefic in 6, 8, 12 houses from Moon).

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
        if not moon_data or not moon_data['HouseNr']:
            return None

        moon_house = moon_data['HouseNr']

        # Calculate the 6th, 8th, and 12th houses from Moon
        vish_houses = [
            (moon_house + 5) % 12 + 1,  # 6th from Moon
            (moon_house + 7) % 12 + 1,  # 8th from Moon
            (moon_house + 11) % 12 + 1  # 12th from Moon
        ]

        # Check for malefics in these houses
        malefics_in_vish_houses = []

        for planet_data in self._iter_planets(planets_data):
            if (planet_data['Object'] in self.malefic_planets and
                    planet_data['HouseNr'] in vish_houses):
                malefics_in_vish_houses.append(planet_data)

        if malefics_in_vish_houses:
            planets_info = [self._format_planet_info(moon_data)]
            planets_info.extend([self._format_planet_info(planet) for planet in malefics_in_vish_houses])
            return self.create_yoga_result("Vish Yoga", planets_info)

        return None

    def check_angarak_yoga(self, chart, planets_data):
        """
        Check for Angarak Yoga - Mars in 1st, 4th, 7th, 8th, or 12th house.

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
        mars_data = self._get_planet_by_name("Mars", planets_data)

        if mars_data and mars_data['HouseNr'] in [1, 4, 7, 8, 12]:
            planets_info = [self._format_planet_info(mars_data)]
            return self.create_yoga_result("Angarak Yoga", planets_info)

        return None

    def check_guru_chandala_yoga(self, chart, planets_data):
        """
        Check for Guru Chandala Yoga - Rahu and Jupiter conjunction.

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
        jupiter_data = self._get_planet_by_name("Jupiter", planets_data)

        # Try both Rahu and North Node (handle different naming conventions)
        rahu_data = self._get_planet_by_name("Rahu", planets_data)
        if not rahu_data:
            rahu_data = self._get_planet_by_name("North Node", planets_data)

        if jupiter_data and rahu_data and jupiter_data['Rasi'] == rahu_data['Rasi']:
            planets_info = [
                self._format_planet_info(jupiter_data),
                self._format_planet_info(rahu_data)
            ]
            return self.create_yoga_result("Guru Chandala Yoga", planets_info)

        return None

    def check_graha_yuddha(self, chart, planets_data):
        """
        Check for Graha Yuddha (Planetary War) - Two planets in close conjunction within 1 degree.

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
        yuddha_yogas = []

        # Get all main planets (exclude Rahu, Ketu, etc.)
        main_planets = []
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                main_planets.append(planet_data)

        # Check each pair of planets
        for i in range(len(main_planets)):
            for j in range(i + 1, len(main_planets)):
                planet1 = main_planets[i]
                planet2 = main_planets[j]

                # Calculate separation angle
                angle = abs(planet1['LonDecDeg'] - planet2['LonDecDeg'])
                if angle > 180:
                    angle = 360 - angle

                # Planetary war occurs when planets are within 1 degree
                if angle < 1:
                    planets_info = [
                        self._format_planet_info(planet1),
                        self._format_planet_info(planet2)
                    ]
                    yuddha_yogas.append(self.create_yoga_result(
                        f"Graha Yuddha ({planet1['Object']}-{planet2['Object']})",
                        planets_info
                    ))

        return yuddha_yogas

    def check_kemadruma_yoga(self, chart, planets_data):
        """
        Check for Kemadruma Yoga - Moon with no planets in 2nd, 12th,
        or its own sign and no aspects.

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
        if not moon_data or not moon_data['HouseNr']:
            return None

        moon_house = moon_data['HouseNr']

        # Calculate 2nd and 12th houses from Moon
        second_from_moon = moon_house % 12 + 1
        twelfth_from_moon = (moon_house - 2) % 12 + 1

        # Check if any planet is in 2nd or 12th from Moon, or in same sign as Moon, or aspects Moon
        supporting_planet_found = False

        for planet_data in self._iter_planets(planets_data):
            # Skip Moon itself
            if planet_data['Object'] == "Moon":
                continue

            # Check if planet is in 2nd or 12th from Moon
            if planet_data['HouseNr'] in [second_from_moon, twelfth_from_moon]:
                supporting_planet_found = True
                break

            # Check if planet is in same sign as Moon
            if planet_data['Rasi'] == moon_data['Rasi']:
                supporting_planet_found = True
                break

            # Check if planet aspects Moon
            if self._are_planets_in_aspect(planet_data['Object'], "Moon", planets_data):
                supporting_planet_found = True
                break

        if not supporting_planet_found:
            planets_info = [self._format_planet_info(moon_data)]
            return self.create_yoga_result("Kemadruma Yoga", planets_info)

        return None

    def get_all_negative_yogas(self, chart, planets_data):
        """
        Get all negative yogas present in the chart.

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

        vish_yoga = self.check_vish_yoga(chart, planets_data)
        if vish_yoga:
            yogas.append(vish_yoga)

        angarak_yoga = self.check_angarak_yoga(chart, planets_data)
        if angarak_yoga:
            yogas.append(angarak_yoga)

        guru_chandala = self.check_guru_chandala_yoga(chart, planets_data)
        if guru_chandala:
            yogas.append(guru_chandala)

        graha_yuddha = self.check_graha_yuddha(chart, planets_data)
        if graha_yuddha:
            yogas.extend(graha_yuddha)

        kemadruma = self.check_kemadruma_yoga(chart, planets_data)
        if kemadruma:
            yogas.append(kemadruma)

        return yogas