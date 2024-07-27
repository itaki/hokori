import json
from adafruit_servokit import ServoKit
import os
import time
from blinky_bits import hex_to_int, get_full_path, backup_file
from main import GATES_FILE, BACKUP_DIR
class Gate:
    def __init__(self, name, gate_info):
        self.name = name
        self.address = hex_to_int(gate_info['io_location']['address'])
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

    def view_gates(self):
        '''Prints a list of all gates'''
        for gate_key, gate_info in self.gates_dict['gates'].items():
            print(f"Gate: {gate_key}, Physical Location: {gate_info['physical_location']}, Status: {gate_info['status']}, "
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
        

# Load JSON data
if __name__ == "__main__":
    gm = Gate_Manager(GATES_FILE, BACKUP_DIR)
    gm.view_gates()

