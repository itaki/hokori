import logging

logger = logging.getLogger(__name__)

class Button:
    def __init__(self, config, board, status_callback):
        self.label = config['label']
        self.pin = config['connection']['pin']
        self.board = board
        self.status_callback = status_callback
        self.status = 'off'

        # Set up the button pin as an input
        self.board.setup_input(self.pin)

        logger.debug(f"Button {self.label} initialized on pin {self.pin}")

    def check_status(self):
        """Check the current status of the button and call the callback if it has changed."""
        try:
            new_status = 'on' if self.board.read_input(self.pin) == 0 else 'off'
            if new_status != self.status:
                self.status = new_status
                self.status_callback(self.status)
                logger.debug(f"Button {self.label} status changed to {self.status}")
        except Exception as e:
            logger.error(f"Error checking status of button {self.label}: {e}")

    def cleanup(self):
        logger.debug(f"Cleaning up Button {self.label}")
