import os
import sys
import json
import logging
import board
import busio
import time
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from rgbled_button import RGBLED_Button
from pole_buttons import Poll_Buttons

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

# Load the configuration file
config_path = os.path.join(parent_dir, 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# LED color styles from the config
rgbled_styles = config.get('RGBLED_button_styles', {
    "RGBLED_off_color": {
        "red": 0,
        "green": 0,
        "blue": 0x6FFF
    },
    "RGBLED_on_color": {
        "red": 0xFFFF,
        "green": 0,
        "blue": 0xFFFF
    }
})

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

# Initialize buttons
buttons = []
for tool in config.get('tools', []):
    if tool.get('button'):
        button = RGBLED_Button(tool['button'], mcp, pca, rgbled_styles)
        buttons.append(button)

# Initialize polling
poller = Poll_Buttons(buttons, rgbled_styles)
poller.start_polling()

try:
    while True:
        # Main program can run other tasks here
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
