import threading
import time

class Poll_Buttons:
    def __init__(self, buttons, rgbled_styles, debounce_time=0.5):
        self.buttons = buttons
        self.rgbled_styles = rgbled_styles
        self.debounce_time = debounce_time  # Debounce time is now configurable
        self.stop_event = threading.Event()  # Create the stop event
        self.thread = None  # Store the thread reference

    def poll_buttons(self):
        while not self.stop_event.is_set():
            for button in self.buttons:
                try:
                    if not button.button.value:  # Button press detected
                        button.toggle()  # No need to pass self.rgbled_styles here
                        time.sleep(self.debounce_time)  # Debounce delay
                except Exception as e:
                    print(f"Error polling button {button}: {e}")
            time.sleep(0.1)  # Small delay to avoid busy-waiting

    def start_polling(self):
        self.thread = threading.Thread(target=self.poll_buttons, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join()
