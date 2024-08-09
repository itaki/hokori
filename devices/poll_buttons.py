import threading
import time

class Poll_Buttons:
    def __init__(self, buttons, rgbled_styles):
        self.buttons = buttons
        self.rgbled_styles = rgbled_styles
        self.stop_event = threading.Event()  # Create the stop event
        self.thread = None  # Store the thread reference

    def poll_buttons(self):
        while not self.stop_event.is_set():
            for button in self.buttons:
                if not button.button.value:  # Button press detected
                    button.toggle()  # No need to pass self.rgbled_styles here
                    time.sleep(0.5)  # Debounce delay
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    def start_polling(self):
        self.thread = threading.Thread(target=self.poll_buttons, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join()
