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


# --------------------- step 1 - prepare eye bitmap translation matrix
        # 0 1 2 3 4 5 6 7 8  9 0 1 2 3 4 5 6 7 
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

        # 0 1 2 3 4 5 6 7 8  9 0 1 2 3 4 5 6 7 
eyes   = [[1,1,0,0,0,0,0,1,1, 1,1,0,0,0,0,0,1,1], # 0 - this is the bitmap array for the eyes. the initial data here is just placeholder
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

def update_eyes(source, mapping, dest):
    for x in range (0,18):
        for y in range (0,12):
            dest[ mapping[y][x] ] = source[y][x]

columndirection=-1
counter=0
y=12

for x in range(0, 18):
    for y_counter in range(0, 12):
        y+=columndirection
        #print (x,y)
        if eyemap[y][17-x] == 0:
            eyemap[y][17-x]=counter
            counter+=1
        else:
            eyemap[y][17-x]=191 #(1 past the end)
    y+=columndirection # not sure why this extra one is needed
    if(columndirection==1):
        columndirection=-1
    else:
        columndirection=1


# --------------------- step 2 - prepare buttons for internal and radio

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

radio_1 = digitalio.DigitalInOut(board.D25) # d25 is A
radio_1.direction = digitalio.Direction.INPUT
radio_1.pull=digitalio.Pull.DOWN

radio_2 = digitalio.DigitalInOut(board.D24) # d24 is C
radio_2.direction = digitalio.Direction.INPUT
radio_2.pull=digitalio.Pull.DOWN

radio_3 = digitalio.DigitalInOut(board.D11) #d11 is B
radio_3.direction = digitalio.Direction.INPUT
#radio_3.pull=digitalio.Pull.DOWN

radio_4 = digitalio.DigitalInOut(board.D10) # d10 is a
radio_4.direction = digitalio.Direction.INPUT
radio_4.pull=digitalio.Pull.DOWN



# --------------------- step 3 - prepare neopixels

pixels=neopixel.NeoPixel(board.D12, 192, brightness=0.2, auto_write=False)
pixels.fill((16,0,0))
pixels.show()
displayio.release_displays()
# --------------------- step 4 - prepare internal display


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


# --------------------- step 5 - enter loop 

while True:
    if radio_1.value==True:
        pixels[1]=(255,0,0)
    else:
        pixels[1]=(0,0,0)

    if radio_2.value==True:
        pixels[2]=(0,255,0)
    else:
        pixels[2]=(0,0,0)
   
    if radio_3.value==True:
        pixels[3]=(255,255,0)
    else:
        pixels[3]=(0,0,0)

    if radio_4.value==True:
        pixels[4]=(0,0,255)
    else:
        pixels[4]=(0,0,0)

    pixels.show()
    pass




colormode=1
changed=False
counter=0
while True:
    for y in range(0,12):
        for x in range (0,18):
            color = ((counter+x) % 18)* (255/18)
            eyes[y][x] = (color, color, color )
    update_eyes(eyes, eyemap, pixels)
    pixels.show()
    counter+=1
    pass


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
