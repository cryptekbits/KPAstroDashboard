from .base_yoga import BaseYoga


class NeutralYogas(BaseYoga):
    def __init__(self):
        super().__init__()

    @staticmethod
    def check_kala_sarpa_yoga(chart, planets_data):
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
                elif rahu_lon > ketu_lon and (ketu_lon < lon < rahu_lon):
                    all_in_arc = False
                    break

        return "Kala Sarpa Yoga" if all_in_arc else None

    @staticmethod
    def check_graha_malika_yoga(chart, planets_data):
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

    def get_all_neutral_yogas(self, chart, planets_data):
        """Get all neutral yogas present in the chart"""
        yogas = []

        kala_sarpa = self.check_kala_sarpa_yoga(chart, planets_data)
        if kala_sarpa:
            yogas.append(kala_sarpa)

        graha_malika = self.check_graha_malika_yoga(chart, planets_data)
        if graha_malika:
            yogas.append(graha_malika)

        return yogas
