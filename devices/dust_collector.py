import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

class Dust_Collector:
    def __init__(self, config, i2c):
        self.id = config.get('id', 'unknown')
        self.label = config.get('label', 'unknown')
        self.i2c = i2c
        self.relay_pin = config.get('relay_pin')
        self.status = 'off'
        self.setup_relay()

    def setup_relay(self):
        if self.relay_pin is not None:
            GPIO.setmode(GPIO.BCM)  # or GPIO.setmode(GPIO.BOARD) depending on your pin numbering
            GPIO.setup(self.relay_pin, GPIO.OUT)
            GPIO.output(self.relay_pin, GPIO.LOW)
            logger.debug(f"Relay pin {self.relay_pin} set up for dust collector {self.label}")
        else:
            logger.error(f"No relay pin configured for dust collector {self.label}")

    def manage_collector(self, tools):
        any_tool_on = any(tool.status == 'on' for tool in tools)
        if any_tool_on:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        if self.status != 'on':
            self.status = 'on'
            logger.info(f"Dust collector {self.label} turned on.")
            if self.relay_pin is not None:
                GPIO.output(self.relay_pin, GPIO.HIGH)
                logger.debug(f"Relay pin {self.relay_pin} activated for dust collector {self.label}")

    def turn_off(self):
        if self.status != 'off':
            self.status = 'off'
            logger.info(f"Dust collector {self.label} turned off.")
            if self.relay_pin is not None:
                GPIO.output(self.relay_pin, GPIO.LOW)
                logger.debug(f"Relay pin {self.relay_pin} deactivated for dust collector {self.label}")

    def cleanup(self):
        if self.relay_pin is not None:
            GPIO.cleanup(self.relay_pin)
            logger.debug(f"Cleaned up GPIO for relay pin {self.relay_pin}")
