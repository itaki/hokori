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
from devices.voltage_sensor_poller import VoltageSensorPoller
from utils.style_manager import Style_Manager
from boards.mcp23017 import MCP23017
from boards.pca9685 import PCA9685
from boards.ads1115 import ADS1115
from adafruit_ads1x15.ads1115 import ADS1115 as Adafruit_ADS1115
import random

# Configuring logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration flags
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

# Initialize tools
tools = []
collectors = []
# Ensure sensor_configs is initialized
sensor_configs = []

for tool_config in config.get('tools', []):
    try:
        # Initialize MCP23017 (button controller) and PCA9685 (LED/Servo controller) based on the config
        mcp = boards.get(tool_config['button']['connection']['board'], None) if 'button' in tool_config and 'connection' in tool_config['button'] else None
        pca_led = boards.get(tool_config['button']['led']['connection']['board'], None) if 'button' in tool_config and 'led' in tool_config['button'] and 'connection' in tool_config['button']['led'] else None
        ads = boards.get(tool_config['volt']['connection']['board'], None) if USE_VOLT_SENSORS and 'volt' in tool_config and 'connection' in tool_config['volt'] else None
        gpio = boards.get(tool_config['relay']['connection']['board'], None) if 'relay' in tool_config and 'connection' in tool_config['relay'] else None

        if 'relay' in tool_config and tool_config['relay'].get('type') == 'collector_relay':
            # Initialize a Dust Collector if the relay type indicates it
            collector = Dust_Collector(tool_config, tools)
            collectors.append(collector)
        else:
            # Collect voltage sensor configurations if sensors are enabled
            if USE_VOLT_SENSORS and ads:
                sensor_configs.append(tool_config['volt'])

            # Initialize the Tool with all the necessary components
            tool = Tool(tool_config, mcp, pca_led, ads, gpio, styles, i2c, boards, poller=None)  # Pass None or the actual poller if initialized earlier
            if tool.button or tool.voltage_sensor or tool.gpio_pin:
                tools.append(tool)
            else:
                logger.error(f"💢 Tool {tool.label} skipped due to invalid configuration.")
    except Exception as e:
        logger.error(f"💢 Failed to initialize tool {tool_config['label']}: {e}")

# Initialize the VoltageSensorPoller after all tools are created, if applicable
if USE_VOLT_SENSORS and sensor_configs:
    voltage_sensor_poller = VoltageSensorPoller(sensor_configs, ads)

else:
    voltage_sensor_poller = None
    logger.info("🔌 Voltage sensors disabled or no configurations provided.")

# Initialize Gate Manager if gates are in use
if USE_GATES:
    gate_manager = Gate_Manager(boards)

# Extract all buttons for polling
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
        if tool.voltage_sensor_poller is not None:
            try:
                logger.info(f"Stopping voltage sensor poller for tool {tool.label}")
                tool.voltage_sensor_poller.stop()
            except Exception as e:
                logger.error(f"Error while stopping voltage sensor poller for tool {tool.label}: {e}")

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
        
    if voltage_sensor_poller:
        try:
            logger.info("Stopping voltage sensor poller")
            voltage_sensor_poller.stop()
        except Exception as e:
            logger.error(f"Error while stopping voltage sensor poller: {e}")
        
    logger.info("All threads and resources cleaned up gracefully.")
