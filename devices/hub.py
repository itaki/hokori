import json
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pca9685 import PCA9685
from adafruit_ads1x15.ads1115 import ADS1115

class Hub:
    def __init__(self, hub_config):
        self.type = hub_config['type']
        self.label = hub_config['label']
        self.id = hub_config['id']
        self.version = hub_config['version']

        # Initialize I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize devices based on the configuration
        self.gpio_expander = self.init_gpio_expander(hub_config['gpio_expander'])
        self.pwm_servo = self.init_pwm_servo(hub_config['pwm_servo'])
        self.ad_converter = self.init_ad_converter(hub_config['ad_converter'])

    def init_gpio_expander(self, gpio_expander_config):
        address = int(gpio_expander_config['i2c_address'], 16)
        return MCP23017(self.i2c, address=address)

    def init_pwm_servo(self, pwm_servo_config):
        address = int(pwm_servo_config['i2c_address'], 16)
        pca = PCA9685(self.i2c, address=address)
        pca.frequency = 60  # Set frequency to 60hz, suitable for servos
        return pca

    def init_ad_converter(self, ad_converter_config):
        address = int(ad_converter_config['i2c_address'], 16)
        return ADS1115(self.i2c, address=address)

    @staticmethod
    def from_json(json_str):
        hub_config = json.loads(json_str)
        return Hub(hub_config)

# Example usage
if __name__ == "__main__":
    hub_json = '''
    {
        "type": "hub",
        "label": "Main Hub",
        "id": "main-hub",
        "version": 1,
        "gpio_expander": {
            "type": "MCP23017",
            "i2c_address": "0x20"
        },
        "pwm_servo": {
            "type": "PCA9685",
            "i2c_address": "0x42"
        },
        "ad_converter": {
            "type": "ADS1115",
            "i2c_address": "0x49"
        }
    }
    '''
    hub = Hub.from_json(hub_json)
    print(f"Hub {hub.label} with ID {hub.id} initialized.")