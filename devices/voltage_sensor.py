import time
import threading
import logging
import statistics

# Constants
NUMBER_OF_OFF_READINGS = 50
NUMBER_OF_READINGS = 30
ACTIVATION_TRIGGER_PERCENT = 50
THRESHOLD_DEVIATION = 1.03
BREATH_BETWEEN_READINGS = 0.1

logger = logging.getLogger(__name__)

class VoltageSensor:
    def __init__(self, config, ads):
        self.label = config.get('label', 'Unknown Voltage Sensor')
        self.pin = config['connection']['pin']
        self.ads = ads  # This should be the instance of ADS1115
        self.threshold_deviation = float(config.get('preferences', {}).get('deviation', THRESHOLD_DEVIATION))
        self.activation_trigger_number = ACTIVATION_TRIGGER_PERCENT * NUMBER_OF_READINGS / 100
        self.status_callback = None
        self.status = "off"
        self.off_average = None
        self.min_threshold = None
        self.max_threshold = None
        self.current_readings = []

        # Thread and synchronization setup
        self.lock = threading.Lock()
        self._stop_thread = threading.Event()

        try:
            logger.debug(f"      🚥 ⚡︎ Adding Voltage Sensor - {self.label} on pin {self.pin}")
            self.gather_off_readings()
            self.set_trigger_thresholds()
            self.thread = threading.Thread(target=self.monitor_appliance, daemon=True)
            self.thread.start()
        except Exception as e:
            logger.error(f"💢 ⚡︎ Failed to initialize Voltage Sensor for {self.label}: {e}")

    def gather_off_readings(self):
        """Collect initial off readings to establish a baseline."""
        while True:
            readings = self.ads.get_readings(self.pin)
            if len(readings) >= NUMBER_OF_OFF_READINGS:
                off_readings = readings[-NUMBER_OF_OFF_READINGS:]  # Take the last NUMBER_OF_OFF_READINGS readings
                self.off_average = statistics.mean(off_readings)
                logger.debug(f"      🚥 ⚡︎ Off readings for {self.label}: Mean of sampled cycles: {self.off_average}")
                break
            else:
                logger.debug(f"      🚥 ⚡︎ Waiting for enough readings for {self.label}, currently have {len(readings)}")
                time.sleep(1)
        
        if not self.off_average:
            logger.error(f"💢 ⚡︎ No valid off readings collected for {self.label}")


    def set_trigger_thresholds(self):
        """Set thresholds for triggering based on off readings."""
        if self.off_average:
            self.min_threshold = self.off_average / self.threshold_deviation
            self.max_threshold = self.off_average * self.threshold_deviation
            logger.debug(f"      🚥 ⚡︎ Thresholds set: Min: {self.min_threshold}, Max: {self.max_threshold}")

    def monitor_appliance(self):
        """Continuously monitor the voltage sensor and update status."""
        while not self._stop_thread.is_set():
            readings = self.ads.get_readings(self.pin)
            if readings:
                with self.lock:
                    self.current_readings.extend(readings)
                    if len(self.current_readings) > NUMBER_OF_READINGS:
                        self.current_readings = self.current_readings[-NUMBER_OF_READINGS:]

                triggers = sum(1 for r in self.current_readings if r < self.min_threshold or r > self.max_threshold)
                new_status = "on" if triggers >= self.activation_trigger_number else "off"

                if new_status != self.status:
                    self.status = new_status
                    if self.status_callback:
                        self.status_callback(self.status)
                    logger.debug(f"      🚥 ⚡︎ {self.label} is {self.status.upper()}")

            time.sleep(BREATH_BETWEEN_READINGS)

    def stop(self):
        """Stop the monitoring thread."""
        self._stop_thread.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            logger.warning(f"Thread for voltage sensor {self.label} did not stop within the timeout period.")
        logger.debug(f"      🛑 Voltage sensor {self.label} stopped cleanly.")

    def set_status_callback(self, callback):
        """Set the callback function for status changes."""
        self.status_callback = callback
