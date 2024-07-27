from gpiozero import DigitalOutputDevice
import time

class Dust_collector:
    def __init__(self, pin, min_uptime):
        self.status = 'off'
        self.last_spin_up = time.time()
        self.min_uptime = min_uptime
        self.relay = DigitalOutputDevice(pin, active_high=True, initial_value=False)

        # turn off rosie relay pin

    def spinup(self):
        if self.status == 'on':  # rosie is currently on
            pass
        elif self.status == 'off':
            self.status = 'on'
            self.relay.on()
            self.last_spin_up = time.time()

    def shutdown(self):
        if self.status != 'off':
            self.relay.off()
            self.status = 'off'

    def uptime(self):
        uptime = time.time() - self.last_spin_up
        return uptime