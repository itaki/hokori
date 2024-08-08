import time
import os
import board
import busio
import logging
import json
from devices.tool import Tool
from devices.gate_manager import Gate_Manager
from devices.dust_collector import Dust_Collector
from devices.hub import Hub

# Constants for configuration files and backup directory
DEVICE_FILE = 'config.json'
GATES_FILE = 'gates.json'
STYLES_FILE = 'styles.json'

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Set logging to DEBUG level for detailed logging
logger = logging.getLogger(__name__)

def main():
    dust_collector = None
    try:
        # Initialize I2C
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Load styles from the styles.json file
        styles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STYLES_FILE)
        
        # Load the configuration from the config.json file
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEVICE_FILE)
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        hubs = [Hub(hub, i2c) for hub in config['hubs']]
        logger.info(f"Initialized {len(hubs)} hubs.")

        tools = [Tool(tool, i2c, styles_path) for tool in config['tools'] if tool['type'] == 'tool']
        logger.info(f"Initialized {len(tools)} tools.")
        
        # Initialize Gate Manager
        gate_manager = Gate_Manager(GATES_FILE, i2c)
        logger.info(f"Gate initialization complete.")
        
        # Initialize Dust Collector
        dust_collector_config = next((device for device in config['tools'] if device['type'] == 'dust_collector'), None)
        dust_collector = Dust_Collector(dust_collector_config, i2c) if dust_collector_config else None
        if dust_collector:
            logger.info(f"Dust collector {dust_collector.label} initialized.")

        # Main loop to check for button presses, voltage, and modifier button presses
        running = True
        while running:
            active_gates = set()
            any_tool_active = False  # Flag to track if any tool is active

            for tool in tools:
                tool.check_button()  # Check the main tool button
                tool.check_voltage()  # Check the voltage sensor
                tool.check_modifiers()  # Check the modifier buttons
                
                if tool.status == 'on':
                    any_tool_active = True
                    active_gates.update(tool.gate_prefs)

            # Open preferred gates and close others only if any tool is active
            if any_tool_active:
                for gate_id, gate in gate_manager.gates.items():
                    if gate_id in active_gates:
                        gate_manager.open_gate(gate_id)
                    else:
                        gate_manager.close_gate(gate_id)

            # Manage dust collector
            if dust_collector:
                dust_collector.manage_collector(tools)

            time.sleep(0.1)  # Small delay to avoid busy waiting

    except FileNotFoundError as e:
        logger.error(e)
        print(e)
        exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt.")
        running = False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        exit(1)
    finally:
        if dust_collector:
            dust_collector.turn_off()
            dust_collector.cleanup()
        logger.info("Clean shutdown complete.")

if __name__ == "__main__":
    main()
