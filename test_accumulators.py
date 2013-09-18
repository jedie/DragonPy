#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    6809 is Big-Endian
    some code is from XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from test_base import BaseTestCase, TestCPU





class CC_AccumulatorTestCase(BaseTestCase):
    def setUp(self):
        self.cpu = TestCPU()

    def test_A01(self):
        self.cpu.accu.A = 0xff
        self.assertEqualHex(self.cpu.accu.A, 0xff)
        self.assertEqual(self.cpu.cc.V, 0)

        self.cpu.accu.A = 0xff + 1
        self.assertEqual(self.cpu.cc.V, 1)
        self.assertEqualHex(self.cpu.accu.A, 0x0) # XXX

    def test_B01(self):
        self.cpu.accu.B = 0x5a
        self.assertEqualHex(self.cpu.accu.B, 0x5a)
        self.assertEqual(self.cpu.cc.V, 0)

        self.cpu.accu.B = 0xff + 10
        self.assertEqual(self.cpu.cc.V, 1)
        self.assertEqualHex(self.cpu.accu.B, 0x9) # XXX

    def test_D01(self):
        self.cpu.accu.A = 0x12
        self.cpu.accu.B = 0xab
        self.assertEqualHex(self.cpu.accu.D, 0x12ab)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_D02(self):
        self.cpu.accu.D = 0xfd89
        self.assertEqualHex(self.cpu.accu.A, 0xfd)
        self.assertEqualHex(self.cpu.accu.B, 0x89)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_D03(self):
        self.cpu.accu.D = 0xffff + 1
        self.assertEqualHex(self.cpu.accu.A, 0x0) # XXX
        self.assertEqualHex(self.cpu.accu.B, 0x0) # XXX
        self.assertEqual(self.cpu.cc.V, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
