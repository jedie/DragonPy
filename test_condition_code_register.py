#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from test_base import BaseTestCase, TestCPU


class CCTestCase(BaseTestCase):
    def setUp(self):
        self.cpu = TestCPU()

    def test_set_get(self):
        for i in xrange(256):
            self.cpu.cc.set(i)
            status_byte = self.cpu.cc.get()
            self.assertEqual(status_byte, i)

    def test_update_NZ_8(self):
        self.cpu.cc.update_NZ_8(r=0x12)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)

        self.cpu.cc.update_NZ_8(r=0x0)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)

        self.cpu.cc.update_NZ_8(r=0x80)
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)

    def test_update_NZ0_16(self):
        self.cpu.cc.update_NZ0_16(r=0x7fff) # 0x7fff == 32767
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

        self.cpu.cc.update_NZ0_16(r=0x00)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 0)

        self.cpu.cc.update_NZ0_16(r=0x8000) # signed 0x8000 == -32768
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_update_NZ0_8(self):
        self.cpu.cc.update_NZ0_8(0x7f)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

        self.cpu.cc.update_NZ0_8(0x100)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 1)

    def test_update_NZVC_8(self):
        a = 1
        b = 2
        r = a + b
        self.cpu.cc.update_NZVC_8(a, b, r)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)
        self.assertEqual(self.cpu.cc.C, 0)

        a = 0xff
        b = 1
        r = a + b
        self.cpu.cc.update_NZVC_8(a, b, r)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 1) # FIXME
        self.assertEqual(self.cpu.cc.C, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)


