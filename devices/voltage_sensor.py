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
    def __init__(self, volt_config, i2c):
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
        self.status = 'off'
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

        if current_max > self.trigger:
            self.status = 'on'
        else:
            self.status = 'off'

        if self.status != self.last_status:
            logger.debug(f" {self.label} Voltage Sensor: {self.status}")
            self.last_status = self.status

    def am_i_on(self):
        return self.status == 'on'

    def stop(self):
        self.stop_event.set()
        self.thread.join()

# Example usage
if __name__ == "__main__":
    # Example config for testing
    volt_config = {
        "label": "VS for test",
        "version": "20 amp",
        "voltage_address": {
            "board_address": "0x49",
            "pin": 0
        },
        "multiplier": 3
    }

    i2c = busio.I2C(board.SCL, board.SDA)

    # Create an instance of Voltage_Sensor
    voltage_sensor = Voltage_Sensor(volt_config, i2c)

    try:
        while True:
            status = voltage_sensor.am_i_on()
            logger.debug(f"Voltage Sensor status is {status}")
            time.sleep(1)
    except KeyboardInterrupt:
        voltage_sensor.stop()
        logger.info("Test interrupted by user")
