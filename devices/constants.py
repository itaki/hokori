# devices/constants.py

import adafruit_ads1x15.ads1115 as ADS

# Mapping of pin numbers to ADS constants
ADS_PIN_NUMBERS = {
    0: ADS.P0, 
    1: ADS.P1, 
    2: ADS.P2, 
    3: ADS.P3
}

# Mapping of version to sensitivity values for ACS712
VERSION_SENSITIVITY_MAP = {
    "5 amp": 0.185,  # Sensitivity for 5A model (185mV/A)
    "20 amp": 0.100,  # Sensitivity for 20A model (100mV/A)
    "30 amp": 0.066  # Sensitivity for 30A model (66mV/A)
}

# Sample size for standard deviation calculation
SAMPLE_SIZE = 10