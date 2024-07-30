import os
import json
import time
# Import the Hub class
from devices.hub import Hub

DEVICE_FILE = 'config.json'

# DeviceManager class
class Device_Manager:
    def __init__(self, device_file=DEVICE_FILE):
        self.device_file = device_file
        self.devices = self.get_devices(device_file)
        self.hubs = self.create_hubs(self.devices)

    def get_devices(self, file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                devices = json.load(f)
            return devices['devices']  # Adjusted to match the JSON structure
        else:
            raise FileNotFoundError(f"Device configuration file '{file}' not found.")

    def create_hubs(self, devices):
        hubs = {}
        for device in devices:
            if device['type'] == 'hub':  # Adjusted to match the JSON structure
                hub_id = device['id']
                hubs[hub_id] = Hub(device)
        return hubs

# Example usage
if __name__ == "__main__":
    manager = Device_Manager()
    print(manager.hubs)