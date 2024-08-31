import time
import threading
import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

# Constants
NUMBER_OF_OFF_READINGS = 50
NUMBER_OF_READINGS = 30
ACTIVATION_TRIGGER_PERCENT = 50
THRESHOLD_DEVIATION = 1.03
ADS_PIN_NUMBERS = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}

logger = logging.getLogger(__name__)

class Voltage_Sensor:
    def __init__(self, volt_config, ads, status_callback):
        self.label = volt_config.get('label', 'unknown')
        self.board_name = volt_config['connection']['board']
        self.ads = ads
        self.pin_number = int(ADS_PIN_NUMBERS[volt_config['connection']['pins'][0]])
        self.threshold_deviation = float(volt_config.get('deviation', THRESHOLD_DEVIATION))
        self.number_of_off_readings = NUMBER_OF_OFF_READINGS
        self.activation_trigger_number = ACTIVATION_TRIGGER_PERCENT * NUMBER_OF_READINGS / 100
        self.min_threshold = None
        self.max_threshold = None
        self.sensor_exists = True
        self.board_exists = ads is not None
        self.readings = []
        self.lock = threading.Lock()
        self._stop_thread = threading.Event()  # Using Event to stop thread
        self.status_callback = status_callback
        self.status = "off"

        try:
            self.chan = AnalogIn(self.ads, self.pin_number)
            self.board_exists = True
            logger.debug(f"      🚥 ⚡︎ Adding Voltage Sensor - {self.label} on {self.board_name} on pin {self.pin_number}")
            self.gather_off_readings()
            self.set_trigger_thresholds()
            self.thread = threading.Thread(target=self.monitor_appliance)
            self.thread.start()
        except Exception as e:
            logger.error(f"💢 ⚡︎ Failed to initialize Voltage Sensor for {self.label}: {e}")
            self.board_exists = False

    def get_reading(self):
        if self.board_exists:
            try:
                return self.chan.voltage
            except Exception as e:
                logger.error(f"💢 ⚡️ Error reading voltage: {self.label} on {self.board_name} at {self.pin_number} {e}")
                return None
        return None

    def gather_off_readings(self):
        off_readings = []
        for _ in range(self.number_of_off_readings):
            reading = self.get_reading()
            if reading is not None:
                off_readings.append(reading)
        self.off_average = statistics.mean(off_readings)
        logger.debug(f"      🚥 ⚡︎ Off readings for {self.label}: Mean of sampled cycles: {self.off_average}")

    def set_trigger_thresholds(self):
        self.min_threshold = self.off_average / self.threshold_deviation
        self.max_threshold = self.off_average * self.threshold_deviation
        logger.debug(f"      🚥 ⚡︎ Thresholds set: Min: {self.min_threshold}, Max: {self.max_threshold}")

    def monitor_appliance(self):
        current_readings = []
        while not self._stop_thread.is_set():
            reading = self.get_reading()
            triggers = 0
            if reading is not None:
                current_readings.append(reading)
            if len(current_readings) > self.number_of_off_readings:
                current_readings.pop(0)
            for reading in current_readings:
                if min(current_readings) < self.min_threshold or max(current_readings) > self.max_threshold:
                    triggers += 1
            if triggers >= self.activation_trigger_number:
                if self.status != "on":
                    self.status = "on"
                    self.status_callback("on")
                    logger.debug(f"      🚥 ⚡︎ {self.label} is ON {min(current_readings)} - max: {max(current_readings)}")
            else:
                if self.status != "off":
                    self.status = "off"
                    self.status_callback("off")
                    logger.debug(f"      🚥 ⚡︎ {self.label} is OFF {min(current_readings)} - max: {max(current_readings)}")
            time.sleep(0.1)

    def stop(self):
        self._stop_thread.set()  # Signal the thread to stop
        self.thread.join(timeout=5)  # Wait for the thread to finish with a timeout
        if self.thread.is_alive():
            logger.warning(f"Thread for voltage sensor {self.label} did not stop within the timeout period.")

# Main loop for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    volt_config = {
        "label": "VS for miter saw",
        "type": "ADS1115",
        "version": "20 amp",
        "connection": {
            "board": "master_control_ad_converter",
            "pins": [3]
        },
        "multiplier": "9"
    }

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c, address=0x48)

    def status_callback(status):
        print(f"Appliance status: {status}")

    voltage_sensor = Voltage_Sensor(volt_config, ads, status_callback)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        voltage_sensor.stop()
        print("Voltage sensor test completed and cleaned up.")
