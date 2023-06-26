# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board
import displayio
import digitalio
import terminalio
import neopixel
from adafruit_display_text import label
import adafruit_displayio_ssd1306
#                            91011121314151617
#         0 1 2 3 4 5 6 7 8  0 1 2 3 4 5 6 7 8
eyemap= [[1,1,0,0,0,0,0,1,1, 1,1,0,0,0,0,0,1,1], # 0
         [1,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,1], # 1
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 2
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 3
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 4 
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 5
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 6
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 7
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 8
         [0,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,0], # 9
         [1,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,1], # 10
         [1,1,0,0,0,0,0,1,1, 1,1,0,0,0,0,0,1,1]] # 11

# 9 6 5
b1 = digitalio.DigitalInOut(board.D9)
b2 = digitalio.DigitalInOut(board.D6)
b3 = digitalio.DigitalInOut(board.D5)
b1.direction = digitalio.Direction.INPUT
b1.pull = digitalio.Pull.UP
b2.direction = digitalio.Direction.INPUT
b2.pull = digitalio.Pull.UP
b3.direction = digitalio.Direction.INPUT
b3.pull = digitalio.Pull.UP
colormode=1


pixels=neopixel.NeoPixel(board.D12, 190, brightness=0.0125, auto_write=False)
pixels.fill((255,255,255))
pixels.show()
displayio.release_displays()

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(128, 32, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(118, 24, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=4)
splash.append(inner_sprite)

# Draw a label
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=28, y=15)
splash.append(text_area)

changed=False




while True:
    if changed == True:
        if colormode==1:
            pixels.fill((255,0,0))
        if colormode==2:
            pixels.fill((0,255,0))
        if colormode==3:
            pixels.fill((0,0,255))
        if colormode==4:
            pixels.fill((255,255,255))
        pixels.show()
        changed=False

    if b1.value == False:
        colormode=1
        changed=True
    if b2.value == False:
        colormode=2
        changed=True
    if b3.value == False:
        colormode=3
        changed=True
    if b3.value == True and b2.value==True and b1.value==True:
        colormode=4
        changed=True



    pass
