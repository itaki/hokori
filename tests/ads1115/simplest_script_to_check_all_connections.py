import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the ADS1115 at address 0x49
ads = ADS1115(i2c, address=0x49)

# Define the four channels
channels = [AnalogIn(ads, i) for i in range(4)]

def read_and_print_channels():
    while True:
        for i, channel in enumerate(channels):
            print(f"Channel {i}: {channel.voltage:.6f} V")
        print("-" * 40)
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        read_and_print_channels()
    except KeyboardInterrupt:
        print("Script stopped by user.")
