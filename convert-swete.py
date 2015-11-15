#! /usr/bin/env python3
#
# Convert Swete XML files to one token per line, with verses.
#
# Copyright 2015 Nathan D. Smith <nathan@smithfam.info>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import re
import unicodedata
import xml.sax

import koine

FILTER_CHARS = ["¶", "[", "]"]

VOLUMES = {1: "old_testament_1901_vol1.xml",
           2: "old_testament_1901_vol1.xml",
           3: "old_testament_1930_vol3.xml"}

OFFSET = {1: 0,
          2: 12,
          3: 27}


class SweteLXX(xml.sax.handler.ContentHandler):
    "Parser for Swete LXX XML"

    def __init__(self, book, task, volume):
        "Initialize varibales"

        self.in_book = False
        self.in_header = False
        self.in_note = False
        self.page_right = False
        self.current_page = 0

        self.target_book = book
        self.task = task
        self.volume = volume
        # Set the cumulative offset of books from one in subsequent volumes
        self.book_offset = OFFSET[self.volume]

        # Regex patterns
        self.verse_pat = re.compile(r'\d{1,3}')

        # Set up the reference
        self.reset_ref()

    def reset_ref(self):
        "Reset the references on book transition"

        self.current_book = ""
        self.current_chapter = 1
        self.current_verse = "001"

    def set_verse(self, verse):
        "Set the current_verse (and sometimes chapter) on transitions"

        # Increment the chapter if the verse goes lower
        if verse < int(self.current_verse):
            self.current_chapter += 1
        self.current_verse = "%03d" % verse
        # Only print verse boundaries in compare mode
        if self.task == "compare":
            print(self.current_verse)

    def unicode_normalize(self, text):
        """Return the given text normalized to Unicode NFC."""

        normalized_text = unicodedata.normalize('NFKC', text)
        return normalized_text

    def startElement(self, name, attrs):
        "Actions for encountering open tags"

        if (name == "div" and "subtype" in attrs.getNames()
           and attrs.getValue("subtype") == "chapter"):
            # A "chapter" in TEI is a "book" for our purposes
            # Only count book that we want
            if (attrs.getValue("n")) == self.target_book:
                self.in_book = True
            # Reset reference info
            self.reset_ref()
            self.current_book = "%02d" % (int(attrs.getValue("n"))
                                          + self.book_offset)

        elif name == "head":
            self.in_header = True

        elif name == "note":
            self.in_note = True

        elif name == "pb" and self.in_book:
            self.current_page = int(attrs.getValue("n"))
            if not self.current_page % 2:
                self.page_right = True
            else:
                self.page_right = False

        elif name == "lb" and self.in_book and self.page_right:
            # When on the right hand side, if the lb is higher than the verse
            # number, there must be a verse break which doesn't appear in
            # tokens, therefore increment the verse
            try:
                lb_verse = int(attrs.getValue("n"))
            except:
                lb_verse = int(self.current_verse) + 1
            if lb_verse > int(self.current_verse):
                self.set_verse(lb_verse)

    def characters(self, data):
        "Handle text"

        # Print the book head tags (titles)
        # if self.in_header:
        #      print(data.encode("UTF-8"))
        # If not in a header, and not in a note
        if self.in_book and not self.in_note and not self.in_header:
            tokens = data.split()
            for token in tokens:
                # Look for verses
                has_verse = self.verse_pat.match(token)
                if has_verse:
                    new_verse = has_verse.group(0)
                    self.set_verse(int(new_verse))
                    # Reform the token without the verse prefix
                    token = token[len(new_verse):]
                # Assuming a verse ended up in its own token, no need
                # to print an empty line
                for char in FILTER_CHARS:
                    token.replace(char, "")
                if len(token) < 1:
                    continue
                end_token = koine.normalize(token)
                # Print only the normalized form
                if self.task == "compare":
                    print(end_token)
                elif self.task == "convert":
                    print("%s%03d%s %s" % (self.current_book,
                                           self.current_chapter,
                                           self.current_verse,
                                           self.unicode_normalize(token)))

    def endElement(self, name):
        "Actions for encountering closed tags"

        if (name == "div" and self.in_book):
            self.in_book = False
            # print("Close book")

        elif name == "head":
            self.in_header = False

        elif name == "note":
            self.in_note = False

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='Convert Swete TEI to one line per token..')
    subs = argparser.add_subparsers(dest='command')
    argparser_diff = subs.add_parser("compare",
                                     help="Print normalized comparison text")
    argparser_convert = subs.add_parser("convert", help="Print converted text")
    argparser.add_argument('--volume', '-v', metavar='<num>', type=int,
                           help='Volume to process.')
    argparser.add_argument('--chapter', '-c', metavar='<num>', type=str,
                           help='Chapter (book) number to process.')

    args = argparser.parse_args()
    vol = open(VOLUMES[args.volume], 'r')
    parser = xml.sax.make_parser()
    parser.setContentHandler(SweteLXX(book=args.chapter, task=args.command,
                                      volume=args.volume))
    parser.parse(vol)
