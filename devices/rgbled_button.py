import logging
from digitalio import Direction, Pull

logger = logging.getLogger(__name__)

class RGBLED_Button:
    def __init__(self, config, mcp, pca, rgbled_styles, status_callback=None, button_pins=None, led_pins=None):
        self.label = config['label']
        self.state = config.get('initial_state', False)  # Allow setting initial state from config
        self.status_callback = status_callback
        self.rgbled_styles = rgbled_styles  # Store the passed styles

        # Use button_pins if provided; otherwise, fall back to the config
        if button_pins is not None:
            pin = button_pins[0]  # Assuming button_pins is a list/tuple with at least one pin
        else:
            pin = config['connection']['pins'][0]

        self.button = mcp.get_pin(pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP

        # Use led_pins if provided; otherwise, fall back to the config
        if led_pins is not None:
            self.leds = [pca.channels[pin] for pin in led_pins]
        else:
            led_pins = config.get('led', {}).get('connection', {}).get('pins', [])
            if len(led_pins) < 3:
                logger.error(f"💢 Insufficient LED pins provided for {self.label}. Expected 3, got {len(led_pins)}.")
                raise ValueError(f"💢 Invalid LED pin configuration for {self.label}")
            else:
                self.leds = [pca.channels[pin] for pin in led_pins]

        # Set the initial LED color based on the initial state
        if self.leds:
            initial_color = self.rgbled_styles["RGBLED_on_color"] if self.state else self.rgbled_styles["RGBLED_off_color"]
            self.set_led_color(initial_color)
            logger.debug(f"      🚥 🖲 Button {self.label} initialized at pin {pin} with LEDs at pins {led_pins} (set to {'ON' if self.state else 'OFF'})")
        else:
            logger.debug(f"      🚥 🖲 Button {self.label} initialized at pin {pin} without valid LEDs configuration.")


    def set_led_color(self, color):
        if self.leds:
            self.leds[0].duty_cycle = 0xFFFF - color["red"]
            self.leds[1].duty_cycle = 0xFFFF - color["green"]
            self.leds[2].duty_cycle = 0xFFFF - color["blue"]

    def toggle(self):
        self.state = not self.state  # Toggle the state
        # Set LED color based on state
        if self.leds:
            color = self.rgbled_styles["RGBLED_on_color"] if self.state else self.rgbled_styles["RGBLED_off_color"]
            self.set_led_color(color)
        
        # If a status callback is provided, call it to update the tool's status
        if self.status_callback:
            new_status = 'on' if self.state else 'off'
            self.status_callback(new_status)
        
        state_str = "ON" if self.state else "OFF"
        logger.debug(f"      🚥 🖲 Button {self.label} toggled to {state_str}")
