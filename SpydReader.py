import os
import time

width = 72 #x coordinate space
height = 20 #y coordinate space
frame = [[]] #width, NB! the x array will contain an array of chars x once anything is drawn

def draw_fill(fill_char: str =" ", bg_char: str =None):
    global frame

    frame = [[fill_char for i in range(width)] for i in range(height)]

def draw_row(char: str, ypos: int, start: int =0, end: int =-1):
    global frame
    if end == -1:
        end = width
    frame[ypos] = [char for i in range (start, end)]

def draw_column(char: str, xpos: int, start: int =0, end: int =-1):
    global frame
    if end == -1:
        end = height - 1
    #implement list comprehension
    for row in frame:
        row[xpos] = char

def draw_char(char: str, xpos: int, ypos: int):
    global frame
    frame[xpos][ypos] = char

def set_resolution(new_width: int, new_height: int):
    global width
    global height

    width = new_width
    height = new_height

def draw_borders():
    draw_column("║", 0)
    draw_column("║", width - 1)
    draw_row("═", 0)
    draw_row("═", height - 1)
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

draw_fill(" ")
draw_borders()
draw_char("#", 1, 2)
refresh()
