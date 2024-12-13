import os

width = 72 #x coordinate space
height = 20 #y coordinate space
frame = [[]] #width, NB! the x array will contain an array of chars x once anything is drawn

def draw_fill(fill_char: str =" ", bg: bool =False, bg_char: str =None):
    global frame

    frame = [[fill_char for i in range(width)] for i in range(height)]

def draw_char(char: str, xpos: int, ypos: int):
    global frame
    frame[xpos][ypos] = char

def set_resolution(new_width: int, new_height: int):
    global width
    global height

    width = new_width
    height = new_height

def draw_borders():
    draw_char("╔", 0, 0)
    draw_char("╗", 0, -1)
    draw_char("╚", -1, 0)
    draw_char("╝", -1, -1)

def refresh():
    os.system('cls')
    for y in frame:
        for char in y:
            print(char, end="")
        print("")

draw_fill()
draw_borders()
draw_char("#", 1, 2)
refresh()