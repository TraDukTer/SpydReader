import os

width = 64 #x coordinate space
height = 40 #y coordinate space
frame = [[]] #width, NB! the x array will contain an array of chars x once anything is drawn

def draw_fill(fill_char: str =" ", bg: bool =False, bg_char: str =None):
    global frame
    frame = [[fill_char]*height]*width

def draw_char(char: str, xpos: int, ypos: int):
    global frame
    pass

def set_resolution(new_width: int, new_height: int):
    global width
    global height

    width = new_width
    height = new_height

def draw_borders():
    pass

def refresh():
    os.system('cls')
    for y in frame:
        for char in y:
            print(char, end="")
        print("")

set_resolution(20, 72)
draw_fill("#")
draw_char("@", 3, 6)
refresh()
