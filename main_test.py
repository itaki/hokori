import os
import json
import logging
import sys
import board
import busio

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(config_path):
    logger.error(f"Configuration file not found at {config_path}. Exiting.")
    sys.exit(1)

with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Confirm that the config file is loaded
print("Config loaded:", config)
print("Boards section:", config.get('boards'))  # This will print the 'boards' section specifically

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize boards
boards = {}
print("Boards before loading:", boards)  # This should print an empty dictionary

for board_config in config.get('boards', []):
    board_type = board_config['type']
    board_id = board_config['id']
    logger.debug(f"Attempting to initialize board {board_id} of type {board_type}.")

    try:
        if board_type == 'MCP23017':
            print(f"Initializing MCP23017 with config: {board_config}")
            boards[board_id] = MCP23017(i2c, board_config)
        elif board_type == 'PCA9685':
            print(f"Initializing PCA9685 with config: {board_config}")
            boards[board_id] = PCA9685(i2c, board_config)
        elif board_type == 'ADS1115':
            print(f"Initializing ADS1115 with config: {board_config}")
            boards[board_id] = ADS1115(i2c, board_config)
        else:
            logger.error(f"Unknown board type {board_type} for board {board_id}")
    except Exception as e:
        logger.error(f"Failed to initialize board {board_config.get('label', 'unknown')}: {e}")

print("Boards after loading:", boards)  # This should print the populated boards dictionary

# Now you can proceed with initializing tools and dust collectors using the `boards` dictionary
