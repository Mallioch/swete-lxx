#!/usr/bin/env python3
#
# swete-correct.py provides an interface for human correction of
# machine-corrected Swete LXX OCR results.
#
# Copyright (c) 2016, 2017 Nathan D. Smith <nathan@smithfam.info>
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
import difflib
import koinenlp
import re

diff_chars = ["?", "-", "+"]

menu_choices = ["n", "c", "i", "d", "f", "v", "q"]


def menu(stdscr, text, operation, correct_text=None):
    """Draw the menu options in the user interface and return the list of
    valid options.

    """

    # Always at the beginning of the list
    menu_options = {
        "n": "no change",
    }

    # logic here for contextual options
    if operation == "insert":
        menu_options["i"] = "insert {}".format(text)
    elif operation == "delete":
        menu_options["d"] = "delete {}".format(text)
    elif operation == "correct":
        menu_options["c"] = "correct {} -> {}".format(text, correct_text)

    # Always at the end of the list
    menu_options["v"] = "versification"
    menu_options["q"] = "quit"

    # out line based on terminal size minus last line, minus options
    out_line = curses.LINES - (1 + len(menu_choices))

    for choice in menu_choices:
        if choice in menu_options:
            option_text = "{}) {}".format(choice, menu_options[choice])
            stdscr.addstr(out_line, 0, option_text)
        else:
            option_text = "{})".format(choice)
            stdscr.addstr(out_line, 0, option_text, curses.A_DIM)

        # Increment output line so we don't overwrite
        out_line += 1

    stdscr.refresh()
    return menu_options


def main(stdscr, book, lines):
    """The main program loop."""

    # Curses set-up
    stdscr.clear()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

    corrections = []
    chapter = 1
    verse = 0

    skip_lines = 0

    # re set-up
    verse_line = re.compile('^\d{3}.*$')

    # Search each line for differences
    for line in range(len(lines)):

        # Break if lines should be skipped
        if skip_lines > 0:
            skip_lines -= 1
            continue

        diff = lines[line][0]
        text = lines[line][2:].strip()
        delta_text = None

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
            if diff_char in diff:
                eval_line = True
                # Delete or correct
                if diff == "-":
                    next_diff = lines[line+1][0]
                    # Correct
                    if next_diff in ["+","?"]:
                        operation = "correct"
                        # skip one line on + line
                        skip_lines = 1
                        if next_diff == "?":
                            # skip two lines on ? line
                            skip_lines = 2
                            delta_text = lines[line+2][2:].strip()
                            ultimate_diff = lines[line+3][0]
                            if ultimate_diff == "?":
                                skip_lines = 3
                        else:
                            delta_text = lines[line+1][2:].strip()
                        ## Backoff for unimportant differences
                        # Punctuation and capitalization
                        text_norm = koinenlp.remove_punctuation(text).lower()
                        delta_norm = koinenlp.remove_punctuation(delta_text).lower()
                        if text_norm == delta_norm:
                            eval_line = False
                        # Delta text has no diacritics
                        if koinenlp.strip_diacritics(text) == delta_text:
                            eval_line = False

                    # Delete
                    else:
                        operation = "delete"
                # Insert
                elif diff == "+":
                    operation = "insert"
        # Prepare to work if eval_line is True
        if eval_line:
            status_line = "L: {} B: {} C: {} V: {}".format(line, book,
                                                           chapter, verse)
            stdscr.addstr((curses.LINES - 1), 0, str(status_line),
                          curses.A_REVERSE)
            # Show context of up to 5 lines (if possible)
            context = (curses.LINES - len(menu_choices)) // 2
            start_line = line - context
            if start_line < 0:
                start_line = 0
            end_line = line + context - 1
            if end_line > (len(lines) - 1):
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
            # Draw menu until legitimate response is received
            need_response = True
            while need_response:
                options = menu(stdscr, text, operation, delta_text)
                resp = stdscr.getkey()
                if resp in options.keys():
                    # Quit and return corrections thus far
                    if resp == "q":
                        return corrections
                    # Append response to log
                    else:
                        need_response = False
                        correct_string = "{} {}:{} {}".format(book, chapter,
                                                              verse,
                                                              options[resp])
                        # Only include actual changes
                        if resp is not "n":
                            corrections.append(correct_string)
            # TODO flesh-out log here, including bcv, and instructions
            # And find out what to do with it
            stdscr.clear()
    # Return corrections if we complete the loop
    return corrections


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='provides an interface for human correction of \
        machine-corrected Swete LXX OCR results.')
    argparser.add_argument('--source', '-s', metavar='<file>',
                           type=argparse.FileType('r'), help='Source file' )
    argparser.add_argument('--delta', '-d', metavar='<file>',
                           type=argparse.FileType('r'), help='Delta file')
    argparser.add_argument('--book', '-b', metavar='<title>',
                           type=str, help='Book title')
    argparser.add_argument('--num', '-n', metavar='<num>',
                           type=int, help='Book number')

    args = argparser.parse_args()

    source_lines = args.source.readlines()
    delta_lines = args.delta.readlines()
    d = difflib.Differ()
    results = list(d.compare(source_lines, delta_lines))

    corrections = curses.wrapper(main, args.book, results)

    for correction in corrections:
        print(correction)
