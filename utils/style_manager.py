import json
import os
import logging

logger = logging.getLogger(__name__)

class Style_Manager:
    def __init__(self, styles_path=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.styles_path = styles_path or os.path.join(self.base_dir, 'styles.json')
        self.styles = self.load_styles()

    def load_styles(self):
        if not os.path.exists(self.styles_path):
            logger.error(f"💢 Styles file not found: {self.styles_path}")
            return self.default_styles()

        try:
            with open(self.styles_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"💢 JSON decode error in styles file: {e}")
        except Exception as e:
            logger.error(f"💢 Failed to load styles: {e}")

        return self.default_styles()

    def get_styles(self):
        return self.styles

    def default_styles(self):
        return {
            "RGBLED_button_styles": {
                "RGBLED_off_color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0x6FFF
                },
                "RGBLED_on_color": {
                    "red": 0xFFFF,
                    "green": 0,
                    "blue": 0xFFFF
                }
            }
        }
