import os
import sys
import time
import asyncio

# Add the parent directory of the current file to the system path
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.append(parent_dir)

import board
import busio
import logging
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017

logger = logging.getLogger(__name__)

class SimpleButton:
    def __init__(self, btn_config, i2c):
        self.id = btn_config.get('id', 'unknown')
        self.label = btn_config.get('label', 'unknown')
        self.physical_location = btn_config.get('physical_location', 'unknown')
        self.connection = btn_config.get('connection', {})

        self.i2c = i2c
        self.button = None

        # Initialize button
        self.initialize_button()

    def initialize_button(self):
        try:
            address = int(self.connection['address'], 16)
            pin = self.connection['pin']
            self.mcp = MCP23017(self.i2c, address=address)
            self.button = self.mcp.get_pin(pin)
            self.button.direction = Direction.INPUT
            self.button.pull = Pull.UP
            logger.debug(f"Button initialized at address {address}, pin {pin}")
        except KeyError as e:
            logger.error(f"Configuration error: missing key {e} in button configuration for {self.label}")
        except Exception as e:
            logger.error(f"Unexpected error initializing button for {self.label}: {e}")

    async def check_button(self):
        last_button_read = True  # Assume unpressed state is high
        while True:
            if self.button is not None:
                current_read = self.button.value
                if last_button_read and not current_read:  # Detect button press (transition from high to low)
                    logger.debug(f"Button press detected for {self.label}")
                    print(f"Button {self.label} pressed")
                    await asyncio.sleep(0.5)  # Simple debounce delay
                last_button_read = current_read
            await asyncio.sleep(0.1)  # Small delay to avoid busy-waiting

async def main():
    logging.basicConfig(level=logging.DEBUG)

    i2c = busio.I2C(board.SCL, board.SDA)

    button_configs = [
        {
            "type": "SimpleButton",
            "label": "Hose Button",
            "id": "hose_button",
            "physical_location": "By the Hose",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 0
            }
        },
        {
            "type": "SimpleButton",
            "label": "LEFT Miter Saw Button",
            "id": "left_miter_saw_button",
            "physical_location": "Above the miter saw",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 1
            }
        },
        {
            "type": "SimpleButton",
            "label": "RIGHT Miter Saw Button",
            "id": "right_miter_saw_button",
            "physical_location": "Above the miter saw",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 2
            }
        },
        {
            "type": "SimpleButton",
            "label": "Test Button",
            "id": "test_button",
            "physical_location": "Test Location",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 3
            }
        }
    ]

    tasks = []
    for config in button_configs:
        logger.debug(f"Initializing button {config['label']}")
        button = SimpleButton(config, i2c)
        tasks.append(asyncio.create_task(button.check_button()))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
