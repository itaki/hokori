import time
import logging
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import DigitalInOut, Direction

logger = logging.getLogger(__name__)

class Dust_Collector:
    def __init__(self, config, i2c):
        self.label = config['label']
        self.id = config['id']
        self.preferences = config['preferences']
        self.relay_config = config['relay']
        self.minimum_up_time = self.preferences.get('minimum_up_time', 30)  # Default minimum up-time to 30 seconds
        self.status = 'off'
        self.spin_up_time = 0
        self.i2c = i2c
        self.initialize_relay()
        self.turn_off()  # Ensure the dust collector is off when initialized

    def initialize_relay(self):
        try:
            address = int(self.relay_config['connection']['address'], 16)
            pin = self.relay_config['connection']['pin']
            self.mcp = MCP23017(self.i2c, address=address)
            self.relay = self.mcp.get_pin(pin)
            self.relay.direction = Direction.OUTPUT
            logger.info(f"Dust collector relay {self.label} initialized at address {hex(address)} on pin {pin}")
        except Exception as e:
            logger.error(f"Error initializing dust collector relay {self.label}: {e}")

    def turn_on(self):
        self.relay.value = True
        self.status = 'on'
        self.spin_up_time = time.time()
        logger.info(f"Dust collector {self.label} turned on")

    def turn_off(self):
        self.relay.value = False
        self.status = 'off'
        logger.info(f"Dust collector {self.label} turned off")

    def manage_collector(self, tools):
        current_time = time.time()
        active_tools = [tool for tool in tools if tool.status == 'on' and tool.preferences.get('use_collector', False)]

        if active_tools:
            if self.status == 'off':
                self.turn_on()
        else:
            up_time_elapsed = current_time - self.spin_up_time
            if self.status == 'on' and up_time_elapsed >= self.minimum_up_time:
                self.turn_off()
