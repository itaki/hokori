import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ADDRESS = 0x48
GAIN = 1

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize ADS1115 at address 0x49
ads = ADS.ADS1115(i2c, address=ADDRESS, gain=GAIN)

# Create a single-ended input on channel 0 (P0)
chan = AnalogIn(ads, ADS.P0)

# Continuously read the voltage
try:
    while True:
        print(f"Voltage: {chan.voltage} V")
        time.sleep(.1)
except KeyboardInterrupt:
    print("Script interrupted by user.")
