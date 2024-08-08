from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
import adafruit_ads1x15.ads1115 as ADS
from adafruit_bus_device.i2c_device import I2CDevice

class Hub:
    def __init__(self, config, i2c):
        self.id = config.get('id', 'unknown')
        self.label = config.get('label', 'unknown')
        self.version = config.get('version', 1)
        self.i2c = i2c

        try:
            self.gpio_expander = self.initialize_gpio_expander(config['gpio_expander'])
            self.pwm_servo = self.initialize_pwm_servo(config['pwm_servo'])
            self.pwm_led = self.initialize_pwm_led(config['pwm_led'])
            self.ad_converter = self.initialize_ad_converter(config['ad_converter'])
        except KeyError as e:
            print(f"Configuration error: missing key {e} in hub configuration for {self.label}")
        except ValueError as e:
            print(f"I2C device error for hub {self.label}: {e}")
        except Exception as e:
            print(f"Unexpected error initializing hub {self.label}: {e}")

    def initialize_gpio_expander(self, config):
        try:
            address = int(config['i2c_address'], 16)
            self.probe_i2c_device(address)
            return MCP23017(self.i2c, address=address)
        except KeyError as e:
            raise KeyError(f"Missing key {e} in gpio_expander configuration")
        except Exception as e:
            raise Exception(f"Error initializing MCP23017: {e}")

    def initialize_pwm_servo(self, config):
        try:
            address = int(config['i2c_address'], 16)
            self.probe_i2c_device(address)
            pwm = PCA9685(self.i2c, address=address)
            pwm.frequency = 50  # Set the frequency to 50hz, adjust as needed
            return pwm
        except KeyError as e:
            raise KeyError(f"Missing key {e} in pwm_servo configuration")
        except Exception as e:
            raise Exception(f"Error initializing PCA9685: {e}")

    def initialize_pwm_led(self, config):
        try:
            address = int(config['i2c_address'], 16)
            self.probe_i2c_device(address)
            pwm = PCA9685(self.i2c, address=address)
            pwm.frequency = 1000  # Set the frequency to 1000hz for LEDs
            return pwm
        except KeyError as e:
            raise KeyError(f"Missing key {e} in pwm_led configuration")
        except Exception as e:
            raise Exception(f"Error initializing PCA9685 for LEDs: {e}")

    def initialize_ad_converter(self, config):
        try:
            address = int(config['i2c_address'], 16)
            self.probe_i2c_device(address)
            return ADS.ADS1115(self.i2c, address=address)
        except KeyError as e:
            raise KeyError(f"Missing key {e} in ad_converter configuration")
        except Exception as e:
            raise Exception(f"Error initializing ADS1115: {e}")

    def probe_i2c_device(self, address):
        try:
            with I2CDevice(self.i2c, address):
                pass  # Device found
        except ValueError:
            raise ValueError(f"No I2C device found at address: 0x{address:02X}")

    def initialize_components(self):
        # Initialization logic for the components if needed
        pass

# Example usage:
if __name__ == "__main__":
    import json
    import board
    import busio

    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize hubs from config
    hubs = [Hub(device, i2c) for device in config['hubs']]

    # Print initialized hubs for verification
    for hub in hubs:
        print(f"Initialized hub: {hub.label} (ID: {hub.id}, Version: {hub.version})")
