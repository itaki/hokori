import json
import os
import sys
import logging
import threading
import time

# Adjust the import path to include the parent directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from devices.rgbled_button import RGBLED_Button
from devices.voltage_sensor import Voltage_Sensor

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c, styles_path):
        self.id = tool_config.get('id', 'unknown')
        self.label = tool_config.get('label', 'unknown')
        self.status = tool_config.get('status', 'off')
        self.preferences = tool_config.get('preferences', {})
        self.button_config = tool_config.get('button', {})
        self.volt_config = tool_config.get('volt', {})

        self.i2c = i2c
        self.styles_path = styles_path
        self.button = None
        self.voltage_sensor = None

        logger.debug(f"Initializing tool {self.label}")

        if self.button_config:
            logger.debug(f"Initializing button for {self.label}")
            self.button = RGBLED_Button(self.button_config, self.i2c, self.styles_path)
            self.button.start()

        if self.volt_config:
            logger.debug(f"Initializing voltage sensor for {self.label}")
            self.voltage_sensor = Voltage_Sensor(self.volt_config, self.i2c)

        self.monitoring_thread = threading.Thread(target=self.update_tool_status)
        self.monitoring_thread.start()

        logger.debug(f"Tool {self.label} initialized with status {self.status}")

    def update_tool_status(self):
        while True:
            button_state = self.button.get_button_state() if self.button else False
            voltage_state = self.voltage_sensor.am_i_on() if self.voltage_sensor else False
            
            if button_state or voltage_state:
                self.set_status('on')
            else:
                self.set_status('off')

            time.sleep(1)  # Adjust the sleep duration as needed

    def set_status(self, status):
        self.status = status
        logger.info(f"Tool {self.label} status set to {self.status}")

    def stop(self):
        if self.button:
            self.button.stop()
        if self.voltage_sensor:
            self.voltage_sensor.stop()
        self.monitoring_thread.join()

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    import board
    import busio

    logging.basicConfig(level=logging.DEBUG)

    # Load the configuration
    config_path = os.path.join(base_dir, 'config.json')
    config = load_config(config_path)

    i2c = busio.I2C(board.SCL, board.SDA)

    tools = []
    for tool_config in config['tools']:
        logger.debug(f"Initializing tool {tool_config['label']}")
        tool = Tool(tool_config, i2c, os.path.join(base_dir, 'styles.json'))
        tools.append(tool)
        time.sleep(1)  # Add a delay to ensure proper initialization

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for tool in tools:
            tool.stop()
        logger.info("Test interrupted by user")
