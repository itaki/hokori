import logging
from rgbled_button import RGBLED_Button

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, tool_config, i2c, button_manager):
        self.config = tool_config
        self.i2c = i2c
        self.button_manager = button_manager
        self.label = tool_config.get('label', 'unknown')
        
        if 'button' in tool_config:
            self.button = RGBLED_Button(tool_config['button'], i2c, 'styles.json')
            self.button_manager.register_button(self.button)
        else:
            self.button = None

        # Initialize other components like voltage sensors if needed
