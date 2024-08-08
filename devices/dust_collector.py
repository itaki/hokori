import time
import logging
import adafruit_mcp230xx.mcp23017 as MCP
import board
import busio

logger = logging.getLogger(__name__)

class Dust_Collector:
    def __init__(self, config, i2c):
        self.id = config.get('id', 'unknown')
        self.label = config.get('label', 'unknown')
        self.preferences = config.get('preferences', {})
        self.spin_up_delay = self.preferences.get('spin_up_delay', 10)
        self.minimum_up_time = self.preferences.get('minimum_up_time', 10)
        self.cool_down_time = self.preferences.get('cool_down_time', 30)
        self.relay_config = config.get('relay', {})
        self.i2c = i2c
        self.mcp = None
        self.relay_pin = None
        self.status = 'off'
        self.last_turned_on_time = None
        self.setup_relay()

    def setup_relay(self):
        relay_conn = self.relay_config.get('connection', {})
        address = int(relay_conn.get('address', '0x20'), 16)
        pin_number = relay_conn.get('pin', 2)
        
        self.mcp = MCP.MCP23017(self.i2c, address=address)
        self.relay_pin = self.mcp.get_pin(pin_number)
        self.relay_pin.switch_to_output(value=False)
        logger.debug(f"Relay pin {pin_number} at address {address} set up for dust collector {self.label}")

    def manage_collector(self, tools):
        any_tool_on = any(tool.status == 'on' for tool in tools)
        if any_tool_on:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        if self.status != 'on':
            self.status = 'on'
            self.last_turned_on_time = time.time()
            logger.info(f"Dust collector {self.label} turned on.")
            if self.relay_pin:
                self.relay_pin.value = True
                logger.debug(f"Relay pin activated for dust collector {self.label}")

    def turn_off(self):
        if self.status == 'on':
            elapsed_time = time.time() - self.last_turned_on_time
            if elapsed_time >= self.minimum_up_time:
                self.status = 'off'
                logger.info(f"Dust collector {self.label} turned off.")
                if self.relay_pin:
                    self.relay_pin.value = False
                    logger.debug(f"Relay pin deactivated for dust collector {self.label}")

    def cleanup(self):
        if self.relay_pin:
            self.relay_pin.value = False
            logger.debug(f"Cleaned up relay pin for dust collector {self.label}")

# Example usage
if __name__ == "__main__":
    import json
    import board
    import busio

    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize dust collectors from config
    dust_collectors = [Dust_Collector(dc, i2c) for dc in config['collectors']]

    # Simulate tools for testing
    class Tool:
        def __init__(self, status):
            self.status = status

    tools = [Tool(status='on'), Tool(status='off')]

    # Manage collectors based on tool status
    for dc in dust_collectors:
        dc.manage_collector(tools)
        time.sleep(5)
        dc.turn_off()
        dc.cleanup()
