import time
import os
import board
import busio
import logging
import json
from devices.tool import Tool
from devices.device_manager import Device_Manager
from devices.gate_manager import Gate_Manager

# Constants for configuration files and backup directory
DEVICE_FILE = 'config.json'
GATES_FILE = 'gates.json'
BACKUP_DIR = '_BU'
STYLES_FILE = 'styles.json'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main loop
def main():
    try:
        # Initialize I2C
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Load styles from the styles.json file
        styles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STYLES_FILE)
        
        # Initialize Device Manager and Gate Manager
        device_manager = Device_Manager(device_file=DEVICE_FILE, styles_path=styles_path)
        gate_manager = Gate_Manager(GATES_FILE, i2c)

        # Debugging: Print the type and structure of gate_manager.gates
        logger.info(f"Type of gate_manager.gates: {type(gate_manager.gates)}")
        logger.info(f"Contents of gate_manager.gates: {gate_manager.gates}")

        # Use tools from the Device Manager
        tools = list(device_manager.tools.values())
        
        logger.info("Tool initialization complete.")
        
        # Main loop to check for button presses and voltage
        while True:
            active_gates = set()
            for tool in tools:
                tool.check_button()
                tool.check_voltage()
                if tool.status == 'on':
                    active_gates.update(tool.gate_prefs)
            
            # Open preferred gates and close others
            for gate_id, gate in gate_manager.gates.items():
                if gate_id in active_gates:
                    gate_manager.open_gate(gate_id)
                else:
                    gate_manager.close_gate(gate_id)
                    
            time.sleep(0.1)  # Small delay to avoid busy waiting

    except FileNotFoundError as e:
        logger.error(e)
        print(e)
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
