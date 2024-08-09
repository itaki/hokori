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
from devices.hub import Hub
from utils.style_manager import Style_Manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(config_path):
    logger.error(f"Configuration file not found at {config_path}. Exiting.")
    sys.exit(1)

with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Load the styles using Style_Manager
style_manager = Style_Manager()
styles = style_manager.get_styles()

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize hubs
hubs = {}
for hub_config in config.get('hubs', []):
    try:
        hub = Hub(hub_config, i2c)
        hubs[hub_config['id']] = hub
    except Exception as e:
        logger.error(f"Failed to initialize hub {hub_config.get('label', 'unknown')}: {e}")

# Initialize tools
tools = []
for tool_config in config.get('tools', []):
    hub_id = tool_config.get('button', {}).get('connection', {}).get('hub')
    if hub_id and hub_id in hubs:
        hub = hubs[hub_id]
        try:
            tool = Tool(tool_config, hub.gpio_expander, hub.pwm_led, styles, i2c)
            if tool.button or tool.voltage_sensor:  # Only add the tool if it was initialized correctly
                tools.append(tool)
            else:
                logger.error(f"Tool {tool.label} skipped due to invalid configuration.")
        except Exception as e:
            logger.error(f"Failed to initialize tool {tool_config.get('label', 'unknown')}: {e}")
    else:
        logger.error(f"Hub {hub_id} not found for tool {tool_config['label']}. Skipping tool creation.")

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
    
    # Cleanup resources gracefully
    poller.stop()
    for dust_collector in dust_collectors:
        dust_collector.cleanup()
    for tool in tools:
        if tool.voltage_sensor is not None:
            tool.voltage_sensor.stop()

    logger.info("All threads and resources cleaned up gracefully.")
