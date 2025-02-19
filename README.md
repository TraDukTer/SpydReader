# SpydReader

SpydReader is a Python-based Rapid Serial Visual Presentation (RSVP) speed-reading aid developed by TraDukTer (J. Suutarinen). As an RSVP solution, it may also be used for peripheral vision reading.

# Table of Contents

1. Description
    1. Features
        1. Input text
        2. Interface
    2. Known issues
    3. Planned features
        1. Input text
        2. Interface
        3. Implementation
2. Requirements
3. License

# 1. Description

SpydReader flashes words (or groups of words) from an input text in the center of a configurable area to force the user to read the words quickly or miss them on the one hand, and to remove the mental overhead of moving the text along on the other. Research on the effects of RSVP on reading speed and comprehension are mixed, but I have found it useful in skimming uninteresting texts. RSVP can also be used to aid in reading with peripheral vision by those whose whose central vision is diminished, who may find it difficult to follow conventionally displayed text without centering it in their vision.

As of January 2025, I am developing SpydReader on my own and am not looking for contributors at this time. I intend to develop SpydReader alone into some kind of minimum lovable product and an entry into my personal programming portfolio. I welcome feedback and input on e.g. future features via my GitHub account, and don't rule out co-operating with other developers at a later date.

## 1.i. Features

### 1.i.a. Input text

SpydReader currently supports input as .txt file and raw text input to the text-based user interface. The current iteration only works on Windows. The .txt file is read into memory in its entirety, so some software limitations to its length apply. The file name can be arbitrary, but the file has to be placed in the /Input folder in the same folder as SpydReader.

### 1.i.b. Interface

SpydReader is currently completely text-based and runs in a terminal. 

Controls while displaying text:
- Space:        pause/unpause
- Up arrow:     increase speed of text (decrease interval between words shown)
- Down arrow:   decrease speed of text (increase interval between words shown)
- Esc:          exit program (will ask for confirmation)

## 1.ii. Known issues

It is possible for SpydReader may stay active but in an unresponsive state that cannot be ended with KeyboardInterrupt, though there are mitigations in place for known cases. This is due to SpydReader using threading; KeyboardInterrupt is only sent to the main thread in Python, so if it exits in an unhandled way, KeyboardInterrupt cannot be processed by SpydReader. SpydReader can always be exited by closing the terminal window in which it is running.

Clicking on the terminal window will hide and pause SpydReader output. This is unintended, but not detrimental. 

## 1.iii. Planned Features

### 1.iii.a. Input text

- Saving progress on .txt files
- Reading large files piecemeal
- Support for other file types
- Support for specifying an input file's path to the program
- File Explorer (or similar) to browse for an input file (not a priority)

### 1.iii.b. Interface

- Control features to move backwards and forwards in text
- Control features to choose the size of the display area
- Displaying several words at a time in various configurations of rows
- Override to enter specific values for text progress and display speed while display is paused
    - instead of incrementing gradually
- Displaying progress in current text
- Verbose in-program descriptions of controls

- configuration file
- running from console with input file etc. as argument to bypass repetitive logic
- Saving progress on a given input file
    - naïve validation (with option to override) that the file is unchanged from previous session
- reliability updates (non-exhaustive):
    - handling words that are too long to display on a single line
    - handling files that are too large to load into memory

- Dedicated TUI (instead of relying on a third-party terminal. Would improve flickering)
- GUI (not a priority)

- All features are intended to be retained despite adding new ones;
    - Terminal mode will be supported when TUI mode is implemented
    - TUI mode will be supported if and hen GUI mode is implemented. 

### 1.iii.c. Implementation

- Linux/UNIX support
- Makefile
- Standalone executable files (would also allow e.g. packaging Keyboard library)


# 2. Requirements

SpydReader uses the [Keyboard library by Boppreh](https://github.com/boppreh/keyboard), which is not provided with Python installation. To run the source code, you either need to install the Keyboard library, e.g. by running `pip install keyboard` in a commandline or download it, e.g. [via PyPi](https://pypi.org/project/keyboard/).

# 3. License

SpydReader is Licensed to the public under the GNU General Public License Version 3 (GPLv3). SpydReader is free for personal use, and it may be developed on, copied or used as a basis or part of other software free of charge. GPLv3 places some restrictions on derivative software and distributed versions, namely that these shall also be licenced under a GNU General Public Licence of version 3 or newer. Any derivative works and distributed versions shall include a copy of the GPLv3 and the copyright notice of SpydReader (copyright_notice.txt). I may be attributed as "TraDukTer", "TraDukTer (J. Suutarinen)" or "Jani Suutarinen" as appropriate for the context.

This section is only intended to give a non-exhaustive overview of the contents of the GNU General Public License Version 3 text and specify how to attribute me as the developer of SpydReader. Where the GPLv3 text and the content of this section conflict, the GPLv3 text shall take precedence.