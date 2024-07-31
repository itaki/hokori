import os
import json
import board
import busio
from devices.hub import Hub
from devices.tool import Tool

DEVICE_FILE = 'config.json'

class Device_Manager:
    def __init__(self, device_file=DEVICE_FILE):
        self.device_file = device_file
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.devices = self.get_devices(device_file)
        self.hubs = self.create_hubs(self.devices)
        self.tools = self.create_tools(self.devices)

    def get_devices(self, file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                config = json.load(f)
            return config['devices']
        else:
            raise FileNotFoundError(f"Device configuration file '{file}' not found.")

    def create_hubs(self, devices):
        hubs = {}
        for device in devices:
            if device['type'] == 'hub':
                hub_id = device['id']
                try:
                    hubs[hub_id] = Hub(device, self.i2c)
                except Exception as e:
                    print(f"Error initializing hub {hub_id}: {e}")
        return hubs

    def create_tools(self, devices):
        tools = {}
        for device in devices:
            if device['type'] == 'tool':
                tool_id = device['id']
                try:
                    tools[tool_id] = Tool(device, self.i2c)
                except Exception as e:
                    print(f"Error initializing tool {tool_id}: {e}")
        return tools

# Example usage
if __name__ == "__main__":
    manager = Device_Manager()
    print(manager.hubs)
    print(manager.tools)
