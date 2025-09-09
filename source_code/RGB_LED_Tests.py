from machine import Pin
from time import sleep
from neopixel import NeoPixel

px = NeoPixel(Pin(0),15,bpp=3)

colours = {
    'R' : (255,0,0),
    'O' : (255,128,0),
    'Y' : (217,255,0),
    'G' : (0,255,0),
    'B' : (0,0,255),
    'I' : (0,179,255),
    'V' : (100,0,255),
    'W' : (255,255,255),
    }

for _ in range(10) :
    for clr in colours.values() :
        px.fill(clr)
        px.write()
        sleep(1)

px.fill((0,0,0))
px.write()