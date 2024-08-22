import time
import threading
import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

# Constants
NUM_SAMPLES = 50
SAMPLES_PER_CYCLE = 10
THESHOLD_MULTIPLIER = 4  # Threshold as a percentage of the mean off reading
ADS_PIN_NUMBERS = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}

logger = logging.getLogger(__name__)

class Voltage_Sensor:
    def __init__(self, volt_config, ads, status_callback):
        self.label = volt_config.get('label', 'unknown')
        self.board_name = volt_config['connection']['board']
        self.ads = ads
        self.pin_number = int(ADS_PIN_NUMBERS[volt_config['connection']['pins'][0]])
        self.multiplier = float(volt_config.get('multiplier', 1.003))  # Default to 1.003 if not provided
        self.samples_per_cycle = SAMPLES_PER_CYCLE
        self.threshold_muliplier = float(volt_config.get('threshold_multiplier', THESHOLD_MULTIPLIER))
        self.min_threshold = None
        self.max_threshold = None
        self.sensor_exists = True
        self.board_exists = ads is not None
        self.readings = []
        self.lock = threading.Lock()
        self._stop_thread = False
        self.status_callback = status_callback

        try:
            self.chan = AnalogIn(self.ads, self.pin_number)  # Pass the ADS1115 instance to AnalogIn
            self.board_exists = True
            logger.debug(f"🚥 ⚡︎ Adding Voltage Sensor on pin {self.pin_number} on ADS1115")
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
                logger.error(f"💢 ⚡︎ Error reading voltage: {e}")
                return None
        return None

    def gather_off_readings(self):
        off_readings = []
        sampled_cycles = []
        sampled_mins = []
        sampled_maxs = []

        for _ in range(NUM_SAMPLES):
            for _ in range(self.samples_per_cycle):
                reading = self.get_reading()
                if reading is not None:
                    off_readings.append(reading)
            sampled_cycles.append(sum(off_readings) / len(off_readings))
            sampled_mins.append(min(off_readings))
            sampled_maxs.append(max(off_readings))
        
        self.off_average = statistics.mean(sampled_cycles)
        self.absolute_min = min(sampled_mins)
        self.absolute_max = max(sampled_maxs)
        logger.debug(f"🚥 ⚡︎ Off readings: Mean of sampled cycles: {self.off_average}. "
                     f"Absolute Min: {self.absolute_min}, Absolute Max: {self.absolute_max}")

    def set_trigger_thresholds(self):
        self.min_threshold = self.absolute_min - ((self.off_average - self.absolute_min) * self.threshold_muliplier)
        self.max_threshold = self.absolute_max + ((self.absolute_max - self.off_average) * self.threshold_muliplier)
        logger.debug(f"🚥 ⚡︎ Thresholds set: Min: {self.min_threshold}, Max: {self.max_threshold}")

    def monitor_appliance(self):
        current_readings = []
        while not self._stop_thread:
            reading = self.get_reading()
            if reading is not None:
                current_readings.append(reading)
            if len(current_readings) > self.samples_per_cycle:
                current_readings.pop(0)

            if min(current_readings) < self.min_threshold or max(current_readings) > self.max_threshold:
                self.status_callback("on")
                #logger.debug(f"🚥 ⚡︎ {self.label} is ON {min(current_readings)} - max: {max(current_readings)}")
            else:
                self.status_callback("off")
                #logger.debug(f"🚥 ⚡︎ {self.label} is OFF {min(current_readings)} - max: {max(current_readings)}")

            time.sleep(0.1)

    def stop(self):
        self._stop_thread = True
        self.thread.join()

# Main loop for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Define Miter Saw voltage sensor configuration
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

    # Initialize I2C bus and ADS1115
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c, address=0x48)  # Replace with the correct I2C address for your ADS1115

    # Status callback function
    def status_callback(status):
        pass
        #print(f"Appliance status: {status}")

    # Initialize and run the Voltage_Sensor
    voltage_sensor = Voltage_Sensor(volt_config, ads, status_callback)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        voltage_sensor.stop()
        print("Voltage sensor test completed and cleaned up.")
