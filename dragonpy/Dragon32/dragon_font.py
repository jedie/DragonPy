#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Tkinter
import itertools
from dragonpy.Dragon32.dragon_charmap import NORMAL, get_rgb_color, \
    get_hex_color, COLORS, INVERTED


BACKGROUND_CHAR = "."
FOREGROUND_CHAR = "X"
CHARS_DICT = {
    u'@': (# COMMERCIAL AT
        "...XXX..",
        "..X...X.",
        "......X.",
        "...XX.X.",
        "..X.X.X.",
        "..X.X.X.",
        "...XXX..",
        "........",
    ),
    u'A': (# LATIN CAPITAL LETTER A
        "....X...",
        "...X.X..",
        "..X...X.",
        "..X...X.",
        "..XXXXX.",
        "..X...X.",
        "..X...X.",
        "........",
    ),
    u'B': (# LATIN CAPITAL LETTER B
        "..XXXX..",
        "...X..X.",
        "...X..X.",
        "...XXX..",
        "...X..X.",
        "...X..X.",
        "..XXXX..",
        "........",
    ),
    u'C': (# LATIN CAPITAL LETTER C
        "...XXX..",
        "..X...X.",
        "..X.....",
        "..X.....",
        "..X.....",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'D': (# LATIN CAPITAL LETTER D
        "..XXXX..",
        "...X..X.",
        "...X..X.",
        "...X..X.",
        "...X..X.",
        "...X..X.",
        "..XXXX..",
        "........",
    ),
    u'E': (# LATIN CAPITAL LETTER E
        "..XXXXX.",
        "..X.....",
        "..X.....",
        "..XXXX..",
        "..X.....",
        "..X.....",
        "..XXXXX.",
        "........",
    ),
    u'F': (# LATIN CAPITAL LETTER F
        "..XXXXX.",
        "..X.....",
        "..X.....",
        "..XXXX..",
        "..X.....",
        "..X.....",
        "..X.....",
        "........",
    ),
    u'G': (# LATIN CAPITAL LETTER G
        "...XXXX.",
        "..X.....",
        "..X.....",
        "..X..XX.",
        "..X...X.",
        "..X...X.",
        "...XXXX.",
        "........",
    ),
    u'H': (# LATIN CAPITAL LETTER H
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..XXXXX.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "........",
    ),
    u'I': (# LATIN CAPITAL LETTER I
        "...XXX..",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "...XXX..",
        "........",
    ),
    u'J': (# LATIN CAPITAL LETTER J
        "......X.",
        "......X.",
        "......X.",
        "......X.",
        "..X...X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'K': (# LATIN CAPITAL LETTER K
        "..X...X.",
        "..X..X..",
        "..X.X...",
        "..XX....",
        "..X.X...",
        "..X..X..",
        "..X...X.",
        "........",
    ),
    u'L': (# LATIN CAPITAL LETTER L
        "..X.....",
        "..X.....",
        "..X.....",
        "..X.....",
        "..X.....",
        "..X.....",
        "..XXXXX.",
        "........",
    ),
    u'M': (# LATIN CAPITAL LETTER M
        "..X...X.",
        "..XX.XX.",
        "..X.X.X.",
        "..X.X.X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "........",
    ),
    u'N': (# LATIN CAPITAL LETTER N
        "..X...X.",
        "..XX..X.",
        "..X.X.X.",
        "..X..XX.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "........",
    ),
    u'O': (# LATIN CAPITAL LETTER O
        "..XXXXX.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..XXXXX.",
        "........",
    ),
    u'P': (# LATIN CAPITAL LETTER P
        "..XXXX..",
        "..X...X.",
        "..X...X.",
        "..XXXX..",
        "..X.....",
        "..X.....",
        "..X.....",
        "........",
    ),
    u'Q': (# LATIN CAPITAL LETTER Q
        "...XXX..",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X.X.X.",
        "..X..X..",
        "...XX.X.",
        "........",
    ),
    u'R': (# LATIN CAPITAL LETTER R
        "..XXXX..",
        "..X...X.",
        "..X...X.",
        "..XXXX..",
        "..X.X...",
        "..X..X..",
        "..X...X.",
        "........",
    ),
    u'S': (# LATIN CAPITAL LETTER S
        "...XXX..",
        "..X...X.",
        "...X....",
        "....X...",
        ".....X..",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'T': (# LATIN CAPITAL LETTER T
        "..XXXXX.",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "........",
    ),
    u'U': (# LATIN CAPITAL LETTER U
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'V': (# LATIN CAPITAL LETTER V
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "...X.X..",
        "...X.X..",
        "....X...",
        "....X...",
        "........",
    ),
    u'W': (# LATIN CAPITAL LETTER W
        "..X...X.",
        "..X...X.",
        "..X...X.",
        "..X.X.X.",
        "..X.X.X.",
        "..XX.XX.",
        "..X...X.",
        "........",
    ),
    u'X': (# LATIN CAPITAL LETTER X
        "..X...X.",
        "..X...X.",
        "...X.X..",
        "....X...",
        "...X.X..",
        "..X...X.",
        "..X...X.",
        "........",
    ),
    u'Y': (# LATIN CAPITAL LETTER Y
        "..X...X.",
        "..X...X.",
        "...X.X..",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "........",
    ),
    u'Z': (# LATIN CAPITAL LETTER Z
        "..XXXXX.",
        "......X.",
        ".....X..",
        "....X...",
        "...X....",
        "..X.....",
        "..XXXXX.",
        "........",
    ),
    u'[': (# LEFT SQUARE BRACKET
        "..XXX...",
        "..X.....",
        "..X.....",
        "..X.....",
        "..X.....",
        "..X.....",
        "..XXX...",
        "........",
    ),
    u'\\': (# REVERSE SOLIDUS
        "..X.....",
        "..X.....",
        "...X....",
        "....X...",
        ".....X..",
        "......X.",
        "......X.",
        "........",
    ),
    u']': (# RIGHT SQUARE BRACKET
        "....XXX.",
        "......X.",
        "......X.",
        "......X.",
        "......X.",
        "......X.",
        "....XXX.",
        "........",
    ),
    u'\u2191': (# UPWARDS ARROW
        "....X...",
        "...XXX..",
        "..X.X.X.",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "........",
    ),
    u'\u2190': (# LEFTWARDS ARROW
        "........",
        "....X...",
        "...X....",
        "..XXXXX.",
        "...X....",
        "....X...",
        "........",
        "........",
    ),
    u' ': (# SPACE
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
    ),
    u'!': (# EXCLAMATION MARK
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "........",
        "....X...",
        "........",
    ),
    u'"': (# QUOTATION MARK
        "...X.X..",
        "...X.X..",
        "...X.X..",
        "........",
        "........",
        "........",
        "........",
        "........",
    ),
    u'#': (# NUMBER SIGN
        "...X.X..",
        "...X.X..",
        "..XX.XX.",
        "........",
        "..XX.XX.",
        "...X.X..",
        "...X.X..",
        "........",
    ),
    u'$': (# DOLLAR SIGN
        "....X...",
        "...XXXX.",
        "..X.....",
        "...XXX..",
        "......X.",
        "..XXXX..",
        "....X...",
        "........",
    ),
    u'%': (# PERCENT SIGN
        "..XX..X.",
        "..XX..X.",
        ".....X..",
        "....X...",
        "...X....",
        "..X..XX.",
        "..X..XX.",
        "........",
    ),
    u'&': (# AMPERSAND
        "...X....",
        "..X.X...",
        "..X.X...",
        "...X....",
        "..X.X.X.",
        "..X..X..",
        "...XX.X.",
        "........",
    ),
    u"'": (# APOSTROPHE
        "...XX...",
        "...XX...",
        "...XX...",
        "........",
        "........",
        "........",
        "........",
        "........",
    ),
    u'(': (# LEFT PARENTHESIS
        "....X...",
        "...X....",
        "..X.....",
        "..X.....",
        "..X.....",
        "...X....",
        "....X...",
        "........",
    ),
    u')': (# RIGHT PARENTHESIS
        "....X...",
        ".....X..",
        "......X.",
        "......X.",
        "......X.",
        ".....X..",
        "....X...",
        "........",
    ),
    u'*': (# ASTERISK
        "........",
        "....X...",
        "...XXX..",
        "..XXXXX.",
        "...XXX..",
        "....X...",
        "........",
        "........",
    ),
    u'+': (# PLUS SIGN
        "........",
        "....X...",
        "....X...",
        "..XXXXX.",
        "....X...",
        "....X...",
        "........",
        "........",
    ),
    u',': (# COMMA
        "........",
        "........",
        "........",
        "..XX....",
        "..XX....",
        "...X....",
        "..X.....",
        "........",
    ),
    u'-': (# HYPHEN-MINUS
        "........",
        "........",
        "........",
        "..XXXXX.",
        "........",
        "........",
        "........",
        "........",
    ),
    u'.': (# FULL STOP
        "........",
        "........",
        "........",
        "........",
        "........",
        "..XX....",
        "..XX....",
        "........",
    ),
    u'/': (# SOLIDUS
        "......X.",
        "......X.",
        ".....X..",
        "....X...",
        "...X....",
        "..X.....",
        "..X.....",
        "........",
    ),
    u'0': (# DIGIT ZERO
        "...XX...",
        "..X..X..",
        "..X..X..",
        "..X..X..",
        "..X..X..",
        "..X..X..",
        "...XX...",
        "........",
    ),
    u'1': (# DIGIT ONE
        "....X...",
        "...XX...",
        "....X...",
        "....X...",
        "....X...",
        "....X...",
        "...XXX..",
        "........",
    ),
    u'2': (# DIGIT TWO
        "...XXX..",
        "..X...X.",
        "......X.",
        "...XXX..",
        "..X.....",
        "..X.....",
        "..XXXXX.",
        "........",
    ),
    u'3': (# DIGIT THREE
        "...XXX..",
        "..X...X.",
        "......X.",
        "....XX..",
        "......X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'4': (# DIGIT FOUR
        ".....X..",
        "....XX..",
        "...X.X..",
        "..XXXXX.",
        ".....X..",
        ".....X..",
        ".....X..",
        "........",
    ),
    u'5': (# DIGIT FIVE
        "..XXXXX.",
        "..X.....",
        "..XXXX..",
        "......X.",
        "......X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'6': (# DIGIT SIX
        "...XXX..",
        "..X.....",
        "..X.....",
        "..XXXX..",
        "..X...X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'7': (# DIGIT SEVEN
        "..XXXXX.",
        "......X.",
        ".....X..",
        "....X...",
        "...X....",
        "..X.....",
        "..X.....",
        "........",
    ),
    u'8': (# DIGIT EIGHT
        "...XXX..",
        "..X...X.",
        "..X...X.",
        "...XXX..",
        "..X...X.",
        "..X...X.",
        "...XXX..",
        "........",
    ),
    u'9': (# DIGIT NINE
        "...XXX..",
        "..X...X.",
        "..X...X.",
        "...XXXX.",
        "......X.",
        "......X.",
        "...XXX..",
        "........",
    ),
    u':': (# COLON
        "........",
        "...XX...",
        "...XX...",
        "........",
        "...XX...",
        "...XX...",
        "........",
        "........",
    ),
    u';': (# SEMICOLON
        "...XX...",
        "...XX...",
        "........",
        "...XX...",
        "...XX...",
        "....X...",
        "...X....",
        "........",
    ),
    u'<': (# LESS-THAN SIGN
        ".....X..",
        "....X...",
        "...X....",
        "..X.....",
        "...X....",
        "....X...",
        ".....X..",
        "........",
    ),
    u'=': (# EQUALS SIGN
        "........",
        "........",
        "..XXXXX.",
        "........",
        "..XXXXX.",
        "........",
        "........",
        "........",
    ),
    u'>': (# GREATER-THAN SIGN
        "...X....",
        "....X...",
        ".....X..",
        "......X.",
        ".....X..",
        "....X...",
        "...X....",
        "........",
    ),
    u'?': (# QUESTION MARK
        "...XX...",
        "..X..X..",
        ".....X..",
        "....X...",
        "....X...",
        "........",
        "....X...",
        "........",
    ),
}




class TkFont(object):
    """
    Important is that CACHE is used. Without cache the garbage-collection
    by Python will "remove" the created images in Tkinter.Canvas!
    """
    CACHE = {}
    def __init__(self, chars_dict, scale_factor):
        assert isinstance(scale_factor, int)
        assert scale_factor > 0

        self.chars_dict = chars_dict
        self.scale_factor = scale_factor

        temp = chars_dict["X"]
        self.width_real = len(temp[0])
        self.height_real = len(temp)

        self.width_scaled = self.width_real * self.scale_factor
        self.height_scaled = self.height_real * self.scale_factor

        print "Every character is %ipx x %ipx (incl. scale factor: %i)" % (
            self.width_scaled, self.height_scaled,
            self.scale_factor
        )

    def _generate_char(self, char, color):
        print "Generate char", char, color
        char_data = self.chars_dict[char]
        foreground, background = get_hex_color(color)
        foreground = "#%s" % foreground
        background = "#%s" % background

        img = Tkinter.PhotoImage(width=self.width_scaled, height=self.height_scaled)

        y = 0
        for line in char_data:
            for scaled_line in itertools.repeat(line, self.scale_factor):
                y += 1
                x = 0
                for bit in scaled_line:
                    for scaled_bit in itertools.repeat(bit, self.scale_factor):
                        x += 1
                        if scaled_bit == BACKGROUND_CHAR:
                            color = background
                        else:
                            assert scaled_bit == FOREGROUND_CHAR
                            color = foreground

                        img.put(color, (x, y))
        return img

    def get_char(self, char, color):
        try:
            return self.CACHE[(char, color)]
        except KeyError:
            img = self._generate_char(char, color)
            self.CACHE[(char, color)] = img
            return img


class TestTkFont(object):
    def __init__(self, row_count, tk_font, colors):
        self.row_count = row_count
        self.tk_font = tk_font
        self.colors = colors
        self.color_index = 0
        self.current_color = self.colors[self.color_index]

        self.root = Tkinter.Tk()
        self.root.title("TkFont Test")

        self.root.bind('<Down>', self.event_arrow_down)
        self.root.bind('<Up>', self.event_arrow_up)

        self.total_width = self.tk_font.width_scaled * self.row_count
        self.total_height = self.tk_font.height_scaled * (len(self.tk_font.chars_dict) / self.row_count)

        print "Window/Canvas geometry: %spx x %spx" % (self.total_width, self.total_height)
        self.root.geometry("+%i+%i" % (self.total_width, self.total_height))

        self.canvas = Tkinter.Canvas(self.root,
            width=self.total_width,
            height=self.total_height,
            bg="#ff0000"
        )
        self.canvas.pack()
        self.add_chars()

    def add_chars(self):
        print "Fill with", self.current_color
        chars_dict = self.tk_font.chars_dict
        for no, char in enumerate(sorted(chars_dict.keys())):
            y, x = divmod(no * self.tk_font.width_scaled, self.total_width)
            y *= self.tk_font.height_scaled
#             print "add %s color: %s to %i x %i" % (
#                 repr(char), self.current_color, x, y
#             )
            img = self.tk_font.get_char(char, self.current_color)

            self.canvas.create_image(x, y,
                image=img,
                state="normal",
                anchor=Tkinter.NW # NW == NorthWest
            )
            # self.root.update() # Not needed here!

    def event_arrow_up(self, event):
        self.color_index += 1
        if self.color_index >= len(self.colors):
            self.color_index = 0
        self.current_color = self.colors[self.color_index]
        self.add_chars()

    def event_arrow_down(self, event):
        self.color_index -= 1
        if self.color_index < 0:
            self.color_index = len(self.colors) - 1
        self.current_color = self.colors[self.color_index]
        self.add_chars()

    def mainloop(self):
        self.root.mainloop()


if __name__ == "__main__":
    tk_font = TkFont(CHARS_DICT,
#         scale_factor=1
#         scale_factor=2
#         scale_factor=3
        scale_factor=4
#         scale_factor=8
    )

    colors = (NORMAL, INVERTED) + COLORS

    t = TestTkFont(
        row_count=8,
        tk_font=tk_font,
        colors=colors,
    )
    t.mainloop()
    print " --- END --- "
