"""
Configuration management for KP Astrology Dashboard.
Handles application settings, default values, and persistence.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    # Location settings
    "location": {
        "latitude": 19.0760,  # Mumbai
        "longitude": 72.8777,
        "timezone": "Asia/Kolkata"
    },

    # Calculation settings
    "calculation": {
        "ayanamsa": "Krishnamurti",  # Default ayanamsa system
        "house_system": "Placidus",  # Default house system
        "interval_minutes": 10,  # Default calculation interval
        "aspects": [0, 90, 180],  # Default aspects to calculate
        "aspect_planets": ["Sun", "Moon", "Mercury", "Venus", "Mars",
                           "Jupiter", "Saturn", "Rahu", "Ketu"]
    },

    # Yoga settings
    "yoga": {
        "days_past": 7,
        "days_future": 30,
        "types": ["positive", "negative", "neutral"],
        "interval_minutes": 30,
    },

    # Display settings
    "display": {
        "show_aspects": True,
        "show_dignities": True,
        "north_indian_style": False,
        "use_24hr": False,
        "show_seconds": True,
    },

    # Path settings
    "paths": {
        "kp_data": "",  # KP_SL_Divisions.csv path
        "ephemeris": "",  # Swiss Ephemeris path
    },

    # Advanced settings
    "advanced": {
        "cache_size_mb": 100,
        "parallel_calculations": True,
        "max_threads": 4,
    },

    # Application settings
    "app": {
        "first_run": True,
        "last_run": None,
        "window_size": [1024, 768],
        "window_position": [100, 100],
    }
}


class ConfigManager:
    """Configuration management singleton for the application."""

    _instance = None

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = DEFAULT_CONFIG.copy()
            cls._instance._config_path = cls._get_config_path()
            cls._instance._load_config()
        return cls._instance

    @staticmethod
    def _get_config_path() -> str:
        """Get the path to the configuration file."""
        # Look in standard locations
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Check for config in app directory
        app_config = os.path.join(app_dir, "kp_astrology_config.json")
        if os.path.exists(app_config):
            return app_config

        # Check for config in user home directory
        home_config = os.path.expanduser("~/.kp_astrology_config.json")
        if os.path.exists(home_config):
            return home_config

        # Default to app directory
        return app_config

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as f:
                    loaded_config = json.load(f)

                # Update the config with loaded values, preserving defaults for missing values
                self._update_nested_dict(self._config, loaded_config)
                logging.info(f"Configuration loaded from {self._config_path}")
            else:
                logging.info("No configuration file found, using defaults")
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")

    def _update_nested_dict(self, d: Dict, u: Dict) -> None:
        """
        Update a nested dictionary with values from another dictionary.
        This preserves nested structure while updating values.
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Update last run timestamp
            self._config["app"]["last_run"] = datetime.now().isoformat()

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)

            # Save configuration
            with open(self._config_path, 'w') as f:
                json.dump(self._config, f, indent=4)

            logging.info(f"Configuration saved to {self._config_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self._config

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value.

        Args:
            section: Configuration section name
            key: Configuration key within section
            default: Default value if not found

        Returns:
            The configuration value or default
        """
        if section in self._config and key in self._config[section]:
            return self._config[section][key]
        return default

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a specific configuration value.

        Args:
            section: Configuration section name
            key: Configuration key within section
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = DEFAULT_CONFIG.copy()
        self.save_config()
        logging.info("Configuration reset to defaults")


# Global app configuration instance
app_config = ConfigManager()


def load_config() -> Dict[str, Any]:
    """Load and return the application configuration."""
    return app_config.get_config()


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """Get a specific application setting."""
    return app_config.get(section, key, default)


def update_setting(section: str, key: str, value: Any) -> None:
    """Update a specific application setting."""
    app_config.set(section, key, value)
    app_config.save_config()


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save settings dictionary to configuration.

    Args:
        settings: Dictionary with settings to save

    Returns:
        bool: True if save was successful
    """
    # Update config with new settings
    for section, section_data in settings.items():
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                app_config.set(section, key, value)
        else:
            # Support flat structure too
            app_config.set("app", section, section_data)

    # Save updated config
    return app_config.save_config()
