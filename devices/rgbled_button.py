import logging
from digitalio import Direction, Pull

logger = logging.getLogger(__name__)

class RGBLED_Button:
    def __init__(self, config, mcp, pca, rgbled_styles):
        self.label = config['label']
        self.state = False  # Initial state is off

        # Initialize the button
        pin = config['connection']['pin']
        self.button = mcp.get_pin(pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP

        # Initialize the LEDs
        led_config = config.get('led', {}).get('connection', {})
        led_pins = led_config.get('pins', [])
        if not led_pins:
            raise KeyError(f"No LED connection pins found for {self.label}")
        self.leds = [pca.channels[pin] for pin in led_pins]

        # Set the initial LED color to off
        self.set_led_color(rgbled_styles["RGBLED_off_color"])
        logger.debug(f"Button {self.label} initialized at pin {pin} with LEDs at pins {led_pins} (set to OFF)")

    def set_led_color(self, color):
        self.leds[0].duty_cycle = 0xFFFF - color["red"]
        self.leds[1].duty_cycle = 0xFFFF - color["green"]
        self.leds[2].duty_cycle = 0xFFFF - color["blue"]

    def toggle(self, rgbled_styles):
        self.state = not self.state  # Toggle the state
        color = rgbled_styles["RGBLED_on_color"] if self.state else rgbled_styles["RGBLED_off_color"]
        self.set_led_color(color)
        state_str = "ON" if self.state else "OFF"
        logger.debug(f"Button {self.label} toggled to {state_str}")
