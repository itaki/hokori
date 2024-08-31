import json
import os
import time
import logging
import curses
from pathlib import Path
from datetime import datetime

import board
import busio
from adafruit_pca9685 import PCA9685 as Adafruit_PCA9685

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants for configuration files and backup directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
GATES_FILE = os.path.join(BASE_DIR, 'gates.json')
BACKUP_DIR = os.path.join(BASE_DIR, '_BU')

# Load the configuration files
def load_config():
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
    return config

def load_gates():
    with open(GATES_FILE, 'r') as gates_file:
        gates = json.load(gates_file)["gates"]
    return gates

# Initialize I2C bus and PCA9685 boards
def initialize_boards(config):
    i2c = busio.I2C(board.SCL, board.SDA)
    boards = {}

    for board_config in config.get('boards', []):
        board_id = board_config['id']
        if board_config.get('purpose') == 'Servo Control':
            try:
                boards[board_id] = Adafruit_PCA9685(i2c, address=int(board_config['i2c_address'], 16))
                boards[board_id].frequency = 50  # 50 Hz is standard for servos
                logger.info(f"Initialized PCA9685 {board_config['label']} at address {board_config['i2c_address']}")
            except Exception as e:
                logger.error(f"Failed to initialize PCA9685 {board_id}: {e}")
        else:
            logger.info(f"Skipping initialization of {board_id} as it is set to {board_config.get('purpose', 'Unknown')}")
    return boards

# Gate class
class Gate:
    def __init__(self, name, gate_info, boards):
        self.name = name
        board_id = gate_info['io_location']['board']
        self.board = boards.get(board_id)

        if self.board is None:
            logger.error(f"Board with ID {board_id} for gate {self.name} not found in boards dictionary.")
            raise ValueError(f"Board with ID {board_id} not found")

        self.pin = gate_info['io_location']['pin']
        self.min_angle = gate_info['min']
        self.max_angle = gate_info['max']
        self.status = gate_info['status']
        self.previous_status = gate_info['status']

    def angle_to_pwm(self, angle):
        min_pulse = 1000  # Minimum pulse width (in microseconds)
        max_pulse = 2000  # Maximum pulse width (in microseconds)
        pulse_range = max_pulse - min_pulse
        angle_range = 180  # Full range of servo angles (typically 0-180 degrees)

        pulse_width = min_pulse + (pulse_range * angle / angle_range)
        return int((pulse_width * 65535) / (1000000 / self.board.frequency))

    def set_angle(self, angle):
        pwm_value = self.angle_to_pwm(angle)
        self.board.channels[self.pin].duty_cycle = pwm_value
        time.sleep(0.5)  # Allow time for the servo to move
        self.board.channels[self.pin].duty_cycle = 0  # Turn off the servo

    def open(self):
        self.set_angle(self.max_angle)
        self.update_status("open")

    def close(self):
        self.set_angle(self.min_angle)
        self.update_status("closed")

    def update_status(self, new_status):
        if self.previous_status != new_status:
            self.previous_status = new_status
            self.status = new_status
            logger.info(f"Gate {self.name} {new_status}.")

# GateManager class
class GateManager:
    def __init__(self, boards, gates_file=GATES_FILE, backup_dir=BACKUP_DIR):
        self.boards = boards  # Store the boards dictionary
        self.gates_file = gates_file
        self.backup_dir = backup_dir
        self.gates = {}
        self.gates_dict = load_gates()
        if self.gates_dict:
            self.build_gates()
            self.close_all_gates()  # Close all gates on initialization

    def build_gates(self):
        '''Builds Gate objects from the loaded gate data'''
        self.gates = {}
        for name, gate_info in self.gates_dict.items():
            try:
                gate = Gate(name, gate_info, self.boards)  # Pass the boards dictionary to the Gate
                self.gates[name] = gate
                logger.debug(f"Gate {name} created with board {gate_info['io_location']['board']} and pin {gate_info['io_location']['pin']}")
            except ValueError as e:
                logger.error(f"Failed to build gate {name}: {e}")

    def close_all_gates(self):
        '''Closes all gates on initialization'''
        for gate in self.gates.values():
            gate.close()
    # end def

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

    def save_gates(self):
        '''Saves the updated gate angles to the gates.json file'''
        for gate_name, gate in self.gates.items():
            self.gates_dict[gate_name]['min'] = gate.min_angle
            self.gates_dict[gate_name]['max'] = gate.max_angle

        self.backup_gates()  # Backup before saving
        with open(self.gates_file, 'w') as gates_file:
            json.dump({"gates": self.gates_dict}, gates_file, indent=4)
        logger.info(f"Gates configuration saved to {self.gates_file}")

    def set_gate_angle(self, stdscr, gate_key, side):
        """ CURSES function so needs wrapping, create interface to adjust the gate"""
        my_gate = self.gates[gate_key]
        pin = my_gate.pin
        key = None
        adjustment = 0
        flagged = True
        angle = my_gate.min_angle if side == 'min' else my_gate.max_angle
        rows_of_info = 8

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        curses.noecho()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        height, width = stdscr.getmaxyx()
        cent_x = int(width // 2)

        while True:
            if key == "KEY_DOWN":
                adjustment = -1
            elif key == "KEY_LEFT":
                adjustment = -10
            elif key == "KEY_UP":
                adjustment = 1
            elif key == "KEY_RIGHT":
                adjustment = 10
            elif key == "q":
                return -1
            elif key == "s":
                return int(angle)
            if adjustment != 0 or flagged:
                flagged = False
                angle += adjustment
                adjustment = 0  
                if angle > 180:
                    angle = 180
                elif angle < 0: 
                    angle = 0
                
                my_gate.set_angle(angle)

            # UI strings and positioning
            title = f"Set {side} for gate {my_gate.name} on pin {my_gate.pin}"[:width-1]
            instructions = "Use arrow keys: 'q' to quit: 's' to save"[:width-1]
            angle_reading = f"Angle: {angle}"[:width-1]
            start_x_title = cent_x - (len(title) // 2)
            start_x_instructions = cent_x - (len(instructions) // 2)
            start_x_angle_reading = cent_x - (len(angle_reading) // 2)

            # Clear the screen
            stdscr.clear()

            # Render status bar and title
            stdscr.addstr(0, 0, title, curses.color_pair(2) | curses.A_BOLD )
            stdscr.addstr(2, start_x_instructions, instructions)
            stdscr.addstr(4, start_x_angle_reading, angle_reading)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            key = stdscr.getkey()

    def set_min(self, gate_key):
        gate_min = curses.wrapper(self.set_gate_angle, gate_key, 'min')
        if gate_min != -1:
            self.gates[gate_key].min_angle = gate_min
            self.save_gates()  # Save after setting the minimum angle
            return True
        return False
    
    def set_max(self, gate_key):
        gate_max = curses.wrapper(self.set_gate_angle, gate_key, 'max')
        if gate_max != -1:
            self.gates[gate_key].max_angle = gate_max
            self.save_gates()  # Save after setting the maximum angle
            return True
        return False

# Main execution
if __name__ == "__main__":
    config = load_config()
    boards = initialize_boards(config)
    gate_manager = GateManager(boards)

    for gate_name in gate_manager.gates:
        logger.info(f"Testing gate {gate_name}")
        if not gate_manager.set_min(gate_name):
            break
        if not gate_manager.set_max(gate_name):
            break

    logger.info("All gates have been set.")