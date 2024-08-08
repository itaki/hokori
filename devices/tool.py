import logging
import time
from rgbled_button import RGBLED_Button
from voltage_sensor import Voltage_Sensor

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c, styles_path):
        self.id = tool_config.get('id', 'unknown')
        self.label = tool_config.get('label', 'unknown')
        self.status = tool_config.get('status', 'off')
        self.preferences = tool_config.get('preferences', {})
        self.button_config = tool_config.get('button', {})
        self.volt_config = tool_config.get('volt', {})

        self.i2c = i2c
        self.styles_path = styles_path
        self.button = None
        self.voltage_sensor = None

        if self.button_config:
            self.button = RGBLED_Button(self.button_config, self.i2c, self.styles_path)
            self.button.start()

        if self.volt_config:
            self.voltage_sensor = Voltage_Sensor(self.volt_config, self.i2c)

        self.monitoring_thread = threading.Thread(target=self.update_tool_status)
        self.monitoring_thread.start()

        logger.debug(f"Tool {self.label} initialized with status {self.status}")

    def update_tool_status(self):
        while True:
            button_state = self.button.get_button_state() if self.button else False
            voltage_state = self.voltage_sensor.am_i_on() if self.voltage_sensor else False
            
            if button_state or voltage_state:
                self.set_status('on')
            else:
                self.set_status('off')

            time.sleep(1)  # Adjust the sleep duration as needed

    def set_status(self, status):
        self.status = status
        logger.info(f"Tool {self.label} status set to {self.status}")

    def stop(self):
        if self.button:
            self.button.stop()
        if self.voltage_sensor:
            self.voltage_sensor.stop()
        self.monitoring_thread.join()

if __name__ == "__main__":
    import board
    import busio

    logging.basicConfig(level=logging.DEBUG)

    # Example tool configuration for testing
    tool_config = {
        "type": "tool",
        "label": "Test Tool",
        "id": "test_tool",
        "status": "off",
        "preferences": {
            "use_collector": True,
            "gate_prefs": ["TEST_GATE"],
            "last_used": 0,
            "spin_down_time": 5
        },
        "button": {
            "label": "Test Button",
            "id": "test_button",
            "type": "RGBLED_Button",
            "physical_location": "Test Location",
            "connection": {
                "hub": "main-hub",
                "address": "0x20",
                "pin": 0
            },
            "led": {
                "label": "Test Button LED",
                "id": "test_button_led",
                "type": "RGBLED",
                "physical_location": "Test Location",
                "connection": {
                    "hub": "main-hub",
                    "address": "0x40",
                    "pins": [0, 1, 2]
                }
            }
        },
        "volt": {
            "label": "VS for test",
            "version": "20 amp",
            "voltage_address": {
                "board_address": "0x49",
                "pin": 0
            },
            "multiplier": 3
        }
    }

    i2c = busio.I2C(board.SCL, board.SDA)

    # Create an instance of Tool
    tool = Tool(tool_config, i2c, 'path/to/styles.json')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tool.stop()
        logger.info("Test interrupted by user")
