import os
import sys
import time
import logging

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

import board
import busio
from devices.rgbled_button import RGBLED_Button  # Import the RGBLED_Button class

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_rgbled_button():
    # Example button configuration for testing
    button_config = {
        "type": "RGBLED_Button",
        "label": "Test Button",
        "id": "test_button",
        "physical_location": "Test Location",
        "status": "off",
        "connection": {
            "hub": "main-hub",
            "address": "0x20",
            "pin": 0
        },
        "led": {
            "label": "Test Button LED",
            "id": "test_button_led",
            "type": "RGBLED",
            "physical_location": "Test Location",
            "connection": {
                "hub": "main-hub",
                "address": "0x40",
                "pins": [0, 1, 2]
            }
        }
    }

    i2c = busio.I2C(board.SCL, board.SDA)

    # Create an instance of RGBLED_Button
    button = RGBLED_Button(button_config, i2c, 'path/to/styles.json')

    try:
        while True:
            button.check_button()
            time.sleep(0.1)  # Small delay to avoid busy-waiting
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")

if __name__ == "__main__":
    test_rgbled_button()
