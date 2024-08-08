import os
import sys
import logging
import board
import busio
from adafruit_pca9685 import PCA9685

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

from utils.style_manager import Style_Manager

logger = logging.getLogger(__name__)

class RGBLED_Button:
    def __init__(self, btn_config, i2c, styles_path):
        self.id = btn_config.get('id', 'unknown')
        self.label = btn_config.get('label', 'unknown')
        self.physical_location = btn_config.get('physical_location', 'unknown')
        self.connection = btn_config.get('connection', {})
        
        self.i2c = i2c
        self.styles = Style_Manager(styles_path).get_styles()
        
        self.led_red = None
        self.led_green = None
        self.led_blue = None
        self.led_type = None

        # Initialize LED
        self._initialize_led(btn_config.get('led', {}))

    def _initialize_led(self, led_config):
        if led_config:
            try:
                logger.debug(f"Creating {self.label} LED at address {led_config['connection']['address']} on pins {led_config['connection']['pins']}")
                address = int(led_config['connection']['address'], 16)
                self.pca = PCA9685(self.i2c, address=address)
                self.pca.frequency = 1000

                if led_config['type'] == "RGBLED":
                    self.led_red = self.pca.channels[led_config['connection']['pins'][0]]
                    self.led_green = self.pca.channels[led_config['connection']['pins'][1]]
                    self.led_blue = self.pca.channels[led_config['connection']['pins'][2]]
                    self.led_type = "RGB"
                    self._set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Initialize LED to off state
                    logger.debug(f"Created RGBLED on {led_config['connection']['pins']}")
                else:
                    logger.warning(f"LED type {led_config['type']} not supported")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in LED configuration for {self.label}")
            except Exception as e:
                logger.error(f"Unexpected error initializing LED for {self.label}: {e}")

    def _set_led_color(self, color):
        if self.led_type == "RGB":
            self.led_red.duty_cycle = 0xFFFF - color["red"]
            self.led_green.duty_cycle = 0xFFFF - color["green"]
            self.led_blue.duty_cycle = 0xFFFF - color["blue"]
            logger.debug(f"Set {self.label} LED color to {color}")

    def update_led(self, state):
        if self.led_type == "RGB":
            if state:
                self._set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_on_color"])  # Set LED to on color
            else:
                self._set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Set LED to off color

if __name__ == "__main__":
    import time
    import board
    import busio
    from button_manager import Button_Manager

    logging.basicConfig(level=logging.DEBUG)

    i2c = busio.I2C(board.SCL, board.SDA)

    button_configs = [
        {
            "type": "RGBLED_Button",
            "label": "Hose Button",
            "id": "hose_button",
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
        },
        {
            "type": "RGBLED_Button",
            "label": "LEFT Miter Saw Button",
            "id": "left_miter_saw_button",
            "physical_location": "Above the miter saw to the left",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 1
            },
            "led": {
                "label": "LEFT Miter Saw Button LED",
                "id": "left_miter_saw_button_LED",
                "type": "RGBLED",
                "physical_location": "Above the miter saw",
                "connection": {
                    "hub": "main-hub",
                    "address": "0x40",
                    "pins": [3, 4, 5]
                }
            }
        },
        {
            "type": "RGBLED_Button",
            "label": "RIGHT Miter Saw Button",
            "id": "right_miter_saw_button",
            "physical_location": "Above the miter saw",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 2
            },
            "led": {
                "label": "RIGHT Miter Saw Button LED",
                "id": "right_miter_saw_button_LED",
                "type": "RGBLED",
                "physical_location": "Above the miter saw",
                "connection": {
                    "hub": "main-hub",
                    "address": "0x40",
                    "pins": [6, 7, 8]
                }
            }
        }
    ]

    # Initialize Button_Manager
    button_manager = Button_Manager(i2c, button_configs)

    # Initialize RGBLED_Buttons
    rgbled_buttons = {}
    for config in button_configs:
        rgbled_buttons[config['label']] = RGBLED_Button(config, i2c, os.path.join(os.path.dirname(__file__), 'styles.json'))

    # Start button polling in the background
    button_manager.start()

    try:
        while True:
            # Check button states and update LEDs accordingly
            for label, button in rgbled_buttons.items():
                state = any(btn_label == label and not btn.value for btn_label, btn in button_manager.buttons)
                button.update_led(state)
            time.sleep(0.1)
    except KeyboardInterrupt:
        button_manager.stop()
        logger.info("Program interrupted by user")
