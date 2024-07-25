import json
import time
import get_full_path
from datetime import datetime
import questionary as q
import shutil #allows for copying a file to make a backup
import os
from styles import custom_style_dope
import blinky_bits as bb
import errno
from adafruit_servokit import ServoKit
from gpiozero import LED, RGBLED, Button
import blinky_bits
kit = ServoKit(channels=16)

#style the questions
style = custom_style_dope
gates_file = 'gates.json'
tools_file = 'tools.json'
backup_directory = '_BU'
force_backup = True


if __name__ == "__main__":
    tools = bb.get_tools('tools.json')
    gates = bb.get_gates('gates.json')
    print (len(gates))
    print (tools['TableSaw'].name)
    

import time
import blinky_bits as bb
import pygame
from gpiozero import LED, RGBLED, Button
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from _drop.gate_creator_decommissioned import Gate_manager


# create some list of shit I got
TOOLS_FILE = 'tools.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'

use_gui = True
use_buttons = False
use_voltage = False
use_gates = True

class Shop_manager():

    use_gui = use_gui
    use_buttons = use_buttons
    use_voltage = use_voltage
    use_gates = use_gates

    def init(self):
        '''SHOP MANAGER'''


        if use_gui: 
            '''intitalizes pygame canvas'''
            pygame.init()

            screen_width = 400
            screen_height = 480
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption('BLINKY')

            gates_width = 60
            terminal_height = 40
            num_of_tool_buttons_x = 3
            button_panel_width = screen_width-gates_width
            button_width = ((screen_width-gates_width)/num_of_tool_buttons_x)
            button_height = (screen_height-terminal_height) / \
                            (num_of_buttons/num_of_tool_buttons_x)
            gate_width = gate_height = (screen_height-terminal_height)/num_of_gates

            bg = '#16171d'
            # red = '#19d1e5'
            # black = (0, 0, 0)
            # white = (255, 255, 255)
            clicked = False

        if use_voltage:
            '''this activates the ADS1115 and talks to the AC715'''
            # Create the I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Create the ADC object using the I2C bus
            ads = ADS.ADS1115(i2c)

            cycles = 0 # sets the number of cycles to 0
            review_cycles = 6 # number of cycles the voltage has to drop below the trigger to confirm the tool is off

gm = Gate_manager(GATES_FILE, BACKUP_DIR)
