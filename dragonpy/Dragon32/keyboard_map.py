#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon Keyboard map:

          LSB              $FF02                    MSB
        | PB0   PB1   PB2   PB3   PB4   PB5   PB6   PB7 <- column
    ----|----------------------------------------------
    PA0 |   0     1     2     3     4     5     6     7    LSB
    PA1 |   8     9     :     ;     ,     -     .     /     $
    PA2 |   @     A     B     C     D     E     F     G     F
    PA3 |   H     I     J     K     L     M     N     O     F
    PA4 |   P     Q     R     S     T     U     V     W     0
    PA5 |   X     Y     Z    Up  Down  Left Right Space     0
    PA6 | ENT   CLR   BRK   N/C   N/C   N/C   N/C  SHFT
    PA7 - Comparator input                                 MSB
     ^
     |
    row

    e.g.:
        'U' $55 -> column: PB5 - row: PA4
        'Y' $59 -> column: PB1 - row: PA5

    http://archive.worldofdragon.org/index.php?title=File:Dragon32Keyboard4.JPG


    CoCo keyboard map:

        | PB0   PB1   PB2   PB3   PB4   PB5   PB6   PB7
    ----|----------------------------------------------
    PA0 |   @     A     B     C     D     E     F     G
    PA1 |   H     I     J     K     L     M     N     O
    PA2 |   P     Q     R     S     T     U     V     W
    PA3 |   X     Y     Z    Up  Down  Left Right Space
    PA4 |   0     1     2     3     4     5     6     7
    PA5 |   8     9     :     ;     ,     -     .     /
    PA6 | ENT   CLR   BRK   N/C   N/C   N/C   N/C  SHFT
"""

from __future__ import absolute_import, division, print_function
import six
xrange = six.moves.xrange

import string

from dragonlib.utils.auto_shift import invert_shift
import logging

log = logging.getLogger(__name__)
from dragonpy.utils.bits import invert_byte, is_bit_set, clear_bit


DRAGON_KEYMAP = {
    # TODO: Use PyGame event.scancode / Tkinter event.keycode constants

    # Key: ((column, row),(column2, row2))
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
    'Up': ((3, 5),), # UP
    'Down': ((4, 5),), # DOWN
    'Left': ((5, 5),), # LEFT
    'Right': ((6, 5),), # RIGHT
    " ": ((7, 5),), # " " (Space)

    'Return': ((0, 6),), # ENTER - Char: '\r'   - keycode: dez.: 36,  hex: $24
    'Home': ((1, 6),), # CLEAR - $6e is "Home" / "Pos 1" button
    'Escape': ((2, 6),), # BREAK - $09 is "Escape" button

    'Shift_L': ((7, 6),), # SHIFT (shift left)
    'Shift_R': ((7, 6),), # SHIFT (shift right)

    # Additional:

    'BackSpace': ((5, 5),), # $08 is Backspace mapped to "LEFT"

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

COCO_ROW_MAP = {
    0:4,
    1:5,
    2:0,
    3:1,
    4:2,
    5:3,
    6:6,
}

# Use the Dragon map and just swap the rows
COCO_KEYMAP = {}
for key, coordinates in list(DRAGON_KEYMAP.items()):
    coco_coordinates = []
    for column, row in coordinates:
        new_row = COCO_ROW_MAP[row]
        coco_coordinates.append((column, new_row))
    COCO_KEYMAP[key] = tuple(coco_coordinates)



def _get_col_row_values(inkey, keymap):
    try:
        col_row_values = keymap[inkey]
    except KeyError:
        col_row_values = ()
        log.critical("Key %r not supported or unknown.", inkey)
    return col_row_values


def _set_bits(pia0b, col_row_values):
    result = 0xff
    for col, row in col_row_values:
        if not is_bit_set(pia0b, bit=col):
            result = clear_bit(result, bit=row)
    return result


def get_dragon_keymatrix_pia_result(inkey, pia0b):
    col_row_values = _get_col_row_values(inkey, DRAGON_KEYMAP)
    result = _set_bits(pia0b, col_row_values)
    return result


def get_coco_keymatrix_pia_result(inkey, pia0b):
    col_row_values = _get_col_row_values(inkey, COCO_KEYMAP)
    result = _set_bits(pia0b, col_row_values)
    return result

def inkey_from_tk_event(event, auto_shift=True):
    if event.keysym_num>64000: # FIXME: Found a boundary number
        inkey=event.keysym
    else:
        inkey=event.char
        if auto_shift:
            inkey = invert_shift(inkey)
    return inkey

def add_to_input_queue(user_input_queue, txt):
    log.debug("Add %s to input queue.", repr(txt))
    txt=txt.replace("\r\n", "\r").replace("\n","\r")
    for char in txt:
        if char == "\r":
            char="Return" # tkinter event.keysym string
        log.debug("Add: %r", char)
        user_input_queue.put(char)

def test(inkey, matrix_name, auto_shift=False):
    """
    >>> test("P", "dragon")
    char/keycode: 'P' -> cols/rows: ((0, 2),)
    PB0 - $ff02 in $fe (11111110) -> $ff00 out $ef (11101111) stored in $0152
    PB1 - $ff02 in $fd (11111101) -> $ff00 out $ff (11111111) stored in $0153
    PB2 - $ff02 in $fb (11111011) -> $ff00 out $ff (11111111) stored in $0154
    PB3 - $ff02 in $f7 (11110111) -> $ff00 out $ff (11111111) stored in $0155
    PB4 - $ff02 in $ef (11101111) -> $ff00 out $ff (11111111) stored in $0156
    PB5 - $ff02 in $df (11011111) -> $ff00 out $ff (11111111) stored in $0157
    PB6 - $ff02 in $bf (10111111) -> $ff00 out $ff (11111111) stored in $0158
    PB7 - $ff02 in $7f (01111111) -> $ff00 out $bf (11111111) stored in $0159
      ^                 ^^^^^^^^                     ^^^^^^^
      |                 ||||||||                     |||||||
    col            col: 76543210              row -> 6543210

    >>> test("P", "coco")
    char/keycode: 'P' -> cols/rows: ((0, 2),)
    PB0 - $ff02 in $fe (11111110) -> $ff00 out $fb (11111011) stored in $0152
    PB1 - $ff02 in $fd (11111101) -> $ff00 out $ff (11111111) stored in $0153
    PB2 - $ff02 in $fb (11111011) -> $ff00 out $ff (11111111) stored in $0154
    PB3 - $ff02 in $f7 (11110111) -> $ff00 out $ff (11111111) stored in $0155
    PB4 - $ff02 in $ef (11101111) -> $ff00 out $ff (11111111) stored in $0156
    PB5 - $ff02 in $df (11011111) -> $ff00 out $ff (11111111) stored in $0157
    PB6 - $ff02 in $bf (10111111) -> $ff00 out $ff (11111111) stored in $0158
    PB7 - $ff02 in $7f (01111111) -> $ff00 out $bf (10111111) stored in $0159
      ^                 ^^^^^^^^                     ^^^^^^^
      |                 ||||||||                     |||||||
    col            col: 76543210              row -> 6543210
    """
    if matrix_name == "dragon":
        col_row_values = _get_col_row_values(inkey, DRAGON_KEYMAP)
    elif matrix_name == "coco":
        col_row_values = _get_col_row_values(inkey, COCO_KEYMAP)
    else:
        raise RuntimeError

    print("char/keycode: %s -> cols/rows: %s" % (repr(inkey), repr(col_row_values)))

    for i in xrange(8):
        pia0b = invert_byte(2 ** i) # written into $ff02
        if matrix_name == "dragon":
            result = get_dragon_keymatrix_pia_result(inkey, pia0b) # read from $ff00
        else:
            result = get_coco_keymatrix_pia_result(inkey, pia0b) # read from $ff00
        addr = 0x152 + i
        print("PB%i - $ff02 in $%02x (%s) -> $ff00 out $%02x (%s) stored in $%04x" % (
            i, pia0b, '{0:08b}'.format(pia0b),
            result, '{0:08b}'.format(result),
            addr,
        ))
    print("  ^                 ^^^^^^^^                     ^^^^^^^")
    print("  |                 ||||||||                     |||||||")
    print("col            col: 76543210              row -> 6543210")


if __name__ == '__main__':
    import doctest
    print(doctest.testmod(
        # verbose=1
    ))

#     import sys
#     sys.exit()

    import tkinter

    import pprint
    pprint.pprint(COCO_KEYMAP)


    def verbose_value(value):
        return "dez.: %i, hex: $%02x" % (value, value)


    class TkKeycodes(object):
        def __init__(self):
            self.root = tkinter.Tk()
            self.root.title("Keycode Test")
            # self.root.geometry("+500+300")
            self.root.bind("<Key>", self.event_key_pressed)
            self.root.update()

        def event_key_pressed(self, event):
            print("event.char: %-6r event.keycode: %-3r event.keysym: %-11r event.keysym_num: %5r" % (
                event.char, event.keycode, event.keysym, event.keysym_num
            ))
            inkey = inkey_from_tk_event(event, auto_shift=True)
            print("inkey from event: %r" % inkey)
            try:
                test(inkey,
                    matrix_name="dragon",
                    # matrix_name="coco",
                )
            except:
                self.root.destroy()
                raise
            print()

        def mainloop(self):
            self.root.mainloop()

    tk_keys = TkKeycodes()
    tk_keys.mainloop()

