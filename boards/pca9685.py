from adafruit_pca9685 import PCA9685 as Adafruit_PCA9685
from adafruit_servokit import ServoKit
import logging

logger = logging.getLogger(__name__)

class PCA9685:
    def __init__(self, i2c, config):
        self.i2c_address = int(config['i2c_address'], 16)
        self.mode = config.get('purpose', 'LED Control')  # Default to LED Control if not specified

        if self.mode == 'Servo Control':
            self.pca = ServoKit(channels=16, i2c=i2c)  # Initialize ServoKit for servo control
            frequency = config.get('frequency', 50)  # Get frequency from config, default to 50Hz for servo control
            self.set_frequency(frequency)
            logger.info(f"Initialized PCA9685 at address {hex(self.i2c_address)} in Servo Control mode with frequency {frequency}Hz")
        else:
            self.pca = Adafruit_PCA9685(i2c, address=self.i2c_address)  # Initialize PCA9685 for LED control
            frequency = config.get('frequency', 1000)  # Get frequency from config, default to 1000Hz for LED control
            self.set_frequency(frequency)
            logger.info(f"Initialized PCA9685 at address {hex(self.i2c_address)} in LED Control mode with frequency {frequency}Hz")

    @property
    def channels(self):
        """Expose channels from the underlying Adafruit_PCA9685 instance."""
        if self.mode == 'LED Control':
            return self.pca.channels
        return None

    def set_frequency(self, frequency):
        """Set the PWM frequency in Hz."""
        if self.mode == 'LED Control':
            self.pca.frequency = frequency
        elif self.mode == 'Servo Control':
            self.pca.frequency = frequency  # This sets the frequency for ServoKit, though typically 50Hz is standard.

    def set_pwm(self, channel, on, off):
        """Set the PWM on/off values for a specific channel."""
        if self.mode == 'LED Control':
            self.pca.channels[channel].duty_cycle = off

    def set_pwm_value(self, channel, value):
        """Set the PWM duty cycle as a 16-bit value (0-65535)."""
        if self.mode == 'LED Control':
            self.pca.channels[channel].duty_cycle = value

    def set_servo_angle(self, channel, angle):
        """Set the servo angle for a specific channel."""
        if self.mode == 'Servo Control':
            self.pca.servo[channel].angle = angle

