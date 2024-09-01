# Importing necessary modules
import os
import json
import time
import logging
import board
import sys
import busio
from boards.mcp23017 import MCP23017
from boards.pca9685 import PCA9685
from boards.ads1115 import ADS1115
from adafruit_ads1x15.ads1115 import ADS1115 as Adafruit_ADS1115
from tool_manager import ToolManager  # Import the new ToolManager

# Configuring logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration flags
USE_GATES = True
USE_COLLECTORS = True
USE_GUI = False

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(config_path):
    logger.error(f"💢 Configuration file not found at {config_path}. Exiting.")
    sys.exit(1)

with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize boards
boards = {}
for board_config in config.get('boards', []):
    board_type = board_config['type']
    board_id = board_config['id']

    try:
        if board_type == 'MCP23017':
            boards[board_id] = MCP23017(i2c, board_config)
        elif board_type == 'PCA9685':
            boards[board_id] = PCA9685(i2c, board_config)
        elif board_type == 'ADS1115':
            boards[board_id] = ADS1115(Adafruit_ADS1115(i2c, address=int(board_config['i2c_address'], 16)), board_config)
        elif board_type == 'Raspberry Pi GPIO':
            boards[board_id] = "Raspberry Pi GPIO"  # Placeholder to represent GPIO
        else:
            logger.error(f"💢 Unknown board type {board_type} for board {board_id}")
    except Exception as e:
        logger.error(f"💢 Failed to initialize board {board_config.get('label', 'unknown')}: {e}")

# Initialize the ToolManager
from tool_manager import ToolManager

# Initialize ToolManager
tool_manager = ToolManager(config.get('tools', []), boards)

try:
    while True:
        tool_manager.start_monitoring()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
    tool_manager.cleanup()
    logger.info("All threads and resources cleaned up gracefully.")
    sys.exit(0)

