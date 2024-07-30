import time
import _drop.blinky_bits as blinky_bits
import pygame
from pygame.locals import *
from gpiozero import LED, RGBLED, Button, DigitalOutputDevice
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from _drop.device_manager_BU import Tool_Manager
import voltage_sensor as vs
from gate_manager import Gate_Manager, get_full_path
import pygame.pg_gui as pg_gui

TOOLS_FILE = 'tools.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'

tm = Tool_Manager(TOOLS_FILE, BACKUP_DIR)
gm = Gate_Manager(GATES_FILE, BACKUP_DIR)

use_gui = True
use_buttons = False
use_voltage = True
use_collector = True

if use_voltage:
    i2c = busio.I2C(board.SCL, board.SDA)

class Dust_collector:
    def __init__(self, pin, min_uptime):
        self.status = 'off'
        self.last_spin_up = time.time()
        self.min_uptime = min_uptime
        self.relay = DigitalOutputDevice(pin, active_high=True, initial_value=False)

    def spinup(self):
        if self.status == 'on':
            pass
        elif self.status == 'off':
            self.status = 'on'
            self.relay.on()
            self.last_spin_up = time.time()

    def shutdown(self):
        if self.status != 'off':
            self.relay.off()
            self.status = 'off'

    def uptime(self):
        uptime = time.time() - self.last_spin_up
        return uptime

def tools_in_use():
    tools_on = []
    for tool in tm.tools:
        current_tool = tm.tools[tool]
        if current_tool.status != 'off':
            tools_on.append(current_tool.name)
            print(f'{current_tool.name} which is tool {current_tool.id_num}' )
    return tools_on

def get_gate_settings(tools):
    open_gates = []
    for t in tools:
        current_tool = tools[t]
        if current_tool.status != 'off':
            for gate_pref in current_tool.gate_prefs:
                if gate_pref not in open_gates:
                    open_gates.append(gate_pref)
    return open_gates

def shop_manager():
    for tool in tm.tools:
        current_tool = tm.tools[tool]
        if current_tool.flagged == True:
            if current_tool.status == 'on':
                if current_tool.spin_down_time >= 0:
                    rosie.spinup()
                gate_settings = get_gate_settings(tm.tools)
                gm.set_gates(gate_settings)
                current_tool.flagged = False
                if current_tool.spin_down_time < 0:
                    current_tool.status = 'off'
            elif current_tool.status == 'off':
                opengates = get_gate_settings(tm.tools)
                tools_on = tools_in_use()
                if tools_on:
                    print(f'There are tools in use {tools_on}')
                    gm.set_gates(opengates)
                else:
                    print(f'There are NO tools in use ')
                    rosie.shutdown()
                current_tool.flagged = False
        if current_tool.status == 'spindown':
            uptime = rosie.uptime()
            purge_time = time.time() - current_tool.last_used
            if uptime < rosie.min_uptime:
                pass
            elif purge_time > current_tool.spin_down_time:
                current_tool.turn_off()

min_uptime = 10
used_pins = tm.get_used_pins()
collector_pin = 25
if collector_pin in used_pins:
    tool_using_pin = tm.whats_on_pin(collector_pin)
    print(f"The assigned collector pin {collector_pin} is being used by {tool_using_pin}")
    print(f"The used pins are {used_pins}")
    exit()
rosie = Dust_collector(collector_pin, min_uptime)

if use_gui:
    screen, gui_buttons, gate_buttons = pg_gui.init_pygame(tm, gm)

if use_voltage:
    tools_with_sensor = vs.get_tools_with_sensor(tm.tools)

run = True

if __name__ == '__main__':
    while run:
        if use_gui:
            pg_gui.draw_gui(screen, gui_buttons, gate_buttons, gm, tm)
            run = pg_gui.handle_events(gui_buttons, gate_buttons, tm, gm)

        if use_voltage:
            for tool in tools_with_sensor:
                selected_tool = tm.tools[tool]
                if selected_tool.override == False:
                    am_i_on = selected_tool.voltage_sensor.am_i_on()
                    if am_i_on and selected_tool.status != 'on':
                        selected_tool.turn_on()
                    elif not am_i_on and selected_tool.status == 'on':
                        selected_tool.spindown()

        shop_manager()

    pygame.quit()