import logging
from .rgbled_button import RGBLED_Button
from .voltage_sensor import Voltage_Sensor

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, mcp, pca, styles, i2c):
        self.label = tool_config['label']
        self.id = tool_config['id']
        self.status = tool_config.get('status', 'off')
        self.status_changed = False  # Flag to track status changes
        self.preferences = tool_config.get('preferences', {})
        self.gate_prefs = self.preferences.get('gate_prefs', [])  # Extract gate_prefs
        self.volt = tool_config.get('volt', {})
        self.keyboard_key = tool_config.get('keyboard_key', None)
        self.physical_location = tool_config.get('physical_location', '')

        # Initialize the button if it exists and is properly configured
        self.button_status = 'off'
        try:
            if 'button' in tool_config and 'label' in tool_config['button']:
                self.button = RGBLED_Button(tool_config['button'], mcp, pca, styles['RGBLED_button_styles'], self.update_status_from_button)
            else:
                self.button = None
        except Exception as e:
            logger.error(f"Error initializing button for tool {self.label}: {e}")
            return  # Skip initialization if button fails

        # Initialize the voltage detector if it exists
        self.voltage_status = 'off'
        try:
            if 'volt' in tool_config and 'voltage_address' in tool_config['volt']:
                self.voltage_sensor = Voltage_Sensor(tool_config['volt'], i2c, self.update_status_from_voltage)
            else:
                self.voltage_sensor = None
        except Exception as e:
            logger.error(f"Error initializing voltage sensor for tool {self.label}: {e}")
            return  # Skip initialization if voltage sensor fails

        logger.debug(f"Tool {self.label} initialized successfully.")

    def toggle_button(self):
        if self.button:
            self.button.toggle()

    def update_status_from_button(self, new_status):
        self.button_status = new_status
        self.update_status()

    def update_status_from_voltage(self, new_status):
        self.voltage_status = new_status
        self.update_status()

    def update_status(self):
        # Combine button and voltage sensor statuses to determine tool status
        new_status = 'on' if self.button_status == 'on' or self.voltage_status == 'on' else 'off'
        if new_status != self.status:
            self.status = new_status
            self.status_changed = True  # Mark the status as changed
            # Log the status change
            print(f"Tool {self.label} status changed to {self.status}")
            logging.info(f"Tool {self.label} status changed to {self.status}")
        else:
            self.status_changed = False  # No change in status

    def reset_status_changed(self):
        self.status_changed = False
