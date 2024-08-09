import os
import json
import time
import logging
import board
import sys
import busio
from devices.poll_buttons import Poll_Buttons
from devices.tool import Tool
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from utils.style_manager import Style_Manager  # Ensure this import is correct

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)  # Make sure this line is correct and that config.json exists and is properly formatted

# Load the styles using Style_Manager
style_manager = Style_Manager()
styles = style_manager.get_styles()

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize MCP23017 based on the first button's connection address
if config.get('tools', []):
    mcp_address = int(config['tools'][0]['button']['connection']['address'], 16)
    mcp = MCP23017(i2c, address=mcp_address)
else:
    logger.error("No valid button configurations found. Exiting.")
    sys.exit(1)

# Initialize PCA9685 for LED control (assuming all LEDs are on the same hub)
pca_address = int(config['tools'][0]['button']['led']['connection']['address'], 16)
pca = PCA9685(i2c, address=pca_address)
pca.frequency = 1000

# Initialize tools
tools = []
for tool_config in config.get('tools', []):
    tool = Tool(tool_config, mcp, pca, styles, i2c)
    tools.append(tool)

# Extract all buttons for polling
buttons = [tool.button for tool in tools if tool.button is not None]

# Initialize polling
poller = Poll_Buttons(buttons, styles['RGBLED_button_styles'])  # Pass the styles to Poll_Buttons
poller.start_polling()

try:
    while True:
        # Check tool statuses and log changes
        for tool in tools:
            tool.update_status()
        time.sleep(1)  # Adjust the sleep time as needed
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
