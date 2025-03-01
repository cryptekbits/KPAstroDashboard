from .positive_yogas import PositiveYogas
from .negative_yogas import NegativeYogas
from .neutral_yogas import NeutralYogas


class YogaManager:
    def __init__(self):
        self.positive_yogas = PositiveYogas()
        self.negative_yogas = NegativeYogas()
        self.neutral_yogas = NeutralYogas()

    def calculate_all_yogas(self, chart, planets_data):
        """Calculate all yogas present in the chart"""
        yogas = []

        # Get positive yogas
        yogas.extend(self.positive_yogas.get_all_positive_yogas(chart, planets_data))

        # Get negative yogas
        yogas.extend(self.negative_yogas.get_all_negative_yogas(chart, planets_data))

        # Get neutral yogas
        yogas.extend(self.neutral_yogas.get_all_neutral_yogas(chart, planets_data))

        return yogas
