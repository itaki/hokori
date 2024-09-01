import logging
import time
import threading
from devices.voltage_sensor import VoltageSensor
from devices.button import Button
from devices.rgbled import RGBLED
from devices.dust_collector import DustCollector
from devices.gate_manager import Gate_Manager

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, tools_config, boards):
        self.tools = []
        self.boards = boards
        self.collectors = {}  # Dictionary to hold dust collector objects
        self.buttons = []  # Collect all buttons for polling
        self.gate_manager = Gate_Manager(boards)  # Initialize the Gate Manager
        self._stop_polling = threading.Event()  # Event to stop polling
        self.initialize_tools(tools_config)
        self.polling_thread = threading.Thread(target=self.poll_buttons)
        self.polling_thread.start()

    def initialize_tools(self, tools_config):
        for tool_config in tools_config:
            tool_type = tool_config.get('type')
            label = tool_config.get('label', 'Unnamed Tool')

            if tool_type == 'button':
                self.initialize_button(tool_config)
            elif tool_type == 'RGBLED':
                self.initialize_rgbled(tool_config)
            elif tool_type == 'voltage_sensor':
                self.initialize_voltage_sensor(tool_config)
            elif tool_type == 'collector':
                self.initialize_dust_collector(tool_config)
            else:
                logger.warning(f"Unknown tool type '{tool_type}' for tool '{label}'. Skipping initialization.")

    def initialize_button(self, config):
        board = self.boards.get(config['connection']['board'])
        if board:
            button = Button(config, board, self.status_callback)
            self.tools.append(button)
            self.buttons.append(button)  # Add button to the polling list
            logger.info(f"Button '{config['label']}' initialized.")
        else:
            logger.error(f"Failed to initialize Button '{config['label']}' - board not found.")

    def poll_buttons(self):
        """Poll all buttons in a single thread."""
        while not self._stop_polling.is_set():
            for button in self.buttons:
                button.check_status()
            time.sleep(0.1)  # Polling interval

    def initialize_rgbled(self, config):
        board = self.boards.get(config['connection']['board'])
        if board:
            rgbled = RGBLED(config, board)
            self.tools.append(rgbled)
            logger.info(f"RGB LED '{config['label']}' initialized.")
        else:
            logger.error(f"Failed to initialize RGB LED '{config['label']}' - board not found.")

    def initialize_voltage_sensor(self, config):
        board = self.boards.get(config['connection']['board'])
        if board:
            voltage_sensor = VoltageSensor(config, board)
            voltage_sensor.set_status_callback(self.status_callback)  # Set the callback separately
            self.tools.append(voltage_sensor)
            logger.info(f"Voltage Sensor '{config['label']}' initialized.")
        else:
            logger.error(f"Failed to initialize Voltage Sensor '{config['label']}' - board not found.")


    def initialize_dust_collector(self, config):
        dust_collector = DustCollector(config)
        self.collectors[config['id']] = dust_collector
        logger.info(f"Dust Collector '{config['label']}' initialized.")

    def status_callback(self, status, tool):
        logger.debug(f"Status update received: {status} for tool {tool.label}")

        if status == "on":
            self.activate_collectors(tool)
        elif status == "off":
            self.deactivate_collectors(tool)
        
        # Notify the Gate Manager of tool status change
        self.gate_manager.set_gates(self.tools)

    def activate_collectors(self, tool):
        collectors_to_activate = tool.config['preferences'].get('use_collector', [])
        for collector_id in collectors_to_activate:
            collector = self.collectors.get(collector_id)
            if collector:
                logger.debug(f"Activating collector {collector_id} for tool {tool.label}")
                collector.turn_on()

    def deactivate_collectors(self, tool):
        collectors_to_check = tool.config['preferences'].get('use_collector', [])
        for collector_id in collectors_to_check:
            collector = self.collectors.get(collector_id)
            if collector:
                if not any(t.status == "on" and collector_id in t.config['preferences'].get('use_collector', []) for t in self.tools):
                    logger.debug(f"Deactivating collector {collector_id} as no tools are using it")
                    collector.turn_off()

    def cleanup(self):
        self._stop_polling.set()  # Signal the polling thread to stop
        self.polling_thread.join(timeout=5)  # Wait for the polling thread to stop
        if self.polling_thread.is_alive():
            logger.warning("Polling thread did not stop within the timeout period.")

        for tool in self.tools:
            if hasattr(tool, 'cleanup'):
                tool.cleanup()

        for collector in self.collectors.values():
            collector.cleanup()

        self.gate_manager.close_all_gates()  # Close all gates during cleanup
