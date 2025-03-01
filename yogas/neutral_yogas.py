from .base_yoga import BaseYoga


class NeutralYogas(BaseYoga):
    """
    Class for calculating neutral yogas (combinations with mixed effects).
    """

    def __init__(self):
        """Initialize the neutral yogas calculator."""
        super().__init__()

    def check_kala_sarpa_yoga(self, chart, planets_data):
        """
        Check for Kala Sarpa Yoga (all planets between Rahu and Ketu).

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
        # Try to get Rahu (North Node) data
        rahu_data = self._get_planet_by_name("Rahu", planets_data)
        if not rahu_data:
            rahu_data = self._get_planet_by_name("North Node", planets_data)

        # Try to get Ketu (South Node) data
        ketu_data = self._get_planet_by_name("Ketu", planets_data)
        if not ketu_data:
            ketu_data = self._get_planet_by_name("South Node", planets_data)

        if not rahu_data or not ketu_data:
            return None

        # Get the main planets (Sun through Saturn)
        main_planets = []
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                main_planets.append(planet_data)

        # If no main planets found, we can't check for this yoga
        if not main_planets:
            return None

        # Get longitudes of Rahu and Ketu
        rahu_lon = rahu_data['LonDecDeg']
        ketu_lon = ketu_data['LonDecDeg']

        # Define arc from Rahu to Ketu (they should be roughly 180° apart)
        # If Rahu is at a smaller longitude than Ketu
        if rahu_lon < ketu_lon:
            # Check if all planets are between Rahu and Ketu
            for planet in main_planets:
                planet_lon = planet['LonDecDeg']
                if planet_lon < rahu_lon or planet_lon > ketu_lon:
                    return None  # Some planet is outside the Rahu-Ketu arc
        else:  # If Rahu is at a larger longitude than Ketu
            # Check if all planets are between Rahu and Ketu (crossing 0° boundary)
            for planet in main_planets:
                planet_lon = planet['LonDecDeg']
                if planet_lon > ketu_lon and planet_lon < rahu_lon:
                    return None  # Some planet is outside the Rahu-Ketu arc

        # If we got here, all planets are between Rahu and Ketu, so Kala Sarpa Yoga is active
        planets_info = [
            self._format_planet_info(rahu_data),
            self._format_planet_info(ketu_data)
        ]

        # Add other planets to the info
        for planet in main_planets:
            planets_info.append(self._format_planet_info(planet))

        return self.create_yoga_result("Kala Sarpa Yoga", planets_info)

    def check_graha_malika_yoga(self, chart, planets_data):
        """
        Check for Graha Malika Yoga (chain of planets in consecutive houses).

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
        # Create a dictionary to track which planets are in which houses
        houses_occupied = {i: [] for i in range(1, 13)}
        planets_by_house = {i: [] for i in range(1, 13)}

        # Only use the main planets for this yoga
        main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        # Map planets to houses
        for planet_data in self._iter_planets(planets_data):
            if planet_data['Object'] in main_planets and planet_data['HouseNr']:
                house_num = planet_data['HouseNr']
                houses_occupied[house_num].append(planet_data['Object'])
                planets_by_house[house_num].append(planet_data)

        # Find the longest sequence of consecutive houses with planets
        max_consecutive = 0
        start_house = 0

        # Check each possible starting house
        for start in range(1, 13):
            consecutive = 0
            current = start

            # Count consecutive houses starting from this house
            while houses_occupied[current]:
                consecutive += 1
                current = current % 12 + 1
                if current == start:  # Full circle, all houses have planets
                    consecutive = 12
                    break

            if consecutive > max_consecutive:
                max_consecutive = consecutive
                start_house = start

        # Need at least 5 consecutive houses with planets for Graha Malika Yoga
        if max_consecutive >= 5:
            planets_info = []

            # Collect planets in the consecutive houses
            current = start_house
            for _ in range(max_consecutive):
                for planet_data in planets_by_house[current]:
                    planets_info.append(self._format_planet_info(planet_data))
                current = current % 12 + 1

            return self.create_yoga_result("Graha Malika Yoga", planets_info)

        return None

    def get_all_neutral_yogas(self, chart, planets_data):
        """
        Get all neutral yogas present in the chart.

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

        kala_sarpa = self.check_kala_sarpa_yoga(chart, planets_data)
        if kala_sarpa:
            yogas.append(kala_sarpa)

        graha_malika = self.check_graha_malika_yoga(chart, planets_data)
        if graha_malika:
            yogas.append(graha_malika)

        return yogas