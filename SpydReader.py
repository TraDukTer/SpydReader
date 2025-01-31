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
# enable ANSI escape sequences
os.system("")
import inspect
import time
import datetime
import re
import threading
import keyboard
import signal
import traceback
from typing import Self


def loggable_controller(func):
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            errorlog(f"Following exception raised by controller:\n{traceback.format_exc()}")
            return None
    return new_func

class globalVars():
    
    def __init__(self):
        self.delay = 100 #delay in milliseconds
        self.seek_increment = 5

        self.debug = True

        self.may_run = threading.Event()
        self.may_run.set()
        self.exit = False

        self.width = 72 #x coordinate space
        self.height = 20 #y coordinate space
        self.frame = [[]] # NB! the y array contains arrays of x chars

        self.text = None
        self.word_index = None
        self.previous_index = None

        self.dialogs: list[Dialog] = []

gvars = globalVars()

class Dialog():
    def __init__(self, message: str):
        self.message = message

    def __eq__(self, other: Self):
        if isinstance(other, self.__class__):
            return self.message == other.message
        else:
            return NotImplemented

    def __ne__(self, other: Self):
        return not self.__eq__(self, other)

    def show(self):
        if self not in gvars.dialogs:
            gvars.dialogs.append(self)
        refresh_UI_elements()

    def hide(self):
        if self in gvars.dialogs:
            gvars.dialogs.remove(self)
        self.clean_up()
        refresh_UI_elements()

    def draw(self):
        xcen = gvars.width // 2
        ystart = 5
        dialogbox_start = xcen - (len(self.message) // 2) - 1

        # TODO: handle multiple lines
        draw_starting(f"╔{"═" * len(self.message)}╗", dialogbox_start, ystart)
        draw_starting(f"║{self.message}║", dialogbox_start, ystart + 1)
        draw_starting(f"╚{"═" * len(self.message)}╝", dialogbox_start, ystart + 2)

    def clean_up(self):
        xcen = gvars.width // 2
        ystart = 5
        dialogbox_start = xcen - (len(self.message) // 2) - 1
        bg_char = " "

        draw_starting(f"{bg_char * (len(self.message) + 2)}", dialogbox_start, ystart + 1)
        draw_starting(f"{bg_char * (len(self.message) + 2)}", dialogbox_start, ystart + 2)
        draw_starting(f"{bg_char * (len(self.message) + 2)}", dialogbox_start, ystart)

pause_dialog = Dialog("PAUSED")
exit_confirmation_dialog = Dialog("Do you want to exit program (y/n)")

# Display and drawing utilities

def draw_fill(fill_char: str =" ", bg_char: str =None):
    gvars.frame = [[fill_char for _ in range(gvars.width)] for i in range(gvars.height)]
    # TODO: bg_char

def draw_row(char: str, ypos: int, start: int = 0, end: int = -1):
    if end == -1:
        end = gvars.width
    gvars.frame[ypos] = [char for _ in range (start, end)]
    # TODO fix start-end, implement frame[ypos] = char*(end-start)

def draw_column(char: str, xpos: int, start: int =0, end: int =-1):
    if end == -1:
        end = gvars.height - 1
    
    for row in gvars.frame:
        row[xpos] = char
    # TODO: start-end

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

def draw_starting(string: str, startingx: int, startingy: int):
    i = 0
    for char in string:
        draw_char(char, startingx + i, startingy)
        i += 1

def draw_borders():
    draw_column("║", 0)
    draw_column("║", gvars.width - 1)
    draw_row("═", 0)
    draw_row("═", gvars.height - 1)
    draw_char("╔", 0, 0)
    draw_char("╗", -1, 0)
    draw_char("╚", 0, -1)
    draw_char("╝", -1, -1)

def print_current_word():
    word = gvars.text[gvars.word_index]
    print_center(word)
    gvars.previous_index = gvars.word_index

def clean_up_previous_word():
    if gvars.previous_index:
        print_center(" " * len(gvars.text[gvars.previous_index]))
    draw_starting(" " * 15, 3, gvars.height - 3)

def print_delay():
    delay_string = f"delay: {str(gvars.delay)}ms"
    draw_starting(delay_string, 3, gvars.height - 3)

def print_calling_function_in_margins():
    '''prints the name of the function that called the function that calls this function in top and bottom margins'''
    draw_starting(inspect.stack()[2].function, 1, 0)
    draw_starting(inspect.stack()[2].function, 1, gvars.height - 1)

def draw_UI_elements():
    clean_up_previous_word()
    print_current_word()
    print_delay()
    for dialog in gvars.dialogs:
        dialog.draw()

def clear_terminal():
    # print the ANSI escape sequence to clear the terminal screen
    print('\033c')

def refresh():
    # TODO: lock printing while updating frame.str
    frame_str = ""
    for row in gvars.frame:
        for char in row:
            frame_str += char
        frame_str += "\n"
    # print the ANSI escape sequence to move the cursor to home (top left corner of window)
    print('\033[H')

    print(frame_str)

def clear_if_concurrent_refresh():
    if gvars.previous_index == gvars.word_index:
        clear_terminal()


def refresh_UI_elements():
    if gvars.debug:
        print_calling_function_in_margins()
    clear_if_concurrent_refresh()
    draw_UI_elements()
    refresh()
    if gvars.debug:
        draw_borders()

# Logging utilities

def log(
        message: str = "message undefined", 
        file_name: str = "log.txt", 
        timestamp: bool = True, 
        overwrite: bool = False, 
        headerline: bool = False):
    # Write mode, default "a"; do not overwrite, write to end of file
    open_text_mode = "a"
    if overwrite:
        open_text_mode = "w"
    with open(file_name, open_text_mode) as logfile:
        # Write line of pound signs as a header to mark out an important line, if active
        if headerline:
            logfile.write("###############\n")
        # Write timestamp before the log message, if active (default active)
        if timestamp:
            logfile.write(str(f"{datetime.datetime.now()}\n"))
        logfile.write(f"{message}\n\n")

def errorlog(message: str = ""):
    log(message, "errorlog.txt")

# Control utilities

@loggable_controller
def toggle_pause() -> bool:
    if gvars.may_run.is_set():
        return set_pause(True)
    else:
        return set_pause(False)

@loggable_controller
def set_pause(state: bool, dialog: bool = True) -> bool:
    if state:
        gvars.may_run.clear()
        if dialog:
            pause_dialog.show()
        return True
    else:
        gvars.may_run.set()
        if dialog:
            pause_dialog.hide()
        return False

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
def increase_delay():
    gvars.delay += 10 if gvars.delay >= 10 else 1
    refresh_UI_elements()

@loggable_controller
def decrease_delay():
    if gvars.delay > 0:
        gvars.delay -= 10 if gvars.delay > 11 else 1
        refresh_UI_elements()

@loggable_controller
def signal_exit(force: bool = False):
    log("Exit function start")

    if gvars.may_run.is_set():
        gvars.may_run.clear()

    if not force:
        exit_confirmation_dialog.show()
        gvars.word_index = gvars.previous_index
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
                exit_confirmation_dialog.hide()
                break
    else:
        log("Exit forced")
        confirm = "y"

    try:
        if confirm == "y":
            gvars.exit = True
            if not gvars.may_run.is_set():
                gvars.may_run.set()
        elif confirm == "n":
            pause_dialog.show()
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
    draw_fill()
    draw_borders()
    gvars.word_index = 0
    while gvars.word_index < len(gvars.text)-1:
        # break loop if main thread asks to exit
        if gvars.exit:
            log("Display loop break")
            break

        # wait if the main thread has called a pause until it calls unpause
        gvars.may_run.wait()

        refresh_UI_elements()
        gvars.word_index += 1
        time.sleep(gvars.delay/1000)

    if not gvars.exit:
        signal_exit()
    log("Display loop end")


def main():
    log("Program started", headerline = True)
    text = input_loop()
    log(f"Text of length {len(text)} input")
    clear_terminal()

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
