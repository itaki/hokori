# Importing necessary modules
import os
import json
import time
import logging
import board
import sys
import busio
from devices.poll_buttons import Poll_Buttons
from devices.tool import Tool
from devices.gate_manager import Gate_Manager
from devices.dust_collector import Dust_Collector
from utils.style_manager import Style_Manager
from boards.mcp23017 import MCP23017
from boards.pca9685 import PCA9685
from adafruit_ads1x15.ads1115 import ADS1115 as Adafruit_ADS1115
import random

# Configuring logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration flag to control gate-related functionality
USE_GATES = True
USE_VOLT_SENSORS = True
USE_BUTTONS = True
USE_COLLECTORS = True
USE_GUI = False

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(config_path):
    logger.error(f"💢 Configuration file not found at {config_path}. Exiting.")
    sys.exit(1)

with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Load the styles using Style_Manager
style_manager = Style_Manager()
styles = style_manager.get_styles()

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize boards
boards = {}  # Change from list to dictionary
for board_config in config.get('boards', []):
    board_type = board_config['type']
    board_id = board_config['id']

    try:
        if board_type == 'MCP23017':
            boards[board_id] = MCP23017(i2c, board_config)
        elif board_type == 'PCA9685':
            boards[board_id] = PCA9685(i2c, board_config)
        elif board_type == 'ADS1115':
            boards[board_id] = Adafruit_ADS1115(i2c, address=int(board_config['i2c_address'], 16))
            logger.info(f"     🔮 Initialized ADS1115 at address {board_config['i2c_address']} and board ID {board_id}")
        elif board_type == 'Raspberry Pi GPIO':
            boards[board_id] = "Raspberry Pi GPIO"  # Placeholder to represent GPIO
        else:
            logger.error(f"💢 Unknown board type {board_type} for board {board_id}")
    except Exception as e:
      logger.error(f"💢 Failed to initialize board {board_config.get('label', 'unknown')}: {e}")

# Initialize tools
tools = []
collectors = []

# Initialize tools and dust collectors
for tool_config in config.get('tools', []):
    try:
        mcp = boards.get(tool_config['button']['connection']['board'], None) if 'button' in tool_config and 'connection' in tool_config['button'] else None
        pca_led = boards.get(tool_config['button']['led']['connection']['board'], None) if 'button' in tool_config and 'led' in tool_config['button'] and 'connection' in tool_config['button']['led'] else None
        if USE_VOLT_SENSORS:
            ads = boards.get(tool_config['volt']['connection']['board'], None) if 'volt' in tool_config and 'connection' in tool_config['volt'] else None
        else:
            logger.info("🔌 Voltage sensors disabled.")
        gpio = boards.get(tool_config['relay']['connection']['board'], None) if 'relay' in tool_config and 'connection' in tool_config['relay'] else None

        # Determine if this is a dust collector or a regular tool
        if 'relay' in tool_config and tool_config['relay'].get('type') == 'collector_relay':
            collector = Dust_Collector(tool_config, tools)
            collectors.append(collector)
        else:
            # Initialize the tool with the appropriate configurations
            tool = Tool(tool_config, mcp, pca_led, ads, gpio, styles, i2c, boards)
            
            if tool.button or tool.voltage_sensor or tool.gpio_pin:
                tools.append(tool)
            else:
                logger.error(f"💢 Tool {tool.label} skipped due to invalid configuration.")
    except Exception as e:
        logger.error(f"💢 Failed to initialize tool {tool_config['label']}: {e}")


# Initialize Gate Manager if gates are in use
if USE_GATES:
    gate_manager = Gate_Manager(boards)  # Pass the boards dictionary to the Gate_Manager

# Extract all buttons for polling
# Initialize polling for buttons
buttons = [tool.button for tool in tools if tool.button is not None]
poller = Poll_Buttons(buttons, styles['RGBLED_button_styles'])
poller.start_polling()

try:
    while True:
        tool_states_changed = any(tool.status_changed for tool in tools)
        if tool_states_changed:
            logger.debug("Detected a tool status change.")
            if USE_GATES:
                gate_manager.set_gates(tools)
            for tool in tools:
                logger.debug(f"🌑 Tool {tool.label} status: {tool.status}")
                tool.reset_status_changed()

        time.sleep(1)
        print(f'running at {time.time()}', end='\r')
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
    
    # Cleanup dust collectors
    for collector in collectors:
        try:
            logger.info(f"Cleaning up collector {collector.label}")
            collector.cleanup()
        except Exception as e:
            logger.error(f"Error while cleaning up collector {collector.label}: {e}")
    
    for tool in tools:
        if tool.voltage_sensor is not None:
            try:
                logger.info(f"Stopping voltage sensor for tool {tool.label}")
                tool.voltage_sensor.stop()
            except Exception as e:
                logger.error(f"Error while stopping voltage sensor for tool {tool.label}: {e}")
        if tool.gpio_pin is not None:
            try:
                logger.info(f"Cleaning up GPIO for tool {tool.label}")
                tool.cleanup()
            except Exception as e:
                logger.error(f"Error while cleaning up GPIO for tool {tool.label}: {e}")

    try:
        logger.info("Stopping poller")
        poller.stop()
    except Exception as e:
        logger.error(f"Error while stopping poller: {e}")
        
    logger.info("All threads and resources cleaned up gracefully.")
