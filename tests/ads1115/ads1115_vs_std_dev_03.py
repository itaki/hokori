import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

# Constants
NUM_SAMPLES = 50
PERCENTAGE_THRESHOLD = 0.20  # Threshold as a percentage of the mean off reading

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

# Gather initial "off" readings and calculate mean
def gather_off_readings(channel, num_samples=NUM_SAMPLES):
    # Discard initial readings to allow the sensor to settle
    for _ in range(num_samples):
        read_current(channel)
    
    off_readings = []
    for _ in range(num_samples):
        off_readings.append(read_current(channel))
    mean_off_current = sum(off_readings) / len(off_readings)
    return mean_off_current

# Main function to monitor the appliance
def monitor_appliance(channel, off_current, percentage_threshold=PERCENTAGE_THRESHOLD, sample_size=NUM_SAMPLES):
    while True:
        current_readings = [read_current(channel) for _ in range(sample_size)]
        max_current = max(current_readings)
        threshold = off_current * (1 + percentage_threshold)
        
        if max_current > threshold:
            print(f"Appliance is ON (Max Current: {max_current:.2f} A, Threshold: {threshold:.2f} A)")
        else:
            print(f"Appliance is OFF (Max Current: {max_current:.2f} A, Threshold: {threshold:.2f} A)")

        time.sleep(0.1)  # Adjust the delay as necessary

if __name__ == "__main__":
    print("Gathering off readings...")
    off_current = gather_off_readings(ADS.P0)
    print(f"Off current baseline: {off_current:.2f} A")
    print("Monitoring appliance...")
    monitor_appliance(ADS.P0, off_current=off_current)
