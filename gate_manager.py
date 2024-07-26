import json
from adafruit_servokit import ServoKit
import os
import time
import shutil
from datetime import datetime

GATES_FILE = "gates.json"
BACKUP_DIR = "_BU"

def get_full_path(filename):
    '''This gets a file associated in the working directory no matter where you run it.
       Useful for VSCode where the terminal doesn't always reside in the directory you are working out of.
    '''
    current_dir = os.path.dirname(__file__)  # get current working directory
    full_path = os.path.join(current_dir, filename)  # set file path
    return full_path

def hex_to_int(hex_str):
    return int(hex_str, 16)

class Gate:
    def __init__(self, name, gate_info):
        self.name = name
        self.physical_location = gate_info.get('physical_location', '')
        self.address = hex_to_int(gate_info['io_location']['address'])
        self.pin = gate_info['io_location']['pin']
        self.min = gate_info['min']
        self.max = gate_info['max']
        self.status = gate_info['status']
        self.init_servo()

    def init_servo(self):
        try:
            self.servo = ServoKit(channels=16, address=self.address).servo[self.pin]
            self.servo.set_pulse_width_range(self.min, self.max)
            return True
        except Exception as e:
            print(f"FAILED to create gate at address {self.address} on pin {self.pin}: {e}")
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
        self.load_gates()

    def load_gates(self):
        '''Loads gates from a JSON file'''
        path_to_gates_file = get_full_path(self.gates_file)
        if os.path.exists(path_to_gates_file):
            print(f"Loading gates from {path_to_gates_file}")
            with open(path_to_gates_file, 'r') as f:
                self.gates_dict = json.load(f)
            self.build_gates()
        else:
            self.gates_dict = {}
            print('No gate file available')

    def build_gates(self):
        '''Builds Gate objects from the loaded gate data'''
        self.gates = {}
        for name, gate_info in self.gates_dict['gates'].items():
            self.gates[name] = Gate(name, gate_info)
            print(f'Gate {name} created with address {gate_info["io_location"]["address"]} and pin {gate_info["io_location"]["pin"]}')

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
            print(f"Gate {name} not found.")

    def close_gate(self, name):
        '''Close a single gate by name'''
        if name in self.gates:
            self.gates[name].close()
        else:
            print(f"Gate {name} not found.")

    def set_gates(self, open_gates):
        '''Takes a list of gates that need to be open and opens them while making sure the rest are closed'''
        for gate_name in self.gates:
            if gate_name in open_gates:
                self.open_gate(gate_name)
            else:
                self.close_gate(gate_name)

    def save_gates(self):
        '''Saves the current gate configuration to a JSON file'''
        full_path = get_full_path(self.gates_file)
        backup_dir_path = get_full_path(self.backup_dir)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file_name = f"{os.path.basename(full_path).split('.')[0]}_{timestamp}.json"
        backup_path = os.path.join(backup_dir_path, backup_file_name)
        if not os.path.exists(backup_dir_path):
            os.makedirs(backup_dir_path)
        shutil.copyfile(full_path, backup_path)
        print(f"Backup of {full_path} created at {backup_path}")
        
        with open(full_path, 'w') as f:
            json.dump(self.gates_dict, f, indent=4)
        print(f"Gates configuration saved to {full_path}")

# Load JSON data
if __name__ == "__main__":
    m = Gate_Manager(GATES_FILE, BACKUP_DIR)
