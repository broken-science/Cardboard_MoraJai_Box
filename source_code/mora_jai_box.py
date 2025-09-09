# coding: utf-8

'''
Play a Mora Jai puzzle box from Blue Prince. Use the colour behaviours to get the winning colour into each corner.


BLACK  - K - Cycle that row one step to the right.
BLUE   - B - Mimic behaviour of centre tile.
GREEN  - G - Swap with tile opposite.
OFF    - - - do nothing.
ORANGE - O - If flanked by two or more tiles of the same colour, adopt that colour.
RED    - R - Change all black tiles to red.
PURPLE - V - Swap with tile below (move down)
PINK   - P - Cycle surrounding tiles clockwise.
WHITE  - W - Toggle itself and neighbouring white tiles on/off.
YELLOW - Y - Swap with tile above (move up)

The Game state is stored as a list of 13 strings.
Tiles are laid out in a 3x3 grid at indices 0-8.
[0] [1] [2]
[3] [4] [5]
[6] [7] [8]

Corners are appended to the end of the list as follows -
[09]    [10]
    game
    grid
[11]    [12]

To win, all four corner tiles must match the colour in that corner of the game grid. 0==9, 2==10, 6==11, 8==12.


TO DO : 
 - Fold button presses into gameState class.
 - Add the option to use DIP switches to toggle difficulty and skip solved boxes.
'''
# Module Imports
from random import choice

from game_boxes import house, sanctum, aries_court, atelier, chandler_challenge

# Comment out from before a + symbol to restrict more difficult puzzles
boxes = list(house.values()) + list(sanctum.values()) + list(aries_court.values()) + list(atelier.values()) + list(chandler_challenge.values())

available_colours = ['K', 'B', 'G', '-', 'O', 'P', 'V', 'W', 'Y']

# List of tiles which surround each tile in clockwise order.
pink_moves = [
  [1,4,3],
  [2,5,4,3,0],
  [5,4,1],
  [0,1,4,7,6],
  [0,1,2,5,8,7,6,3],
  [8,7,4,1,2],
  [3,4,7],
  [3,4,5,8,6],
  [7,4,5]
  ]


# List of which tiles neighbour each tile.
flank_checks = [
  [1,3],
  [0,2,4],
  [1,5],
  [0,4,6],
  [1,3,5,7],
  [2,4,8],
  [3,7],
  [4,6,8],
  [5,7]
  ]


# Hexcodes for each colour which a tile can be
tile_colours = {
  'K' : '#000000',
  'B' : '#0000FF',
  'G' : '#00FF00',
  '-' : '#101010',
  'O' : '#F45500',
  'R' : '#FF0000',
  'V' : '#490089',
  'P' : '#E600FF',
  'W' : '#D0D0D0',
  'Y' : '#FFFF00'
    }

# Emoji heart tiles for playing in a terminal.
colour_tiles = {
  'K' : '🖤',
  'B' : '💙',
  'G' : '💚',
  '-' : '🔘',
  'O' : '🧡',
  'R' : '❤️',
  'V' : '💜',
  'P' : '💖',
  'W' : '🤍',
  'Y' : '💛'
  }


def hex_to_rgb(hexcode: str): # Convert Hex Codes to RGB for displaying on Neopixels
  r,g,b = int(hexcode[1:3],16), int(hexcode[3:5],16), int(hexcode[5:7],16)
  return ((r,g,b))

def half_bright(inp) : # Half the luminance of a passed colour.
  return tuple(x//2 for x in inp)

def col_avg(c1,c2) : # Average out two colours - for non-activated corners.
    half_c1 = half_bright(c1)
    return tuple((x+y)//2 for (x,y) in zip(half_c1,c2))


# Handle Changes to game board  
def cycle_right(tiles: list[str]) -> list[str] :
  # Move the colour at each index to the position of the following index. EG [ R G B ] becomes [ B R G ]
  return tiles[-1:] + tiles[:-1]

def cycle_left(tiles: list[str]) -> list[str] :
  return tiles[1:] + tiles[0]

def swap(grid: list[str], i: int, j: int) -> list[str] :
  temp = grid[i]
  grid[i] = grid[j]
  grid[j] = temp
  return grid

# Move the tiles at a list of positions to the next position along.
def cycle_tiles(grid: list[str], tiles: list[int], cw=True) -> list[str] :
  if cw:
    tiles = tiles[::-1]
  for i in range(len(tiles)-1) :
    swap(grid, tiles[i], tiles[i+1])
  return grid

# Flip a tile between on and off
def toggle_tile(grid: list[str], pos: int, col: str) :
  if grid[pos] == col :
    grid[pos] = '-'
  else :
    grid[pos] = col
  return grid

# Interrogate a list to determine if there is a clear majority of similar entries.
def get_majority(fl) :
  fl.sort()
  tests = [len(fl), len(set(fl))] # Compare number of entries with number of unique entries.
  if tests == [2,1] : # 2 neighbours, the same
    return fl[0]
  elif tests == [3,1] or tests == [3,2] : # 3 neighbours, all one or two colours.
    return fl[1]
  elif tests == [4,1] : # Four neighbours, all one colour.
    return fl[0]
  elif tests == [4,2] and fl[1] == fl[2] : # 3 neighbours the same colour, fails if there are 2x2 colours.
    return fl[1]
  elif tests == [4,3] : # 2 neighbours the same but 3 distinct neighbour states
    cycled = fl[1:] + [fl[0]] # Move first element to last place, the majority tile will overlap.
    matches = []
    for (x,y) in zip(fl,cycled) :
      if x == y :
        matches.append(x)
    if matches == [] :
      matches = ['']
    return matches[0]
  else :
    return ''

# Deal with Inputs - Colour behaviours
def press_black(grid: list[str], pos: int) : # Cycle row of pressed button one step to the right.
  line = pos // 3
  cycle_tiles(grid, [3*line,3*line+1,3*line+2], True)
  return grid
  
def press_blue(grid: list[str], i: int) : # Check which colour is index 4 and act as if blue is that colour.
  cen = grid[4]
  if cen == 'K' :
    grid = press_black(grid, i)
  elif cen == 'B' :
    pass
  elif cen == 'G' :
    grid = press_green(grid, i)
  elif cen == '-' :
    grid = press_off(grid, i)
  elif cen == 'O' :
    grid = press_orange(grid, i)
  elif cen == 'R' :
    grid = press_red(grid, i)
  elif cen == 'V' :
    grid = press_purple(grid, i)
  elif cen == 'P' :
    grid = press_pink(grid, i)
  elif cen == 'W' :
    grid = press_white(grid, i)
  elif cen == 'Y' :
    grid = press_yellow(grid, i)
  else :
    pass
  return grid

def press_green(grid: list[str], pos: int) : # Swap pressed tile with one directly opposite
  if pos != 4 :
    swap(grid, pos, 8-pos)
  return grid

def press_off(grid: list[str], pos: int) : # Do nothing
  return grid

def press_orange(grid: list[str], pos: int) : # Adopt the coour of the majority of neighbours
  flanks = [grid[i] for i in flank_checks[pos]]
  maj = get_majority(flanks)
  print(f'{maj}: majority')
  if maj != '':
    grid[pos] = maj
  return grid

def press_red(grid: list[str], pos: int) : # Change all black tiles to red and all white tiles to black
  corners = grid[9:]
  new_grid = ['R' if x == 'K' else x for x in grid[:9]]
  print()
  grid = ['K' if x == 'W' else x for x in new_grid]
  return grid + corners

def press_purple(grid: list[str], pos: int) : # Swap purple tile with one directly beiow. Do nothing if purple on bottom row.
  if pos < 6 :
    swap(grid, pos, pos+3)
  return grid

def press_pink(grid: list[str], pos: int) : # Cycle surrounding tiles clockwise around pressed tile.
  grid = cycle_tiles(grid, pink_moves[pos], True)
  return grid

def press_white(grid: list[str], pos: int) : # Toggle neighbouring white/off tiles in a + pattern.
  col = grid[pos] # Should only ever be 'W' or 'B'
  grid = toggle_tile(grid, pos, col)
  for tile in flank_checks[pos] :
    if grid[tile] in [col,'-'] :
      grid = toggle_tile(grid, tile, col)
  return grid
  
def press_yellow(grid: list[str], pos: int) : # Swap with tile above. Do nothing if on top row.
  if pos > 2 :
    swap(grid, pos, pos-3)
  return grid


# ------------------------------------

# Class to store information about a particular game
class gameState :
  def __init__(self) :
    return
  
  def start_new_game(self) :
    '''
    Begins a new game for this instance of the gameState.
    Resets move counter and copies the start configuration to start_grid.
    '''
    # self.grid = choice(boxes)[:]
    self.grid = [i for i in choice(boxes)] # If stored as a string
    self.moves = 0
    self.corners = [False, False, False, False]
    self.start_grid = self.grid[:]
    self.v = False
    self.wrongs = 0
  
  def print_to_screen(self) :
    '''
    Prints the present gameState to the terminal.
    Heart will be printed if corner is selected, else the colour code is shown.
    '''
    disp_corners = [colour_tiles[self.grid[i+9]] if self.corners[i] else self.grid[i+9] for i in range(4)]
    #print(disp_corners)
    print([disp_corners[0]] + [' ' for _ in range(3)] + [disp_corners[1]])
    for i in range(3) :  
      print([' '] + [colour_tiles[x] for x in self.grid[3*i:3*i+3]] + [' '])
    print([disp_corners[2]] + [' ' for _ in range(3)] + [disp_corners[3]])
    return
    
  def game_reset(self) :
    '''
    gameState,game_reset()
    Takes no arguments. Resets the current game in progress to the initial grid.
    No new game is generated.
    '''
    self.grid = self.start_grid[:]
    self.moves = 0
    self.wrongs = 0
    self.corners = [False, False, False, False]
    return

  def corner_inp(self,n) :
    '''
    Corner Inputs. If colour matches target, mark True. Check we are in the initial state and increment a counter if so.
    Else, simply reset the current game.
    '''
    grid_corners = [self.grid[i] for i in [0,2,6,8]] # Extract corner values from game grid
    if grid_corners[n] == self.grid[n+9] :
      self.corners[n] = True # Set True if tiles match
    elif self.grid == self.start_grid : # Are we already in a start state?
      self.wrongs += 1 # Increment counter towards refresh scenario
      self.corners = [False, False, False, False]
    else :
      self.game_reset()
      
    # Choose a random new game after a number of wrong presses
    if self.wrongs >= 5 :
      self.start_new_game()
      return
  
  def corner_checks(self) :
    '''
    Checks corners after each button press and flags any which no longer match their corresponding game tile.
    '''
    get_corners = [self.grid[i] for i in [0,2,6,8]]
    for i in range(4) :
      if self.corners[i] :
        self.corners[i] = get_corners[i] == self.grid[i+9]
    #print(get_corners, self.grid[9:],self.corners)
    return

  def inp(self, cmd) :
    '''
    Input handler.
    '''
    if self.v: # Do nothing if playing win animation
      return
    
    cmd = cmd.lower()
    if cmd.startswith('q') :
      exit()
    for n in ['1','2','3','4','5','6','7','8','9'] :
      if cmd == n:
        i = int(n)-1 # Tiles are indexed 0-8 but players input 1-9 in a phone keypad style.
        col = self.grid[i]
        print(f'Tile {n} is {colour_tiles[col]}')
        if col == 'K' :
          self.grid = press_black(self.grid, i)
        elif col == 'B' :
          self.grid = press_blue(self.grid, i)
        elif col == 'G' :
          self.grid = press_green(self.grid, i)
        elif col == '-' :
          self.grid = press_off(self.grid, i)
        elif col == 'O' :
          self.grid = press_orange(self.grid, i)
        elif col == 'R' :
          self.grid = press_red(self.grid, i)
        elif col == 'V' :
          self.grid = press_purple(self.grid, i)
        elif col == 'P' :
          self.grid = press_pink(self.grid, i)
        elif col == 'W' :
          self.grid = press_white(self.grid, i)
        elif col == 'Y' :
          self.grid = press_yellow(self.grid, i)
        else :
          pass
      
    for n in ['c1','c2','c3','c4'] : # Corner buttons.
      if cmd == n :
       i = int(n[1])-1
       print(f'Corner {i} is {self.grid[i+9]}')
       self.corner_inp(i)
    
    return
    
# Write out gameState in the order of NeoPixels. The order of neopix_order may need editing depending on 
  def show_neopixels(self) :
    neopix_order = [9,0,1,2,10,5,4,3,11,6,7,8,12]
    pix_order = [hex_to_rgb(tile_colours[self.grid[i]]) for i in neopix_order]
    for i,state in zip([0,4,8,12],self.corners) :
      if not state :
        pix_order[i] = col_avg(pix_order[i],hex_to_rgb(tile_colours['-']))
    #print(pix_order)
    return pix_order
    
  def check_win(self) :
    return self.corners == [True, True, True, True]
    
# ----------------------------------------

# Only run this code if not importing the game
if __name__ == '__main__' :
  while True:
  # Initialise the game
    gg = gameState()
    gg.start_new_game()
    
    while not gg.v :
      gg.print_to_screen()
      cmd = input('> ')
      gg.moves += 1
      gg.inp(cmd)
      gg.corner_checks()
      gg.v = gg.check_win()
  
    print(f'Solved in {gg.moves} moves!')
