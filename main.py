import time 

from gpiozero import LED, RGBLED, Button, DigitalOutputDevice
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import voltage_sensor as vs
from device_manager import Device_Manager
from gate_manager import Gate_Manager
from blinky_bits import get_full_path, hex_to_int

# create some list of stuff I got
DEVICE_FILE = 'devices.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'

tm = Device_Manager(DEVICE_FILE, BACKUP_DIR)
gm = Gate_Manager(GATES_FILE, BACKUP_DIR) # create the gate manager

# set which interfaces to use

use_gui = False
use_keyboard = False

if use_gui: 
    import pg_gui as pg_gui
    pg_gui = pg_gui.PG_GUI()
    gui_buttons = create_tool_gui_buttons()
    gate_buttons = create_gate_gui_buttons()


################################################################################
# START APP HERE
################################################################################


run = True

if __name__ == '__main__':
    while run:


        if use_voltage:
            tools_with_sensor = vs.get_tools_with_sensor(tm.tools)
            

        # run through all the tools to see if they are on
        shop_manager()
    
pygame.quit()
