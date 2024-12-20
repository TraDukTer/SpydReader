import os
import time
import re
import threading
import keyboard

width = 72 #x coordinate space
height = 20 #y coordinate space
frame = [[]] #width, NB! the x array will contain an array of chars x once anything is drawn
paused = False
delay = 0.1
done = False

def draw_fill(fill_char: str =" ", bg_char: str =None):
    global frame

    frame = [[fill_char for i in range(width)] for i in range(height)]

def draw_row(char: str, ypos: int, start: int =0, end: int =-1):
    global frame
    if end == -1:
        end = width
    frame[ypos] = [char for i in range (start, end)]
#   TODO frame[ypos] = char*(end-start)

def draw_column(char: str, xpos: int, start: int =0, end: int =-1):
    global frame
    if end == -1:
        end = height - 1
    
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

def print_starting(string: str, startingx: int, startingy: int):
    i = 0
    for char in string:
        draw_char(char, startingx + i, startingy)
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
    command = input("To input string to speedread as text, press enter. \nTo read from file, input filename: ")
    if command == "":
        text = input("Input string to speedread: ")
    else:
        while True:
            try:
                with open(f"Input/{command}", "r", encoding="utf8") as file:
                    text = file.read()
                break
            except FileNotFoundError:
                command = input("Input .txt filename with file extension. File must be in the SpydReader Input folder:")
    
    return text

def display_loop(text: str):
    global done
    text = re.split(" |\n", text)
    draw_fill(" ")
    draw_borders()
    while not paused:
        for word in text:
            print_center(word)
            refresh()
            time.sleep(delay)
            print_center(" " * len(word))
            print_starting(f"delay: {str(delay)}s", 3, height - 3)
        done = True

text = input_loop()
display_thread = threading.Thread(target = display_loop(text), name = "display_thread")
display_thread.start()

while not done:
    if keyboard.is_pressed('space'):
        if not paused:
            paused = True
            display_thread.wait()
        else:
            paused = False
            display_thread.notify()
    if keyboard.is_pressed('up arrow'):
        if delay <= 0.01:
            delay -= 0.01
    if keyboard.is_pressed('down arrow'):
        delay += 0.01

display_thread.join()


