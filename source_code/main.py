from machine import Pin
from time import sleep, ticks_ms, ticks_diff
from neopixel import NeoPixel
import mora_jai_box as mj


# Fixed LED and initialise NeoPixels
led_builtin = Pin(25, Pin.OUT)
px = NeoPixel(Pin(0),15)

# Map of { GPIO Pin : user input }. Needs editing if pin layout changes
pin_map = {
    '6'  : '1',
    '13' : '2',
    '14' : '3',
    '10' : '4',
    '11' : '5',
    '12' : '6',
    '7'  : '7',
    '8'  : '8',
    '9'  : '9',
    '19' : 'c4',
    '20' : 'c3',
    '21' : 'c2',
    '22' : 'c1'
    }

# If using a different pin layout, the first number inside each set of brackets will need edited.
cor4 = Pin(19, Pin.IN, Pin.PULL_UP)
cor3 = Pin(20, Pin.IN, Pin.PULL_UP)
cor2 = Pin(21, Pin.IN, Pin.PULL_UP)
cor1 = Pin(22, Pin.IN, Pin.PULL_UP)
btn1 = Pin(6, Pin.IN, Pin.PULL_UP)
btn2 = Pin(13, Pin.IN, Pin.PULL_UP)
btn3 = Pin(14, Pin.IN, Pin.PULL_UP)
btn4 = Pin(10, Pin.IN, Pin.PULL_UP)
btn5 = Pin(11, Pin.IN, Pin.PULL_UP)
btn6 = Pin(12, Pin.IN, Pin.PULL_UP)
btn7 = Pin(7, Pin.IN, Pin.PULL_UP)
btn8 = Pin(8, Pin.IN, Pin.PULL_UP)
btn9 = Pin(9, Pin.IN, Pin.PULL_UP)

px.fill((0,0,0))
px.write()

# Startup Animation
for col in mj.tile_colours.values() :
    px.fill(mj.hex_to_rgb(col))
    px.write()
    sleep(0.3)

# Switch pixels off
px.fill((0,0,0))
px.write()


inp_cmd = ''
debounce_time = 200
last_press = ticks_ms()


def callback(pin) :
    global inp_cmd, last_press
    # Ignore rapid triggers
    if ticks_diff(ticks_ms(), last_press) < debounce_time :
        return

    # Get ID of pressed Pin.
    # If KeyError is thrown, uncomment the second p_id declaration and comment out the first.
    msg = f'{pin}'
    p_id = msg.split(',')[0].split('IO')[1]
    #p_id = msg.split(',')[0].split('(')[1]
    inp_cmd = pin_map[p_id]
    last_press = ticks_ms()
    sleep(0.01)
    return

# Setup hardware interrupts
for inp in [cor1,cor2,cor3,cor4,btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9] :
    inp.irq(trigger=Pin.IRQ_RISING, handler=callback)

# Begin main game loop
while True :
    my_game = mj.gameState()
    my_game.start_new_game()
    game_grid = my_game.show_neopixels()
    
    for i,col in enumerate(game_grid) :
        px[i] = col
    px.write()

    while not my_game.v :
        if inp_cmd == '' :
            pass
        else :
            #cmd = input('> ')
            my_game.moves += 1
            my_game.inp(inp_cmd)
            my_game.corner_checks()
            game_grid = my_game.show_neopixels()
            for i,col in enumerate(game_grid) :
                px[i] = col
            px.write()
            inp_cmd = ''
            my_game.v = my_game.check_win()
          
    # Victory Animation - Fill in the box Blue
    sleep(1)
    px.fill((0,0,0))
    for i in range(13) :
        px[i] = mj.hex_to_rgb(pico_tile_colours['B'])
        px.write()
        sleep(0.3)
    sleep(1)
    
        
