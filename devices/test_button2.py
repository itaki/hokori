import time
import board
import busio
import logging
import os
import json
import sys

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

from devices.rgbled_button import RGBLED_Button  # Import for button

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c, styles_path):
        self.id = tool_config.get('id', 'unknown')
        self.label = tool_config.get('label', 'unknown')
        self.preferences = tool_config.get('preferences', {})
        self.status = tool_config.get('status', 'off')  # Initialize status
        self.override = False
        self.gate_prefs = set(self.preferences.get('gate_prefs', []))
        self.spin_down_time = self.preferences.get('spin_down_time', 0)
        self.last_used = 0
        self.flagged = True

        self.i2c = i2c
        self.styles_path = styles_path
        self.button = None
        self.button_state = False  # Initialize button state

        # Initialize button
        try:
            self.initialize_button(tool_config.get('button', {}))
        except Exception as e:
            logger.error(f"Unexpected error initializing tool {self.label}: {e}")

        logger.debug(f"Tool {self.label} initialized with ID {self.id}")

    def initialize_button(self, btn_config):
        if btn_config:
            try:
                self.button = RGBLED_Button(btn_config, self.i2c, self.styles_path)
                logger.debug(f"Tool button initialized for tool {self.label}")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in tool button configuration for {self.label}")
            except TypeError as e:
                logger.error(f"Type error: {e} in tool button configuration for {self.label}")
            except Exception as e:
                logger.error(f"Unexpected error initializing tool button for {self.label}: {e}")

    def check_button(self):
        if self.button:
            self.button.check_button()
            if self.button.button_state != self.button_state:
                self.button_state = self.button.button_state
                state_str = "off" if not self.button_state else "on"
                logger.debug(f"Button is now {state_str} on tool {self.label}")
                self.set_status(state_str)
                self.button.update_led(state_str)

    def set_status(self, status):
        if self.status != status:
            self.status = status
            logger.debug(f"Tool {self.label} status changed to {self.status}")

# Example usage
if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)

    # Load the configuration from the config.json file
    config_file = os.path.join(parent_dir, 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)

    styles_file = os.path.join(parent_dir, 'styles.json')

    tools = [Tool(tool, i2c, styles_file) for tool in config['devices'] if tool['type'] == 'tool']
    try:
        while True:
            for tool in tools:
                tool.check_button()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
