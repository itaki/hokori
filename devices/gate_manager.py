import json
import logging
from adafruit_servokit import ServoKit
import os
import time

DEVICE_FILE = 'config.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'
class Gate:
    def __init__(self, name, gate_info):
        self.name = name
        self.address = int(gate_info['io_location']['address'], 16)
        self.pin = gate_info['io_location']['pin']
        self.min = gate_info['min']
        self.max = gate_info['max']
        self.status = gate_info['status']
        self.init_servo()

    def init_servo(self):
        try:
            self.servo = ServoKit(channels=16, address=self.address).servo[self.pin]
            return True
        except Exception as e:
            logging.debug(f"FAILED to create gate at address {self.address} on pin {self.pin}: {e}")
            return False
        
    def open(self):
        self.servo.angle = self.max
        self.status = "open"
        print(f"Gate {self.name} opened.")
    
    def close(self):
        self.servo.angle = self.min
        self.status = "closed"
        print(f"Gate {self.name} closed.")
    
    def identify(self):
        i = 0
        while i < 20:
            self.servo.angle = 80
            time.sleep(.2)
            self.servo.angle = 100
            time.sleep(.2)
            i += 1
        if self.status == 'open':
            self.open()
        else:
            self.close()

class Gate_Manager:
    def __init__(self, gates_file=GATES_FILE, backup_dir=BACKUP_DIR):
        self.gates_file = gates_file
        self.backup_dir = backup_dir
        self.gates = {}
        self.gates_dict = self.load_gates()
        self.build_gates()

    def load_gates(self):
        '''Loads gates from a JSON file'''
        if os.path.exists(self.gates_file):
            logging.debug(f"Loading gates from {self.gates_file}")
            with open(self.gates_file, 'r') as f:
                self.gates_dict = json.load(f)
            return self.gates_dict
        else:
            self.gates_dict = {}
            logging.debug('No gate file available')

    def build_gates(self):
        '''Builds Gate objects from the loaded gate data'''
        self.gates = {}
        for name, gate_info in self.gates_dict['gates'].items():
            self.gates[name] = Gate(name, gate_info)
            logging.debug(f'Gate {name} created with address {gate_info["io_location"]["address"]} and pin {gate_info["io_location"]["pin"]}')

    def open_all_gates(self):
        '''Open all gates'''
        for gate in self.gates.values():
            gate.open()

    def close_all_gates(self):
        '''Close all gates'''
        for gate in self.gates.values():
            gate.close()

    def open_gate(self, name):
        '''Open a single gate by name'''
        if name in self.gates:
            self.gates[name].open()
        else:
            logging.debug(f"Gate {name} not found.")

    def close_gate(self, name):
        '''Close a single gate by name'''
        if name in self.gates:
            self.gates[name].close()
        else:
            logging.debug(f"Gate {name} not found.")

    def view_gates(self):
        '''Prints a list of all gates'''
        for gate_key, gate_info in self.gates_dict['gates'].items():
            logging.debug(f"Gate: {gate_key}, Physical Location: {gate_info['physical_location']}, Status: {gate_info['status']}, "
          f"IO Location Address: {gate_info['io_location']['address']}, IO Location Pin: {gate_info['io_location']['pin']}, "
          f"Min: {gate_info['min']}, Max: {gate_info['max']}")
            
    def get_gate_settings(tools):
        open_gates = []
        for t in tools:
            current_tool = tools[t]
            if current_tool.status != 'off':
                for gate_pref in current_tool.gate_prefs:
                    if gate_pref not in open_gates:
                        open_gates.append(gate_pref)
        return open_gates
    
    def set_gates(tools):
        pass
        

# Load JSON data
if __name__ == "__main__":
    gm = Gate_Manager(GATES_FILE, BACKUP_DIR)
    gm.view_gates()

