import time 
import json
import os
import logging

from device_manager import Device_Manager
from gate_manager import Gate_Manager

# create some list of stuff I got
DEVICE_FILE = 'config.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'

# set logging level
#LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(level=LOG_LEVEL)

# Determine the directory where main.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the location of config.json based on the current directory
config_path = os.path.join(current_dir, DEVICE_FILE)
gates_path = os.path.join(current_dir, GATES_FILE)

dm = Device_Manager(config_path) # create the device manager
#gm = Gate_Manager(gates_path) # create the gate manager


# set which interfaces to use

use_gui = False
use_keyboard = False
use_buttons = True
use_voltage = False
use_gates = False



################################################################################
# START APP HERE
################################################################################


run = False

if __name__ == '__main__':
    while run:
        pass

    

