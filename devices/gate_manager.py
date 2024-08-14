import json
import logging
from adafruit_servokit import ServoKit
import os
import time
from datetime import datetime

# Constants for configuration files and backup directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVICE_FILE = os.path.join(BASE_DIR, 'config.json')
GATES_FILE = os.path.join(BASE_DIR, 'gates.json')
BACKUP_DIR = os.path.join(BASE_DIR, '_BU')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'gate_manager.log')

# Ensure the logs and backup directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Gate:
    def __init__(self, name, gate_info, boards):
        self.name = name
        board_id = gate_info['io_location']['board']
        self.board = boards.get(board_id)  # Retrieve the board instance from the boards dictionary

        if self.board is None:
            logger.error(f"Board with ID {board_id} for gate {self.name} not found in boards dictionary.")
            raise ValueError(f"Board with ID {board_id} not found")

        self.pin = gate_info['io_location']['pin']
        self.min = gate_info['min']
        self.max = gate_info['max']
        self.status = gate_info['status']
        self.previous_status = gate_info['status']  # Initialize with the current status

        try:
            if hasattr(self.board, 'servo'):  # Check if this board is for servo control
                self.servo = self.board.servo[self.pin]
            else:
                self.servo = None
                logger.warning(f"Board {board_id} for gate {self.name} does not support servo control.")
            self.init_servo()
            logger.debug(f"Gate {self.name} initialized on board {board_id} at pin {self.pin}")
        except ValueError as e:
            logger.error(f"Error initializing gate {self.name} at pin {self.pin}: {e}")
            logger.warning(f"Gate {self.name} will not be functional due to initialization failure.")
            self.servo = None

    def init_servo(self):
        if self.servo:
            try:
                self.servo.set_pulse_width_range(1000, 2000)  # Set default pulse width range
            except Exception as e:
                logger.error(f"Failed to set pulse width range for gate {self.name}: {e}")
                self.servo = None

    def start_pwm(self):
        if self.servo:
            pass  # Implement specific initialization needed for your servo here

    def stop_pwm(self):
        if self.servo:
            self.servo.fraction = None  # This should turn off the PWM signal

    def open(self):
        if self.servo and self.status != "open":
            self.start_pwm()
            self.servo.angle = self.max
            time.sleep(0.5)  # Allow time for the servo to move
            self.stop_pwm()
            self.update_status("open")
    
    def close(self):
        if self.servo and self.status != "closed":
            self.start_pwm()
            self.servo.angle = self.min
            time.sleep(0.5)  # Allow time for the servo to move
            self.stop_pwm()
            self.update_status("closed")
    
    def update_status(self, new_status):
        if self.previous_status != new_status:
            self.previous_status = new_status
            self.status = new_status
            logger.info(f"Gate {self.name} {new_status}.")
    
    def identify(self):
        if self.servo:
            self.start_pwm()
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
            self.stop_pwm()

class Gate_Manager:
    def __init__(self, boards, gates_file=GATES_FILE, backup_dir=BACKUP_DIR):
        self.boards = boards  # Store the boards dictionary
        self.gates_file = gates_file
        self.backup_dir = backup_dir
        self.gates = {}
        self.gates_dict = self.load_gates()
        if self.gates_dict:
            self.build_gates()
            self.close_all_gates()  # Close all gates on initialization

    def load_gates(self):
        '''Loads gates from a JSON file'''
        absolute_path = os.path.abspath(self.gates_file)
        logger.debug(f"Attempting to load gates from {absolute_path}")
        
        if os.path.exists(self.gates_file):
            logger.debug(f"Loading gates from {self.gates_file}")
            with open(self.gates_file, 'r') as f:
                try:
                    gates_dict = json.load(f)
                    if "gates" in gates_dict:
                        return gates_dict
                    else:
                        logger.error("Invalid gate file structure: 'gates' key not found")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON from gate file: {e}")
                    return None
        else:
            logger.debug('No gate file available')
            return None

    def build_gates(self):
        '''Builds Gate objects from the loaded gate data'''
        self.gates = {}
        for name, gate_info in self.gates_dict['gates'].items():
            try:
                gate = Gate(name, gate_info, self.boards)  # Pass the boards dictionary to the Gate
                if gate.servo:  # Only add the gate if it initialized successfully
                    self.gates[name] = gate
                    logger.debug(f'Gate {name} created with board {gate_info["io_location"]["board"]} and pin {gate_info["io_location"]["pin"]}')
                else:
                    logger.warning(f'Gate {name} could not be initialized and will be skipped.')
            except ValueError as e:
                logger.error(f"Failed to build gate {name}: {e}")

    def backup_gates(self):
        '''Backs up the gates configuration to a timestamped file in the backup directory'''
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file = os.path.join(self.backup_dir, f'gates_backup_{timestamp}.json')
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.gates_dict, f, indent=4)
            logger.info(f"Gates configuration backed up to {backup_file}")
        except Exception as e:
            logger.error(f"Failed to backup gates configuration: {e}")

    def test_gates(self):
        '''Cycles each gate to its minimum and then maximum angle'''
        for gate in self.gates.values():
            logger.info(f"Testing gate {gate.name}")
            gate.close()
            time.sleep(1)  # Wait for 1 second at min position
            gate.open()
            time.sleep(1)  # Wait for 1 second at max position

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
            logger.debug(f"Gate {name} not found.")

    def close_gate(self, name):
        '''Close a single gate by name'''
        if name in self.gates:
            self.gates[name].close()
        else:
            logger.debug(f"Gate {name} not found.")

    def view_gates(self):
        '''Prints a list of all gates'''
        for gate_key, gate_info in self.gates_dict['gates'].items():
            logger.debug(f"Gate: {gate_key}, Physical Location: {gate_info['physical_location']}, Status: {gate_info['status']}, "
          f"IO Location Board: {gate_info['io_location']['board']}, IO Location Pin: {gate_info['io_location']['pin']}, "
          f"Min: {gate_info['min']}, Max: {gate_info['max']}")

    def get_gate_settings(self, tools):
        '''Get gate settings based on the tool status'''
        open_gates = []
        for t in tools:
            current_tool = tools[t]
            if current_tool.status != 'off':
                for gate_pref in current_tool.gate_prefs:
                    if gate_pref in self.gates and gate_pref not in open_gates:
                        open_gates.append(gate_pref)
        return open_gates
    
    def set_gates(self, tools):
        '''Set gates based on tool preferences'''
        open_gates = self.get_gate_settings(tools)
        for gate_name, gate in self.gates.items():
            if gate_name in open_gates:
                gate.open()
            else:
                gate.close()
