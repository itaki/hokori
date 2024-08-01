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

        # Log detailed configuration
        logger.debug(f"Button config: {btn_config}")
        logger.debug(f"Button connection: {self.connection}")

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
            logger.debug(f"Initial button value for {self.label}: {self.button.value}")
        except KeyError as e:
            logger.error(f"Configuration error: missing key {e} in button configuration for {self.label}")
        except Exception as e:
            logger.error(f"Unexpected error initializing button for {self.label}: {e}")

    def initialize_led(self, led_config):
        if led_config:
            try:
                logger.info(f"Creating {self.label} LED at address {led_config['connection']['address']} on pins {led_config['connection']['pins']}")
                address = int(led_config['connection']['address'], 16)
                self.pca = PCA9685(self.i2c, address=address)
                self.pca.frequency = 1000

                if led_config['type'] == "RGBLED":
                    self.led_red = self.pca.channels[led_config['connection']['pins'][0]]
                    self.led_green = self.pca.channels[led_config['connection']['pins'][1]]
                    self.led_blue = self.pca.channels[led_config['connection']['pins'][2]]
                    self.led_type = "RGB"
                    self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Initialize LED to off state
                    logger.info(f"Created RGBLED on {led_config['connection']['pins']}")
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
        if self.button is not None:
            current_read = self.button.value
            if self.last_button_read and not current_read:
                self.button_state = not self.button_state
                state_str = "off" if not self.button_state else "on"
                logger.info(f"Button is now {state_str} on tool {self.label}")
                self.update_led(state_str)
            self.last_button_read = current_read

    def update_led(self, status):
        if self.led_type == "RGB":
            if status == 'on':
                self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_on_color"])  # Set LED to on color
            elif status == 'off':
                self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Set LED to off color
