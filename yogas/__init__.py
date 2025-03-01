from .positive_yogas import PositiveYogas
from .negative_yogas import NegativeYogas
from .neutral_yogas import NeutralYogas


class YogaManager:
    """
    YogaManager integrates all yoga calculations and provides metadata about each yoga.
    It supports single-point calculations as well as calculations over a date range.
    """

    def __init__(self):
        self.positive_yogas = PositiveYogas()
        self.negative_yogas = NegativeYogas()
        self.neutral_yogas = NeutralYogas()

        # Define yoga nature and descriptions
        self.yoga_metadata = {
            # Positive Yogas - Excellent
            "Budha-Aditya Yoga": {
                "nature": "Excellent",
                "description": "Sun and Mercury conjunction. Enhances intelligence, communication skills, and decision-making."
            },
            "Raja Yoga": {
                "nature": "Excellent",
                "description": "Combination of trine and angle lords. Brings power, authority, status, and success."
            },
            "Hamsa Yoga": {
                "nature": "Excellent",
                "description": "Jupiter in angle in own sign or exalted. Brings spiritual growth, wisdom, and prosperity."
            },
            "Malavya Yoga": {
                "nature": "Excellent",
                "description": "Venus in angle in own sign or exalted. Brings wealth, luxury, and artistic talents."
            },
            "Bhadra Yoga": {
                "nature": "Excellent",
                "description": "Mercury in angle in own sign or exalted. Enhances intelligence, analytical skills, and communication."
            },
            "Ruchaka Yoga": {
                "nature": "Excellent",
                "description": "Mars in angle in own sign or exalted. Brings leadership, courage, and energy."
            },
            "Sasa Yoga": {
                "nature": "Excellent",
                "description": "Saturn in angle in own sign or exalted. Brings discipline, longevity, and material success."
            },
            "Neech Bhanga Raja Yoga": {
                "nature": "Excellent",
                "description": "Debilitated planet with its lord well placed. Cancels negative effects and brings unexpected success."
            },

            # Positive Yogas - Good
            "Gaja-Kesari Yoga": {
                "nature": "Good",
                "description": "Moon and Jupiter in quadrant. Brings wisdom, prosperity, and spiritual growth."
            },
            "Gajakesari Yoga": {
                "nature": "Good",
                "description": "Moon and Jupiter in quadrant. Brings wisdom, prosperity, and spiritual growth."
            },
            "Dhana Yoga": {
                "nature": "Good",
                "description": "Lords of 2nd and 11th houses connected. Brings wealth and financial prosperity."
            },
            "Lakshmi Yoga": {
                "nature": "Good",
                "description": "Lords of 5th and 9th houses connected. Brings wealth, luck, and divine blessings."
            },
            "Guru-Mangala Yoga": {
                "nature": "Good",
                "description": "Jupiter in 2nd, 5th, or 11th house. Brings financial growth and prosperity."
            },
            "Guru-Shukra Yoga": {
                "nature": "Good",
                "description": "Jupiter and Venus conjunction. Brings wealth, happiness, and artistic abilities."
            },
            "Amala Yoga": {
                "nature": "Good",
                "description": "Sun in 10th house with Jupiter or Venus aspect. Brings reputation, fame, and success."
            },

            # Negative Yogas - Bad
            "Guru Chandala Yoga": {
                "nature": "Bad",
                "description": "Jupiter and Rahu conjunction. Creates confusion in wisdom, obstacles in education, and false beliefs."
            },
            "Angarak Yoga": {
                "nature": "Bad",
                "description": "Mars in 1st, 4th, 7th, 8th, or 12th house. Creates anger, accidents, and conflicts."
            },
            "Graha Yuddha": {
                "nature": "Bad",
                "description": "Planetary war - two planets in close conjunction. Creates conflicts in the significations of both planets."
            },
            "Kemadruma Yoga": {
                "nature": "Bad",
                "description": "Moon with no planets in 2nd, 12th, or its own sign. Creates instability, emotional imbalance, and poverty."
            },

            # Negative Yogas - Worst
            "Vish Yoga": {
                "nature": "Worst",
                "description": "Malefic in 6, 8, 12 houses from Moon. Creates poison-like consequences in life areas affected."
            },
            "Kala Sarpa Yoga": {
                "nature": "Worst",
                "description": "All planets between Rahu and Ketu. Creates obstacles, delays, and struggles in life."
            },

            # Neutral Yogas
            "Graha Malika Yoga": {
                "nature": "Neutral",
                "description": "Chain of planets in consecutive houses. Creates mixed results depending on the planets involved."
            },
        }

    def get_yoga_metadata(self, yoga_name):
        """
        Get the nature and description of a yoga by its name.

        Parameters:
        -----------
        yoga_name : str
            The name of the yoga

        Returns:
        --------
        dict
            Dictionary with "nature" and "description" keys
        """
        # Extract base yoga name without any qualifying text
        base_name = yoga_name
        if "(" in yoga_name:
            base_name = yoga_name.split("(")[0].strip()

        metadata = self.yoga_metadata.get(base_name, {
            "nature": "Neutral",
            "description": "No specific description available for this yoga."
        })

        return metadata

    def calculate_all_yogas(self, chart, planets_data):
        """
        Calculate all yogas present in the chart and add metadata.

        Parameters:
        -----------
        chart : VedicHoroscopeData
            The chart data object
        planets_data : list or DataFrame
            Planetary position data

        Returns:
        --------
        list
            List of yoga dictionaries containing yoga information, nature, and description
        """
        yogas = []

        # Get positive yogas
        positive_yogas = self.positive_yogas.get_all_positive_yogas(chart, planets_data)
        for yoga in positive_yogas:
            metadata = self.get_yoga_metadata(yoga["name"])
            yoga["nature"] = metadata["nature"]
            yoga["description"] = metadata["description"]
            yogas.append(yoga)

        # Get negative yogas
        negative_yogas = self.negative_yogas.get_all_negative_yogas(chart, planets_data)
        for yoga in negative_yogas:
            metadata = self.get_yoga_metadata(yoga["name"])
            yoga["nature"] = metadata["nature"]
            yoga["description"] = metadata["description"]
            yogas.append(yoga)

        # Get neutral yogas
        neutral_yogas = self.neutral_yogas.get_all_neutral_yogas(chart, planets_data)
        for yoga in neutral_yogas:
            metadata = self.get_yoga_metadata(yoga["name"])
            yoga["nature"] = metadata["nature"]
            yoga["description"] = metadata["description"]
            yogas.append(yoga)

        return yogas