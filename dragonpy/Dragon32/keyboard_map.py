#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon Keyboard map:

        | PB0   PB1   PB2   PB3   PB4   PB5   PB6   PB7
    ----|----------------------------------------------
    PA0 |   0     1     2     3     4     5     6     7
    PA1 |   8     9     :     ;     ,     -     .     /
    PA2 |   @     A     B     C     D     E     F     G
    PA3 |   H     I     J     K     L     M     N     O
    PA4 |   P     Q     R     S     T     U     V     W
    PA5 |   X     Y     Z    Up  Down  Left Right Space
    PA6 | ENT   CLR   BRK   N/C   N/C   N/C   N/C  SHFT

    e.g.:
        'U' $55 -> col: 5 - row: 4
        'Y' $59 -> col: 1 - row: 5

    http://archive.worldofdragon.org/index.php?title=File:Dragon32Keyboard4.JPG
"""

import string

from dragonpy.utils.bits import invert_byte, is_bit_set, clear_bit
from dragonpy.utils.logging_utils import log


DRAGON_KEYMAP = {
    # TODO: Use PyGame event.scancode / Tkinter event.keycode constants

    "0": ((0, 0),), # 0
    "1": ((1, 0),), # 1
    "2": ((2, 0),), # 2
    "3": ((3, 0),), # 3
    "4": ((4, 0),), # 4
    "5": ((5, 0),), # 5
    "6": ((6, 0),), # 6
    "7": ((7, 0),), # 7

    "8": ((0, 1),), # 8
    "9": ((1, 1),), # 9
    ":": ((2, 1),), # :
    ";": ((3, 1),), # ;
    ",": ((4, 1),), # ,
    "-": ((5, 1),), # -
    ".": ((6, 1),), # .
    "/": ((7, 1),), # /

    "@": ((0, 2),), # @
    "A": ((1, 2),), # A
    "B": ((2, 2),), # B
    "C": ((3, 2),), # C
    "D": ((4, 2),), # D
    "E": ((5, 2),), # E
    "F": ((6, 2),), # F
    "G": ((7, 2),), # G

    "H": ((0, 3),), # H
    "I": ((1, 3),), # I
    "J": ((2, 3),), # J
    "K": ((3, 3),), # K
    "L": ((4, 3),), # L
    "M": ((5, 3),), # M
    "N": ((6, 3),), # N
    "O": ((7, 3),), # O

    "P": ((0, 4),), # P
    "Q": ((1, 4),), # Q
    "R": ((2, 4),), # R
    "S": ((3, 4),), # S
    "T": ((4, 4),), # T
    "U": ((5, 4),), # U
    "V": ((6, 4),), # V
    "W": ((7, 4),), # W

    "X": ((0, 5),), # X
    "Y": ((1, 5),), # Y
    "Z": ((2, 5),), # Z
    0x6f: ((3, 5),), # UP
    0x74: ((4, 5),), # DOWN
    0x71: ((5, 5),), # LEFT
    0x72: ((6, 5),), # RIGHT
    " ": ((7, 5),), # " " (Space)

    "\r": ((0, 6),), # ENTER - Char: '\r'   - keycode: dez.: 36,  hex: $24
    0x6e: ((1, 6),), # CLEAR - $6e is "Home" / "Pos 1" button
    "\x1b": ((2, 6),), # BREAK - $09 is "Escape" button

    0x32: ((7, 6),), # SHIFT (shift left)
    0x3e: ((7, 6),), # SHIFT (shift right)

    # Additional:

    "\x08": ((5, 5),), # $08 is Backspace mapped to "LEFT"

    # Shifted keys:

    "!": ((7, 6), (1, 0)), # Shift + "1"
    '"': ((7, 6), (2, 0)), # Shift + "2"
    "#": ((7, 6), (3, 0)), # Shift + "3"
    "$": ((7, 6), (4, 0)), # Shift + "4"
    "%": ((7, 6), (5, 0)), # Shift + "5"
    "&": ((7, 6), (6, 0)), # Shift + "6"
    "'": ((7, 6), (7, 0)), # Shift + "7"

    "(": ((7, 6), (0, 1)), # Shift + "8"
    ")": ((7, 6), (1, 1)), # Shift + "9"
    "*": ((7, 6), (2, 1)), # Shift + ":"
    "+": ((7, 6), (3, 1)), # Shift + ";"
    "<": ((7, 6), (4, 1)), # Shift + ","
    "=": ((7, 6), (5, 1)), # Shift + "-"
    ">": ((7, 6), (6, 1)), # Shift + "."
    "?": ((7, 6), (7, 1)), # Shift + "/"

    "a":  ((7, 6), (1, 2)), # Shift + "A"
    "b":  ((7, 6), (2, 2)), # Shift + "B"
    "c":  ((7, 6), (3, 2)), # Shift + "C"
    "d":  ((7, 6), (4, 2)), # Shift + "D"
    "e":  ((7, 6), (5, 2)), # Shift + "E"
    "f":  ((7, 6), (6, 2)), # Shift + "F"
    "g":  ((7, 6), (7, 2)), # Shift + "G"

    "h":  ((7, 6), (0, 3)), # Shift + "H"
    "i":  ((7, 6), (1, 3)), # Shift + "I"
    "j":  ((7, 6), (2, 3)), # Shift + "J"
    "k":  ((7, 6), (3, 3)), # Shift + "K"
    "l":  ((7, 6), (4, 3)), # Shift + "L"
    "m":  ((7, 6), (5, 3)), # Shift + "M"
    "n":  ((7, 6), (6, 3)), # Shift + "N"
    "o":  ((7, 6), (7, 3)), # Shift + "O"

    "p":  ((7, 6), (0, 4)), # Shift + "P"
    "q":  ((7, 6), (1, 4)), # Shift + "Q"
    "r":  ((7, 6), (2, 4)), # Shift + "R"
    "s":  ((7, 6), (3, 4)), # Shift + "S"
    "t":  ((7, 6), (4, 4)), # Shift + "T"
    "u":  ((7, 6), (5, 4)), # Shift + "U"
    "v":  ((7, 6), (6, 4)), # Shift + "V"
    "w":  ((7, 6), (7, 4)), # Shift + "W"

    "x":  ((7, 6), (0, 5)), # Shift + "X"
    "y":  ((7, 6), (1, 5)), # Shift + "Y"
    "z":  ((7, 6), (2, 5)), # Shift + "Z"
}


def get_dragon_col_row_values(char_or_code, auto_shift=True):
    if auto_shift and isinstance(char_or_code, basestring):
        if char_or_code in string.ascii_lowercase:
#             log.critical("auto shift lowercase char %s to UPPERCASE", repr(char_or_code))
            char_or_code = char_or_code.upper()
        elif char_or_code in string.ascii_uppercase:
#             log.critical("auto shift UPPERCASE char %s to lowercase", repr(char_or_code))
            char_or_code = char_or_code.lower()

    try:
        col_row_values = DRAGON_KEYMAP[char_or_code]
    except KeyError:
        col_row_values = ()
        log.critical("Key %s not supported or unknown.", repr(char_or_code))
    return col_row_values


def get_dragon_pia_result(char_or_code, pia0b, auto_shift=True):
    col_row_values = get_dragon_col_row_values(char_or_code, auto_shift=auto_shift)

    result = 0xff
    for col, row in col_row_values:
        if not is_bit_set(pia0b, bit=col):
            result = clear_bit(result, bit=row)
    return result


def test(char_or_code, auto_shift):
    """
    e.g.:

    input char is: 'U' $55 -> col: 5 - row: 4
    bit 0 - $ff02 in $fe (11111110) -> $ff00 out $ff (11111111) stored in $0152
    bit 1 - $ff02 in $fd (11111101) -> $ff00 out $ff (11111111) stored in $0153
    bit 2 - $ff02 in $fb (11111011) -> $ff00 out $ff (11111111) stored in $0154
    bit 3 - $ff02 in $f7 (11110111) -> $ff00 out $ff (11111111) stored in $0155
    bit 4 - $ff02 in $ef (11101111) -> $ff00 out $ff (11111111) stored in $0156
    bit 5 - $ff02 in $df (11011111) -> $ff00 out $ef (11101111) stored in $0157
    bit 6 - $ff02 in $bf (10111111) -> $ff00 out $ff (11111111) stored in $0158
    bit 7 - $ff02 in $7f (01111111) -> $ff00 out $ff (11111111) stored in $0159

    input char is: 'Y' $59 -> col: 1 - row: 5
    bit 0 - $ff02 in $fe (11111110) -> $ff00 out $ff (11111111) stored in $0152
    bit 1 - $ff02 in $fd (11111101) -> $ff00 out $df (11011111) stored in $0153
    bit 2 - $ff02 in $fb (11111011) -> $ff00 out $ff (11111111) stored in $0154
    bit 3 - $ff02 in $f7 (11110111) -> $ff00 out $ff (11111111) stored in $0155
    bit 4 - $ff02 in $ef (11101111) -> $ff00 out $ff (11111111) stored in $0156
    bit 5 - $ff02 in $df (11011111) -> $ff00 out $ff (11111111) stored in $0157
    bit 6 - $ff02 in $bf (10111111) -> $ff00 out $ff (11111111) stored in $0158
    bit 7 - $ff02 in $7f (01111111) -> $ff00 out $ff (11111111) stored in $0159
    """
    col_row_values = get_dragon_col_row_values(char_or_code, auto_shift=auto_shift)
    print "char/keycode: %s -> cols/rows: %s" % (repr(char_or_code), repr(col_row_values))

    for i in xrange(8):
        pia0b = invert_byte(2 ** i) # written into $ff02
        result = get_dragon_pia_result(char_or_code, pia0b) # read from $ff00
        addr = 0x152 + i
        print "PB%i - $ff02 in $%02x (%s) -> $ff00 out $%02x (%s) stored in $%04x" % (
            i, pia0b, '{0:08b}'.format(pia0b),
            result, '{0:08b}'.format(result),
            addr,
        )
    print "  ^                 ^^^^^^^^                     ^^^^^^^"
    print "  |                 ||||||||                     |||||||"
    print "col            col: 76543210              row -> 6543210"
    print


if __name__ == '__main__':
#    import doctest
#    print doctest.testmod(
#        #verbose=1
#    )

    import sys
    import Tkinter


    def verbose_value(value):
        return "dez.: %i, hex: $%02x" % (value, value)


    class TkKeycodes(object):
        def __init__(self):
            self.root = Tkinter.Tk()
            self.root.title("Keycode Test")
            # self.root.geometry("+500+300")
            self.root.bind("<Key>", self.event_key_pressed)
            self.root.update()

        def event_key_pressed(self, event):
            char_or_code = event.char or event.keycode

            print "Char: %s - keycode: %s - char_or_code: %s" % (
                repr(event.char), verbose_value(event.keycode),
                repr(char_or_code)
            )
            try:
                test(char_or_code,
#                     auto_shift=True
                    auto_shift=False
                )
            except:
                self.root.destroy()
                raise
            print

        def mainloop(self):
            self.root.mainloop()

    tk_keys = TkKeycodes()
    tk_keys.mainloop()

