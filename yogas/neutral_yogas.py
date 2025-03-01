from .base_yoga import BaseYoga


class NeutralYogas(BaseYoga):
    def __init__(self):
        super().__init__()

    def check_kala_sarpa_yoga(self, chart, planets_data):
        """
        Check for Kala Sarpa Yoga (all planets between Rahu and Ketu)
        """
        rahu_data = None
        ketu_data = None
        other_planets = []

        for planet in self._iter_planets(planets_data):
            if planet['Object'] in ["North Node", "Rahu"]:
                rahu_data = planet
            elif planet['Object'] in ["South Node", "Ketu"]:
                ketu_data = planet
            elif planet['Object'] in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                other_planets.append(planet)

        if rahu_data is None or ketu_data is None:
            return None

        rahu_lon = rahu_data['LonDecDeg']
        ketu_lon = ketu_data['LonDecDeg']

        # Define arc from Rahu to Ketu
        if rahu_lon < ketu_lon:
            # If Rahu is earlier in the zodiac than Ketu
            rahu_ketu_arc = [rahu_lon, ketu_lon]
        else:
            # If Rahu is later in the zodiac than Ketu
            rahu_ketu_arc = [rahu_lon, ketu_lon + 360]

        # Check if all planets are in this arc
        all_in_arc = True
        for planet in other_planets:
            lon = planet['LonDecDeg']
            if rahu_lon < ketu_lon and (lon < rahu_lon or lon > ketu_lon):
                all_in_arc = False
                break
            elif rahu_lon > ketu_lon and (ketu_lon < lon < rahu_lon):
                all_in_arc = False
                break

        if all_in_arc:
            planets_info = [
                f"Rahu ({rahu_data['Rasi']} {rahu_data['LonDecDeg']:.2f}°)",
                f"Ketu ({ketu_data['Rasi']} {ketu_data['LonDecDeg']:.2f}°)"
            ]
            
            # Add other planets to the info
            for planet in other_planets:
                planets_info.append(f"{planet['Object']} ({planet['Rasi']} {planet['LonDecDeg']:.2f}°)")
                
            return {"name": "Kala Sarpa Yoga", "planets_info": planets_info}
        
        return None

    def check_graha_malika_yoga(self, chart, planets_data):
        """
        Check for Graha Malika Yoga (chain of planets in consecutive houses)
        """
        # Create a dictionary to track which planets are in which houses
        houses_occupied = {i: [] for i in range(1, 13)}

        # Only use the main planets for this yoga
        main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        planet_data_by_house = {}

        for planet in self._iter_planets(planets_data):
            if planet['Object'] in main_planets and planet['HouseNr']:
                houses_occupied[planet['HouseNr']].append(planet['Object'])
                if planet['HouseNr'] not in planet_data_by_house:
                    planet_data_by_house[planet['HouseNr']] = []
                planet_data_by_house[planet['HouseNr']].append(planet)

        # Check for consecutive houses with planets
        consecutive_count = 0
        max_consecutive = 0
        consecutive_start = 0
        
        for i in range(1, 13):
            if houses_occupied[i]:
                if consecutive_count == 0:
                    consecutive_start = i
                consecutive_count += 1
            else:
                consecutive_count = 0
            
            if consecutive_count > max_consecutive:
                max_consecutive = consecutive_count
                consecutive_start_house = consecutive_start

        # Check first house after 12th to handle wrapping around the chart
        wrap_consecutive = 0
        wrap_start = 0
        
        if houses_occupied[1]:
            # Count backwards from 12
            for i in range(12, 0, -1):
                if houses_occupied[i]:
                    if wrap_consecutive == 0:
                        wrap_start = i
                    wrap_consecutive += 1
                else:
                    break
                    
            # Count forward from 1
            forward_count = 0
            for i in range(1, 13):
                if houses_occupied[i]:
                    forward_count += 1
                else:
                    break
                    
            if wrap_consecutive + forward_count > max_consecutive:
                max_consecutive = wrap_consecutive + forward_count
                consecutive_start_house = wrap_start

        # Need at least 5 consecutive houses with planets for Graha Malika Yoga
        if max_consecutive >= 5:
            planets_info = []
            
            # Collect planets in the consecutive houses
            for i in range(max_consecutive):
                house = (consecutive_start_house + i - 1) % 12 + 1
                for planet_data in planet_data_by_house.get(house, []):
                    planets_info.append(
                        f"{planet_data['Object']} (House {house}, {planet_data['Rasi']} {planet_data['LonDecDeg']:.2f}°)"
                    )
            
            return {"name": "Graha Malika Yoga", "planets_info": planets_info}
        
        return None

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
