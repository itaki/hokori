import time
import board
import busio
import threading
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017

# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create MCP23017 instance at address 0x20
mcp = MCP23017(i2c, address=0x20)

# Set up RGB LED on pins 5, 6, 7
led_red = mcp.get_pin(5)
led_green = mcp.get_pin(6)
led_blue = mcp.get_pin(7)

# Configure pins as outputs
led_red.direction = Direction.OUTPUT
led_green.direction = Direction.OUTPUT
led_blue.direction = Direction.OUTPUT

# Set initial state to off
led_red.value = False
led_green.value = False
led_blue.value = False

# Define the software PWM function
def pwm_cycle(red, green, blue, cycles=100):
    red_on_time = red / 255.0
    green_on_time = green / 255.0
    blue_on_time = blue / 255.0
    cycle_time = 0.02  # 20ms cycle time for a smooth PWM

    for _ in range(cycles):
        start_time = time.monotonic()
        
        # Turn on LEDs based on their duty cycle
        led_red.value = red_on_time > 0
        led_green.value = green_on_time > 0
        led_blue.value = blue_on_time > 0

        # Determine the minimum on-time to sleep
        min_on_time = min(red_on_time, green_on_time, blue_on_time)
        if min_on_time > 0:
            time.sleep(min_on_time)
        
        # Turn off LEDs as their on-time elapses
        if red_on_time < green_on_time:
            led_red.value = False
            if green_on_time - red_on_time > 0:
                time.sleep(green_on_time - red_on_time)
            led_green.value = False
            if blue_on_time - green_on_time > 0:
                time.sleep(blue_on_time - green_on_time)
            led_blue.value = False
        else:
            led_green.value = False
            if red_on_time - green_on_time > 0:
                time.sleep(red_on_time - green_on_time)
            led_red.value = False
            if blue_on_time - red_on_time > 0:
                time.sleep(blue_on_time - red_on_time)
            led_blue.value = False

        # Ensure the cycle time is maintained
        elapsed_time = time.monotonic() - start_time
        if elapsed_time < cycle_time:
            time.sleep(cycle_time - elapsed_time)

# Function to run the PWM cycle in a separate thread
def run_pwm_cycle(red, green, blue):
    while True:
        pwm_cycle(red, green, blue, cycles=50)

# Test colors
colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "off": (0, 0, 0),
}

# Function to switch colors
def switch_colors():
    for color_name, (red, green, blue) in colors.items():
        print(f"Setting LED to {color_name}")
        global current_color
        current_color = (red, green, blue)
        time.sleep(2)

# Create a thread for the PWM cycle
pwm_thread = threading.Thread(target=run_pwm_cycle, args=(0, 0, 0))
pwm_thread.daemon = True  # Allows thread to be killed when main program exits
pwm_thread.start()

# Main loop to switch colors every 2 seconds
current_color = (0, 0, 0)
switch_thread = threading.Thread(target=switch_colors)
switch_thread.start()

while switch_thread.is_alive():
    red, green, blue = current_color
    pwm_cycle(red, green, blue, cycles=50)
