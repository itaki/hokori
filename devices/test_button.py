import logging
import board
import busio
import os
import json
import sys

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

from devices.rgbled_button import RGBLED_Button

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Example configuration for testing
button_config = {
    "label": "Hose Button",
    "id": "hose_button",
    "type": "RGBLED_Button",
    "physical_location": "By the Hose",
    "connection": {
        "hub": "main-hub",
        "address": "0x20",
        "pin": 0
    },
    "led": {
        "label": "Hose LED",
        "id": "hose_button_LED",
        "type": "RGBLED",
        "physical_location": "On the Hose Button",
        "connection": {
            "hub": "main-hub",
            "address": "0x40",
            "pins": [0, 1, 2]
        }
    }
}

if __name__ == "__main__":
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    try:
        logger.debug(f"Button configuration: {button_config}")
        logger.debug(f"Button configuration type: {type(button_config)}")
        print(button_config)
        button = RGBLED_Button(button_config, i2c, {})
        logger.info("Button initialized successfully")
    except KeyError as e:
        logger.error(f"Configuration error: missing key {e} in button configuration")
    except TypeError as e:
        logger.error(f"Type error: {e} in button configuration")
    except Exception as e:
        logger.error(f"Unexpected error initializing button: {e}")
