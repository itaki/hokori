import logging
import RPi.GPIO as GPIO  # Import the RPi.GPIO module

logger = logging.getLogger(__name__)

class Dust_Collector:
    def __init__(self, collector_config):
        self.label = collector_config.get('label', 'unknown')
        self.status = 'off'
        self.gpio_pin = None
        self.setup_relay(collector_config)

    def setup_relay(self, collector_config):
        relay_conn = collector_config.get('relay', {}).get('connection', {})
        hub = relay_conn.get('hub', 'local')

        if hub == 'local':
            self.gpio_pin = relay_conn.get('pin', 21)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
            logger.debug(f"GPIO pin {self.gpio_pin} set up for dust collector {self.label}")
        else:
            logger.error(f"Invalid hub: {hub} for dust collector {self.label}")

    def turn_on(self):
        if self.status != 'on':
            self.status = 'on'
            logger.info(f"Dust collector {self.label} turned on.")
            if self.gpio_pin is not None:
                GPIO.output(self.gpio_pin, GPIO.HIGH)
                logger.debug(f"GPIO pin {self.gpio_pin} activated for dust collector {self.label}")

    def turn_off(self):
        if self.status != 'off':
            self.status = 'off'
            logger.info(f"Dust collector {self.label} turned off.")
            if self.gpio_pin is not None:
                GPIO.output(self.gpio_pin, GPIO.LOW)
                logger.debug(f"GPIO pin {self.gpio_pin} deactivated for dust collector {self.label}")

    def manage_collector(self, tools):
        any_tool_on = any(tool.status == 'on' for tool in tools)
        if any_tool_on:
            self.turn_on()
        else:
            self.turn_off()

    def cleanup(self):
        if self.gpio_pin is not None:
            GPIO.output(self.gpio_pin, GPIO.LOW)
            GPIO.cleanup(self.gpio_pin)
            logger.debug(f"Cleaned up GPIO pin for dust collector {self.label}")
