#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon Keyboard map:

        | PB0   PB1   PB2   PB3   PB4   PB5   PB6   PB7
    ----|----------------------------------------------
    PA0 |   0     1     2     3     4     5     6     7
    PA1 |   8     9     *     ;     ,     -     .     /
    PA2 |   @     A     B     C     D     E     F     G
    PA3 |   H     I     J     K     L     M     N     O
    PA4 |   P     Q     R     S     T     U     V     W
    PA5 |   X     Y     Z    Up  Down  Left Right Space
    PA6 | ENT   CLR   BRK   N/C   N/C   N/C   N/C  SHFT

    e.g.:
        'U' $55 -> col: 5 - row: 4
        'Y' $59 -> col: 1 - row: 5
"""

from dragonpy.utils.bits import invert_byte, is_bit_set, clear_bit


DRAGON_KEYMAP = {
    0x30: (0, 0), #  0
    0x31: (1, 0), #  1
    0x32: (2, 0), #  2
    0x33: (3, 0), #  3
    0x34: (4, 0), #  4
    0x35: (5, 0), #  5
    0x36: (6, 0), #  6
    0x37: (7, 0), #  7

    0x38: (0, 1), #  8
    0x39: (1, 1), #  9
    0x2a: (2, 1), #  *
    0x3b: (3, 1), #  ;
    0x2c: (4, 1), #  ,
    0x2d: (5, 1), #  -
    0x2e: (6, 1), #  .
    0x2f: (7, 1), #  /

    0x40: (0, 2), #  @
    0x41: (1, 2), #  A
    0x42: (2, 2), #  B
    0x43: (3, 2), #  C
    0x44: (4, 2), #  D
    0x45: (5, 2), #  E
    0x46: (6, 2), #  F
    0x47: (7, 2), #  G

    0x48: (0, 3), #  H
    0x49: (1, 3), #  I
    0x4a: (2, 3), #  J
    0x4b: (3, 3), #  K
    0x4c: (4, 3), #  L
    0x4d: (5, 3), #  M
    0x4e: (6, 3), #  N
    0x4f: (7, 3), #  O

    0x50: (0, 4), #  P
    0x51: (1, 4), #  Q
    0x52: (2, 4), #  R
    0x53: (3, 4), #  S
    0x54: (4, 4), #  T
    0x55: (5, 4), #  U
    0x56: (6, 4), #  V
    0x57: (7, 4), #  W

    0x58: (0, 5), #  X
    0x59: (1, 5), #  Y
    0x5a: (2, 5), #  Z
    0x11148: (3, 5), #  UP - PyGame scancode! FIXME: All codes must be unique!
    0x50: (4, 5), #  DOWN - PyGame scancode!
    0x4b: (5, 5), #  LEFT - PyGame scancode!
    0x4d: (6, 5), #  RIGHT - PyGame scancode!
    0x20: (7, 5), #  " " (Space)

    0x0d: (0, 6), #  ENTER
    0x08: (1, 6), #  CLEAR
    0x1b: (2, 6), #  BREAK

    0x2a: (7, 6), #  SHIFT - PyGame scancode!
}


def get_dragon_col_row_values(value):
    col, row = DRAGON_KEYMAP[value]
    return col, row


# def get_dragon_rows(value):
#    """
#    0x55 U
#    col: 5 - row: 4
#    0 $20 00100000
#    1 $20 00100000
#    2 $20 00100000
#    3 $20 00100000
#    4 $ff 11111111
#    5 $20 00100000
#    6 $20 00100000
#    """
#    print hex(value), chr(value)
#
#    col, row = get_dragon_col_row_values(value)
#    print "col: %s - row: %s" % (col, row)
#    values = []
#    for row_no in xrange(7):
#        if row_no == row:
#            values.append(0xff)
#        else:
#            values.append(1 << col)
#
#        print "%i $%02x %s" % (row_no, values[-1], '{0:08b}'.format(values[-1]))
#    print
#    return values


# def get_dragon_rows(value):
#    """
#    0x55 U
#    col: 5 - row: 4
#    0 $00 00000000
#    1 $00 00000000
#    2 $00 00000000
#    3 $00 00000000
#    4 $20 00100000
#    5 $00 00000000
#    6 $00 00000000
#    """
#    print hex(value), chr(value)
#
#    col, row = get_dragon_col_row_values(value)
#    print "col: %s - row: %s" % (col, row)
#    values = []
#    for row_no in xrange(7):
#        if row_no == row:
#            values.append(1 << col)
#        else:
#            values.append(0x00)
#        print "%i $%02x %s" % (row_no, values[-1], '{0:08b}'.format(values[-1]))
#    print
#    return values


# def get_dragon_rows(value):
#    """
#    0x55 U
#    col: 5 - row: 4
#    0 $ff 11111111
#    1 $ff 11111111
#    2 $ff 11111111
#    3 $ff 11111111
#    4 $df 11011111
#    5 $ff 11111111
#    6 $ff 11111111
#    """
#    print hex(value), chr(value)
#
#    col, row = get_dragon_col_row_values(value)
#    print "col: %s - row: %s" % (col, row)
#    values = []
#    for row_no in xrange(7):
#        if row_no == row:
#            values.append(0xff & ~(1 << col))
#        else:
#            values.append(0xff)
#        print "%i $%02x %s" % (row_no, values[-1], '{0:08b}'.format(values[-1]))
#    print
#    return values


def get_dragon_rows(value):
    """
    0x55 U
    col: 5 - row: 4
    0 $df 11011111
    1 $df 11011111
    2 $df 11011111
    3 $df 11011111
    4 $00 00000000
    5 $df 11011111
    6 $df 11011111
    """
    print hex(value), chr(value)

    col, row = get_dragon_col_row_values(value)
    print "col: %s - row: %s" % (col, row)
    values = []
    for row_no in xrange(7):
        if row_no == row:
            values.append(0x00)
        else:
            values.append(0xff & ~(1 << col))
        print "%i $%02x %s" % (row_no, values[-1], '{0:08b}'.format(values[-1]))
    print
    return values


def get_dragon_pia_result2(keycode, pia0b):
#    print hex(keycode), chr(keycode)

    col, row = get_dragon_col_row_values(keycode)

#    print "col: %s - row: %s" % (col, row)
    # print '{0:08b}'.format(col),
#    print "row:", '{0:08b}'.format(row)

#    print "pia0b:", hex(pia0b), '{0:08b}'.format(pia0b)
    pia0b_mask = invert_byte(pia0b)
#     print "pia0b mask 1:", hex(pia0b_mask), '{0:08b}'.format(pia0b_mask)
    pia0b_mask = pia0b_mask >> 1
#     print "pia0b mask 2:", hex(pia0b_mask), '{0:08b}'.format(pia0b_mask)

    result = (1 << row) & pia0b_mask
#     result = row & pia0b_mask
    result = invert_byte(result)

#    print "result: AND", '{0:08b}'.format(row & pia0b_mask)
#    print "result: XOR", '{0:08b}'.format(row ^ pia0b_mask)

    return result

def get_dragon_pia_result(keycode, pia0b):
    col, row = get_dragon_col_row_values(keycode)

#     print col, row, '{0:08b}'.format(col), '{0:08b}'.format(row)
    result = 0xff

    if not is_bit_set(pia0b, bit=col):
        result = clear_bit(result, bit=row)

    return result


def test(char):
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
    char_value = ord(char)
    col, row = get_dragon_col_row_values(char_value)
    print "input char is: %s $%02x -> col: %s - row: %s" % (repr(char), char_value, col, row)

    for i in xrange(8):
        pia0b = invert_byte(2 ** i) # written into $ff02
        result = get_dragon_pia_result(char_value, pia0b) # read from $ff00
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
#     import doctest
#     print doctest.testmod(
#         #verbose=1
#     )

    test(char="U")
    test(char="Y")
    test(char="H")
    test(char="0")
    test(char="1")
    test(char="2")

    import sys
    sys.exit()

    get_dragon_rows(ord("U"))
    get_dragon_rows(ord("9"))
    get_dragon_rows(0x0d) # ENTER


    print "Test! input something! (Type 'q' or 'x' for quit)"
    while True:
        char = sys.stdin.read(1)
        sys.stdout.write("\n")

        sys.stdout.write("Your input: %i %s" % (ord(char), repr(char)))

        value = ord(char.upper())
        dragon_value = DRAGON_KEYMAP[value]

        sys.stdout.write(" - Mapped value: $%02x" % dragon_value)
        col, row = COL_ROW_MAP[dragon_value]
        sys.stdout.write(" - col: %s - row: %s" % (col, row))
        col = ~col & 0xff
        row = ~row & 0xff
        # ~ print col, row
        sys.stdout.write(" - bits: %s | %s" % (
            '{0:08b}'.format(col),
            '{0:08b}'.format(row)
        ))

        sys.stdout.write("\n")
        sys.stdout.flush()

        if char in ("q", "x"):
            print "Bye!"
            break

