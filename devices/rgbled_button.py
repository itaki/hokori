import os
import sys
import time
import threading

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

import board
import busio
import logging
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
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
        
        self.button = None
        self.led_red = None
        self.led_green = None
        self.led_blue = None
        self.led_type = None
        self.button_state = False  # False = off, True = on
        self.last_button_read = True  # Assume unpressed state is high
        self.running = False
        self.thread = None

        # Initialize button and LED
        self.initialize_button()
        self.initialize_led(btn_config.get('led', {}))

    def initialize_button(self):
        try:
            address = int(self.connection['address'], 16)
            pin = self.connection['pin']
            self.mcp = MCP23017(self.i2c, address=address)
            self.button = self.mcp.get_pin(pin)
            self.button.direction = Direction.INPUT
            self.button.pull = Pull.UP
            logger.debug(f"Button initialized at address {address}, pin {pin}")
        except KeyError as e:
            logger.error(f"Configuration error: missing key {e} in button configuration for {self.label}")
        except Exception as e:
            logger.error(f"Unexpected error initializing button for {self.label}: {e}")

    def initialize_led(self, led_config):
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
                    self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Initialize LED to off state
                    logger.debug(f"Created RGBLED on {led_config['connection']['pins']}")
                else:
                    logger.warning(f"LED type {led_config['type']} not supported")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in LED configuration for {self.label}")
            except Exception as e:
                logger.error(f"Unexpected error initializing LED for {self.label}: {e}")

    def set_led_color(self, color):
        if self.led_type == "RGB":
            self.led_red.duty_cycle = 0xFFFF - color["red"]
            self.led_green.duty_cycle = 0xFFFF - color["green"]
            self.led_blue.duty_cycle = 0xFFFF - color["blue"]

    def check_button(self):
        while self.running:
            if self.button is not None:
                current_read = self.button.value
                if self.last_button_read and not current_read:  # Detect button press (transition from high to low)
                    logger.debug(f"Button press detected for {self.label}")
                    time.sleep(0.05)  # Small delay to debounce
                    if not self.button.value:  # Confirm the button is still pressed
                        self.button_state = not self.button_state  # Toggle button state
                        logger.debug(f"Button state toggled to: {self.button_state} on tool {self.label}")
                        self.update_led(self.button_state)
                self.last_button_read = current_read
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.check_button)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()

    def get_button_state(self):
        return self.button_state

    def update_led(self, state):
        if self.led_type == "RGB":
            if state:
                self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_on_color"])  # Set LED to on color
            else:
                self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Set LED to off color

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

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
        button.start()  # Start the button thread
        while True:
            time.sleep(1)
            state = button.get_button_state()
            logger.debug(f"Button state is {state}")
    except KeyboardInterrupt:
        button.stop()
        logger.info("Test interrupted by user")
