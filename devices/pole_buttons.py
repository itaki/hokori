import threading
import time

class Poll_Buttons:
    def __init__(self, buttons, rgbled_styles):
        self.buttons = buttons
        self.rgbled_styles = rgbled_styles

    def poll_buttons(self):
        while True:
            for button in self.buttons:
                if not button.button.value:  # Button press detected
                    button.toggle(self.rgbled_styles)
                    time.sleep(0.5)  # Debounce delay
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    def start_polling(self):
        polling_thread = threading.Thread(target=self.poll_buttons, daemon=True)
        polling_thread.start()
