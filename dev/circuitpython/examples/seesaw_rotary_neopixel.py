# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT

"""I2C rotary encoder NeoPixel color picker and brightness setting example."""
import board
from adafruit_seesaw import seesaw, neopixel, rotaryio, digitalio

try:
    import _pixelbuf
except ImportError:
    import adafruit_pypixelbuf as _pixelbuf

# For use with the STEMMA connector on QT Py RP2040
# import busio
# i2c = busio.I2C(board.SCL1, board.SDA1)
# seesaw = seesaw.Seesaw(i2c, 0x36)

seesaw = seesaw.Seesaw(board.I2C(), 0x36)

encoder = rotaryio.IncrementalEncoder(seesaw)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
switch = digitalio.DigitalIO(seesaw, 24)

pixel = neopixel.NeoPixel(seesaw, 6, 1)
pixel.brightness = 0.5

last_position = -1
color = 0  # start at red

while True:

    # negate the position to make clockwise rotation positive
    position = -encoder.position

    if position != last_position:
        print(position)

        if switch.value:
            # Change the LED color.
            if position > last_position:  # Advance forward through the colorwheel.
                color += 1
            else:
                color -= 1  # Advance backward through the colorwheel.
            color = (color + 256) % 256  # wrap around to 0-256
            pixel.fill(_pixelbuf.colorwheel(color))

        else:  # If the button is pressed...
            # ...change the brightness.
            if position > last_position:  # Increase the brightness.
                pixel.brightness = min(1.0, pixel.brightness + 0.1)
            else:  # Decrease the brightness.
                pixel.brightness = max(0, pixel.brightness - 0.1)

    last_position = position
