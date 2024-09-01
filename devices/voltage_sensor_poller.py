import time
import threading
import logging

# Constants
ACTIVATION_TRIGGER_PERCENT = 50
NUMBER_OF_READINGS = 30
THRESHOLD_DEVIATION = 1.03

logger = logging.getLogger(__name__)

class VoltageSensorPoller:
    def __init__(self, ad_converter, sensors_config):
        if not ad_converter:
            raise ValueError("AD_Converter instance is required.")
        
        self.ad_converter = ad_converter
        self.sensors = []  # List to hold sensor configurations and states
        self._stop_thread = threading.Event()

        # Initialize sensors based on the provided configuration
        for volt_config in sensors_config:
            sensor = {
                'label': volt_config.get('label', 'unknown'),
                'pin_number': volt_config['connection']['pins'][0],
                'threshold_deviation': float(volt_config.get('deviation', THRESHOLD_DEVIATION)),
                'status_callback': volt_config.get('status_callback', lambda status: None),
                'status': 'off',
                'min_threshold': None,
                'max_threshold': None,
                'current_readings': [],
                'activation_trigger_number': ACTIVATION_TRIGGER_PERCENT * NUMBER_OF_READINGS / 100,
                'off_average': None
            }
            self.sensors.append(sensor)

        # Start polling in a separate thread
        self.thread = threading.Thread(target=self.poll_sensors)
        self.thread.start()

    def set_trigger_thresholds(self, sensor):
        """Set the min and max thresholds for each sensor based on off readings."""
        sensor['min_threshold'] = sensor['off_average'] / sensor['threshold_deviation']
        sensor['max_threshold'] = sensor['off_average'] * sensor['threshold_deviation']
        logger.debug(f"      🚥 ⚡︎ Thresholds set for {sensor['label']}: Min: {sensor['min_threshold']}, Max: {sensor['max_threshold']}")

    def gather_off_readings(self, sensor):
        """Gather initial off readings to calculate the average."""
        off_readings = []
        pin_number = sensor['pin_number']

        while len(self.ad_converter.readings[pin_number]) < NUMBER_OF_READINGS:
            time.sleep(0.1)  # Wait until enough readings are available

        for _ in range(NUMBER_OF_READINGS):
            reading = self.ad_converter.readings[pin_number][-1]
            off_readings.append(reading)
            time.sleep(0.01)  # Add slight delay between readings

        sensor['off_average'] = sum(off_readings) / len(off_readings)
        logger.debug(f"      🚥 ⚡︎ Off readings for {sensor['label']}: Mean of sampled cycles: {sensor['off_average']}")

    def poll_sensors(self):
        """Poll sensors, monitor readings, and trigger status updates."""
        for sensor in self.sensors:
            # Wait until there are enough readings
            while len(self.ad_converter.readings[sensor['pin_number']]) < NUMBER_OF_READINGS:
                time.sleep(0.1)

            # Once there are enough readings, gather the off readings and set thresholds
            self.gather_off_readings(sensor)
            self.set_trigger_thresholds(sensor)

        while not self._stop_thread.is_set():
            for sensor in self.sensors:
                pin_number = sensor['pin_number']

                # Check if there are enough readings; skip if not
                if len(self.ad_converter.readings[pin_number]) < NUMBER_OF_READINGS:
                    continue

                reading = self.ad_converter.readings[pin_number][-1]
                
                sensor['current_readings'].append(reading)
                if len(sensor['current_readings']) > NUMBER_OF_READINGS:
                    sensor['current_readings'].pop(0)

                triggers = sum(1 for r in sensor['current_readings'] if r < sensor['min_threshold'] or r > sensor['max_threshold'])

                if triggers >= sensor['activation_trigger_number']:
                    if sensor['status'] != "on":
                        sensor['status'] = "on"
                        sensor['status_callback']("on")
                        logger.debug(f"      🚥 ⚡︎ {sensor['label']} is ON (min: {min(sensor['current_readings'])}, max: {max(sensor['current_readings'])})")
                else:
                    if sensor['status'] != "off":
                        sensor['status'] = "off"
                        sensor['status_callback']("off")
                        logger.debug(f"      🚥 ⚡︎ {sensor['label']} is OFF (min: {min(sensor['current_readings'])}, max: {max(sensor['current_readings'])})")

            time.sleep(0.1)

    def stop(self):
        """Stop the polling thread."""
        self._stop_thread.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            logger.warning(f"VoltageSensorPoller did not stop within the timeout period.")
