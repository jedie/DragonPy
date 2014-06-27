#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from test_base import BaseTestCase, TestCPU
import logging
import sys
from tests.test_base import TextTestRunner2
from cpu_utils.MC6809_registers import signed8


class CCTestCase(BaseTestCase):
    def test_set_get(self):
        for i in xrange(256):
            self.cpu.cc.set(i)
            status_byte = self.cpu.cc.get()
            self.assertEqual(status_byte, i)

    def test_HalfCarry(self):
        half_carry_must_set = range(0, 255, 16)
        for i in xrange(256):
            self.cpu.cc.set(0x00)
            self.cpu.cc.update_HNZVC_8(a=0, b=i, r=i) # e.g.: 0+2=2
            a = 0
            b = i
            r = i
            print i, self.cpu.cc.H, (0b00010000 & i) >> 5
#             if i in half_carry_must_set:
#                 self.assertEqual(self.cpu.cc.H, 1, "Error in %i" % i)
#             else:
#                 self.assertEqual(self.cpu.cc.H, 0, "Error in %i" % i)

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
    log = logging.getLogger("DragonPy")
    log.setLevel(
#        1
#         10 # DEBUG
#         20 # INFO
#         30 # WARNING
        40 # ERROR
#         50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    # XXX: Disable hacked XRoar trace
    import cpu6809; cpu6809.trace_file = None

    unittest.main(
        argv=(
            sys.argv[0],
#            "CCTestCase.test_HNZVC_8",

        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )


