import logging
import RPi.GPIO as GPIO  # Import the RPi.GPIO module
import threading
import time

logger = logging.getLogger(__name__)

class Dust_Collector:
    def __init__(self, collector_config, tools):
        self.label = collector_config.get('label', 'unknown')
        self.status = 'off'
        self.gpio_pin = None
        self.tools = tools  # List of tools to monitor
        self.stop_event = threading.Event()  # Event to stop the thread
        self.spin_down_time = collector_config.get('preferences', {}).get('spin_down_time', 30)  # Default to 30 seconds

        try:
            self.setup_relay(collector_config)
        except KeyError as e:
            logger.error(f"Error in Dust_Collector setup: Missing key {e}")
            raise  # Re-raise the exception to be caught in main.py

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def setup_relay(self, collector_config):
        relay_conn = collector_config.get('relay', {}).get('connection', {})
        logger.debug(f"Setting up relay for {self.label} with config: {relay_conn}")
        self.gpio_pin = relay_conn.get('pins', [21])[0]  # Assuming 'pins' is a list; take the first pin
        if not self.gpio_pin:
            raise KeyError("pin")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
        logger.debug(f"GPIO pin {self.gpio_pin} set up for dust collector {self.label}")

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

    def run(self):
        """Main loop to manage the dust collector based on tool statuses."""
        while not self.stop_event.is_set():
            self.manage_collector()
            time.sleep(1)  # Adjust sleep time as needed

    def manage_collector(self):
        any_tool_on = False
        max_spin_down_time = 0

        for tool in self.tools:
            if tool.status == 'on' and tool.preferences.get('use_collector', False):
                any_tool_on = True
                max_spin_down_time = max(max_spin_down_time, tool.preferences.get('spin_down_time', self.spin_down_time))

        if any_tool_on:
            self.turn_on()
        elif self.status == 'on':
            logger.info(f"Dust collector {self.label} will spin down in {max_spin_down_time} seconds.")
            time.sleep(max_spin_down_time)
            self.turn_off()

    def cleanup(self):
        self.stop_event.set()  # Signal the thread to stop
        self.thread.join()  # Wait for the thread to finish

        if self.gpio_pin is not None:
            GPIO.output(self.gpio_pin, GPIO.LOW)
            GPIO.cleanup(self.gpio_pin)
            logger.debug(f"Cleaned up GPIO pin for dust collector {self.label}")
