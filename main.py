import os
import sys
import time
import json
import logging
import board
import busio
from tool import Tool
from button_manager import Button_Manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config = load_config(config_path)

    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Initialize Button_Manager with button configs
    button_configs = [tool['button'] for tool in config['tools'] if 'button' in tool]
    button_manager = Button_Manager(i2c, button_configs)

    tools = []
    for tool_config in config['tools']:
        tool = Tool(tool_config, i2c, button_manager)
        tools.append(tool)

    button_manager.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        button_manager.stop()
        logger.info("Program interrupted by user")
