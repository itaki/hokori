import logging

logger = logging.getLogger(__name__)

class RGBLED:
    def __init__(self, config, pca9685):
        self.label = config.get('label', 'Unknown LED')
        self.board = pca9685
        self.pins = config['connection']['pins']
        self.on_colors = config['preferences']['on_colors']
        self.off_colors = config['preferences']['off_colors']
        self.status = "off"

        # Setup PCA9685 pins for RGB LED
        if self.board:
            logger.info(f"💡 RGB LED '{self.label}' initialized on PCA9685 board, pins {self.pins}")
        else:
            logger.error(f"💡 RGB LED '{self.label}' could not be initialized due to missing PCA9685 board")

    def turn_on(self):
        """Turn on the RGB LED with the 'on' color."""
        if self.board:
            for pin, color_value in zip(self.pins, self.on_colors):
                self.board.set_pwm(pin, 0, color_value)
            self.status = "on"
            logger.debug(f"💡 RGB LED '{self.label}' turned on with colors {self.on_colors}")

    def turn_off(self):
        """Turn off the RGB LED (set to 'off' color)."""
        if self.board:
            for pin, color_value in zip(self.pins, self.off_colors):
                self.board.set_pwm(pin, 0, color_value)
            self.status = "off"
            logger.debug(f"💡 RGB LED '{self.label}' turned off with colors {self.off_colors}")

    def cleanup(self):
        """Clean up resources."""
        # PCA9685 handles cleanup internally, so no GPIO cleanup required here
        logger.info(f"🧹 Cleaned up resources for RGB LED '{self.label}'")
