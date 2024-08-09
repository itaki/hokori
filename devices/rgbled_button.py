import logging
from digitalio import Direction, Pull

logger = logging.getLogger(__name__)

class RGBLED_Button:
    def __init__(self, config, mcp, pca, rgbled_styles, status_callback=None):
        self.label = config['label']
        self.state = False  # Initial state is off
        self.status_callback = status_callback
        self.rgbled_styles = rgbled_styles  # Store the passed styles

        # Initialize the button
        pin = config['connection']['pin']
        self.button = mcp.get_pin(pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP

        # Initialize the LEDs
        led_pins = config.get('led', {}).get('connection', {}).get('pins', [])
        self.leds = [pca.channels[pin] for pin in led_pins]

        # Set the initial LED color to off
        self.set_led_color(self.rgbled_styles["RGBLED_off_color"])
        logger.debug(f"Button {self.label} initialized at pin {pin} with LEDs at pins {led_pins} (set to OFF)")

    def set_led_color(self, color):
        self.leds[0].duty_cycle = 0xFFFF - color["red"]
        self.leds[1].duty_cycle = 0xFFFF - color["green"]
        self.leds[2].duty_cycle = 0xFFFF - color["blue"]

    def toggle(self):
        self.state = not self.state  # Toggle the state
        # Set LED color based on state
        color = self.rgbled_styles["RGBLED_on_color"] if self.state else self.rgbled_styles["RGBLED_off_color"]
        self.set_led_color(color)
        
        # If a status callback is provided, call it to update the tool's status
        if self.status_callback:
            new_status = 'on' if self.state else 'off'
            self.status_callback(new_status)
        
        state_str = "ON" if self.state else "OFF"
        logger.debug(f"Button {self.label} toggled to {state_str}")
