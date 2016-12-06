#!/usr/bin/env python3
#
# swete-correct.py provides an interface for human correction of
# machine-corrected Swete LXX OCR results.
#
# Copyright (c) 2016 Nathan D. Smith <nathan@smithfam.info>
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import curses
import re

diff_chars = ["<", ">", "|"]


def menu(stdscr, line):
    """Draw the menu options in the user interface."""

    elements = line.split()
    ref = elements[0]
    new = elements[-1]

    menu_options = {
        "n": "no change",
        "c": "correct {} to {}".format(new, ref),
        "i": "insert {}".format(ref),
        "d": "delete {}".format(new),
        "v": "versification",
        "q": "quit"
    }

    # Always at the beginning of the list
    options = ["n"]

    # logic here for contextual options
    if "<" in elements:
        options.append("i")
    elif ">" in elements:
        options.append("d")
    elif "|" in elements:
        options.append("c")

    # Always at the end of the list
    options.extend(["v", "q"])

    # out line based on terminal size minus last line, minus options
    out_line = curses.LINES - (1 + len(options))

    for option in options:
        option_text = "{}) {}".format(option, menu_options[option])
        stdscr.addstr(out_line, 0, option_text)
        # Increment output line so we don't overwrite
        out_line += 1


def main(stdscr, book, lines):
    """The main program loop."""

    # Curses set-up
    stdscr.clear()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

    corrections = []
    chapter = 1
    verse = 0

    # re set-up
    verse_line = re.compile('^\d{3}.*$')

    # Search each line for differences
    for line in range(len(lines)):
        text = lines[line]

        # Update reference based on left column
        if verse_line.match(text):
            old_verse = verse
            verse = int(text[0:3])
            # Update chapter if verse num goes down
            if old_verse > verse:
                chapter += 1

        eval_line = False
        # Look for diff_chars in line and set flag to eval_line
        for diff_char in diff_chars:
            if diff_char in lines[line]:
                eval_line = True
        # Prepare to work if eval_line is True
        if eval_line:
            status_line = "L: {} B: {} C: {} V: {}".format(line, book,
                                                           chapter, verse)
            stdscr.addstr((curses.LINES - 1), 0, str(status_line), curses.A_REVERSE)
            # Show context of up to 5 lines (if possible)
            start_line = line - 6
            if start_line < 0:
                start_line = 0
            end_line = line + 7
            if end_line > ( len(lines) - 1 ):
                end_line = len(lines) - 1
            display_lines = lines[start_line:end_line]
            for num in range(len(display_lines)):
                # If this is the line, emphasize
                if display_lines[num] == lines[line]:
                    stdscr.addstr(num, 0, display_lines[num],
                                  curses.A_BOLD)
                else:
                    stdscr.addstr(num, 0, display_lines[num],
                                  curses.color_pair(1))

            stdscr.refresh()
            menu(stdscr, text)
            resp = stdscr.getkey()
            corrections.append(resp)
            stdscr.clear()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='provides an interface for human correction of \
        machine-corrected Swete LXX OCR results.')
    argparser.add_argument('--file', '-f', metavar='<file>',
                           type=argparse.FileType('r'), help='File to process')

    args = argparser.parse_args()

    book = args.file.name.split(".")[0]
    lines = args.file.readlines()

    curses.wrapper(main, book, lines)
