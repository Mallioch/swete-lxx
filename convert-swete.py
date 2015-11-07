#! /usr/bin/env python
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

import xml.sax


class SweteLXX(xml.sax.handler.ContentHandler):
    "Parser for Swete LXX XML"

    def __init__(self):
        "Initialize varibales"

        self.in_book = False
        self.in_header = False
        self.in_note = False
        self.current_book = ""

    def startElement(self, name, attrs):
        "Actions for encountering open tags"

        if (name == "div" and "subtype" in attrs.getNames()
           and attrs.getValue("subtype") == "chapter"):
            self.in_book = True
            self.current_book = "%02d" % int(attrs.getValue("n"))
            print "Entering book %s" % self.current_book

        elif name == "head":
            self.in_header = True

        elif name == "note":
            self.in_note = True

    def characters(self, data):
        "Handle text"

        # Print the book head tags (titles)
        if self.in_header:
            print data.encode("UTF-8")
        # If not in a header, and not in a note
        elif self.in_book and not self.in_note:
            tokens = data.split()
            for token in tokens:
                print "%s %s" % (self.current_book, token.encode("UTF-8"))

    def endElement(self, name):
        "Actions for encountering closed tags"

        if (name == "div" and self.in_book):
            self.in_book = False
            print "Close book"

        elif name == "head":
            self.in_header = False

        elif name == "note":
            self.in_note = False

if __name__ == "__main__":
    vol = open('source/old_testament_1901_vol1.xml', 'r')
    parser = xml.sax.make_parser()
    parser.setContentHandler(SweteLXX())
    parser.parse(vol)
