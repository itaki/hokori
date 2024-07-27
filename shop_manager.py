import json
from datetime import datetime
import questionary as q
import shutil #allows for copying a file to make a backup
import os
from curses_styles import custom_style_dope
import blinky_bits as bb
import errno
from adafruit_servokit import ServoKit
from gpiozero import LED, RGBLED, Button
import blinky_bits
kit = ServoKit(channels=16)


import time
import blinky_bits as bb
import pygame
from gpiozero import LED, RGBLED, Button
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gate_manager import Gate_Manager


# create some list of shit I got
TOOLS_FILE = 'tools.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'

use_gui = True
use_buttons = False
use_voltage = False
use_gates = True

class Shop_manager():

    def check_tools():
        '''the shop manager takes the tools list and checks each one to see what it needs to do'''
        for tool in tm.tools:
            current_tool = tm.tools[tool]
            if current_tool.flagged == True:  # if a tool has been flagged make sure to address it
            
                if current_tool.status == 'on':
                    if current_tool.spin_down_time >= 0:
                        rosie.spinup()
                    gate_settings = get_gate_settings(tm.tools)  # this need to be a shop_manager method that talks to tools and then tells gm what to do
                    gm.set_gates(gate_settings)
                    current_tool.flagged = False
                    if current_tool.spin_down_time < 0:  # use -1 to not turn tool on at all
                        current_tool.status = 'off'

                elif current_tool.status == 'off':
                    opengates = get_gate_settings(tm.tools) 
                    tools_on = tools_in_use()
                    if tools_on: 
                        print(f'There are tools in use {tools_on}')
                        gm.set_gates(opengates)                  
                    else:
                        print(f'There are NO tools in use ')  # check to see if any tools are on
                        rosie.shutdown()
                    current_tool.flagged = False
            
            if current_tool.status == 'spindown':
                uptime = rosie.uptime()
                purge_time = time.time() - current_tool.last_used
                if uptime < rosie.min_uptime:
                    pass            
                elif purge_time > current_tool.spin_down_time:
                    current_tool.turn_off()

    def tools_in_use():
        tools_on = []
        for tool in tm.tools:
            current_tool = tm.tools[tool]
            if current_tool.status != 'off':
                tools_on.append(current_tool.name)
                print(f'{current_tool.name} which is tool {current_tool.id_num}' )
        return tools_on

    for tool in tools_with_sensor:
                selected_tool = tm.tools[tool]
                if selected_tool.override == False:
                    am_i_on = tm.tools[tool].voltage_sensor.am_i_on()
                    if am_i_on and tm.tools[tool].status != 'on':
                        tm.tools[tool].turn_on()
                    elif not am_i_on and tm.tools[tool].status == 'on':
                        tm.tools[tool].spindown()