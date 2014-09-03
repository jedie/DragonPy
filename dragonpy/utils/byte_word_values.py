#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    some code is borrowed from:
    XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


def signed5(x):
    """ convert to signed 5-bit """
    if x > 0xf: # 0xf == 2**4-1 == 15
        x = x - 0x20 # 0x20 == 2**5 == 32
    return x

def signed8(x):
    """ convert to signed 8-bit """
    if x > 0x7f: # 0x7f ==  2**7-1 == 127
        x = x - 0x100 # 0x100 == 2**8 == 256
    return x

def unsigned8(x):
    """ convert a signed 8-Bit value into a unsigned value """
    if x < 0:
        x = x + 0x0100 # 0x100 == 2**8 == 256
    return x

def signed16(x):
    """ convert to signed 16-bit """
    if x > 0x7fff: # 0x7fff ==  2**15-1 == 32767
        x = x - 0x10000 # 0x100 == 2**16 == 65536
    return x


def word2bytes(value):
    """
    >>> word2bytes(0xff09)
    (255, 9)

    >>> [hex(i) for i in word2bytes(0xffab)]
    ['0xff', '0xab']

    >>> word2bytes(0xffff +1)
    Traceback (most recent call last):
    ...
    AssertionError
    """
    assert 0 <= value <= 0xffff
    return (value >> 8, value & 0xff)


def bytes2word(byte_list):
    """
    >>> bytes2word([0xff,0xab])
    65451

    >>> hex(bytes2word([0xff,0xab]))
    '0xffab'
    """
    assert len(byte_list) == 2
    return (byte_list[0] << 8) + byte_list[1]


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(verbose=0))
