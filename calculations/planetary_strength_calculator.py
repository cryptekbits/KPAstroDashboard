import pandas as pd
import math
from astro_engine.core import VedicHoroscopeData


class PlanetaryStrengthCalculator:
    """
    Class for calculating various planetary strengths according to Vedic astrology.
    This includes Shadbala (six-fold strength) and Digbala (directional strength).
    """

    def __init__(self, position_calculator):
        """
        Initialize with a position calculator.
        
        Parameters:
        -----------
        position_calculator : PlanetPositionCalculator
            The position calculator to use for getting planetary positions
        """
        self.position_calculator = position_calculator
        
        # Natural friends and enemies of planets
        self.natural_relationships = {
            "Sun": {
                "friends": ["Moon", "Mars", "Jupiter"],
                "enemies": ["Venus", "Saturn"],
                "neutral": ["Mercury"]
            },
            "Moon": {
                "friends": ["Sun", "Mercury"],
                "enemies": ["Saturn"],
                "neutral": ["Mars", "Jupiter", "Venus"]
            },
            "Mercury": {
                "friends": ["Sun", "Venus"],
                "enemies": ["Moon"],
                "neutral": ["Mars", "Jupiter", "Saturn"]
            },
            "Venus": {
                "friends": ["Mercury", "Saturn"],
                "enemies": ["Sun", "Moon"],
                "neutral": ["Mars", "Jupiter"]
            },
            "Mars": {
                "friends": ["Sun", "Moon", "Jupiter"],
                "enemies": ["Mercury"],
                "neutral": ["Venus", "Saturn"]
            },
            "Jupiter": {
                "friends": ["Sun", "Moon", "Mars"],
                "enemies": ["Mercury", "Venus"],
                "neutral": ["Saturn"]
            },
            "Saturn": {
                "friends": ["Mercury", "Venus"],
                "enemies": ["Sun", "Moon", "Mars"],
                "neutral": ["Jupiter"]
            },
            # Adding relationships for Rahu and Ketu based on traditional texts
            "Rahu": {
                "friends": ["Venus", "Saturn"],
                "enemies": ["Sun", "Moon"],
                "neutral": ["Mercury", "Mars", "Jupiter"]
            },
            "Ketu": {
                "friends": ["Mercury", "Venus"],
                "enemies": ["Moon"],
                "neutral": ["Sun", "Mars", "Jupiter", "Saturn"]
            },
            # Modern planets - relationships based on modern interpretations
            "Uranus": {
                "friends": ["Mercury", "Saturn"],
                "enemies": ["Venus", "Moon"],
                "neutral": ["Sun", "Mars", "Jupiter"]
            },
            "Neptune": {
                "friends": ["Venus", "Moon"],
                "enemies": ["Mercury", "Saturn"],
                "neutral": ["Sun", "Mars", "Jupiter"]
            }
        }
        
        # Exaltation and debilitation degrees for planets
        self.exaltation_debilitation = {
            "Sun": {"exaltation": 10, "exaltation_sign": "Aries", "debilitation": 10, "debilitation_sign": "Libra"},
            "Moon": {"exaltation": 3, "exaltation_sign": "Taurus", "debilitation": 3, "debilitation_sign": "Scorpio"},
            "Mercury": {"exaltation": 15, "exaltation_sign": "Virgo", "debilitation": 15, "debilitation_sign": "Pisces"},
            "Venus": {"exaltation": 27, "exaltation_sign": "Pisces", "debilitation": 27, "debilitation_sign": "Virgo"},
            "Mars": {"exaltation": 28, "exaltation_sign": "Capricorn", "debilitation": 28, "debilitation_sign": "Cancer"},
            "Jupiter": {"exaltation": 5, "exaltation_sign": "Cancer", "debilitation": 5, "debilitation_sign": "Capricorn"},
            "Saturn": {"exaltation": 20, "exaltation_sign": "Libra", "debilitation": 20, "debilitation_sign": "Aries"},
            # Adding exaltation/debilitation for Rahu and Ketu
            "Rahu": {"exaltation": 3, "exaltation_sign": "Taurus", "debilitation": 3, "debilitation_sign": "Scorpio"},
            "Ketu": {"exaltation": 3, "exaltation_sign": "Scorpio", "debilitation": 3, "debilitation_sign": "Taurus"},
            # Modern planets - based on modern interpretations
            "Uranus": {"exaltation": 15, "exaltation_sign": "Scorpio", "debilitation": 15, "debilitation_sign": "Taurus"},
            "Neptune": {"exaltation": 10, "exaltation_sign": "Pisces", "debilitation": 10, "debilitation_sign": "Virgo"}
        }
        
        # Directional strengths (Digbala)
        # Planets are strongest in these houses
        self.digbala_houses = {
            "Sun": 10,      # 10th house
            "Moon": 4,      # 4th house
            "Mercury": 1,   # 1st house
            "Venus": 4,     # 4th house
            "Mars": 10,     # 10th house
            "Jupiter": 1,   # 1st house
            "Saturn": 7,    # 7th house
            # Adding digbala houses for Rahu, Ketu, and modern planets
            "Rahu": 3,      # 3rd house (based on some traditions)
            "Ketu": 9,      # 9th house (based on some traditions)
            "Uranus": 11,   # 11th house (innovation, groups)
            "Neptune": 12,  # 12th house (spirituality, dissolution)
            "Ascendant": 1  # 1st house (self)
        }
        
        # Rashis (signs) and their lords
        self.rashi_lords = {
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
        
        # Moolatrikona signs for planets
        self.moolatrikona_signs = {
            "Sun": "Leo",
            "Moon": "Taurus",
            "Mercury": "Virgo",
            "Venus": "Libra",
            "Mars": "Aries",
            "Jupiter": "Sagittarius",
            "Saturn": "Aquarius",
            # Adding moolatrikona for Rahu, Ketu, and modern planets
            "Rahu": "Gemini",    # Based on some traditions
            "Ketu": "Sagittarius", # Based on some traditions
            "Uranus": "Aquarius",
            "Neptune": "Pisces"
        }
        
        # Define theoretical ranges for each bala
        self.bala_ranges = {
            "Digbala": {"min": 0, "max": 60},
            "Sthanabala": {"min": 30, "max": 210},
            "Shadbala": {"min": 35, "max": 330}
        }

    def calculate_digbala(self, planet_name, house_number):
        """
        Calculate Digbala (directional strength) for a planet.
        
        Parameters:
        -----------
        planet_name : str
            The name of the planet
        house_number : int
            The house number where the planet is located
            
        Returns:
        --------
        float
            The Digbala strength value (0-60)
        """
        if planet_name not in self.digbala_houses:
            return 0
            
        optimal_house = self.digbala_houses[planet_name]
        
        # Calculate the distance from the optimal house
        distance = min(abs(house_number - optimal_house), 12 - abs(house_number - optimal_house))
        
        # Maximum strength (60) when in optimal house, decreasing as distance increases
        strength = max(0, 60 - (distance * 10))
        
        return strength
        
    def calculate_sthanabala(self, planet_name, rashi, house_number, sign_degree):
        """
        Calculate Sthanabala (positional strength) for a planet.
        
        Parameters:
        -----------
        planet_name : str
            The name of the planet
        rashi : str
            The sign where the planet is located
        house_number : int
            The house number where the planet is located
        sign_degree : float
            The degree within the sign
            
        Returns:
        --------
        dict
            Dictionary with different components of Sthanabala
        """
        # Initialize result
        result = {
            "uchcha_bala": 0,  # Exaltation strength
            "saptavargaja_bala": 0,  # Strength from divisional charts
            "ojha_yugma_bala": 0,  # Odd-Even strength
            "kendradi_bala": 0,  # Quadrant strength
            "drekkana_bala": 0,  # Decanate strength
            "total": 0  # Total Sthanabala
        }
        
        # Calculate Uchcha Bala (Exaltation Strength)
        if planet_name in self.exaltation_debilitation:
            exalt_info = self.exaltation_debilitation[planet_name]
            
            if rashi == exalt_info["exaltation_sign"]:
                # Calculate distance from exact exaltation point
                distance = abs(sign_degree - exalt_info["exaltation"])
                # Maximum strength at exact exaltation point, decreasing as distance increases
                result["uchcha_bala"] = max(0, 60 - (distance * 2))
            elif rashi == exalt_info["debilitation_sign"]:
                # Calculate distance from exact debilitation point
                distance = abs(sign_degree - exalt_info["debilitation"])
                # Minimum strength at exact debilitation point, increasing as distance increases
                result["uchcha_bala"] = min(30, distance * 1)
            else:
                # Default moderate strength for other positions
                result["uchcha_bala"] = 30
        
        # Calculate Kendradi Bala (Quadrant Strength)
        # Planets in kendras (1, 4, 7, 10) are strong
        if house_number in [1, 4, 7, 10]:
            result["kendradi_bala"] = 60
        # Planets in panapharas (2, 5, 8, 11) have medium strength
        elif house_number in [2, 5, 8, 11]:
            result["kendradi_bala"] = 30
        # Planets in apoklimas (3, 6, 9, 12) have lowest strength
        else:
            result["kendradi_bala"] = 15
            
        # Calculate Ojha-Yugma Bala (Odd-Even Strength)
        # Odd signs: Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
        # Even signs: Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces
        odd_signs = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]
        even_signs = ["Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"]
        
        # Sun, Mars, Jupiter prefer odd signs
        if planet_name in ["Sun", "Mars", "Jupiter", "Ketu", "Uranus"]:
            if rashi in odd_signs:
                result["ojha_yugma_bala"] = 45
            else:
                result["ojha_yugma_bala"] = 15
        # Moon, Venus, Saturn prefer even signs
        elif planet_name in ["Moon", "Venus", "Saturn", "Rahu", "Neptune"]:
            if rashi in even_signs:
                result["ojha_yugma_bala"] = 45
            else:
                result["ojha_yugma_bala"] = 15
        # Mercury and Ascendant are neutral
        elif planet_name in ["Mercury", "Ascendant"]:
            result["ojha_yugma_bala"] = 30
            
        # Calculate Drekkana Bala (Decanate Strength)
        decanate = int(sign_degree / 10) + 1  # 1, 2, or 3
        
        # First decanate is strongest for Sun, Jupiter, Uranus
        if planet_name in ["Sun", "Jupiter", "Uranus"] and decanate == 1:
            result["drekkana_bala"] = 45
        # Second decanate is strongest for Mars, Mercury, Rahu
        elif planet_name in ["Mars", "Mercury", "Rahu"] and decanate == 2:
            result["drekkana_bala"] = 45
        # Third decanate is strongest for Moon, Venus, Saturn, Neptune, Ketu
        elif planet_name in ["Moon", "Venus", "Saturn", "Neptune", "Ketu"] and decanate == 3:
            result["drekkana_bala"] = 45
        # Ascendant is strong in all decanates
        elif planet_name == "Ascendant":
            result["drekkana_bala"] = 45
        else:
            result["drekkana_bala"] = 15
            
        # Calculate total Sthanabala
        result["total"] = (
            result["uchcha_bala"] + 
            result["saptavargaja_bala"] + 
            result["ojha_yugma_bala"] + 
            result["kendradi_bala"] + 
            result["drekkana_bala"]
        )
        
        return result
        
    def calculate_shadbala(self, planet_data):
        """
        Calculate Shadbala (six-fold strength) for a planet.
        
        Parameters:
        -----------
        planet_data : dict
            Dictionary containing planet data
            
        Returns:
        --------
        dict
            Dictionary with different components of Shadbala
        """
        planet_name = planet_data["Planet"]
        rashi = planet_data["Rashi"]
        house_number = int(planet_data["House"]) if planet_data["House"] != "-" else 0
        sign_degree = planet_data["LonDecDeg"] % 30
        
        # Initialize result
        result = {
            "sthanabala": 0,  # Positional strength
            "digbala": 0,     # Directional strength
            "kalabala": 0,    # Temporal strength
            "chestabala": 0,  # Motional strength
            "naisargikabala": 0,  # Natural strength
            "drigbala": 0,    # Aspectual strength
            "total": 0        # Total Shadbala
        }
        
        # Calculate Sthanabala (Positional Strength)
        sthanabala = self.calculate_sthanabala(planet_name, rashi, house_number, sign_degree)
        result["sthanabala"] = sthanabala["total"]
        
        # Calculate Digbala (Directional Strength)
        result["digbala"] = self.calculate_digbala(planet_name, house_number)
        
        # Calculate Naisargikabala (Natural Strength)
        # Fixed values for each planet
        naisargikabala_values = {
            "Saturn": 5,
            "Mercury": 20,
            "Mars": 30,
            "Venus": 40,
            "Jupiter": 50,
            "Moon": 50,
            "Sun": 60,
            # Adding values for Rahu, Ketu, and modern planets
            "Rahu": 25,
            "Ketu": 25,
            "Uranus": 35,
            "Neptune": 45,
            "Ascendant": 60
        }
        result["naisargikabala"] = naisargikabala_values.get(planet_name, 0)
        
        # Calculate total Shadbala
        result["total"] = (
            result["sthanabala"] + 
            result["digbala"] + 
            result["kalabala"] + 
            result["chestabala"] + 
            result["naisargikabala"] + 
            result["drigbala"]
        )
        
        return result
        
    def add_planetary_strengths(self, planet_positions_df):
        """
        Add planetary strength columns to the planet positions DataFrame.
        
        Parameters:
        -----------
        planet_positions_df : pandas.DataFrame
            DataFrame with planet positions
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame with added planetary strength columns
        """
        # Create a copy of the DataFrame to avoid modifying the original
        df = planet_positions_df.copy()
        
        # Add new columns for planetary strengths with range information in the column name
        df["Digbala (0-60)"] = 0.0
        df["Sthanabala (30-210)"] = 0.0
        df["Shadbala (35-330)"] = 0.0
        
        # Calculate strengths for each planet
        for index, row in df.iterrows():
            planet_name = row["Planet"]
            
            # Get house number
            house_number = int(row["House"]) if row["House"] != "-" else 0
            
            # Calculate Digbala
            digbala = self.calculate_digbala(planet_name, house_number)
            df.at[index, "Digbala (0-60)"] = round(digbala, 2)
            
            # Calculate Sthanabala
            sthanabala = self.calculate_sthanabala(
                planet_name, 
                row["Rashi"], 
                house_number, 
                row["LonDecDeg"] % 30
            )
            df.at[index, "Sthanabala (30-210)"] = round(sthanabala["total"], 2)
            
            # Calculate Shadbala
            shadbala = self.calculate_shadbala(row)
            df.at[index, "Shadbala (35-330)"] = round(shadbala["total"], 2)
            
        return df
        
    def get_bala_ranges(self):
        """
        Get the theoretical ranges for each bala.
        
        Returns:
        --------
        dict
            Dictionary with min and max values for each bala
        """
        return self.bala_ranges 