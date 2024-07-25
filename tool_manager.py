import os
import json
import time
from gpiozero import PWMLED, RGBLED, Button, OutputDevice
from pathlib import Path
import voltage_sensor as vs
import board
import busio
import adafruit_pca9685
import get_full_path

i2c = busio.I2C(board.SCL, board.SDA)

TOOLS_FILE = 'tools.json'
BACKUP_DIR = '_BU'
on_led_color = 0xffff
spindown_led_color = 0x8888
off_led_color = 0x1111
on_rgb_color = {'bright': (.51, .9, 0), 'dark': (.6, 1, .1)}
spindown_rgb_color = {'bright': (1, .59, 0), 'dark': (0, 0, 0)}
off_rgb_color = {'bright': (.1, .82, .90), 'dark': (.1, .82, .90)}

class Tool:
    def __init__(self, tool):
        self.tool_dict = tool
        self.pins_used = []
        self.id_num = tool['id_num']
        self.name = tool['name']
        self.status = 'off'
        self.override = False
        self.gate_prefs = tool['gate_prefs']
        if tool['button'] != {}:
            self.create_button(tool['button'])
            self.pins_used.append(tool['button']['pin'])

        if tool['led'] != {}:
            self.create_led(tool['led'])
            if tool['led']['type'] == 'PWMLED':
                self.pins_used.append(tool['led']['pin'])
            elif tool['led']['type'] == 'RGB':
                self.pins_used.extend(tool['led']['pins'])

        if tool['volt'] != {}:
            self.voltage_sensor = vs.Voltage_Sensor(tool['volt'])
            print(f"Initialized Voltage Sensor for {self.name}")

        self.keyboard_key = tool['keyboard_key']       
        self.spin_down_time = tool['spin_down_time']
        self.last_used = 0
        self.flagged = True

    def create_button(self, btn_dict):
        print(f"Creating {self.name} button at address {btn_dict['address']} on pin {btn_dict['pin']}")
        if btn_dict['address'] == 'pi':  # a button that is directly attached to the pi
            self.btn = Button(btn_dict['pin'])
            self.btn.when_pressed = self.button_cycle
        else:
            print('Buttons not directly connected to pi are not supported right now')

    def create_led(self, led_dict):
        if led_dict['address'] == 'pi':
            if led_dict['type'] == "RGB":
                self.led = RGBLED(led_dict['pins'][0], led_dict['pins'][1], led_dict['pins'][2])
                self.led_type = "RGB"
                print(f"created RGBLED on {led_dict['pins'][0]}, {led_dict['pins'][1]}, {led_dict['pins'][2]}")
            elif led_dict['type'] == "PWMLED":
                self.led = PWMLED(led_dict['pin'], initial_value=0)
                self.led_type = "PWMLED"
                print(f"Creating an {led_dict['type']} LED on {led_dict['address']} on pin {led_dict['pin']}")
            elif led_dict['type'] == "RELAY":
                self.led = OutputDevice(led_dict['pin'], initial_value=False)
                self.led_type = "RELAY"
            else:
                print(f"no led created for {self.name}")
        else:
            print('LEDs not directly connected to pi are not supported right now')

    def button_cycle(self):
        if self.status == 'on':
            self.override = False
            print(f"{self.name} button pressed. Tool and Override OFF")
            self.spindown()
        else:
            self.override = True
            print(f"{self.name} button pressed. Tool and Override engaged")
            self.turn_on()

    def turn_on(self):
        self.status = 'on'
        self.flagged = True
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(.51, .9, 0), off_color=(.6, 1, .1), n=None, background=True)
            elif self.led_type == "PWMLED":
                self.led.on()
            elif self.led_type == "RELAY":
                self.led.on()
        print(f'----------->{self.name} turned ON')

    def spindown(self):
        self.status = 'spindown'
        self.last_used = time.time()
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(1, .59, 0), off_color=(0, 0, 0), n=None, background=True)
            elif self.led_type == "PWMLED":
                self.led.pulse(fade_in_time=1, fade_out_time=1, n=None, background=True)
            elif self.led_type == "RELAY":
                pass
        print(f'----------->{self.name} set to SPINDOWN for {self.spin_down_time}')

    def turn_off(self):
        self.status = 'off'
        self.flagged = True
        if hasattr(self, "led"):
            if self.led_type == "RGB":
                self.led.color = (.1, .82, .90)
            elif self.led_type == "PWMLED":
                self.led.value = .1
            elif self.led_type == "RELAY":
                self.led.off()
        print(f'----------->{self.name} turned OFF')

class Tool_Manager:
    def __init__(self, tools_file="tools.json", backup_dir="_BU"):
        self.get_tools(tools_file)
        self.backup_dir = backup_dir

    def get_tools(self, file):
        tools_list = []
        tools = {}
        if os.path.exists(file):  # if there is a tools file load it
            file_path = get_full_path.path(file)  # set the file path
            with open(file_path, 'r') as f:  # read the tool list
                tools_list = json.load(f)  # load tool list into python

            for tool in tools_list:
                tools[tool['name']] = Tool(tool)  # build all the tools
        self.tools = tools

    def get_used_pins(self):
        all_used_pins = []
        for tool in self.tools:
            selected_tool = self.tools[tool]
            all_used_pins.extend(selected_tool.pins_used)
        return all_used_pins

    def whats_on_pin(self, pin):
        for tool in self.tools:
            selected_tool = self.tools[tool]
            if pin in selected_tool.pins_used:
                return selected_tool.name
        return "No Tool"

if __name__ == '__main__':
    tm = Tool_Manager(TOOLS_FILE, BACKUP_DIR)
    pins_in_use = tm.get_used_pins()
    pins_in_use.sort()
    print(f"{pins_in_use}")
