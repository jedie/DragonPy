#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon Keyboard map:

        | PB0   PB1   PB2   PB3   PB4   PB5   PB6   PB7
    ----|----------------------------------------------
    PA0 |   0     1     2     3     4     5     6     7   <- 0x00 - 0x07
    PA1 |   8     9     *     ;     ,     -     .     /   <- 0x08 - 0x0f
    PA2 |   @     A     B     C     D     E     F     G   <- 0x10 - 0x17
    PA3 |   H     I     J     K     L     M     N     O   <- 0x18 - 0x1f
    PA4 |   P     Q     R     S     T     U     V     W   <- 0x20 - 0x27
    PA5 |   X     Y     Z    Up  Down  Left Right Space   <- 0x28 - 0x2f
    PA6 | ENT   CLR   BRK   N/C   N/C   N/C   N/C  SHFT   <- 0x30 - 0x37

    e.g.:
    "U" pressed: col = 5 - row = 4 => 0xfb => 11111011
    "A" pressed: col = 1 - row = 2 => 0xbf => 10111111

"""
from dragonpy.utils.bits import invert_byte


DRAGON_KEYMAP = {
    0x30: 0x00, # 0
    0x31: 0x01, # 1
    0x32: 0x02, # 2
    0x33: 0x03, # 3
    0x34: 0x04, # 4
    0x35: 0x05, # 5
    0x36: 0x06, # 6
    0x37: 0x07, # 7

    0x38: 0x08, # 8
    0x39: 0x09, # 9
    0x2a: 0x0a, # *
    0x3b: 0x0b, # ;
    0x2c: 0x0c, # ,
    0x2d: 0x0d, # -
    0x2e: 0x0e, # .
    0x2f: 0x0f, # /

    0x40: 0x10, # @
    0x41: 0x11, # A
    0x42: 0x12, # B
    0x43: 0x13, # C
    0x44: 0x14, # D
    0x45: 0x15, # E
    0x46: 0x16, # F
    0x47: 0x17, # G

    0x48: 0x18, # H
    0x49: 0x19, # I
    0x4a: 0x1a, # J
    0x4b: 0x1b, # K
    0x4c: 0x1c, # L
    0x4d: 0x1d, # M
    0x4e: 0x1e, # N
    0x4f: 0x1f, # O

    0x50: 0x20, # P
    0x51: 0x21, # Q
    0x52: 0x22, # R
    0x53: 0x23, # S
    0x54: 0x24, # T
    0x55: 0x25, # U
    0x56: 0x26, # V
    0x57: 0x27, # W

    0x58: 0x28, # X
    0x59: 0x29, # Y
    0x5a: 0x2a, # Z
    0x48: 0x2b, # UP - PyGame scancode!
    0x50: 0x2c, # DOWN - PyGame scancode!
    0x4b: 0x2d, # LEFT - PyGame scancode!
    0x4d: 0x2e, # RIGHT - PyGame scancode!
    0x20: 0x2f, # " " (Space)

    0x0d: 0x30, # ENTER
    0x08: 0x31, # CLEAR
    0x1b: 0x32, # BREAK

    0x2a: 0x37, # SHIFT - PyGame scancode!
}

COL_ROW_MAP = {}
for i in xrange(56):
    col = i & 7
    row = (i >> 3) & 7
    COL_ROW_MAP[i] = (col, row)
#    print i, col, row, '{0:08b}'.format(col), '{0:08b}'.format(row)


def get_dragon_col_row_values(value):
    dragon_value = DRAGON_KEYMAP[value]
    col, row = COL_ROW_MAP[dragon_value]
#    col = ~col & 0xff
#    row = ~row & 0xff
    return col, row


#def get_dragon_rows(value):
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


#def get_dragon_rows(value):
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


#def get_dragon_rows(value):
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


def get_dragon_pia_result(keycode, pia0b):
    """
    keycode -> the pressed key
    pia0b -> $ff02 -> PIA 0 B side Data register

    "U" -> row: 4 -> 00000100
        if pia0b==00000000: result=111111011
        if pia0b==11111111: result=111111111
        if pia0b==11111011: result=111111011

    >>> '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('00000000', 2)))
    '11011111'

    >>> '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('11111111', 2)))
    '11111111'
    >>> '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('10111111', 2)))
    '11111111'
    >>> '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('11101111', 2)))
    '11111111'

    >>> '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('11011111', 2)))
    '11011111'

    >>> '{0:08b}'.format(get_dragon_pia_result(0x00, pia0b=int('00000000', 2)))
    '11111111'
    """
    if keycode == 0x00:
        return 0xff
#    print hex(keycode), chr(keycode)

    col, row = get_dragon_col_row_values(keycode)

#    print "col: %s - row: %s" % (col, row)
    #print '{0:08b}'.format(col),
#    print "row:", '{0:08b}'.format(row)

#    print "pia0b:", hex(pia0b), '{0:08b}'.format(pia0b)
    pia0b_inverted = invert_byte(pia0b)
#    print "pia0b inverted:", hex(pia0b_inverted), '{0:08b}'.format(pia0b_inverted)

#    result = (1 << col) & pia0b_inverted
    result = (1 << row) & pia0b_inverted
    result = invert_byte(result)

#    print "result: AND", '{0:08b}'.format(row & pia0b_inverted)
#    print "result: XOR", '{0:08b}'.format(row ^ pia0b_inverted)

    return result






if __name__ == '__main__':
    import doctest
    print doctest.testmod(
        #verbose=1
    )

    print '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=0x00))
    print '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=0xff))
    print '{0:08b}'.format(get_dragon_pia_result(ord("U"), pia0b=int('11011111', 2)))

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
        #~ print col, row
        sys.stdout.write(" - bits: %s | %s" % (
            '{0:08b}'.format(col),
            '{0:08b}'.format(row)
        ))

        sys.stdout.write("\n")
        sys.stdout.flush()

        if char in ("q", "x"):
            print "Bye!"
            break

