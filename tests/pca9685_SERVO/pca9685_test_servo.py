import board
import busio
import adafruit_pca9685
import time
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16, address=0x42)
# i2c = busio.I2C(board.SCL, board.SDA)
# hat = adafruit_pca9685.PCA9685(i2c)
min = 0
max =180

while True:
    kit.servo[0].angle = min 
    time.sleep(2)
    kit.servo[0].angle = max
    time.sleep(2)