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
import signal
import traceback

def get_decorator():
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                errorlog(f"Following exception raised by controller:\n{traceback.format_exc()}")
                return None
        return new_func
    return decorator

loggable_controller = get_decorator()

class globalVars():
    pass

gvars = globalVars()
gvars.delay = 100 #delay in milliseconds
gvars.may_run = threading.Event()
gvars.may_run.set()
gvars.exit = False

width = 72 #x coordinate space
height = 20 #y coordinate space
frame = [[]] #width, NB! the y array will contain an array of chars x once anything is draw

# Display and drawing utilities

def draw_fill(fill_char: str =" ", bg_char: str =None):
    global frame

    frame = [[fill_char for i in range(width)] for i in range(height)]
#   TODO: bg_char

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
#   TODO: start-end

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
        #Write line of pound signs as a header to mark out an important line, if active
        if headerline:
            logfile.write("###############\n")
        #Write timestamp before the log message, if active (default active)
        if timestamp:
            logfile.write(str(f"{datetime.datetime.now()}\n"))
        logfile.write(f"{message}\n\n")

def errorlog(message: str = ""):
    log(message, "errorlog.txt")

# Control utilities

@loggable_controller
def toggle_pause() -> bool:
    if gvars.may_run.is_set():
        gvars.may_run.clear()
        print("paused")
        return False
    else:
        gvars.may_run.set()
        print("unpaused")
        return True

@loggable_controller
def increase_delay():
    gvars.delay += 10 if gvars.delay >= 10 else 1

@loggable_controller
def decrease_delay():
    if gvars.delay > 0:
        gvars.delay -= 10 if gvars.delay > 11 else 1

@loggable_controller
def signal_exit(force: bool = False):
    log("Exit function start")

    if gvars.may_run.is_set():
        toggle_pause()

    if not force:
        while True:
            try:
                confirm = input("Do you want to exit program (y/n): ")
            except EOFError:
                errorlog(f"Following exception raised on exit\n{str(traceback.format_exc())}")
                log("Exit forced")
                confirm = "y"
                break
            if confirm == "y":
                log("Exit confirmed")
                break
            elif confirm == "n":
                log("Exit cancelled")
                break
    else:
        log("Exit forced")
        confirm = "y"

    try:
        if confirm == "y":
            gvars.exit = True
            if not gvars.may_run.is_set():
                toggle_pause()
    except Exception:
        errorlog(f"Following exception raised on exit\n{str(traceback.format_exc())}")

    log("Exit function end")

@loggable_controller
def set_resolution(new_width: int, new_height: int):
    global width
    global height

    width = new_width
    height = new_height

# _None is only included because the signal library calls signal.signal() with two arguments.
@loggable_controller
def ctrl_c(signum, _None):
    log("Keyboard interrupt detected")
    if signum == 2:
        signal_exit(force=True)


# Core functionality

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
        gvars.may_run.wait()
        print_center(word)
        refresh()
        time.sleep(gvars.delay/1000)
        print_center(" " * len(word))
        print_starting(f"delay: {str(gvars.delay)}ms", 3, height - 3)

    if not gvars.exit:
        signal_exit()
    log("Display loop end")


def main():
    log("Program started", headerline = True)
    text = input_loop()
    log(f"Text of length {len(text)} input")

    display_thread = threading.Thread(target = display_loop, args = (text, ))

    display_thread.start()
    log("Display thread started")

    signal.signal(signal.SIGINT, ctrl_c)

    keyboard.add_hotkey('space', toggle_pause)
    keyboard.add_hotkey('up', decrease_delay)
    keyboard.add_hotkey('down', increase_delay)
    keyboard.add_hotkey('esc', signal_exit)

    # Don't try to join Display thread until exit is intended
    while not gvars.exit:
        pass

    log("Waiting for display thread to exit")
    exited = False
    while not exited:
        try:
            display_thread.join()
            log("Display thread exited")
            exited = True
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    try:
        main()
    except Exception:
        errorlog(f"Following exception raised in main:\n {traceback.format_exc()}")
        log("Main thread exited with exception")
        signal_exit(force=True)
