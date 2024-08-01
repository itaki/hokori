import time
import os
import board
import busio
import logging
import json
from devices.tool import Tool
from devices.device_manager import Device_Manager
from devices.gate_manager import Gate_Manager
from utils.style_manager import Style_Manager

# Constants for configuration files and backup directory
DEVICE_FILE = 'config.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'
STYLES_FILE = 'styles.json'

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Main loop
def main():
    try:
        # Initialize I2C
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize Device Manager and Gate Manager
        device_manager = Device_Manager(device_file=DEVICE_FILE)
        gate_manager = Gate_Manager(GATES_FILE, i2c)

        # Load styles from the styles.json file
        style_manager = Style_Manager(STYLES_FILE)
        styles = style_manager.get_styles()

        # Use tools from the Device Manager
        tools = [Tool(tool, i2c, styles) for tool in device_manager.devices if tool['type'] == 'tool']
        
        logger.info("Tool initialization complete.")
        
        # Main loop to check for button presses and voltage
        while True:
            for tool in tools:
                tool.check_button()
                tool.check_voltage()
            time.sleep(0.1)  # Small delay to avoid busy waiting

    except FileNotFoundError as e:
        logger.error(e)
        print(e)
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
