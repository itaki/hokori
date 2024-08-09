import os
import sys
import time
import threading
import json

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

import board
import busio
import logging
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration file
config_path = os.path.join(parent_dir, 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Extract button configurations from the config file
button_configs = []
for tool in config.get('tools', []):
    button = tool.get('button', {})
    if button:
        connection = button.get('connection', {})
        led = button.get('led', {})
        if connection:
            button_configs.append({
                "label": button.get('label', 'Unknown Button'),
                "id": button.get('id', 'unknown_id'),
                "physical_location": button.get('physical_location', 'Unknown Location'),
                "connection": {
                    "hub": connection.get('hub', 'unknown_hub'),
                    "address": connection.get('address', '0x00'),
                    "pin": connection.get('pin', 0)
                },
                "led_connection": {
                    "hub": led.get('connection', {}).get('hub', 'unknown_hub'),
                    "address": led.get('connection', {}).get('address', '0x00'),
                    "pins": led.get('connection', {}).get('pins', [0, 1, 2])
                }
            })

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
if button_configs:
    mcp_address = int(button_configs[0]['connection']['address'], 16)
    mcp = MCP23017(i2c, address=mcp_address)
else:
    logger.error("No valid button configurations found. Exiting.")
    sys.exit(1)

# Initialize PCA9685 for LED control (assuming all LEDs are on the same hub)
pca_address = int(button_configs[0]['led_connection']['address'], 16)
pca = PCA9685(i2c, address=pca_address)
pca.frequency = 1000

# Initialize buttons, LEDs, and their states
buttons = []

def set_led_color(leds, color):
    leds[0].duty_cycle = 0xFFFF - color["red"]
    leds[1].duty_cycle = 0xFFFF - color["green"]
    leds[2].duty_cycle = 0xFFFF - color["blue"]


for config in button_configs:
    try:
        pin = config['connection']['pin']
        button = mcp.get_pin(pin)
        button.direction = Direction.INPUT
        button.pull = Pull.UP
        
        led_pins = config['led_connection']['pins']
        leds = [pca.channels[pin] for pin in led_pins]  # Direct channel access
        
        # Initialize button state and set LED to off color
        buttons.append({
            "label": config['label'],
            "button": button,
            "leds": leds,
            "state": False  # Initial state is off
        })
        
        set_led_color(leds, rgbled_styles["RGBLED_off_color"])
        
        logger.debug(f"Button {config['label']} initialized at pin {pin} with LEDs at pins {led_pins} (set to OFF)")
    except Exception as e:
        logger.error(f"Error initializing button {config['label']}: {e}")



def poll_buttons():
    while True:
        for button_config in buttons:
            label = button_config["label"]
            button = button_config["button"]
            leds = button_config["leds"]
            
            if not button.value:  # Button press detected
                button_config["state"] = not button_config["state"]  # Toggle the state
                state_str = "ON" if button_config["state"] else "OFF"
                
                # Set LED color based on state
                color = rgbled_styles["RGBLED_on_color"] if button_config["state"] else rgbled_styles["RGBLED_off_color"]
                set_led_color(leds, color)
                
                logger.debug(f"Button {label} toggled to {state_str}")
                time.sleep(0.5)  # Debounce delay
        time.sleep(0.1)  # Small delay to avoid busy-waiting

# Start polling in a background thread
polling_thread = threading.Thread(target=poll_buttons, daemon=True)
polling_thread.start()

try:
    while True:
        # Main program can run other tasks here
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
