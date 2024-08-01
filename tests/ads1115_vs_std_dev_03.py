import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the ADS1115 ADC (address 0x49)
ads = ADS.ADS1115(i2c, address=0x49)
ads.gain = 1

# Function to read current value from ACS712 sensor
def read_current(channel):
    # Create an AnalogIn object for the specified channel
    chan = AnalogIn(ads, channel)
    # Convert the ADC value to voltage (assuming a 5V reference)
    voltage = chan.voltage
    # ACS712-20A output sensitivity (100 mV/A)
    sensitivity = 0.100
    # Calculate the current in Amps
    current = (voltage - 2.5) / sensitivity
    return current

# Gather initial "off" readings and calculate mean and standard deviation
def gather_off_readings(channel, num_samples=10):
    off_readings = []
    for _ in range(num_samples):
        off_readings.append(read_current(channel))
    mean_off_current = sum(off_readings) / len(off_readings)
    stddev_off_current = statistics.stdev(off_readings)
    return mean_off_current, stddev_off_current

# Main function to monitor the appliance
def monitor_appliance(channel, off_current, stddev_off_current, stddev_multiplier=3, consecutive_threshold=5):
    threshold = stddev_off_current * stddev_multiplier
    on_counter = 0
    
    while True:
        current = read_current(channel)
        deviation = abs(current - off_current)
        
        if deviation > threshold:
            on_counter += 1
        else:
            on_counter = 0
        
        if on_counter >= consecutive_threshold:
            print(f"Appliance is ON (Current: {current:.2f} A, Deviation: {deviation:.2f} A, Baseline: {off_current:.2f} A, Threshold: {threshold:.2f} A)")
        else:
            print(f"Appliance is OFF (Current: {current:.2f} A, Deviation: {deviation:.2f} A, Baseline: {off_current:.2f} A, Threshold: {threshold:.2f} A)")

        time.sleep(0.001)

if __name__ == "__main__":
    print("Gathering off readings...")
    off_current, stddev_off_current = gather_off_readings(ADS.P0)
    print(f"Off current baseline: {off_current:.2f} A")
    print(f"Off current standard deviation: {stddev_off_current:.2f} A")
    print("Monitoring appliance...")
    monitor_appliance(ADS.P0, off_current=off_current, stddev_off_current=stddev_off_current)
