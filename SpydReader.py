#############################################################################
#                                                                           #
# SpydReader is a Rapid Serial Visual Presentation reading aid.             #
# Copyright (C) 2025  TraDukTer / J. Suutarinen                             #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.    #
#                                                                           #
# Contact the author via https://github.com/TraDukTer/SpydReader            #
#                                                                           #
#############################################################################

import os
import time
import datetime
import re
import threading
import keyboard
import traceback

class globalVars():
    pass

width = 72 #x coordinate space
height = 20 #y coordinate space
frame = [[]] #width, NB! the y array will contain an array of chars x once anything is draw
gvars = globalVars()
gvars.delay = 100 #delay in milliseconds
gvars.running = threading.Condition()
gvars.paused = False
gvars.exit = False

# Settings

def set_resolution(new_width: int, new_height: int):
    global width
    global height

    width = new_width
    height = new_height

# Display and drawing utilities

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

# Logging utilities

def log(
        message: str = "message undefined", 
        file_name: str = "log.txt", 
        timestamp: bool = True, 
        overwrite: bool = False, 
        headerline: bool = False):
    #Write mode, default "a"; do not overwrite, write to end of file
    open_text_mode = "a"
    if overwrite:
        open_text_mode = "w"
    with open(file_name, open_text_mode) as logfile:
        #Write line of pound signs as a header to mark out an importnat line, if active
        if headerline:
            logfile.write("###############\n")
        #Write timestamp before the log message, if active (default active)
        if timestamp:
            logfile.write(str(datetime.datetime.now()) + "\n")
        logfile.write(message+"\n\n")

def errorlog(message):
    log(message, "errorlog.txt")

# Control utilities

def toggle_pause() -> bool:
    if gvars.paused:
        time.sleep(0.1)
        gvars.paused = False
        print("unpaused")
        gvars.running.notify()
        gvars.running.release()
    elif not gvars.paused:
        gvars.running.acquire()
        gvars.paused = True
        print("paused")
        time.sleep(0.1)

def exit(force: bool = False):
    if not gvars.paused:
        toggle_pause()
    confirm = None
    if not force:
        while True:
            confirm = input("Are you sure you want to quit? (y/n): ")
            if confirm == "y":
                log("Exit confirmed")
                break
            elif confirm == "n":
                log("Exit cancelled")
                break
    else: 
        log("Exit forced")
        confirm = "y"

    if confirm == "y":
        try:
            gvars.exit = True
            toggle_pause()
            toggle_pause()
        except Exception:
            errorlog(f"Following exception thrown on exit\n{str(traceback.format_exc())}")

    log("Exit function end")

# Core functionality loops

def input_loop() -> str:
    log("Input loop start")
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
                continue
    
    log("Input loop end")
    return text

def display_loop(text: str):
    log("Display loop start")
    text = re.split(" |\n", text)
    draw_fill(" ")
    draw_borders()
    for word in text:
        if gvars.exit:
            log("Display loop break")
            break
        with gvars.running:
            while gvars.paused:
                gvars.running.wait()
        print_center(word)
        refresh()
        time.sleep(gvars.delay/1000)
        print_center(" " * len(word))
        print_starting(f"delay: {str(gvars.delay)}ms", 3, height - 3)

    log("Display loop end")

def control_loop():
# TODO: something blocks keyboard interrupt.
    log("Control loop start")
    while not gvars.exit:
        if gvars.exit:
            log("Control loop break")
            break
        keypress = "undefined"
        try: 
            if keyboard.is_pressed('space'):
                keypress = "space"
                toggle_pause()
                continue
            if keyboard.is_pressed('up arrow'):
                keypress = "up"
                if gvars.delay >= 11:
                    gvars.delay -= 10
                elif gvars.delay > 1:
                    gvars.delay -= 1
                time.sleep(0.1)
            if keyboard.is_pressed('down arrow'):
                keypress = "down"
                if gvars.delay < 10:
                    gvars.delay += 1
                else:
                    gvars.delay += 10
                time.sleep(0.1)
            if keyboard.is_pressed('esc'):
                exit()
                continue
        except Exception:
            errorlog(f"Following exception thrown on keypress {keypress}\n{str(traceback.format_exc())}")

    log("Control loop end")

def main():
    try:
        log("Program started", headerline = True)
        text = input_loop()

        log(f"Text of length {len(text)} input")
        display_thread = threading.Thread(target = display_loop, args = (text, ))
        control_thread = threading.Thread(target = control_loop)
        log("Threads started")
        display_thread.start()
        control_thread.start()

        while not gvars.exit:
            time.sleep(100)
    except KeyboardInterrupt:
        log("KeyboardInterrupt caught")
        exit(force = True)
    except Exception:
        errorlog(f"Following exception thrown in main\n{str(traceback.format_exc())}")


    display_thread.join()
    control_thread.join()
    log("Threads joined")

if __name__ == '__main__':
    main()