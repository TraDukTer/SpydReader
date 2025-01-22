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
    
    def __init__(self):
        self.delay = 100 #delay in milliseconds
        self.seek_increment = 5
        self.may_run = threading.Event()
        self.may_run.set()
        self.exit = False
        self.width = 72 #x coordinate space
        self.height = 20 #y coordinate space
        self.frame = [[]] # NB! the y array contains arrays of x chars

gvars = globalVars()

# Display and drawing utilities

def draw_fill(fill_char: str =" ", bg_char: str =None):
    gvars.frame = [[fill_char for _ in range(gvars.width)] for i in range(gvars.height)]
#   TODO: bg_char

def draw_row(char: str, ypos: int, start: int = 0, end: int = -1):
    if end == -1:
        end = gvars.width
    gvars.frame[ypos] = [char for _ in range (start, end)]
#   TODO fix start-end, implement frame[ypos] = char*(end-start)

def draw_column(char: str, xpos: int, start: int =0, end: int =-1):
    if end == -1:
        end = gvars.height - 1
    
    for row in gvars.frame:
        row[xpos] = char
#   TODO: start-end

def draw_char(char: str, xpos: int, ypos: int):
    gvars.frame[ypos][xpos] = char

def print_center(string: str):
    ycen = gvars.height // 2
    xcen = gvars.width // 2
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

def print_in_dialog(string: str):
    xcen = gvars.width // 2
    ystart = 5
    dialogbox_start = xcen - (len(string) // 2) - 1

#   TODO: handle multiple lines
#   draw the left edge of the dialog box with box-drawing characters
    draw_char("╔", dialogbox_start, ystart)
    draw_char("║", dialogbox_start, ystart + 1)
    draw_char("╚", dialogbox_start, ystart + 2)

#   draw the right edge of the dialog box with box-drawing characters
    draw_char("╗", dialogbox_start + len(string) + 1, ystart)
    draw_char("║", dialogbox_start + len(string) + 1, ystart + 1)
    draw_char("╝", dialogbox_start + len(string) + 1, ystart + 2)

    i = 1
    for char in string:
        draw_char("═", dialogbox_start + i, ystart)
        draw_char(char, dialogbox_start + i, ystart + 1)
        draw_char("═", dialogbox_start + i, ystart + 2)
        i += 1

    refresh()

# TODO: implement dialogs as class
def clean_up_dialog(string: str):
    xcen = gvars.width // 2
    ystart = 5
    dialogbox_start = xcen - (len(string) // 2) - 1
    bg_char = " "

    i = 0
    for _ in f" {string} ":
        draw_char(bg_char, dialogbox_start + i, ystart)
        draw_char(bg_char, dialogbox_start + i, ystart + 1)
        draw_char(bg_char, dialogbox_start + i, ystart + 2)
        i += 1

    refresh_UI_elements()

def draw_borders():
    draw_column("║", 0)
    draw_column("║", gvars.width - 1)
    draw_row("═", 0)
    draw_row("═", gvars.height - 1)
    draw_char("╔", 0, 0)
    draw_char("╗", -1, 0)
    draw_char("╚", 0, -1)
    draw_char("╝", -1, -1)

def refresh():
    # TODO: lock printing while updating frame.str
    frame_str = ""
    for row in gvars.frame:
        for char in row:
            frame_str += char
        frame_str += "\n"
    os.system('cls')
    print(frame_str)

def refresh_UI_elements():
    # TODO: how to lock printing to stop jumbled words without locking update to length of delay
    word = gvars.text[gvars.word_index]
    print_center(word)
    delay_string = f"delay: {str(gvars.delay)}ms"
    print_starting(delay_string, 3, gvars.height - 3)
    refresh()
    time.sleep(gvars.delay/1000)
    print_center(" " * len(word))
    print_starting(" " * len(delay_string), 3, gvars.height - 3)


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
        print_in_dialog("PAUSED")
        return False
    else:
        gvars.may_run.set()
        clean_up_dialog("PAUSED")
        return True

@loggable_controller
def increase_delay():
    gvars.delay += 10 if gvars.delay >= 10 else 1

def get_appropriate_increment() -> int:
    if gvars.may_run.is_set():
        return gvars.seek_increment
    else:
        return 1

@loggable_controller
def rewind():
    increment = get_appropriate_increment()
    if gvars.word_index - increment >= 0:
        gvars.word_index -= increment
    else:
        gvars.word_index = 0
    refresh_UI_elements()

@loggable_controller
def skip_forward():
    increment = get_appropriate_increment()
    if gvars.word_index + increment < len(gvars.text) -1:
        gvars.word_index += increment
    else:
        gvars.word_index = len(gvars.text) -1
    refresh_UI_elements()

@loggable_controller
def decrease_delay():
    if gvars.delay > 0:
        gvars.delay -= 10 if gvars.delay > 11 else 1

@loggable_controller
def signal_exit(force: bool = False):
    log("Exit function start")

    if gvars.may_run.is_set():
        gvars.may_run.clear()

    if not force:
        print_in_dialog("Do you want to exit program (y/n)")
        while True:
            try:
                confirm = input("(y/n): ")
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
        clean_up_dialog("Do you want to exit program (y/n)")
    else:
        log("Exit forced")
        confirm = "y"

    try:
        if confirm == "y":
            gvars.exit = True
            if not gvars.may_run.is_set():
                if gvars.word_index > 0:
                    gvars.word_index -= 1
                gvars.may_run.set()
        elif confirm == "n":
            if gvars.word_index > 0:
                gvars.word_index -= 1
            gvars.may_run.set()
            toggle_pause()
    except Exception:
        errorlog(f"Following exception raised on exit\n{str(traceback.format_exc())}")

    log("Exit function end")

@loggable_controller
def set_resolution(new_width: int, new_height: int):

    gvars.width = new_width
    gvars.height = new_height

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
    gvars.text = [word for word in re.split(" |\n", text) if word]
    draw_fill(" ")
    draw_borders()
    gvars.word_index = 0
    while gvars.word_index < len(gvars.text)-1:
        # break loop if main thread asks to exit
        if gvars.exit:
            log("Display loop break")
            break
        # wait if main thread has paused asked to pause and until it asks to unpause
        gvars.may_run.wait()
        refresh_UI_elements()
        gvars.word_index += 1

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
    keyboard.add_hotkey('left', rewind)
    keyboard.add_hotkey('right', skip_forward)

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
