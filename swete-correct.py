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

diff_chars = ["<", ">", "|"]

def main(stdscr, lines):
    stdscr.clear()

    # Search each line for differences
    for line in range(len(lines)):
        eval_line = False
        # Look for diff_chars in line and set flag to eval_line
        for diff_char in diff_chars:
            if diff_char in lines[line]:
                eval_line = True
        # Prepare to work if eval_line is True
        if eval_line:
            stdscr.addstr(23, 0, str(line))
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
                                  curses.A_STANDOUT)
                else:
                    stdscr.addstr(num, 0, display_lines[num])

            stdscr.refresh()
            stdscr.getkey()
            stdscr.clear()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='provides an interface for human correction of \
        machine-corrected Swete LXX OCR results.')
    argparser.add_argument('--file', '-f', metavar='<file>',
                           type=argparse.FileType('r'), help='File to process')

    args = argparser.parse_args()

    lines = args.file.readlines()

    curses.wrapper(main, lines)
