import os
import time
import re

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
    frame[ypos][xpos] = char

def print_center(string: str):
    ycen = height // 2
    xcen = width // 2
    string_start = xcen - (len(string) // 2)

    i = 0
    for char in string:
        draw_char(char, string_start + i, ycen)
        i += 1

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
    draw_char("╗", -1, 0)
    draw_char("╚", 0, -1)
    draw_char("╝", -1, -1)

def refresh():
    frame_str = ""
    for row in frame:
        for char in row:
            frame_str += char
        frame_str += "\n"
    os.system('cls')
    print(frame_str)

def input_loop() -> str:
    command = input("To input string to speedread as text, press enter. To read from file, input filename: ")
    if command == "":
        text = input("Input string to speedread: ")
    else:
        while True:
            try:
                file = open(command, "r", encoding="utf8")
                text = file.read()
                file.close()
                break
            except FileNotFoundError:
                command = input("Input .txt filename with file extension. File must be in the same directory as SpydReader:")
            i += 1
    
    return text
        

        
text = input_loop()
text = re.split(" |\n", text)
draw_fill(" ")
draw_borders()
for word in text:
    print_center(word)
    refresh()
    time.sleep(0.1)
    print_center(" " * len(word))
