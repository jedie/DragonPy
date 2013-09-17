#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    6809 is Big-Endian
    Based on XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging


log = logging.getLogger("DragonPy")


def signed8(x):
    """ convert to signed 8-bit """
    if x > 0x7f: # 0x7f ==  2**7-1 == 127
        x = x - 0x100 # 0x100 == 2**8 == 256
    return x


def signed16(x):
    """ convert to signed 16-bit """
    if x > 0x7fff: # 0x7fff ==  2**15-1 == 32767
        x = x - 0x10000 # 0x100 == 2**16 == 65536
    return x


class ConditionCodeRegister(object):
    """
    CC - 8 bit condition code register bits
    E - 0x80 - bit 7 - Entire register state stacked
    F - 0x40 - bit 6 - FIRQ interrupt masked
    H - 0x20 - bit 5 - Half-Carry
    I - 0x10 - bit 4 - IRQ interrupt masked
    N - 0x08 - bit 3 - Negative result (twos complement)
    Z - 0x04 - bit 2 - Zero result
    V - 0x02 - bit 1 - Overflow
    C - 0x01 - bit 0 - Carry (or borrow)
    """
    def __init__(self, *args, **kwargs):
        self.flag_E = 0
        self.flag_F = 0
        self.flag_H = 0
        self.flag_I = 0
        self.flag_N = 0
        self.flag_Z = 0
        self.flag_V = 0
        self.flag_C = 0

    def status_from_byte(self, status):
        self.flag_E, \
        self.flag_F, \
        self.flag_H, \
        self.flag_I, \
        self.flag_N, \
        self.flag_Z, \
        self.flag_V, \
        self.flag_C = [0 if status & x == 0 else 1 for x in (128, 64, 32, 16, 8, 4, 2, 1)]

    def status_as_byte(self):
        return self.flag_C | \
            self.flag_V << 1 | \
            self.flag_Z << 2 | \
            self.flag_N << 3 | \
            self.flag_I << 4 | \
            self.flag_H << 5 | \
            self.flag_F << 6 | \
            self.flag_E << 7

    ####

    def set_Z8(self, r):
        self.flag_Z = 1 if r & 0xff == 0 else 0

    def set_Z16(self, r):
        self.flag_Z = 1 if r & 0xffff == 0 else 0

    def set_N8(self, r):
        self.flag_N = 1 if signed8(r) < 0 else 0

    def set_N16(self, r):
        self.flag_N = 1 if signed16(r) < 0 else 0

    def set_H(self, a, b, r): # TODO: Add tests
        self.flag_H = 1 if (a ^ b ^ r) & 0x10 else 0

    def set_C8(self, r):
        self.flag_C = 1 if r & 0x100 else 0

    def set_C16(self, r):
        self.flag_C = 1 if r & 0x10000 else 0

    def set_V8(self, a, b, r): # FIXME
        self.flag_V = 1 if (a ^ b ^ r ^ (r >> 1)) & 0x80 else 0

    def set_V16(self, a, b, r): # FIXME
        self.flag_V = 1 if (a ^ b ^ r ^ (r >> 1)) & 0x8000 else 0

    ####

    def set_NZ8(self, r):
        self.set_N8(r)
        self.set_Z8(r)

    def set_NZ16(self, r):
        self.set_N16(r)
        self.set_Z16(r)

    def set_NZC8(self, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.set_C8(r)

    def set_NZC16(self, r):
        self.set_N16(r)
        self.set_Z16(r)
        self.set_C16(r)

    def set_NZVC8(self, a, b, r): # FIXME
        self.set_N8(r)
        self.set_Z8(r)
        self.set_V8(a, b, r)
        self.set_C8(r)

    def set_NZVC16(self, a, b, r): # FIXME
        self.set_N16(r)
        self.set_Z16(r)
        self.set_V16(a, b, r)
        self.set_C16(r)


#------------------------------------------------------------------------------
# TODO: move into separate test.py:

import unittest

class CCTestCase(unittest.TestCase):
    def setUp(self):
        self.cc = ConditionCodeRegister()

    def test_status_from_byte_to_byte(self):
        for i in xrange(256):
            self.cc.status_from_byte(i)
            status_byte = self.cc.status_as_byte()
            self.assertEqual(status_byte, i)

    def test_set_NZ8(self):
        self.cc.set_NZ8(r=0x12)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 0)

        self.cc.set_NZ8(r=0x0)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 1)

        self.cc.set_NZ8(r=0x80)
        self.assertEqual(self.cc.flag_N, 1)
        self.assertEqual(self.cc.flag_Z, 0)

    def test_set_NZ16(self):
        self.cc.set_NZ16(r=0x7fff) # 0x7fff == 32767
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 0)

        self.cc.set_NZ16(r=0x00)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 1)

        self.cc.set_NZ16(r=0x8000) # signed 0x8000 == -32768
        self.assertEqual(self.cc.flag_N, 1)
        self.assertEqual(self.cc.flag_Z, 0)

    def test_set_NZC8(self): # FIXME: C ???
        self.cc.set_NZC8(0x7f)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 0)
        self.assertEqual(self.cc.flag_C, 0)

        self.cc.set_NZC8(0x100)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 1)
        self.assertEqual(self.cc.flag_C, 1)

    def test_set_NZVC8(self):
        a = 1
        b = 2
        r = a + b
        self.cc.set_NZVC8(a, b, r)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 0)
        self.assertEqual(self.cc.flag_V, 0)
        self.assertEqual(self.cc.flag_C, 0)

        a = 255
        b = 1
        r = a + b
        self.cc.set_NZVC8(a, b, r)
        self.assertEqual(self.cc.flag_N, 0)
        self.assertEqual(self.cc.flag_Z, 1)
        self.assertEqual(self.cc.flag_V, 1)
        self.assertEqual(self.cc.flag_C, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

