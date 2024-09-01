import logging
import RPi.GPIO as GPIO
import threading
import time

logger = logging.getLogger(__name__)

class DustCollector:
    def __init__(self, config):
        self.label = config.get('label', 'Unknown Collector')
        self.board_id = config['connection']['board']
        self.pin = config['connection']['pins'][0]
        self.spin_up_delay = config['preferences'].get('spin_up_delay', 5)
        self.minimum_up_time = config['preferences'].get('minimum_up_time', 10)
        self.cool_down_time = config['preferences'].get('cool_down_time', 30)
        self.relay_status = "off"
        self._stop_thread = threading.Event()

        # Setup GPIO for relay
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

        logger.info(f"🌀 Dust Collector '{self.label}' initialized on board {self.board_id}, pin {self.pin}")

        self.thread = threading.Thread(target=self._manage_collector)
        self.thread.start()

    def _manage_collector(self):
        """Manage the dust collector relay based on the status."""
        while not self._stop_thread.is_set():
            if self.relay_status == "on":
                time.sleep(self.minimum_up_time)
                self.turn_off()
            time.sleep(1)

    def turn_on(self):
        if self.relay_status != "on":
            self.relay_status = "on"
            GPIO.output(self.pin, GPIO.HIGH)
            logger.debug(f"🌀 Dust Collector '{self.label}' turned on")

    def turn_off(self):
        if self.relay_status != "off":
            self.relay_status = "off"
            GPIO.output(self.pin, GPIO.LOW)
            logger.debug(f"🌀 Dust Collector '{self.label}' turned off")

    def cleanup(self):
        """Stop the thread and clean up GPIO resources."""
        self._stop_thread.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            logger.warning(f"Dust Collector '{self.label}' thread did not stop within the timeout period.")
        GPIO.cleanup(self.pin)
        logger.info(f"🧹 Cleaned up GPIO for Dust Collector '{self.label}'")
