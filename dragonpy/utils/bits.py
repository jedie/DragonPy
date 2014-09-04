#!/usr/bin/env python
# coding: utf-8

"""
    Utilities around bit manipulations
    ==================================

    Links:
        https://wiki.python.org/moin/BitManipulation
        https://wiki.python.org/moin/BitwiseOperators

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


def is_bit_set(value, bit):
    """
    Return True/False if the bit at offset >bit< is 1 or 0 in given value.

    bit 7 |      | bit 0
       ...10111101

    e.g.:

    >>> is_bit_set(0x01, bit=0) # 00000001
    True
    >>> is_bit_set(0xfd, bit=1) # 11111101
    False
    >>> is_bit_set(int('10000000', 2), bit=7)
    True
    >>> is_bit_set(int('01111111', 2), bit=7)
    False
    >>> is_bit_set(int('1111000011110000', 2), bit=11)
    False
    >>> is_bit_set(int('1111000011110000', 2), bit=12)
    True
    """
    return False if value & 2 ** bit == 0 else True


def get_bit(value, bit):
    """
    return 1 or 0 from the bit at the given offset >bit<, e.g.:

    >>> get_bit(0x01, bit=0) # 00000001
    1
    >>> get_bit(0xfd, bit=1) # 11111101
    0
    >>> get_bit(int('10000000', 2), bit=7)
    1
    >>> get_bit(int('01111111', 2), bit=7)
    0
    >>> get_bit(int('1111000011110000', 2), bit=11)
    0
    >>> get_bit(int('1111000011110000', 2), bit=12)
    1
    """
    return 0 if value & 2 ** bit == 0 else 1


def set_bit(value, bit):
    """
    returns an integer with the bit at offset >bit< set to 1.

    >>> set_bit(0x00, 2)
    4
    >>> set_bit(0x00, 7)
    128
    >>> '{0:08b}'.format(set_bit(int('00000000', 2), bit=5))
    '00100000'
    >>> '{0:08b}'.format(set_bit(int('10101010', 2), bit=0))
    '10101011'
    >>> '{0:08b}'.format(set_bit(int('1111000011110000', 2), bit=10))
    '1111010011110000'
    >>> '{0:08b}'.format(set_bit(int('11111111', 2), bit=3))
    '11111111'
    """
    return value | 1 << bit


def clear_bit(value, bit):
    """
    returns an integer with the bit at offset >bit< set to 0.

    >>> clear_bit(128, 7)
    0
    >>> clear_bit(0, 2)
    0

    >>> '{0:08b}'.format(clear_bit(int('11111111', 2), bit=5))
    '11011111'

    >>> '{0:08b}'.format(clear_bit(int('1111000011110000', 2), bit=13))
    '1101000011110000'
    """
    return value & ~(1 << bit)


def toggle_bit(value, bit):
    """
    >>> toggle_bit(128, 7)
    0
    >>> toggle_bit(0, 7)
    128

    >>> '{0:08b}'.format(toggle_bit(int('11111111', 2), bit=5))
    '11011111'
    >>> '{0:08b}'.format(toggle_bit(int('11011111', 2), bit=5))
    '11111111'

    >>> '{0:08b}'.format(toggle_bit(int('1111000011110000', 2), bit=13))
    '1101000011110000'
    >>> '{0:08b}'.format(toggle_bit(int('1101000011110000', 2), bit=13))
    '1111000011110000'
    """
    return value ^ 1 << bit


def invert_byte(value):
    """
    >>> '{0:08b}'.format(invert_byte(int('00001000',2)))
    '11110111'

    >>> '{0:08b}'.format(invert_byte(int('10101010',2)))
    '01010101'

    >>> '{0:08b}'.format(invert_byte(int('00110011',2)))
    '11001100'
    """
    return 2 ** 8 + ~value



if __name__ == "__main__":
    import doctest
    print(doctest.testmod(verbose=0))
