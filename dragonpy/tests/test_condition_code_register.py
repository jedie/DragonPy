#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from dragonlib.utils import six
xrange = six.moves.xrange

import unittest

from dragonpy.tests.test_base import BaseCPUTestCase
from dragonlib.utils.byte_word_values import signed8


class CCTestCase(BaseCPUTestCase):
    def test_set_get(self):
        for i in xrange(256):
            self.cpu.cc.set(i)
            status_byte = self.cpu.cc.get()
            self.assertEqual(status_byte, i)

    def test_HNZVC_8(self):
        for i in xrange(280):
            self.cpu.cc.set(0x00)
            r = i + 1 # e.g. ADDA 1 loop
            self.cpu.cc.update_HNZVC_8(a=i, b=1, r=r)
            # print r, self.cpu.cc.get_info

            # test half carry
            if r % 16 == 0:
                self.assertEqual(self.cpu.cc.H, 1)
            else:
                self.assertEqual(self.cpu.cc.H, 0)

            # test negative
            if 128 <= r <= 255:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if signed8(r) == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if r == 128 or r > 256:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if r > 255:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

            # Test that CC registers doesn't reset automaticly
            self.cpu.cc.set(0xff)
            r = i + 1 # e.g. ADDA 1 loop
            self.cpu.cc.update_HNZVC_8(a=i, b=1, r=r)
            # print "+++", r, self.cpu.cc.get_info
            self.assertEqualHex(self.cpu.cc.get(), 0xff)


    def test_update_NZ_8_A(self):
        self.cpu.cc.update_NZ_8(r=0x12)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)

    def test_update_NZ_8_B(self):
        self.cpu.cc.update_NZ_8(r=0x0)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_update_NZ_8_C(self):
        self.cpu.cc.update_NZ_8(r=0x80)
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)

    def test_update_NZ0_16_A(self):
        self.cpu.cc.update_NZ0_16(r=0x7fff) # 0x7fff == 32767
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZ0_16_B(self):
        self.cpu.cc.update_NZ0_16(r=0x00)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZ0_16_C(self):
        self.cpu.cc.update_NZ0_16(r=0x8000) # signed 0x8000 == -32768
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZ0_8_A(self):
        self.cpu.cc.update_NZ0_8(0x7f)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZ0_8_B(self):
        self.cpu.cc.update_NZ0_8(0x100)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZV_8_B(self):
        self.cpu.cc.update_NZ0_8(0x100)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)


