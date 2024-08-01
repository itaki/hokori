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

from devices.rgbled_button import RGBLED_Button
from devices.voltage_sensor import VoltageSensor
from utils.style_manager import Style_Manager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c, styles_path):
        self.id = tool_config.get('id', 'unknown')
        self.label = tool_config.get('label', 'unknown')
        self.preferences = tool_config.get('preferences', {})
        self.status = 'off'
        self.last_status = 'off'  # Keep track of the last status
        self.override = False
        self.gate_prefs = self.preferences.get('gate_prefs', [])
        self.spin_down_time = self.preferences.get('spin_down_time', 0)
        self.last_used = 0
        self.flagged = True

        self.i2c = i2c
        self.styles_path = styles_path
        self.button = None
        self.voltage_sensor = None
        self.button_state = False  # Initialize button state

        # Initialize components
        try:
            self.initialize_button(tool_config.get('button', {}))
            self.initialize_voltage_sensor(tool_config.get('volt', {}))
        except Exception as e:
            logger.error(f"Unexpected error initializing tool {self.label}: {e}")

    def initialize_button(self, btn_config):
        if btn_config:
            try:
                # Log the button configuration being passed
                logger.debug(f"Button configuration for tool {self.label}: {btn_config}")
                logger.debug(f"Button configuration type for tool {self.label}: {type(btn_config)}")
                self.button = RGBLED_Button(btn_config, self.i2c, self.styles_path)
                logger.info(f"Button initialized for tool {self.label}")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in button configuration for {self.label}")
            except TypeError as e:
                logger.error(f"Type error: {e} in button configuration for {self.label}")
            except Exception as e:
                logger.error(f"Unexpected error initializing button for tool {self.label}: {e}")

    def initialize_voltage_sensor(self, volt_config):
        if volt_config:
            try:
                self.voltage_sensor = VoltageSensor(volt_config, self.i2c)
                logger.info(f"Voltage sensor initialized for tool {self.label}")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in voltage sensor configuration for {self.label}")
            except Exception as e:
                logger.error(f"Unexpected error initializing voltage sensor for {self.label}: {e}")

    def check_button(self):
        if self.button:
            self.button.check_button()

    def check_voltage(self):
        if self.voltage_sensor:
            is_on = self.voltage_sensor.am_i_on()
            status = "ON" if is_on else "OFF"
            if status != self.last_status:
                logger.info(f"{self.label} is {status}")
                self.last_status = status

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
                tool.check_voltage()
            time.sleep(0.1)
    except KeyboardInterrupt:
        for tool in tools:
            if tool.voltage_sensor:
                tool.voltage_sensor.stop()
