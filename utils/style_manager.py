import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define default styles
default_styles = {
    "RGBLED_button_styles": {
        "RGBLED_on_color": {
            "name": "bright_purple",
            "red": 65535,
            "green": 0,
            "blue": 65535
        },
        "RGBLED_off_color": {
            "name": "dark_blue",
            "red": 0,
            "green": 0,
            "blue": 28671
        }
    }
}

class Style_Manager:
    _instance = None

    def __new__(cls, styles_path=None):
        if cls._instance is None:
            cls._instance = super(Style_Manager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, styles_path=None):
        if self._initialized:
            return
        self.styles_path = styles_path
        self.styles = self.load_styles()
        self._initialized = True

    def load_styles(self):
        try:
            with open(self.styles_path, 'r') as f:
                styles = json.load(f)
            logger.debug(f"Loaded styles from {self.styles_path}: {styles}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load styles.json, using default styles. Error: {e}")
            styles = default_styles

        # Ensure the necessary keys are present
        if "RGBLED_button_styles" not in styles or \
           "RGBLED_on_color" not in styles["RGBLED_button_styles"] or \
           "RGBLED_off_color" not in styles["RGBLED_button_styles"]:
            logger.warning("Missing required keys in styles, using default styles.")
            styles = default_styles

        return styles

    def get_styles(self):
        return self.styles
