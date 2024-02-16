# board is esp32s3devkitc1

import board
import neopixel
import time
from rainbowio import colorwheel


print("Example Neopixel!")
pixel_pin = board.IO38
print(pixel_pin)

num_pixels = 1
led = neopixel.NeoPixel(pixel_pin, 1)  # for S3 boards
led.brightness = 0.3

while True:
    led[0] = (255, 0, 0)
    time.sleep(0.5)
    led[0] = (0, 255, 0)
    time.sleep(0.5)
    led[0] = (0, 0, 255)
    time.sleep(0.5)
    led[0] = (0, 0, 0)