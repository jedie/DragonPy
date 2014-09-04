#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import unittest
from dragonpy.tests.test_base import BaseCPUTestCase


class CC_AccumulatorTestCase(BaseCPUTestCase):
    def test_A_01(self):
        self.cpu.accu_a.set(0xff)
        self.assertEqualHex(self.cpu.accu_a.get(), 0xff)

    def test_A_02(self):
        self.cpu.accu_a.set(0xff + 1)
        self.assertEqualHex(self.cpu.accu_a.get(), 0x00)

    def test_B_01(self):
        self.cpu.accu_b.set(0x5a)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x5a)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_B_02(self):
        self.cpu.accu_b.set(0xff + 10)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x09)

    def test_D_01(self):
        self.cpu.accu_a.set(0x12)
        self.cpu.accu_b.set(0xab)
        self.assertEqualHex(self.cpu.accu_d.get(), 0x12ab)

    def test_D_02(self):
        self.cpu.accu_d.set(0xfd89)
        self.assertEqualHex(self.cpu.accu_a.get(), 0xfd)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x89)

    def test_D_03(self):
        self.cpu.accu_d.set(0xffff + 1)
        self.assertEqualHex(self.cpu.accu_a.get(), 0x00)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x00)


if __name__ == '__main__':
    unittest.main(verbosity=2)
