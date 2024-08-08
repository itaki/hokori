import time
import threading
import logging
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import Direction, Pull

logger = logging.getLogger(__name__)

class Button_Manager:
    def __init__(self, i2c, button_configs):
        self.i2c = i2c
        self.button_configs = button_configs
        self.buttons = []
        self.running = False

        self._initialize_buttons()

    def _initialize_buttons(self):
        for config in self.button_configs:
            try:
                address = int(config['connection']['address'], 16)
                pin = config['connection']['pin']
                mcp = MCP23017(self.i2c, address=address)
                button = mcp.get_pin(pin)
                button.direction = Direction.INPUT
                button.pull = Pull.UP
                self.buttons.append((config['label'], button))
                logger.debug(f"Button {config['label']} initialized at address {address}, pin {pin}")
            except KeyError as e:
                logger.error(f"Configuration error: missing key {e} in button configuration for {config['label']}")
            except Exception as e:
                logger.error(f"Unexpected error initializing button for {config['label']}: {e}")

    def _poll_buttons(self):
        while self.running:
            for label, button in self.buttons:
                if not button.value:  # Button press detected
                    logger.debug(f"Button {label} pressed")
                    print(f"Button {label} pressed")
                    time.sleep(0.5)  # Debounce delay
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._poll_buttons, daemon=True)
            self.thread.start()
            logger.debug("Started button polling thread")

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
            logger.debug("Stopped button polling thread")
