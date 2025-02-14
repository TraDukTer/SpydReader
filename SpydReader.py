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

# Decorator that saves all exceptions raised by decorated function to file
def loggable_controller(func):
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            errorlog(f"Following exception raised by controller:\n{traceback.format_exc()}")
            return None
    return new_func

# placeholder class to reveal variables across functions
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
        '''
        Create dialog in the middle of the fifth row from the top with argument message as text

        TODO: support other dialog positions
        '''
        self.message = message
        self.message_lines = re.split("\n", message)
        self.message_width = max(len(line) for line in self.message_lines)

    def __eq__(self, other: Self):
        if isinstance(other, self.__class__):
            return self.message == other.message
        else:
            return NotImplemented

    def __ne__(self, other: Self):
        return not self.__eq__(self, other)

    def show(self):
        '''Add dialog to dialog stack and refresh UI (which e.g. draws dialogs to frame in order of stack).'''
        if self not in gvars.dialogs:
            gvars.dialogs.append(self)
        refresh_UI_elements()

    def hide(self, refresh: bool = True):
        '''
        Remove dialog from dialog stack, print over it with whitespace in frame and refresh UI (by default)

        If refresh is False, skip refreshing UI
        (useful for minimizing UI cycles when one dialog is switched for another)
        '''
        if self in gvars.dialogs:
            gvars.dialogs.remove(self)
        self.clean_up()
        if refresh:
            refresh_UI_elements()

    def draw(self):
        '''
        Draw dialog to frame

        TODO: support dialog positions besides center of 5th row
        '''
        xcen = gvars.width // 2
        ystart = 5
        dialogbox_start = xcen - (self.message_width // 2) - 1

        draw_starting(f"╔{"═" * self.message_width}╗", dialogbox_start, ystart)

        current_line = 0
        for line in self.message_lines:
            draw_starting(f"║{line.center(self.message_width)}║", dialogbox_start, ystart + current_line + 1)
            current_line += 1
        draw_starting(f"╚{"═" * self.message_width}╝", dialogbox_start, ystart + current_line + 1)

    def clean_up(self):
        '''Print over dialog with whitespace in frame'''
        xcen = gvars.width // 2
        ystart = 5
        dialogbox_start = xcen - (self.message_width // 2) - 1
        bg_char = " "

        for i in range(len(self.message_lines) + 2):
            draw_starting(f"{bg_char * (self.message_width + 2)}", dialogbox_start, ystart + i)

pause_dialog = Dialog("PAUSED\npress space to unpause")
exit_confirmation_dialog = Dialog("Do you want to exit program (y/n)")

# Input validation utilities

def check_that_input_is_char(char: str, argument_name: str|None = None):
    '''Raise ValueError if argument is not a string or is longer than 1 character'''
    if not isinstance(char, str) or len(char) > 1:
        error_message = f"{inspect.stack()[1].function} only accepts a single character"
        error_message += f" for argument {argument_name}." if not argument_name == None else "."

        raise ValueError(error_message)

# Display and drawing utilities

def draw_fill(fill_char: str =" ", bg_char: str =None):
    '''Fill frame with designated character'''
    check_that_input_is_char(fill_char, "fill_char")
    gvars.frame = [[fill_char for _ in range(gvars.width)] for i in range(gvars.height)]
    # TODO: bg_char

def draw_row(char: str, ypos: int, start: int = 0, end: int = -1):
    '''
    Replace all characters on designated row in frame with designated character

    TODO: implement filling only from and to designated index without affecting rest of row
    '''
    check_that_input_is_char(char, "char")

    if end == -1:
        end = gvars.width

    gvars.frame[ypos] = [char for _ in range (start, end)]
    # TODO fix start-end, implement frame[ypos] = char*(end-start)

def draw_column(char: str, xpos: int, start: int =0, end: int =-1):
    '''
    Replace all characters on designated column in frame with designated character

    TODO: implement filling only from and to designated index without affecting rest of column
    '''
    check_that_input_is_char(char, "char")

    if end == -1:
        end = gvars.height - 1
    
    for row in gvars.frame:
        row[xpos] = char
    # TODO: start-end

def draw_char(char: str, xpos: int, ypos: int):
    '''Replace character in designated x and y coordinates in frame with designated character'''
    check_that_input_is_char(char, "char")
    gvars.frame[ypos][xpos] = char

def print_center(string: str):
    '''Replace characters centered on center row in frame with designated string'''
    ycen = gvars.height // 2
    xcen = gvars.width // 2
    string_start = xcen - (len(string) // 2)

    i = 0
    for char in string:
        draw_char(char, string_start + i, ycen)
        i += 1

def draw_starting(string: str, startingx: int, row: int):
    '''Replace characters on designated row in frame with designated string starting from designated index'''
    i = 0
    for char in string:
        draw_char(char, startingx + i, row)
        i += 1

def draw_borders():
    '''Replace characters on the edge of frame with box-drawing characters'''
    draw_column("║", 0)
    draw_column("║", gvars.width - 1)
    draw_row("═", 0)
    draw_row("═", gvars.height - 1)
    draw_char("╔", 0, 0)
    draw_char("╗", -1, 0)
    draw_char("╚", 0, -1)
    draw_char("╝", -1, -1)

def print_current_word():
    '''Print current word from current text to center of frame'''
    word = gvars.text[gvars.word_index]
    print_center(word)
    gvars.previous_index = gvars.word_index

def clean_up_previous_word():
    '''Replace characters of the previously printed word with whitespace in center of frame'''
    if not gvars.previous_index == None:
        print_center(" " * len(gvars.text[gvars.previous_index]))

def print_delay():
    '''print current delay between words in milliseconds to bottom left corner of frame'''
    delay_string = f"delay: {str(gvars.delay)}ms"
    draw_starting(" " * 15, 3, gvars.height - 3) # clean up previous delay string
    draw_starting(delay_string, 3, gvars.height - 3)

def print_calling_function_in_margins():
    '''Print name of function that called function that calls this function to top and bottom edges of frame'''
    draw_starting(inspect.stack()[2].function, 1, 0)
    draw_starting(inspect.stack()[2].function, 1, gvars.height - 1)

def draw_UI_elements():
    '''
    Update frame matrix with current state of UI elements (but don't print them yet)

    TODO: make (some) UI elements configurable
    '''
    clean_up_previous_word()
    print_current_word()
    print_delay()
    # draw dialogs in order of dialog stack (as topmost UI element)
    for dialog in gvars.dialogs:
        dialog.draw()

def clear_terminal():
    '''Print ANSI escape sequence to clear terminal screen'''
    print('\033c')

def refresh():
    '''
    Print current contents of frame to terminal.

    Assign contents of frame matrix to multi-line string
    Move cursor to top left corner of terminal window
    Print aforementioned string to terminal (overwriting previous frame in terminal)
    '''
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
    '''
    Clear terminal screen if current word was also the previous printed word

    Placeholder / last resort solution to circumvent bug that prints two frames before moving cursor to beginning of terminal screen
    '''
    if gvars.previous_index == gvars.word_index:
        clear_terminal()


def refresh_UI_elements():
    '''Update frame with current state of UI elements and overwrite the previous frame in terminal'''

    # print name of the function that called this function in top and bottom borders if debug mode is set
    if gvars.debug:
        print_calling_function_in_margins()
    clear_if_concurrent_refresh() # clear instead of moving cursor if double frame print bug likely
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
    '''
    Write designated message to designated file on a new line

    by default, create file if not extant and append to end on new line
    timestamp: if True, precede message with date and time on new line
    overwrite: if True, create file if not extant or overwrite extant file
    headerline: if True, precede message with line of pound signs
    '''


    # Write mode, default "a"; do not overwrite, write to end of file, create new file if not extant
    open_text_mode = "a"
    if overwrite:
        open_text_mode = "w"
    with open(file_name, open_text_mode) as logfile:
        # Write line of pound signs as a header to mark out an important line, if set (not set by default)
        if headerline:
            logfile.write("###############\n")
        # Write timestamp before the log message, if set (set by default)
        if timestamp:
            logfile.write(str(f"{datetime.datetime.now()}\n"))
        logfile.write(f"{message}\n\n")

def errorlog(message: str = ""):
    '''Write designated message to end of errorlog.txt on new line'''
    log(message, "errorlog.txt")

# Control utilities

@loggable_controller
def toggle_pause() -> bool:
    '''Pause if not paused, unpause if paused.'''
    if gvars.may_run.is_set():
        return set_pause(True)
    else:
        return set_pause(False)

@loggable_controller
def set_pause(state: bool, dialog: bool = True) -> bool:
    '''
    Pause if state == True, else unpause

    dialog: if True, show pause dialog if paused and hide pause dialog of unpaused, default True
    '''
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
    '''Return currently configured seek increment if not paused, else return 1'''
    if gvars.may_run.is_set():
        return gvars.seek_increment
    else:
        return 1

@loggable_controller
def rewind():
    '''Increment index of current word in text backwards'''
    increment = get_appropriate_increment()
    if gvars.word_index - increment >= 0:
        gvars.word_index -= increment
    else:
        gvars.word_index = 0
    refresh_UI_elements()

@loggable_controller
def skip_forward():
    '''Increment index of current word in text forwards'''
    increment = get_appropriate_increment()
    if gvars.word_index + increment < len(gvars.text) -1:
        gvars.word_index += increment
    else:
        gvars.word_index = len(gvars.text) -1
    refresh_UI_elements()

@loggable_controller
def increase_delay():
    '''Increase sleep duration between words'''
    gvars.delay += 10 if gvars.delay >= 10 else 1
    refresh_UI_elements()

@loggable_controller
def decrease_delay():
    '''Decrease sleep duration between words'''
    if gvars.delay > 0:
        gvars.delay -= 10 if gvars.delay > 11 else 1
        refresh_UI_elements()

@loggable_controller
def signal_exit(force: bool = False):
    '''
    Exit program gracefully

    force: if True, do not ask for user confirmation, default False
    if not forced, ask for user confirmation. If not confirmed, resume program paused'''
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
                exit_confirmation_dialog.hide(False)
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
    '''Set resolution to designated width and height'''

    gvars.width = new_width
    gvars.height = new_height

# _None is only included because the signal library calls signal.signal() with two arguments.
@loggable_controller
def ctrl_c(signum, _None):
    '''Capture keyboard interrupt from console and force exit if detected'''
    log("Keyboard interrupt detected")
    if signum == 2:
        signal_exit(force=True)


# Core functionality

def input_loop() -> str:
    '''
    Elicit text to display from user

    user may either enter the name of a text file in the SpydReader file system or press enter
    to enter text as a string of characters (e.g. copy-paste) directly into the terminal

    text file is read into memory in its entirety
    '''

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
    '''
    Print the word at the current index in text to the middle of the frame and increment the index

    start by splitting each word (substring delimited by space or line break) in text into an element of a list
    initialize frame by filling it with spaces and drawing borders
    in a loop,
     check if exit is called. If yes, break loop
     wait if pause has been called, resume when pause cleared
     update the UI elements and print them to terminal
     finally wait for designated delay before starting next iteration

    if last index of text is reached, signal main to exit program
    '''

    log("Display loop start")
    gvars.text = [word for word in re.split(" |\n", text) if word]
    draw_fill()
    draw_borders()
    gvars.word_index = 0
    while gvars.word_index < len(gvars.text)-1:
        # break loop if main thread calls to exit
        if gvars.exit:
            log("Display loop break")
            break

        # wait if main thread has called a pause until it calls unpause
        gvars.may_run.wait()

        refresh_UI_elements()
        gvars.word_index += 1
        time.sleep(gvars.delay/1000)

    # if end of text is reached, call exit (with user confirmation)
    if not gvars.exit:
        signal_exit()
    log("Display loop end")


def main():
    log("Program started", headerline = True)
    text = input_loop()
    log(f"Text of length {len(text)} input")

    # initialize thread for display_loop
    display_thread = threading.Thread(target = display_loop, args = (text, ))

    # clear terminal so that first frame is printed at the top of terminal
    clear_terminal()

    display_thread.start()
    log("Display thread started")

    # listen for keyboard interrupt
    signal.signal(signal.SIGINT, ctrl_c)

    # listen for keyboard controls
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
        # save any exception that interrupts main thread to file
        # (display thread may overwrite the exception in terminal)
        errorlog(f"Following exception raised in main:\n {traceback.format_exc()}")
        log("Main thread exited with exception")
        # if main thread is interrupted by an exception, force a graceful exit of the program
        signal_exit(force=True)
