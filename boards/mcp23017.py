from adafruit_mcp230xx.mcp23017 import MCP23017 as Adafruit_MCP23017
from digitalio import Direction, Pull
import logging

logger = logging.getLogger(__name__)

class MCP23017:
    def __init__(self, i2c, config):
        self.i2c_address = int(config['i2c_address'], 16)
        self.mcp = Adafruit_MCP23017(i2c, address=self.i2c_address)
        self.pins = [self.mcp.get_pin(i) for i in range(16)]  # MCP23017 has 16 GPIO pins (0-15)
        logger.info(f"     🔮 Initialized MCP23017 at address {hex(self.i2c_address)} as board ID {config['id']}")

    def get_pin(self, pin_number):
        """Returns the pin object for the given pin number."""
        return self.pins[pin_number]

    def setup_pin(self, pin, direction, pullup=False):
        if direction == "input":
            self.pins[pin].direction = Direction.INPUT
            if pullup:
                self.pins[pin].pull = Pull.UP
        elif direction == "output":
            self.pins[pin].direction = Direction.OUTPUT

    def write_pin(self, pin, value):
        self.pins[pin].value = value

    def read_pin(self, pin):
        return self.pins[pin].value
