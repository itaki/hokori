import logging
import threading
import time
import RPi.GPIO as GPIO
from .rgbled_button import RGBLED_Button
from .voltage_sensor import Voltage_Sensor

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, mcp, pca, ads, gpio, styles, i2c, boards):
        self.label = tool_config['label']
        self.id = tool_config['id']
        self.status = tool_config.get('status', 'off')
        self.status_changed = False
        self.preferences = tool_config.get('preferences', {})
        self.gate_prefs = self.preferences.get('gate_prefs', [])
        self.volt = tool_config.get('volt', {})
        self.keyboard_key = tool_config.get('keyboard_key', None)
        self.physical_location = tool_config.get('physical_location', '')

        # Initialize button if available
        self.button_status = 'off'
        try:
            if mcp and 'button' in tool_config:
                #logger.debug(f"🌑 Initializing button for tool {self.label} with config: {tool_config['button']}")
                button_pins = tool_config['button']['connection']['pins']
                led_pins = tool_config['button']['led']['connection']['pins'] if 'led' in tool_config['button'] else []
                self.button = RGBLED_Button(tool_config['button'], mcp, pca, styles['RGBLED_button_styles'], self.update_status_from_button)
            else:
                self.button = None
                #logger.warning(f"🌟 No button configuration found for tool {self.label}")
        except Exception as e:
            logger.error(f"💢 Error initializing button for tool {self.label}: {e}")
            raise

        # Initialize voltage sensor if available
        self.voltage_status = 'off'
        try:
            if ads and 'volt' in tool_config:
                #logger.debug(f"🌑 Initializing voltage sensor for tool {self.label} with config: {tool_config['volt']}")
                self.voltage_sensor = Voltage_Sensor(tool_config['volt'], ads, self.update_status_from_voltage)
            else:
                self.voltage_sensor = None
                #logger.warning(f"🌟 No voltage sensor configuration found for tool {self.label}")
        except Exception as e:
            logger.error(f"💢 Error initializing voltage sensor for tool {self.label}: {e}")
            raise

        # Initialize relay (dust collector)
        self.relay_status = 'off'
        self.gpio_pin = None  # Initialize gpio_pin attribute
        try:
            if gpio and 'relay' in tool_config:
                #logger.debug(f"🌑 Initializing relay for tool {self.label} with config: {tool_config['relay']}")
                relay_pins = tool_config['relay']['connection']['pins']
                self.gpio_pin = relay_pins[0]  # Assume single pin for relay control
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
                self.thread = threading.Thread(target=self.run_relay, daemon=True)
                self.thread.start()
                logger.info(f"     🔮 Initialized Tool {self.label} successfully.")
            else:
                self.gpio_pin = None
                #logger.warning(f"🌟 No relay configuration found for tool {self.label}")
        except Exception as e:
            logger.error(f"💢 Error initializing relay for tool {self.label}: {e}")
            raise

        

    def run_relay(self):
        """Threaded function to manage the dust collector based on tool status."""
        while True:
            self.manage_collector()
            time.sleep(1)  # Adjust sleep time as needed

    def manage_collector(self):
        """Manage the dust collector relay based on the tool's status."""
        if self.status == 'on':
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        if self.relay_status != 'on':
            self.relay_status = 'on'
            #logger.info(f"🔵 Tool {self.label} turned on.")
            if self.gpio_pin is not None:
                GPIO.output(self.gpio_pin, GPIO.HIGH)

    def turn_off(self):
        if self.relay_status != 'off':
            self.relay_status = 'off'
            #logger.info(f"🔵 Tool {self.label} turned off.")
            if self.gpio_pin is not None:
                GPIO.output(self.gpio_pin, GPIO.LOW)

    def toggle_button(self):
        """Toggle the button state."""
        if self.button:
            self.button.toggle()

    def update_status_from_button(self, new_status):
        self.button_status = new_status
        self.update_status()
        

    def update_status_from_voltage(self, new_status):
        self.voltage_status = new_status
        self.update_status()

    def update_status(self):
        """Combine button and voltage sensor statuses to determine tool status."""
        new_status = 'on' if self.button_status == 'on' or self.voltage_status == 'on' else 'off'
        if new_status != self.status:
            self.status = new_status
            self.status_changed = True
            if self.status == 'on':
                icon = "💫"
            else:
                icon = "💤"        
            logger.info(f"🔵 {icon} Tool {self.label} status changed to {self.status} {icon}")
        else:
            self.status_changed = False


    def reset_status_changed(self):
        self.status_changed = False

    def cleanup(self):
        """Cleanup GPIO resources."""
        if self.relay_status == 'on':
            self.turn_off()
        if self.gpio_pin is not None:
            GPIO.cleanup(self.gpio_pin)
        logger.debug(f"🌑 Cleaned up GPIO for tool {self.label}")
