"""
Base class for all Yogas in KP Astrology.
Provides the foundation for defining, detecting and categorizing yogas.
"""
from enum import Enum
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable


class YogaType(Enum):
    """Enumeration of yoga types for categorization and display."""
    POSITIVE = "positive"  # Beneficial yogas (green)
    NEGATIVE = "negative"  # Challenging yogas (red)
    NEUTRAL = "neutral"  # Neutral yogas (yellow)


class Yoga:
    """Base class for all yogas in the system."""

    def __init__(self,
                 name: str,
                 description: str,
                 yoga_type: YogaType,
                 required_planets: List[str] = None):
        """
        Initialize a yoga definition.

        Args:
            name: The name of the yoga
            description: A brief description of the yoga and its effects
            yoga_type: The type/category of the yoga (positive, negative, neutral)
            required_planets: List of planets required for this yoga
        """
        self.name = name
        self.description = description
        self.yoga_type = yoga_type
        self.required_planets = required_planets or []

    def check_yoga(self, chart_data: Dict, planets_data: List) -> bool:
        """
        Check if this yoga is present in the given chart.
        Must be implemented by subclasses.

        Args:
            chart_data: The chart data
            planets_data: List of planet data

        Returns:
            True if the yoga is present, False otherwise
        """
        raise NotImplementedError("Subclasses must implement check_yoga method")

    def get_participating_planets(self, chart_data: Dict, planets_data: List) -> List[Dict]:
        """
        Get the list of planets participating in this yoga.

        Args:
            chart_data: The chart data
            planets_data: List of planet data

        Returns:
            List of dictionaries with planet information
        """
        # This is a default implementation, subclasses may override
        participating_planets = []

        for planet in planets_data:
            if planet.Object in self.required_planets:
                participating_planets.append({
                    "name": planet.Object,
                    "house": planet.HouseNr,
                    "sign": planet.Rasi
                })

        return participating_planets

    def get_yoga_strength(self, chart_data: Dict, planets_data: List) -> float:
        """
        Get the strength of this yoga (0.0 to 1.0).

        Args:
            chart_data: The chart data
            planets_data: List of planet data

        Returns:
            Strength value between 0.0 and 1.0
        """
        # Default implementation - subclasses may implement more sophisticated logic
        return 1.0 if self.check_yoga(chart_data, planets_data) else 0.0

    def to_dict(self) -> Dict:
        """Convert yoga to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.yoga_type.value,
            "required_planets": self.required_planets
        }

    def __str__(self) -> str:
        """String representation of the yoga."""
        return f"{self.name} ({self.yoga_type.value.capitalize()} Yoga)"


class YogaResult:
    """Class to store the result of a yoga detection."""

    def __init__(self,
                 yoga: Yoga,
                 is_active: bool,
                 start_time: datetime,
                 participating_planets: List[Dict] = None,
                 strength: float = 1.0):
        """
        Initialize a yoga result.

        Args:
            yoga: The yoga that was detected
            is_active: Whether the yoga is active
            start_time: When the yoga became active
            participating_planets: List of planets participating in this yoga
            strength: Strength of the yoga (0.0 to 1.0)
        """
        self.yoga = yoga
        self.is_active = is_active
        self.start_time = start_time
        self.end_time = None  # Will be set when the yoga ends
        self.participating_planets = participating_planets or []
        self.strength = strength

    def end(self, end_time: datetime) -> None:
        """
        Set the end time for this yoga result.

        Args:
            end_time: When the yoga ended
        """
        self.end_time = end_time

    def get_duration(self) -> Optional[float]:
        """
        Get the duration of this yoga in hours.

        Returns:
            Duration in hours or None if ongoing
        """
        if not self.end_time:
            return None

        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600  # Convert to hours

    def get_planet_details(self) -> str:
        """
        Get formatted details of participating planets.

        Returns:
            String with planet details in format: "Planet1 (House1, Sign1), Planet2 (House2, Sign2)"
        """
        if not self.participating_planets:
            return ""

        planet_details = []
        for planet in self.participating_planets:
            house = planet.get("house", "")
            sign = planet.get("sign", "")
            planet_details.append(f"{planet['name']} (H{house}, {sign})")

        return ", ".join(planet_details)

    def to_dict(self) -> Dict:
        """Convert yoga result to dictionary representation."""
        return {
            "yoga_name": self.yoga.name,
            "yoga_type": self.yoga.yoga_type.value,
            "description": self.yoga.description,
            "is_active": self.is_active,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M") if self.end_time else "Ongoing",
            "participating_planets": self.get_planet_details(),
            "strength": self.strength
        }


class YogaRegistry:
    """Registry for all yoga classes in the system."""

    _yogas = {}  # Class variable to store registered yogas

    @classmethod
    def register(cls, yoga_class):
        """
        Register a yoga class.

        Args:
            yoga_class: The yoga class to register
        """
        cls._yogas[yoga_class.__name__] = yoga_class
        return yoga_class  # Return the class to allow usage as a decorator

    @classmethod
    def get_all_yogas(cls) -> List[Yoga]:
        """
        Get instances of all registered yogas.

        Returns:
            List of yoga instances
        """
        return [yoga_cls() for yoga_cls in cls._yogas.values()]

    @classmethod
    def get_yoga_by_name(cls, name: str) -> Optional[Yoga]:
        """
        Get a yoga instance by name.

        Args:
            name: Name of the yoga

        Returns:
            Yoga instance or None if not found
        """
        for yoga_cls in cls._yogas.values():
            yoga = yoga_cls()
            if yoga.name == name:
                return yoga
        return None

    @classmethod
    def get_yogas_by_type(cls, yoga_type: YogaType) -> List[Yoga]:
        """
        Get all yogas of a specific type.

        Args:
            yoga_type: Type of yogas to get

        Returns:
            List of yoga instances
        """
        return [yoga_cls() for yoga_cls in cls._yogas.values()
                if yoga_cls().yoga_type == yoga_type]