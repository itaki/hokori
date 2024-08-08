import os
import json
import board
import busio
import logging
from devices.hub import Hub
from devices.tool import Tool

DEVICE_FILE = 'config.json'
logger = logging.getLogger(__name__)

class Device_Manager:
    def __init__(self, device_file=DEVICE_FILE, styles_path=None):
        self.device_file = device_file
        self.styles_path = styles_path
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.devices = self.get_devices(device_file)
        self.hubs = self.create_hubs(self.devices.get('hubs', []))
        self.tools = self.create_tools(self.devices.get('tools', []))
        logger.debug("Device_Manager initialized.")

    def get_devices(self, file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                config = json.load(f)
            logger.debug(f"Loaded devices from {file}")
            return config
        else:
            raise FileNotFoundError(f"Device configuration file '{file}' not found.")

    def create_hubs(self, hubs_config):
        hubs = {}
        for device in hubs_config:
            hub_id = device['id']
            try:
                hubs[hub_id] = Hub(device, self.i2c)
                logger.debug(f"Initialized hub {hub_id}")
            except Exception as e:
                logger.error(f"Error initializing hub {hub_id}: {e}")
        return hubs

    def create_tools(self, tools_config):
        tools = {}
        for device in tools_config:
            tool_id = device['id']
            try:
                tools[tool_id] = Tool(device, self.i2c, self.styles_path)
                logger.debug(f"Initialized tool {tool_id}")
            except Exception as e:
                logger.error(f"Error initializing tool {tool_id}: {e}")
        return tools

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    manager = Device_Manager(styles_path='styles.json')
    print(manager.hubs)
    print(manager.tools)
