#! /usr/bin/env python3
# -*- coding: utf-8 -*
#
# koine.py
# A library for common NLP tasks for Koine Greek
# (c) 2015 Nathan D. Smith <nathan@smithfam.info>
#
# This file incorporates beta2unicode.py, which is covered by the
# following copyright notice:
#
# Copyright (c) 2004 James Tauber <http://jtauber.com/>
#
# The MIT License
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


from __future__ import unicode_literals
import unicodedata

# List of stopwords obtained from Perseus Hopper source code and converted to
# UTF-8 with final sigmas.
# http://sourceforge.net/projects/perseus-hopper/
# Path: sgml/reading/properties/stoplists/greek.stop
stopwords = ["μή",
             "ἑαυτοῦ",
             "ἄν",
             "ἀλλ'",
             "ἀλλά",
             "ἄλλος",
             "ἀπό",
             "ἄρα",
             "αὐτός",
             "δ'",
             "δέ",
             "δή",
             "διά",
             "δαί",
             "δαίς",
             "ἔτι",
             "ἐγώ",
             "ἐκ",
             "ἐμός",
             "ἐν",
             "ἐπί",
             "εἰ",
             "εἰμί",
             "εἴμι",
             "εἰς",
             "γάρ",
             "γε",
             "ἡ",
             "ἤ",
             "καί",
             "κατά",
             "μέν",
             "μετά",
             "μή",
             "ὁ",
             "ὅδε",
             "ὅς",
             "ὅστις",
             "ὅτι",
             "οὕτως",
             "οὗτος",
             "οὔτε",
             "οὖν",
             "οὐδείς",
             "οἱ",
             "οὐ",
             "οὐδέ",
             "οὐκ",
             "περί",
             "πρός",
             "σύ",
             "σύν",
             "τά",
             "τε",
             "τήν",
             "τῆς",
             "τῇ",
             "τι",
             "τί",
             "τις",
             "τίς",
             "τό",
             "τοί",
             "τοιοῦτος",
             "τόν",
             "τούς",
             "τοῦ",
             "τῶν",
             "τῷ",
             "ὑμός",
             "ὑπέρ",
             "ὑπό",
             "ὡς",
             "ὦ",
             "ὥστε",
             "ἐάν",
             "παρά",
             "σός"]


class Trie:
    def __init__(self):
        self.root = [None, {}]

    def add(self, key, value):
        curr_node = self.root
        for ch in key:
            curr_node = curr_node[1].setdefault(ch, [None, {}])
        curr_node[0] = value

    def find(self, key):
        curr_node = self.root
        for ch in key:
            try:
                curr_node = curr_node[1][ch]
            except KeyError:
                return None
        return curr_node[0]

    def findp(self, key):
        curr_node = self.root
        remainder = key
        for ch in key:
            try:
                curr_node = curr_node[1][ch]
            except KeyError:
                return (curr_node[0], remainder)
            remainder = remainder[1:]
        return (curr_node[0], remainder)

    def convert(self, keystring):
        valuestring = ""
        key = keystring
        while key:
            value, key = self.findp(key)
            if not value:
                return (valuestring, key)
            valuestring += value
        return (valuestring, key)


def _beta_to_unicode_trie():
    """Return a Trie object configured for betacode conversion."""

    t = Trie()

    t.add("#",       "\u0374")
    t.add("*A",      "\u0391")
    t.add("*B",      "\u0392")
    t.add("*G",      "\u0393")
    t.add("*D",      "\u0394")
    t.add("*E",      "\u0395")
    t.add("*Z",      "\u0396")
    t.add("*H",      "\u0397")
    t.add("*Q",      "\u0398")
    t.add("*I",      "\u0399")
    t.add("*K",      "\u039A")
    t.add("*L",      "\u039B")
    t.add("*M",      "\u039C")
    t.add("*N",      "\u039D")
    t.add("*C",      "\u039E")
    t.add("*O",      "\u039F")
    t.add("*P",      "\u03A0")
    t.add("*R",      "\u03A1")
    t.add("*S",      "\u03A3")
    t.add("*T",      "\u03A4")
    t.add("*U",      "\u03A5")
    t.add("*F",      "\u03A6")
    t.add("*X",      "\u03A7")
    t.add("*Y",      "\u03A8")
    t.add("*W",      "\u03A9")

    t.add("A",      "\u03B1")
    t.add("B",      "\u03B2")
    t.add("G",      "\u03B3")
    t.add("D",      "\u03B4")
    t.add("E",      "\u03B5")
    t.add("Z",      "\u03B6")
    t.add("H",      "\u03B7")
    t.add("Q",      "\u03B8")
    t.add("I",      "\u03B9")
    t.add("K",      "\u03BA")
    t.add("L",      "\u03BB")
    t.add("M",      "\u03BC")
    t.add("N",      "\u03BD")
    t.add("C",      "\u03BE")
    t.add("O",      "\u03BF")
    t.add("P",      "\u03C0")
    t.add("R",      "\u03C1")

    t.add("S\n",    "\u03C2")
    t.add("S,",     "\u03C2,")
    t.add("S.",     "\u03C2.")
    t.add("S:",     "\u03C2:")
    t.add("S;",     "\u03C2;")
    t.add("S]",     "\u03C2]")
    t.add("S@",     "\u03C2@")
    t.add("S_",     "\u03C2_")
    t.add("S",      "\u03C3")

    t.add("T",      "\u03C4")
    t.add("U",      "\u03C5")
    t.add("F",      "\u03C6")
    t.add("X",      "\u03C7")
    t.add("Y",      "\u03C8")
    t.add("W",      "\u03C9")

    t.add("I+",     "\u03CA")
    t.add("U+",     "\u03CB")

    # stigma, assuming a numeral is intended when digamma is read in betacode
    t.add("*V",     "\u03DA")
    t.add("V",      "\u03DB")

    t.add("A)",     "\u1F00")
    t.add("A(",     "\u1F01")
    t.add("A)\\",   "\u1F02")
    t.add("A(\\",   "\u1F03")
    t.add("A)/",    "\u1F04")
    t.add("A(/",    "\u1F05")
    t.add("E)",     "\u1F10")
    t.add("E(",     "\u1F11")
    t.add("E)\\",   "\u1F12")
    t.add("E(\\",   "\u1F13")
    t.add("E)/",    "\u1F14")
    t.add("E(/",    "\u1F15")
    t.add("H)",     "\u1F20")
    t.add("H(",     "\u1F21")
    t.add("H)\\",   "\u1F22")
    t.add("H(\\",   "\u1F23")
    t.add("H)/",    "\u1F24")
    t.add("H(/",    "\u1F25")
    t.add("I)",     "\u1F30")
    t.add("I(",     "\u1F31")
    t.add("I)\\",   "\u1F32")
    t.add("I(\\",   "\u1F33")
    t.add("I)/",    "\u1F34")
    t.add("I(/",    "\u1F35")
    t.add("O)",     "\u1F40")
    t.add("O(",     "\u1F41")
    t.add("O)\\",   "\u1F42")
    t.add("O(\\",   "\u1F43")
    t.add("O)/",    "\u1F44")
    t.add("O(/",    "\u1F45")
    t.add("U)",     "\u1F50")
    t.add("U(",     "\u1F51")
    t.add("U)\\",   "\u1F52")
    t.add("U(\\",   "\u1F53")
    t.add("U)/",    "\u1F54")
    t.add("U(/",    "\u1F55")
    t.add("W)",     "\u1F60")
    t.add("W(",     "\u1F61")
    t.add("W)\\",   "\u1F62")
    t.add("W(\\",   "\u1F63")
    t.add("W)/",    "\u1F64")
    t.add("W(/",    "\u1F65")

    t.add("A)=",    "\u1F06")
    t.add("A(=",    "\u1F07")
    t.add("H)=",    "\u1F26")
    t.add("H(=",    "\u1F27")
    t.add("I)=",    "\u1F36")
    t.add("I(=",    "\u1F37")
    t.add("U)=",    "\u1F56")
    t.add("U(=",    "\u1F57")
    t.add("W)=",    "\u1F66")
    t.add("W(=",    "\u1F67")

    t.add("*A)",     "\u1F08")
    t.add("*)A",     "\u1F08")
    t.add("*A(",     "\u1F09")
    t.add("*(A",     "\u1F09")
    #
    t.add("*(\A",    "\u1F0B")
    t.add("*A)/",    "\u1F0C")
    t.add("*)/A",    "\u1F0C")
    t.add("*A(/",    "\u1F0F")
    t.add("*(/A",    "\u1F0F")
    t.add("*E)",     "\u1F18")
    t.add("*)E",     "\u1F18")
    t.add("*E(",     "\u1F19")
    t.add("*(E",     "\u1F19")
    #
    t.add("*(\E",    "\u1F1B")
    t.add("*E)/",    "\u1F1C")
    t.add("*)/E",    "\u1F1C")
    t.add("*E(/",    "\u1F1D")
    t.add("*(/E",    "\u1F1D")

    t.add("*H)",     "\u1F28")
    t.add("*)H",     "\u1F28")
    t.add("*H(",     "\u1F29")
    t.add("*(H",     "\u1F29")
    t.add("*H)\\",   "\u1F2A")
    t.add(")\\*H",   "\u1F2A")
    t.add("*)\\H",    "\u1F2A")
    #
    t.add("*H)/",    "\u1F2C")
    t.add("*)/H",    "\u1F2C")
    #
    t.add("*)=H",    "\u1F2E")
    t.add("(/*H",    "\u1F2F")
    t.add("*(/H",    "\u1F2F")
    t.add("*I)",     "\u1F38")
    t.add("*)I",     "\u1F38")
    t.add("*I(",     "\u1F39")
    t.add("*(I",     "\u1F39")
    #
    #
    t.add("*I)/",    "\u1F3C")
    t.add("*)/I",    "\u1F3C")
    #
    #
    t.add("*I(/",    "\u1F3F")
    t.add("*(/I",    "\u1F3F")
    #
    t.add("*O)",     "\u1F48")
    t.add("*)O",     "\u1F48")
    t.add("*O(",     "\u1F49")
    t.add("*(O",     "\u1F49")
    #
    #
    t.add("*(\O",    "\u1F4B")
    t.add("*O)/",    "\u1F4C")
    t.add("*)/O",    "\u1F4C")
    t.add("*O(/",    "\u1F4F")
    t.add("*(/O",    "\u1F4F")
    #
    t.add("*U(",     "\u1F59")
    t.add("*(U",     "\u1F59")
    #
    t.add("*(/U",    "\u1F5D")
    #
    t.add("*(=U",    "\u1F5F")

    t.add("*W)",     "\u1F68")
    t.add("*W(",     "\u1F69")
    t.add("*(W",     "\u1F69")
    #
    #
    t.add("*W)/",    "\u1F6C")
    t.add("*)/W",    "\u1F6C")
    t.add("*W(/",    "\u1F6F")
    t.add("*(/W",    "\u1F6F")

    t.add("*A)=",    "\u1F0E")
    t.add("*)=A",    "\u1F0E")
    t.add("*A(=",    "\u1F0F")
    t.add("*W)=",    "\u1F6E")
    t.add("*)=W",    "\u1F6E")
    t.add("*W(=",    "\u1F6F")
    t.add("*(=W",    "\u1F6F")

    t.add("A\\",    "\u1F70")
    t.add("A/",     "\u1F71")
    t.add("E\\",    "\u1F72")
    t.add("E/",     "\u1F73")
    t.add("H\\",    "\u1F74")
    t.add("H/",     "\u1F75")
    t.add("I\\",    "\u1F76")
    t.add("I/",     "\u1F77")
    t.add("O\\",    "\u1F78")
    t.add("O/",     "\u1F79")
    t.add("U\\",    "\u1F7A")
    t.add("U/",     "\u1F7B")
    t.add("W\\",    "\u1F7C")
    t.add("W/",     "\u1F7D")

    t.add("A)|",    "\u1F80")
    t.add("A)/|",   "\u1F84")
    t.add("A(/|",   "\u1F85")
    t.add("A)=|",   "\u1F86")
    t.add("*A)|",   "\u1F88")
    t.add("*A)=|",  "\u1F8E")
    t.add("H)|",    "\u1F90")
    t.add("H(|",    "\u1F91")
    t.add("H)/|",   "\u1F94")
    t.add("H)=|",   "\u1F96")
    t.add("H(=|",   "\u1F97")
    t.add("W)|",    "\u1FA0")
    t.add("W)/|",   "\u1FA4")
    t.add("W(=|",   "\u1FA7")
    t.add("*W)/|",  "\u1FAC")

    t.add("A=",     "\u1FB6")
    t.add("H=",     "\u1FC6")
    t.add("I=",     "\u1FD6")
    t.add("U=",     "\u1FE6")
    t.add("W=",     "\u1FF6")

    t.add("I\\+",   "\u1FD2")
    t.add("I/+",    "\u1FD3")
    t.add("I+/",    "\u1FD3")
    t.add("U\\+",   "\u1FE2")
    t.add("U/+",    "\u1FE3")

    t.add("A|",     "\u1FB3")
    t.add("A/|",    "\u1FB4")
    t.add("H|",     "\u1FC3")
    t.add("H/|",    "\u1FC4")
    t.add("W|",     "\u1FF3")
    t.add("W|/",    "\u1FF4")
    t.add("W/|",    "\u1FF4")

    t.add("A=|",    "\u1FB7")
    t.add("H=|",    "\u1FC7")
    t.add("W=|",    "\u1FF7")

    t.add("R(",     "\u1FE4")
    t.add("*R(",    "\u1FEC")
    t.add("*(R",    "\u1FEC")

#    t.add("~",      u"~")
    t.add("-",      "-")

#    t.add("(null)", u"(null)")
#    t.add("&", "&")

    t.add("0", "0")
    t.add("1", "1")
    t.add("2", "2")
    t.add("3", "3")
    t.add("4", "4")
    t.add("5", "5")
    t.add("6", "6")
    t.add("7", "7")
    t.add("8", "8")
    t.add("9", "9")

    t.add("@", "@")
    t.add("$", "$")

    t.add(" ", " ")

    t.add(".", ".")
    t.add(",", ",")
    t.add("'", "'")
    t.add(":", ":")
    t.add(";", ";")
    t.add("_", "_")

    t.add("[", "[")
    t.add("]", "]")

    t.add("\n", "")

    return t


def simplify_tag(tag):
    """Simplify the given tag, returning only the POS portion.

    This function may be given as the tag_mapping_function to the
    nltk.corpus.reader.TaggedCorpusReader (or similar) class. This allows the
    argument simplify_tags=True to be passed to tagged_* methods on corpora."""

    # Derived from examples here:
    # http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tag.simplify-pysrc.html

    try:
        if '-' in tag:
            tag = tag.split('-')[0]
        return tag
    except:
        return tag


def convert_to_unicode(text):
    """Return the given betacode text as Unicode (with diacritics)."""

    result_tokens = []
    trie = _beta_to_unicode_trie()
    tokens = text.split()
    for token in tokens:
        a, b = trie.convert(token)
        if b:
            print((a.encode("UTF-8"), b))
            raise Exception
        result_tokens.append(a)
    result_text = ' '.join(result_tokens)
    return result_text


def strip_diacritics(text):
    """Return the given text string with Unicode diacritics removed."""

    # http://stackoverflow.com/a/518232
    decomposed_text = unicodedata.normalize('NFD', text)
    stripped_text = [char for char in decomposed_text if
                     unicodedata.category(char) != 'Mn']
    result_text = ''.join(stripped_text)
    return result_text


def unicode_normalize(text):
    """Return the given text normalized to Unicode NFC."""

    normalized_text = unicodedata.normalize('NFC', text)
    return normalized_text


def final_sigma(text):
    """Return the given text with final sigmas normalized to normal sigmas."""

    result_text = text.replace("\u03C2", "\u03C3")
    return result_text


def lowercase(text):
    """Return the given text in lowercase."""

    lowercase_text = text.lower()
    return lowercase_text


def remove_elision(text, diacritics=False):
    """Return the given text with all instances of elision removed.

    Pass diacritics=True if the input text contains diacritics. These
    must be removed for elisions can be detected and removed."""

    # All cases of elision derived from SBLGNT
    elisions = (
        ("αλλ’", "αλλα"),
        ("ανθ’", "αντι"),
        ("απ’", "απο"),
        ("αφ’", "απο"),
        ("δ’", "δε"),
        ("δι’", "δια"),
        ("επ’", "επι"),
        ("εφ’", "επι"),
        ("καθ’", "κατα"),
        ("κατ’", "κατα"),
        ("μεθ’", "μετα"),
        ("μετ’", "μετα"),
        ("μηδ’", "μηδε"),
        ("ουδ’", "ουδε"),
        ("παρ’", "παρα"),
        ("τουτ’", "τουτο"),
        ("υπ’", "υπο"),
        ("υφ’", "υπο")
        )

    if diacritics:
        text = strip_diacritics(text)
    # Standardize on the unicode elision character
    text = text.replace("'", "’")
    for orig, removed in elisions:
        text = text.replace(orig, removed)
    return text


def remove_assimilation(text):
    """Return the given text with all instances of assimilation normalized."""

    pass


def remove_punctuation(text):
    """Return the given text with punctuation removed."""

    punctuation = [".", ",", ";", "·", "[", "]", "§"]

    for item in punctuation:
        text = text.replace(item, "")
    return text


def normalize(text, betacode=False):
    """Return the given text in a normalized form suitable for indexing.

    Namely, return after converting to lowercase, removing diacritics,
    converting final sigma to sigma, expanding elision to the full
    form and normalizing for unicode. Pass betacode=True as an
    optional secord parameter to indicate that the text is in betacode
    format.

    """

    if betacode:
        text = convert_to_unicode(text)
    text = unicode_normalize(text)
    text = remove_punctuation(text)
    text = lowercase(text)
    text = final_sigma(text)
    text = strip_diacritics(text)
    text = remove_elision(text)
    # text = remove_assimilation(text)

    return text
