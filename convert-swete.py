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

import codecs
import xml.sax


class SweteLXX(xml.sax.handler.ContentHandler):
    "Parser for Swete LXX XML"

    def startElement(self, name, attrs):
        "Actions for encountering open tags"

        if ( name == "div" and "subtype" in attrs.getNames()
             and attrs.getValue("subtype") == "chapter" ):
            print attrs.getValue("n")


if __name__ == "__main__":
    vol = open('source/old_testament_1901_vol1.xml', 'r')
    parser = xml.sax.make_parser()
    parser.setContentHandler(SweteLXX())
    parser.parse(vol)
