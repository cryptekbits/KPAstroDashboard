from .base_yoga import BaseYoga

class NegativeYogas(BaseYoga):
    def __init__(self):
        super().__init__()
        
    def check_vish_yoga(self, chart, planets_data):
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
        
    def check_angarak_yoga(self, chart, planets_data):
        """Check for Angarak Yoga - Mars in 1st, 4th, 7th, 8th, or 12th house"""
        for planet in planets_data:
            if planet.Object == "Mars" and planet.HouseNr in [1, 4, 7, 8, 12]:
                return True
        return False
        
    def check_guru_chandala_yoga(self, chart, planets_data):
        """Check for Guru Chandala Yoga - Rahu and Jupiter conjunction"""
        return (self._are_specific_planets_conjunct("Jupiter", "Rahu", planets_data) or
                self._are_specific_planets_conjunct("Jupiter", "North Node", planets_data))
                
    def check_graha_yuddha(self, chart, planets_data):
        """Check for Graha Yuddha (Planetary War) - Two planets in close conjunction within 1 degree"""
        yuddha_yogas = []
        
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
                    yuddha_yogas.append(f"Graha Yuddha ({planet1.Object}-{planet2.Object})")
                    
        return yuddha_yogas
        
    def check_kemadruma_yoga(self, chart, planets_data):
        """
        Check for Kemadruma Yoga - Moon with no planets in 2nd, 12th, 
        or its own sign and no aspects
        """
        moon_data = None
        for planet in planets_data:
            if planet.Object == "Moon":
                moon_data = planet
                break

        if not moon_
            return False

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

        return not has_supporting_planet
        
    def get_all_negative_yogas(self, chart, planets_data):
        """Get all negative yogas present in the chart"""
        yogas = []
        
        if self.check_vish_yoga(chart, planets_data):
            yogas.append("Vish Yoga")
            
        if self.check_angarak_yoga(chart, planets_data):
            yogas.append("Angarak Yoga")
            
        if self.check_guru_chandala_yoga(chart, planets_data):
            yogas.append("Guru Chandala Yoga")
            
        graha_yuddha = self.check_graha_yuddha(chart, planets_data)
        if graha_yuddha:
            yogas.extend(graha_yuddha)
            
        if self.check_kemadruma_yoga(chart, planets_data):
            yogas.append("Kemadruma Yoga")
            
        return yogas
