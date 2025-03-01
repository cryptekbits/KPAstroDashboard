from .base_yoga import BaseYoga


class NegativeYogas(BaseYoga):
    def __init__(self):
        super().__init__()

    def check_vish_yoga(self, chart, planets_data):
        """Check for Vish Yoga (Malefic in 6, 8, 12 houses from Moon)"""
        moon_house = None
        moon_data = None
        malefic_planets = []

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                moon_house = planet['HouseNr']
                moon_data = planet
            elif planet['Object'] in ["Sun", "Mars", "Saturn", "Rahu", "Ketu", "North Node", "South Node"]:
                malefic_planets.append(planet)

        if moon_house:
            vish_houses = [(moon_house + 5) % 12 + 1, (moon_house + 7) % 12 + 1, (moon_house + 11) % 12 + 1]
            
            involved_planets = []
            for p in malefic_planets:
                if p['HouseNr'] in vish_houses:
                    involved_planets.append(f"{p['Object']} ({p['Rasi']} {p['LonDecDeg']:.2f}°)")
            
            if involved_planets:
                # Add Moon to the planets info
                if moon_data:
                    involved_planets.insert(0, f"Moon ({moon_data['Rasi']} {moon_data['LonDecDeg']:.2f}°)")
                
                return {
                    "name": "Vish Yoga", 
                    "planets_info": involved_planets
                }

        return False

    def check_angarak_yoga(self, chart, planets_data):
        """Check for Angarak Yoga - Mars in 1st, 4th, 7th, 8th, or 12th house"""
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Mars" and planet['HouseNr'] in [1, 4, 7, 8, 12]:
                planets_info = [
                    f"Mars (House {planet['HouseNr']}, {planet['Rasi']} {planet['LonDecDeg']:.2f}°)"
                ]
                return {"name": "Angarak Yoga", "planets_info": planets_info}
        return None

    def check_guru_chandala_yoga(self, chart, planets_data):
        """Check for Guru Chandala Yoga - Rahu and Jupiter conjunction"""
        jupiter_data = None
        rahu_data = None
        
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Jupiter":
                jupiter_data = planet
            elif planet['Object'] in ["Rahu", "North Node"]:
                rahu_data = planet
        
        if jupiter_data and rahu_data and (
            self._are_specific_planets_conjunct("Jupiter", "Rahu", planets_data) or
            self._are_specific_planets_conjunct("Jupiter", "North Node", planets_data)
        ):
            planets_info = [
                f"Jupiter ({jupiter_data['Rasi']} {jupiter_data['LonDecDeg']:.2f}°)",
                f"Rahu ({rahu_data['Rasi']} {rahu_data['LonDecDeg']:.2f}°)"
            ]
            return {"name": "Guru Chandala Yoga", "planets_info": planets_info}
        
        return None

    def check_graha_yuddha(self, chart, planets_data):
        """Check for Graha Yuddha (Planetary War) - Two planets in close conjunction within 1 degree"""
        yuddha_yogas = []
        planets_list = list(self._iter_planets(planets_data))
        
        for i, planet1 in enumerate(planets_list):
            if planet1['Object'] not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                continue

            for j in range(i + 1, len(planets_list)):
                planet2 = planets_list[j]
                if planet2['Object'] not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                    continue

                # Calculate separation angle
                angle = abs(planet1['LonDecDeg'] - planet2['LonDecDeg'])
                if angle > 180:
                    angle = 360 - angle

                if angle < 1:
                    planets_info = [
                        f"{planet1['Object']} ({planet1['Rasi']} {planet1['LonDecDeg']:.2f}°)",
                        f"{planet2['Object']} ({planet2['Rasi']} {planet2['LonDecDeg']:.2f}°)"
                    ]
                    yuddha_yogas.append({
                        "name": f"Graha Yuddha ({planet1['Object']}-{planet2['Object']})",
                        "planets_info": planets_info
                    })

        return yuddha_yogas

    def check_kemadruma_yoga(self, chart, planets_data):
        """
        Check for Kemadruma Yoga - Moon with no planets in 2nd, 12th, 
        or its own sign and no aspects
        """
        moon_data = None
        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                moon_data = planet
                break

        if not moon_data:
            return None

        # Find Moon's house
        moon_house = moon_data['HouseNr']

        # Check if planets occupy 2nd from Moon, 12th from Moon, or same sign as Moon
        has_supporting_planet = False
        supporting_planet = None

        # Calculate 2nd and 12th houses from Moon
        second_from_moon = moon_house % 12 + 1
        twelfth_from_moon = (moon_house - 2) % 12 + 1

        for planet in self._iter_planets(planets_data):
            if planet['Object'] == "Moon":
                continue

            # Check if planet is in 2nd or 12th from Moon
            if planet['HouseNr'] in [second_from_moon, twelfth_from_moon]:
                has_supporting_planet = True
                supporting_planet = planet
                break

            # Check if planet is in same sign as Moon
            if planet['Rasi'] == moon_data['Rasi']:
                has_supporting_planet = True
                supporting_planet = planet
                break

            # Check if planet is aspecting Moon (simplified check)
            if self._are_planets_in_aspect(planet['Object'], "Moon", planets_data):
                has_supporting_planet = True
                supporting_planet = planet
                break

        if not has_supporting_planet:
            planets_info = [
                f"Moon ({moon_data['Rasi']} {moon_data['LonDecDeg']:.2f}°)"
            ]
            return {"name": "Kemadruma Yoga", "planets_info": planets_info}
        
        return None

    def get_all_negative_yogas(self, chart, planets_data):
        """Get all negative yogas present in the chart"""
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
