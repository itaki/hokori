import time
import threading
import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Constants
NUM_SAMPLES = 50
SENSOR_DETECTION_THRESHOLD = 1.6
ERROR_THRESHOLD = 2.5
TRIGGER_THRESHOLD = 1.003
ADS_PIN_NUMBERS = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}

logger = logging.getLogger(__name__)



class Voltage_Sensor:
    def __init__(self, volt_config, ads, status_callback):
        self.label = volt_config.get('label', 'unknown')
        self.board_name = volt_config['connection']['board']
        self.ads = ads
        self.pin_number = int(ADS_PIN_NUMBERS[volt_config['connection']['pins'][0]])
        self.sensor_detection_threshold = SENSOR_DETECTION_THRESHOLD
        self.error_threshold = ERROR_THRESHOLD
        self.min_readings = NUM_SAMPLES
        self.readings = []
        self.error_raised = False
        self.sensor_exists = True
        self.board_exists = ads is not None
        self.reading = 0  # Initialize self.reading
        self.trigger = None
        self.lock = threading.Lock()
        self._stop_thread = False
        self.status_callback = status_callback


        try:
            self.chan = AnalogIn(self.ads, self.pin_number)  # Pass the ADS1115 instance to AnalogIn
            self.board_exists = True
            logger.info(f"Adding Voltage Sensor on pin {self.pin_number} on ADS1115")
            reading = self.get_reading()
            logger.info(f"Current voltage reading is {reading}")
            self.set_trigger_voltage()
            self.thread = threading.Thread(target=self.collect_readings)
            self.thread.start()
        except Exception as e:
            logger.error(f"Failed to initialize Voltage Sensor for {self.label}: {e}")
            self.board_exists = False

        print(f"Type of self.chan: {type(self.chan)}")  # Should be <class 'adafruit_ads1x15.analog_in.AnalogIn'>


    def get_reading(self):
        if self.board_exists and not self.error_raised:
            try:
                reading = self.chan.voltage
                with self.lock:
                    self.readings.append(reading)
                    if len(self.readings) > self.min_readings:
                        self.readings.pop(0)
                    max_reading = max(self.readings)
                    self.reading = max_reading  # Store the max reading in self.reading
                return max_reading
            except AttributeError as e:
                logger.error(f"Attribute error while reading voltage: {e}")
                self.error_raised = True
                return 0
            except OSError as e:
                logger.error(f"I2C communication error: {e}")
                return 0
            except Exception as e:
                logger.error(f"Unexpected error while reading voltage: {e}")
                return 0
        else:
            return 0

    def collect_readings(self):
        while not self._stop_thread:
            self.get_reading()
            self.update_status()
            time.sleep(0.001)

    def in_good_range(self):
        if self.sensor_detection_threshold < self.reading < self.error_threshold:
            self.error_raised = False
            self.sensor_exists = True
            return True
        elif not self.error_raised:
            self.error_raised = True
            if self.sensor_detection_threshold > self.reading:
                logger.warning(f"No sensor on pin {self.pin_number}")
            if self.reading > self.error_threshold:
                logger.warning(f"Problem with sensor on pin {self.pin_number}")
        self.sensor_exists = False
        return False

    def am_i_on(self):
        if self.board_exists:
            reading = self.reading
            if self.in_good_range() and self.sensor_exists:
                return reading > self.trigger
            elif self.in_good_range():
                self.set_trigger_voltage()
                return self.am_i_on()
            else:
                return False
        else:
            return False

    def set_trigger_voltage(self):
        reading = self.reading  # Use the already initialized self.reading
        if self.in_good_range():
            self.trigger = reading * TRIGGER_THRESHOLD
            logger.info(f"Setting trigger point on pin {self.pin_number} to {self.trigger}")

    def update_status(self):
        status = "on" if self.am_i_on() else "off"
        self.status_callback(status)

    def stop(self):
        self._stop_thread = True
        self.thread.join()


