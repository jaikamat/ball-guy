# robocopy . d:\ /mir /xd .git
# git add .
# git commit -m ""
# git push origin main

import board
import os
import supervisor
import displayio
import digitalio
import terminalio
import neopixel
from adafruit_display_text import label
from bmp_reader import BMPReader

import adafruit_displayio_ssd1306

# functions for timekeeping
_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

_TICKS_STARTTIME = supervisor.ticks_ms()

def ticks_add(ticks, delta):
    "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (ticks + delta) % _TICKS_PERIOD

def ticks_diff(ticks1, ticks2):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff

def get_frametime():
    return ticks_diff(supervisor.ticks_ms(), _TICKS_STARTTIME)

# functions for light, etc
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) # if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)




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
radio_3.pull=digitalio.Pull.DOWN # TODO: verify if this was required or not

radio_4 = digitalio.DigitalInOut(board.D10) # d10 is a
radio_4.direction = digitalio.Direction.INPUT
radio_4.pull=digitalio.Pull.DOWN



# --------------------- step 3 - prepare neopixels

pixels=neopixel.NeoPixel(board.D12, 192, brightness=0.2, auto_write=False)
pixels.fill((16,0,0))
pixels.show()
displayio.release_displays()
# --------------------- step 4 - prepare internal display

# TODO: Get rid of all the extra stuff here
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
# --------------------- prepare state machine

state_display = 0 # 0-3 to match the RF token
state_brightness = 0 # 0-3 for low/mid/high

desired_fps = 30
frame_time = 1000 / desired_fps

last_tick = get_frametime()
frame = 0

current_tick=0 # make this a global
time_screentimeoutlength = 1000 # default length of mode text timeout on screen
flag_update_text = True # preset to show initial start text
flag_update_text_countingdown = True
state_last_text = 0 
time_screentimeout = last_tick+time_screentimeoutlength

# for reaction mode, 0 is neutral, and 1-2-3 are three different emotions. code is set to start as if the first button got clicked
reaction_length=2500 
reaction_mode = 1
reaction_timeout = last_tick + reaction_length

partymode = False               # party mode is a toggle
partybutton_inhibit = False     # this gets set when the party mode button is detected, and makes it so that the party mode won't toggle until the button has been let go
                                # this will prevent rapid cycling when the button is held, although a time based cooldown might be required to prevent bounce
partybutton_inhibit_timer = current_tick # --- a cooldown was required
# inhibit and bounce protection is not needed for the button, because the initial keypress just sets that reaction mode and updates the cooldown timer
# and it'll turn off on its own. this allows the reaction to stay longer if the button is held down.
# limitation - this means the reaction can only be a repeating cycle rather than a specific animation because that would need more time keeping.

# functions for setting reaction mode (code dupication reduction)
def set_reaction(mode):
        global reaction_mode
        global reaction_timeout
        reaction_mode=mode
        reaction_timeout=current_tick + reaction_length # ew a function accessing global state
        # TODO: add call to trigger the internal display
        # print("set reaction mode")
# --------------------- prepare reactions

def reactioncount(reactionid):
    files = os.listdir("/img/" + str(reactionid))
    cels = len(files)
    for file in files:
        print("found cel:" + file)
    return cels
reaction= [ reactioncount(0), reactioncount(1), reactioncount(2), reactioncount(3)]
# TODO: figure out a way to add variable lengths to each cel
print(reaction)

def loadreactionframe(reactionid, frame):
    img=BMPReader("/img/"+str(reactionid)+"/"+str(frame)+".bmp")
    img_data=img.get_pixels()
    for x in range(0,18):
        for y in range(0,12):
            eyes[y][x]=img_data[x][y]
    del img_data
    del img

loadreactionframe(0,1)   
update_eyes(eyes, eyemap, pixels)
pixels.show()

while True:
    pass

reaction_defaultframetime = 1000
reaction_frame = 0
reaction_nextframetime = current_tick + reaction_defaultframetime
# --------------------- enter loop 

counter=0 # temp for party mode tests

while True:
    current_tick = get_frametime()
    elapsed_time = ticks_diff(current_tick, last_tick)
    if elapsed_time >= frame_time:
        frame+=1
        last_tick = current_tick

    if radio_1.value==True: # party mode toggle
        #print("party")
        if partybutton_inhibit == False:
            partymode = not partymode
            partybutton_inhibit=True
            partybutton_inhibit_timer=current_tick+250
            print("toggled party mode")
            # TODO: Send message to screen to report that party mode was toggled
        else:
            if(current_tick > partybutton_inhibit_timer):
                partybutton_inhibit=False   
    if radio_2.value==True:
        set_reaction(1)
    if radio_3.value==True:
        set_reaction(2)
    if radio_4.value==True:
        set_reaction(3)

    # handle reaction timeout
    if (reaction_timeout < current_tick) and (reaction_mode != 0): 
        print("reaction timed out " + str(reaction_mode))
        reaction_mode=0
    
        # TODO: send message to screen

    # handle party mode
    if(partymode):
        for y in range(0,12):
            for x in range (0,18):
                color = ((counter+x) % 18)* (255/18)
                eyes[y][x] = (color, color, color )
        update_eyes(eyes, eyemap, pixels)
        pixels.show()
        counter+=1

    else:
        if reaction_mode==0:
            pixels.fill((64,64,64))
        elif reaction_mode==1:
            pixels.fill((64,0,0))
        elif reaction_mode==2:
            pixels.fill((0,64,0))
        elif reaction_mode==3:
            pixels.fill((0,0,64))


    pixels.show()
    pass

