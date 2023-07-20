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
import random
import math
import time
import adafruit_fancyled
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

radio_1 = digitalio.DigitalInOut(board.A0) # d25 is A
radio_1.direction = digitalio.Direction.INPUT
radio_1.pull=digitalio.Pull.DOWN

radio_2 = digitalio.DigitalInOut(board.A1) # d24 is C
radio_2.direction = digitalio.Direction.INPUT
radio_2.pull=digitalio.Pull.DOWN

radio_3 = digitalio.DigitalInOut(board.A2) #d11 is B
radio_3.direction = digitalio.Direction.INPUT
radio_3.pull=digitalio.Pull.DOWN # TODO: verify if this was required or not

radio_4 = digitalio.DigitalInOut(board.A3) # d10 is a
radio_4.direction = digitalio.Direction.INPUT
radio_4.pull=digitalio.Pull.DOWN

brightness_switch = digitalio.DigitalInOut(board.D24)
brightness_switch.direction = digitalio.Direction.INPUT
brightness_switch.pull=digitalio.Pull.UP


# --------------------- step 3 - prepare neopixels
# OLD version - board.D12
pixels=neopixel.NeoPixel(board.D25, 192, brightness=0.1, auto_write=False)
pixels.fill((8,8,8))
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
reaction_mode = 0
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
        # note - the reaction length time gets bypassed by blink mode reaction switching
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
reaction= [ reactioncount(0), reactioncount(1), reactioncount(2), reactioncount(3), reactioncount(4)]
# TODO: figure out a way to add variable lengths to each cel
print(reaction)

def loadreactionframe(reactionid, frame):
    img=BMPReader("/img/"+str(reactionid)+"/"+str(frame)+".bmp")
    #img.to_string()
    img_data=img.get_pixels()
    for x in range(0,18):
        for y in range(0,12):
            pix=img_data[x][y]
            pix=( img.get_pixel_r(x,y), img.get_pixel_g(x,y),img.get_pixel_b(x,y))
            #print(pix)
            eyes[y][x]=pix
    del img_data
    del img

loadreactionframe(0,1)
update_eyes(eyes, eyemap, pixels)
pixels.show()
reaction_defaultframetime = 750
reaction_frame = 0 # a running counter, the update function does the math to pick the right frame in sequence
reaction_nextframetime = 0 + reaction_defaultframetime # this get updated by the return from the update function1
reaction_frame_needs_update = True # trigger to make the next image load

next_blink = get_frametime() + 5000 # random.randint(500,3500)
# TODO  reaction mode 4 is blink, add code to make end of reaction go to blink mode for a moment after a reaction times out - DONE
#       however need to add an inhibit variable so that timeout for blink mode doesn't retrigger blink mode - DONE



def reactionframe(reactionid, framecounter):
    #global reaction_defaultframetime
    #global reaction # get from the higher scope
    # TODO: add custom length and flow support
    frameid = framecounter % reaction[reactionid]
    #print("reaction frame " + str(frameid) + " this reaction has " + str(reaction[reactionid]) + " frames") 
    
    if(reactionid==0):
        randomframe = random.randint(1, reaction[reactionid])
        print("random frame: " + str(randomframe))
        loadreactionframe(reactionid, randomframe) # +1 to handle the images being 1..x rather than 0..x, TODO maybe change this 
    else:
        loadreactionframe(reactionid, frameid+1) # +1 to handle the images being 1..x rather than 0..x, TODO maybe change this 

    if(reactionid == 4):
        # blink mode
        return 750
    if (reactionid ==1) or (reactionid == 2) or (reactionid == 3):
        return 250
    else:
        return random.randint(1000,4000) #reaction_defaultframetime # TODO: handle anything custom here

# --------------------- enter loop 

counter=0 # temp for party mode tests
last_reaction = reaction_mode # state varible to ensure we handle button logic properly
print("entering mainloop-----------")

last_brightness=not brightness_switch.value

while True:
    if(last_brightness != brightness_switch.value):
        last_brightness=brightness_switch.value
        if brightness_switch.value==True:
            pixels.brightness=1.0 # setBrightness(255)             
        else:
            pixels.brightness=0.20 # setBrightness(64)


    current_tick = get_frametime()
    elapsed_time = ticks_diff(current_tick, last_tick)
    if elapsed_time >= frame_time:
        frame+=1
        last_tick = current_tick
    if (current_tick >= reaction_nextframetime) and (reaction_frame_needs_update == False):
        reaction_frame += 1
        print("reaction frame update " + str(reaction_frame))
        reaction_frame_needs_update=True


    if radio_1.value==True: # party mode toggle
        #print("party")
        if partybutton_inhibit == False:
            partymode = not partymode
            partybutton_inhibit=True
            partybutton_inhibit_timer=current_tick+1000 # increased from 250
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

    if(next_blink < current_tick):
        if (partymode==True) or (reaction_mode != 0): # (reaction_mode==4): # if we're in party mode, or we're already blinking, defer the blink
            next_blink=current_tick + random.randint(5000,10000)
        else:
            print("blink")
            reaction_mode=4
            reaction_timeout=current_tick+500
            next_blink=current_tick + random.randint(5000,10000)

    
    # handle reaction timeout
    if (reaction_timeout < current_tick) and (reaction_mode != 0): 
        print("reaction timed out " + str(reaction_mode))
        if (reaction_mode == 4): # blink mode times out to idle
            reaction_mode=0
            #reaction_nextframetime=current_tick + random.randint(2000,4000)
            #reaction_timeout = current_tick+random.randint(2000,4000) # this was required because blink return wasn't working
        else:
            reaction_mode=4 # all other reactions time out to blink
            reaction_timeout = current_tick+500
        reaction_frame_needs_update=True
    
        # TODO: send message to screen
    if (last_reaction != reaction_mode): # this ensures that the new reaction gets presented immediately
            last_reaction = reaction_mode
            reaction_frame_needs_update=True
    # handle party mode
    # TODO: Change this to make party mode overwrite default idle mode but allow reactions to occur - DONE
    if(partymode and reaction_mode==0):
        party_submode = int((current_tick / 2000) % 4)
        #print(party_submode)
        #party_submode=4
        if(party_submode == 0):
            counter+=2
            eye1=wheel(counter % 255)
            eye2=wheel((counter + 128) % 255)
            for y in range(0,12):
                for x in range (0,9):
                    eyes[y][x]=eye1
            for y in range(0,12):
                for x in range (9,18):
                    eyes[y][x]=eye2
        elif(party_submode ==1): # TODO: add a secondary multiplier to make these pulse more quickly along side the fade
            for y in range(0,12):  # TODO: make this one switch between up/down modes randomly
                eyecolor = wheel(((counter)+(y*4)) % 255)
                for x in range (0,18):
                    eyes[y][x]=eyecolor
        elif(party_submode ==2): # TODO: make this one go from outside in or inside out
            for y in range(0,12):
                eyecolor = wheel(((counter)+(y*4)) % 255)
                for x in range (0,18):
                    eyes[11-y][x]=eyecolor
        elif(party_submode ==3):
            #print(math.sin(counter))
            for y in range(0,12):
                for x in range (0,18):
                    hue = 4.0 + math.sin((x+counter/5.0) / 2.0) + math.sin(math.cos(((y+counter/2.4) / 2.3))) \
				    + math.cos((x + y) / 3.2) + math.cos(counter/11.0)
                    
                    hue = hue * 32.0
                    #print(hue)
                    eyecolor =  wheel( int(hue))
                    eyes[y][x]=eyecolor
        elif(party_submode ==4):
                
            for y in range(0,12):
                for x in range (0,18):
                    hue = 1 + (math.sin((counter+y)/2.5)*math.cos(x/2))
                    eyecolor=wheel(hue*127)
                    eyes[y][x]=eyecolor


        else:

            for y in range(0,12):
                for x in range (0,18):
                    color = ((counter+x) % 18)* (255/18)
                    if (party_submode==0):
                        eyes[y][x] = (color, color, color)
                    if (party_submode==1):
                        eyes[y][x] = (color, 0, 0)
                    if (party_submode==2):
                        eyes[y][x] = (0, color, 0)
                    if (party_submode==3):
                        eyes[y][x] = (0, 0, color)
                                            


        update_eyes(eyes, eyemap, pixels)
        pixels.show()
        counter+=1
    else:
        if(reaction_frame_needs_update == True):
            #print("reaction frame needs update")
            reaction_nextframetime = current_tick + reactionframe(reaction_mode,reaction_frame)
            reaction_frame_needs_update=False
            update_eyes(eyes,eyemap, pixels)
            pixels.show()

    pass

