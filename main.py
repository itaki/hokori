import os
import json
import time
import logging
import board
import sys
import busio
from devices.poll_buttons import Poll_Buttons
from devices.tool import Tool
from devices.dust_collector import Dust_Collector
from devices.gate_manager import Gate_Manager
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from utils.style_manager import Style_Manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

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

# Initialize dust collectors
dust_collectors = []
for dc_config in config.get('collectors', []):
    dust_collector = Dust_Collector(dc_config)
    dust_collectors.append(dust_collector)

# Initialize Gate Manager
gate_manager = Gate_Manager()

# Extract all buttons for polling
buttons = [tool.button for tool in tools if tool.button is not None]

# Initialize polling
poller = Poll_Buttons(buttons, styles['RGBLED_button_styles'])
poller.start_polling()

# Helper function to update gates based on current tool statuses
def update_gates():
    active_tools = [tool for tool in tools if tool.status == 'on']
    if active_tools:
        gate_manager.set_gates({tool.id: tool for tool in active_tools})

try:
    while True:
        # We assume tools are updated in the background, so we only need to react to changes
        tool_states_changed = any(tool.status_changed for tool in tools)
        
        # If any tool status changed, update gates
        if tool_states_changed:
            update_gates()
            for tool in tools:
                tool.reset_status_changed()  # Reset the status changed flag after processing

        
        # Manage dust collectors
        for dust_collector in dust_collectors:
            dust_collector.manage_collector(tools)
        
        time.sleep(1)  # Adjust the sleep time as needed
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
    for dust_collector in dust_collectors:
        dust_collector.cleanup()
