import board
import busio
import logging
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import threading
import time

# Set up logging
logger = logging.getLogger(__name__)

# Constants
VERSION_SENSITIVITY_MAP = {
    "5 amp": 0.185,
    "20 amp": 0.100,
    "30 amp": 0.066
}
SAMPLE_SIZE = 50
TRIGGER_THRESHOLD = 1.003

class Voltage_Sensor:
    def __init__(self, volt_config, i2c, status_callback):
        self.label = volt_config.get('label', 'unknown')
        self.board_address = int(volt_config['voltage_address']['board_address'], 16)
        self.pin = volt_config['voltage_address']['pin']
        self.multiplier = volt_config.get('multiplier', 1)
        self.sensitivity = VERSION_SENSITIVITY_MAP[volt_config['version']]
        self.i2c = i2c
        self.ads = None
        self.chan = None
        self.std_dev_threshold = None
        self.readings = []
        self.trigger = None
        self.status_callback = status_callback
        self.last_status = 'off'

        self.initialize_sensor()
        self.initialize_std_dev_threshold()

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.monitor_voltage)
        self.thread.start()

    def initialize_sensor(self):
        try:
            self.ads = ADS1115(self.i2c, address=self.board_address)
            self.chan = AnalogIn(self.ads, self.pin)
            logger.debug(f"Voltage sensor {self.label} initialized at address {hex(self.board_address)} on pin {self.pin}")
        except Exception as e:
            logger.error(f"Error initializing voltage sensor {self.label}: {e}")

    def get_reading(self):
        if self.chan is not None:
            return self.chan.voltage
        return 0

    def calculate_std_dev(self):
        if len(self.readings) == 0:
            return 0
        mean = sum(self.readings) / len(self.readings)
        variance = sum((x - mean) ** 2 for x in self.readings) / len(self.readings)
        return variance ** 0.5

    def initialize_std_dev_threshold(self):
        initial_readings = [self.get_reading() for _ in range(SAMPLE_SIZE)]
        self.readings.extend(initial_readings)
        initial_std_dev = self.calculate_std_dev()
        self.std_dev_threshold = initial_std_dev * self.multiplier
        self.trigger = max(self.readings) * TRIGGER_THRESHOLD
        logger.debug(f"Initialized std_dev_threshold for {self.label}: {self.std_dev_threshold}")

    def monitor_voltage(self):
        while not self.stop_event.is_set():
            self.update_status()
            time.sleep(0.001)

    def update_status(self):
        current_read = self.get_reading()
        self.readings.append(current_read)
        if len(self.readings) > SAMPLE_SIZE:
            self.readings.pop(0)
        current_max = max(self.readings)

        new_status = 'on' if current_max > self.trigger else 'off'
        if new_status != self.last_status:
            logger.debug(f"{self.label} Voltage Sensor: {new_status}")
            self.status_callback(new_status)
            self.last_status = new_status

    def stop(self):
        self.stop_event.set()
        self.thread.join()
