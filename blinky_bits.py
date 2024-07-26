import json
import time
import datetime
import get_full_path
import os
import shutil #allows for copying a file to make a backup
import errno
from adafruit_servokit import ServoKit
from gpiozero import LED, RGBLED, Button
kit = ServoKit(channels=16)

def center_x(width, string):
    '''Takes curses terminal width and a string and determines where to start it to center it'''
    return int((width // 2) - (len(string) // 2) - len(string) % 2)

class Tool:
    def __init__(self,
                 id_num,
                 name,
                 status,
                 override,
                 gate_prefs,
                 button_pin=0,
                 led_type='none',
                 r_pin=0,
                 g_pin=0,
                 b_pin=0,
                 voltage_pin=12,
                 amp_trigger=10,
                 keyboard_key=0,
                 last_used=0,
                 spin_down_time=5,
                 flagged=False):
        self.id_num = id_num
        self.name = name
        self.status = status
        self.override = override
        self.gate_prefs = gate_prefs
        self.button_pin = button_pin
        self.led_type = led_type
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
        self.voltage_pin = voltage_pin
        self.amp_trigger = amp_trigger
        self.keyboard_key = keyboard_key
        self.last_used = last_used
        self.spin_down_time = spin_down_time
        self.flagged = flagged

        # if self.button_pin != 0:
        #     print(f"Creating {self.name} on {self.button_pin}")
        #     # create a button object and put it in the dictionary
        #     self.btn = Button(self.button_pin)
        #     self.btn.when_pressed = self.button_cycle
        #     print(f"led type = {self.led_type}")
        #     if self.led_type == "RGB":
        #         self.led = RGBLED(self.r_pin, self.g_pin, self.b_pin)
        #         print(f"created RGBLED on {self.r_pin, self.g_pin, self.b_pin}")
        #         self.led.color = (1,1,1)
        #     elif self.led_type == "LED":
        #         self.led = LED(self.r_pin)
        #         print(f"created LED on {self.r_pin}")
        #     else:
        #         print(f"no button created for {self.name}")


    def button_cycle(self):
        '''this runs when a real hard button is pressed. It overrides the voltage'''
        if self.status == 'on':
            self.override = False
            print(f"Override OFF")
            self.spindown()
        else:
            self.override = True
            print(f"Override engaged because {self.name} is on")
            self.turn_on()



    def turn_on(self):
        self.status = 'on'
        self.flagged = True
        if self.button_pin != 0:
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(.51, .9, 0), off_color=(.6, 1, .1), n=None, background=True)
            elif self.led_type == "LED":
                self.led.on
        print(f'----------->{self.name} turned ON')

    def spindown(self):
        self.status = 'spindown'
        self.last_used = time.time()
        if self.button_pin != 0:
            if self.led_type == "RGB":
                self.led.pulse(fade_in_time=1, fade_out_time=1, on_color=(1, .59 , 0), off_color=(0, 0, 0), n=None, background=True)
            elif self.led_type == "LED":
                self.led.off
        print(f'----------->{self.name} set to SPINDOWN for {self.spin_down_time}')

    def turn_off(self):
        self.status = 'off'
        self.flagged = True
        if self.button_pin != 0:
            if self.led_type == "RGB":
                self.led.color = (.1, .82, .90)
            elif self.led_type == "LED":
                self.led.off
        print(f'----------->{self.name} turned OFF')


class Gate:
    def __init__(self, name, number, location, status, pin, minimum, maximum, info):
        self.name = name
        self.number = number
        self.location = location
        self.status = status
        self.pin = pin
        self.min = minimum
        self.max = maximum

    def open(self):

        kit.servo[self.pin].angle = self.max
        print(f'opening {self.name}')
        # send maximum to gate
        self.status = 0

       

    def close(self):

        kit.servo[self.pin].angle = self.min
        print(f'closing {self.name}')
        # send minimum to gate
        self.status = 1




def get_tools(file = 'tools.json'):
    tools_list = []
    tools = {}
        # LOAD ALL THE TOOLS
    if os.path.exists(file): # if there is a tools file load it
        file_path = get_full_path.path(file)  # set the file path
        with open(file_path, 'r') as f:  # read the tool list
            tools_list = json.load(f)  # load tool list into python

        for tool in tools_list:
            tools[tool['name']] = Tool(
                tool['id_num'],
                tool['name'],
                tool['status'],
                tool['override'],
                tool['gate_prefs'],
                tool['button_pin'],
                tool['led_type'],
                tool['r_pin'],
                tool['g_pin'],
                tool['b_pin'],
                tool['voltage_pin'],
                tool['amp_trigger'],
                tool['keyboard_key'],
                tool['last_used'],
                tool['spin_down_time'],
                tool['flagged']
            )
            # 1print(tool)
    return tools
    #print(f'These are your tools {tools}')

def get_gates(file): 
    gates_list = []  # list
    gates = {}
        # LOAD ALL THE GATES
    if os.path.exists(file): # if there is a gates file load it
        file_path = get_full_path.path(file)  # set the file path
        with open(file_path, 'r') as f:  # read the gate list
            gates_list = json.load(f)  # load gate list into python

        for gate in gates_list:
            gates[gate['name']] = Gate(
                gate['name'],
                gate['number'],
                gate['location'],
                gate['status'],
                gate['pin'],
                gate['min'],
                gate['max'],
                gate['info']
            )
            # 1print(tool)
    return(gates)
    #print(f'These are your tools {gates}')

def backup_file(file, note = '', backup_directory = '_BU'):
    '''Takes backup directory and file_name and backs the file up with date stamp'''
    name_parts = file.split ('.')
    f_name = name_parts[0]
    ext = name_parts[-1]
    now = datetime.datetime.now() # get the current time
    tail = now.strftime('%Y%m%d-%H%M%S')
    try:
        os.makedirs(backup_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    destination = backup_directory+'/'+f_name+'-'+tail+'_'+note+'.'+ext
    shutil.copy (file, destination)
    print(f"{file} backed up to {destination}")


if __name__ == "__main__":
    tools = get_tools('tools.json')
    gates = get_gates('gates.json')
    print (len(gates))
    print (tools['TableSaw'].name)
    for tool in tools:
        pass