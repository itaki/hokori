import time
import board
import busio
import logging
import os
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from utils.style_manager import Style_Manager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c):
        self.id = tool_config['id']
        self.label = tool_config['label']
        self.preferences = tool_config.get('preferences', {})
        self.status = 'off'
        self.override = False
        self.gate_prefs = self.preferences.get('gate_prefs', [])
        self.spin_down_time = self.preferences.get('spin_down_time', 0)
        self.last_used = 0
        self.flagged = True
        self.led_type = None
        self.button_state = False  # False = off, True = on
        self.last_button_read = True  # Assume unpressed state is high

        self.i2c = i2c
        self.styles = Style_Manager().get_styles()
        self.button = None
        self.led = None

        # Initialize components
        try:
            self.initialize_button(tool_config.get('button', {}))
            self.initialize_led(tool_config.get('led', {}))
        except KeyError as e:
            logger.error(f"Configuration error: missing key {e} in tool configuration for {self.label}")
        except ValueError as e:
            logger.error(f"I2C device error for tool {self.label}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing tool {self.label}: {e}")

    def initialize_button(self, btn_config):
        if btn_config:
            logger.info(f"Creating {self.label} button at address {btn_config['connection']['address']} on pin {btn_config['connection']['pin']}")
            address = int(btn_config['connection']['address'], 16)
            pin = btn_config['connection']['pin']
            self.mcp = MCP23017(self.i2c, address=address)
            self.button = self.mcp.get_pin(pin)
            self.button.direction = Direction.INPUT
            self.button.pull = Pull.UP
            logger.debug(f"Initial button value for {self.label}: {self.button.value}")

    def initialize_led(self, led_config):
        if led_config:
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
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                if status == 'on':
                    self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_on_color"])  # Set LED to on color
                elif status == 'off':
                    self.set_led_color(self.styles["RGBLED_button_styles"]["RGBLED_off_color"])  # Set LED to off color


# Example usage
if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    config = {
        "devices": [
            {
                "type": "tool",
                "label": "Hose",
                "id": "hose",
                "preferences": {
                    "use_collector": True,
                    "gate_prefs": ["HOSE"],
                    "last_used": 0,
                    "spin_down_time": 0
                },
                "button": {
                    "label": "Hose Button",
                    "id": "hose_button",
                    "type": "RGBLED_Button",
                    "physical_location": "By the Hose",
                    "connection": {
                        "hub": "main-hub",
                        "address": "0x20",
                        "pin": 0
                    }
                },
                "led": {
                    "label": "Hose LED",
                    "id": "hose_button_LED",
                    "type": "RGBLED",
                    "physical_location": "On the Hose Button",
                    "connection": {
                        "hub": "main-hub",
                        "address": "0x42",
                        "pins": [13, 14, 15]
                    }
                },
                "volt": {}
            }
        ]
    }
    tools = [Tool(tool, i2c) for tool in config['devices'] if tool['type'] == 'tool']
    while True:
        for tool in tools:
            tool.check_button()
        time.sleep(0.1)
