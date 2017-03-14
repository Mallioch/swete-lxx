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
menu_choices = ["n", "c", "i", "d", "v", "q"]
punctuation = [".", ",", ";", "·", "[", "]", "§"]


def backoff(text, delta_text):
    """Return True if evaluation should continue, or False if the backoff
    algorithm found that the surface differences in text, delta are trivial

    """

    text_norm = koinenlp.remove_punctuation(text).lower()
    delta_norm = koinenlp.remove_punctuation(delta_text).lower()

    # This function is only called in contexts in which eval_line is True
    eval_line = True

    if text_norm == delta_norm:
        eval_line = False
    # Delta text has no diacritics
    elif koinenlp.strip_diacritics(text) == delta_text:
        eval_line = False
    # Elision is no worry
    elif (text_norm[-1] == "’") and (delta_norm[-1] == "'"):
        eval_line = False

    return eval_line


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


def main(stdscr, book, lines, book_num):
    """The main program loop."""

    # Curses set-up
    stdscr.clear()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)

    corrections = []
    out_tokens = []
    chapter = 1
    verse = 1

    skip_lines = 0

    # re set-up
    verse_line = re.compile('^\d{3}.*$')

    # Search each line for differences
    for line in range(len(lines)):

        would_skip_lines = 0
        # Break if lines should be skipped
        if skip_lines > 0:
            skip_lines -= 1
            continue

        diff = lines[line][0]
        text = koinenlp.unicode_normalize(lines[line][2:].strip())
        if text in punctuation:
            punct_token = True
        else:
            punct_token = False
        delta_text = None

        # Update reference based on left column
        verse_match = verse_line.match(text)
        if verse_match:
            old_verse = verse
            verse = int(text[0:3])
            # Update chapter if verse num goes down
            if old_verse > verse:
                chapter += 1
        verse_string = "%s%03d%03d " % (book_num, chapter, verse)

        eval_line = False
        # Look for diff_chars in line and set flag to eval_line

        for diff_char in diff_chars:
            if diff_char in diff:
                eval_line = True
                # Delete or correct
                if diff == "-":
                    next_diff = lines[line+1][0]
                    # Correct
                    if next_diff == "+":
                        operation = "correct"
                        delta_text = koinenlp.unicode_normalize(lines[line+1][2:].strip())
                        would_skip_lines = 1

                        # Check backoff
                        eval_line = backoff(text, delta_text)
                        # If backoff returns negative, skip a line
                        if not eval_line:
                            skip_lines = 1

                    elif next_diff == "?":
                        operation = "correct"
                        delta_text = koinenlp.unicode_normalize(lines[line+2][2:].strip())
                        # skip two lines on ? line
                        skip_lines = 2
                        # If there is a subsequent ? line, skip even more
                        ultimate_diff = lines[line+3][0]
                        if ultimate_diff == "?":
                            skip_lines = 3

                        # Check backoff
                        eval_line = backoff(text, delta_text)

                    # Delete
                    else:
                        # No need to eval punctuation
                        if punct_token:
                            eval_line = False
                        else:
                            operation = "delete"
                # Insert
                elif diff == "+":
                    operation = "insert"
                # Failed correct, don't actually eval
                elif diff == "?":
                    eval_line = False
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
                        return corrections, out_tokens
                    # Append response to log
                    else:
                        need_response = False
                        correct_string = "{} {}:{} {}".format(book, chapter,
                                                              verse,
                                                              options[resp])
                        # Only include actual changes
                        if resp is not "n":
                            corrections.append(correct_string)
                        # Append appropriate tokens to out_tokens
                        if operation == "insert":
                            if (resp == "i") and (not verse_match):
                                out_tokens.append(verse_string + text)
                        else:
                            if resp == "n":
                                out_tokens.append(verse_string + text)
                        if resp == "c":
                            # Actually skip only if correction made without ?
                            if would_skip_lines > 0:
                                skip_lines = would_skip_lines
                            out_tokens.append(verse_string + delta_text)
            # TODO flesh-out log here, including bcv, and instructions
            # And find out what to do with it
            stdscr.clear()
        # Non-evaluated lines are appended
        else:
            # Do not output verse change tokens
            if not verse_match:
                out_tokens.append(verse_string + text)
        # Append punctuation to previous out_token
        if punct_token:
            out_tokens[-2] += text
            out_tokens.pop()
    # Return corrections if we complete the loop
    return corrections, out_tokens


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
    argparser.add_argument('--out', '-o', metavar='<file>',
                           type=argparse.FileType('w'), help='Output file' )

    args = argparser.parse_args()

    source_lines = args.source.readlines()
    delta_lines = args.delta.readlines()
    d = difflib.Differ()
    results = list(d.compare(source_lines, delta_lines))

    corrections, out_tokens = curses.wrapper(main, args.book, results, args.num)

    for correction in corrections:
        print(correction)

    args.out.writelines("{}\n".format(out_token) for out_token in out_tokens)
