import os
import json
import board
import busio
import time
import math

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Import module for ADS1115
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ads_pin_numbers = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}

class Voltage_Sensor:
    def __init__(self, volt, sample_size=100):
        if 'voltage_address' not in volt:
            raise ValueError("Missing 'voltage_address' in voltage sensor configuration")
        
        self.board_address = volt['voltage_address']['board_address']
        self.pin_number = ads_pin_numbers[volt['voltage_address']['pin']]
        self.sensitivity = volt['sensitivity']
        self.sample_size = sample_size
        self.readings = []
        self.board_exists = None
        self.sensor_exists = False
        self.std_dev_threshold = None

        try:
            self.ads = ADS.ADS1115(i2c, address=self.board_address)
            self.chan = AnalogIn(self.ads, self.pin_number)
            self.board_exists = True
            print(f"⚡ Adding Voltage Sensor on pin {self.pin_number} on ADS1115 at address {hex(self.board_address)}")
            self.initialize_std_dev_threshold()
        except Exception as e:
            print(f"■■■■■ ERROR! ■■■■■■  ADS11x5 not found at {hex(self.board_address)}. Cannot create voltage sensor: {e}")
            self.board_exists = False

    def get_reading(self):
        '''Gets a new reading from the sensor'''
        if self.board_exists:
            try:
                reading = self.chan.voltage
                self.readings.append(reading)
                if len(self.readings) > self.sample_size:
                    self.readings.pop(0)
                return reading
            except Exception as e:
                print(f"ERROR GETTING READING FROM {hex(self.board_address)} at PIN {self.pin_number}: {e}")
                return 0
        return 0

    def calculate_std_dev(self):
        '''Calculates the standard deviation of the readings'''
        if len(self.readings) == 0:
            return 0
        mean = sum(self.readings) / len(self.readings)
        variance = sum((x - mean) ** 2 for x in self.readings) / len(self.readings)
        std_dev = math.sqrt(variance)
        return std_dev

    def initialize_std_dev_threshold(self):
        '''Initializes the standard deviation threshold based on initial readings when the tool is assumed to be OFF'''
        initial_readings = []
        for _ in range(self.sample_size):
            initial_readings.append(self.get_reading())

        initial_std_dev = self.calculate_std_dev()
        self.std_dev_threshold = initial_std_dev * self.sensitivity
        print(f"Initialized standard deviation threshold to {self.std_dev_threshold}")

    def am_i_on(self):
        '''Determines if the device plugged into the sensor is currently on'''
        if not self.board_exists:
            return False
        self.get_reading()
        current_std_dev = self.calculate_std_dev()
        #print(f"Current std dev: {current_std_dev}, Threshold: {self.std_dev_threshold}")
        return current_std_dev > self.std_dev_threshold

def get_tools_with_sensor(tools):
    '''Returns a list of tools that have a voltage sensor'''
    tools_with_sensor = []
    for tool in tools.values():
        if hasattr(tool, 'voltage_sensor'):
            print(f"Tool {tool.name} has a voltage sensor")
            tools_with_sensor.append(tool.name)
        else:
            print(f"Tool {tool.name} does not have a voltage sensor")
    return tools_with_sensor

if __name__ == "__main__":
    pass
