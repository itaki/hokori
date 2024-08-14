import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

logger = logging.getLogger(__name__)

class ADS1115:
    def __init__(self, i2c, config):
        self.i2c_address = int(config['i2c_address'], 16)
        self.ads = ADS.ADS1115(i2c, address=self.i2c_address)
        logger.info(f"Initialized ADS1115 at address {hex(self.i2c_address)}")
        print('ahdkahsdfkhakhfekuauusehasuehfahsef')

        # Setting up channels
        self.channels = {
            0: AnalogIn(self.ads, ADS.P0),
            1: AnalogIn(self.ads, ADS.P1),
            2: AnalogIn(self.ads, ADS.P2),
            3: AnalogIn(self.ads, ADS.P3)
        }

    def read_voltage(self, channel):
        """Reads the voltage from the specified channel (0-3)."""
        if channel in self.channels:
            voltage = self.channels[channel].voltage
            logger.debug(f"Read voltage: {voltage} from channel: {channel}")
            return voltage
        else:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are 0-3.")

    def read_raw_value(self, channel):
        """Reads the raw ADC value from the specified channel (0-3)."""
        if channel in self.channels:
            raw_value = self.channels[channel].value
            logger.debug(f"Read raw value: {raw_value} from channel: {channel}")
            return raw_value
        else:
            raise ValueError(f"Invalid channel: {channel}. Valid channels are 0-3.")
