#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test store and load ops

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
import sys
import unittest

from dragonlib.utils.unittest_utils import TextTestRunner2
from dragonpy.tests.test_base import BaseStackTestCase


log = logging.getLogger("DragonPy")


class Test6809_Store(BaseStackTestCase):
    def test_STA_direct(self):
        self.cpu.direct_page.set(0x41)
        self.cpu.accu_a.set(0xad)
        self.cpu_test_run(start=0x4000, end=None, mem=[0x97, 0xfe]) # STA <$fe (Direct)
        self.assertEqualHex(self.cpu.memory.read_byte(0x41fe), 0xad)

    def test_STB_extended(self):
        self.cpu.accu_b.set(0x81)
        self.cpu_test_run(start=0x4000, end=None, mem=[0xF7, 0x50, 0x10]) # STB $5010 (Extended)
        self.assertEqualHex(self.cpu.memory.read_byte(0x5010), 0x81)

    def test_STD_extended(self):
        self.cpu.accu_d.set(0x4321)
        self.cpu_test_run(start=0x4000, end=None, mem=[0xFD, 0x50, 0x01]) # STD $5001 (Extended)
        self.assertEqualHex(self.cpu.memory.read_word(0x5001), 0x4321)

    def test_STS_indexed(self):
        self.cpu.system_stack_pointer.set(0x1234)
        self.cpu.index_x.set(0x0218)
        self.cpu_test_run(start=0x1b5c, end=None, mem=[0x10, 0xef, 0x83]) # STS ,R-- (indexed)
        self.assertEqualHex(self.cpu.memory.read_word(0x0216), 0x1234) # 0x0218 -2 = 0x0216



class Test6809_Load(BaseStackTestCase):
    def test_LDD_immediate(self):
        self.cpu.accu_d.set(0)
        self.cpu_test_run(start=0x4000, end=None, mem=[0xCC, 0xfe, 0x12]) # LDD $fe12 (Immediate)
        self.assertEqualHex(self.cpu.accu_d.get(), 0xfe12)

    def test_LDD_extended(self):
        self.cpu.memory.write_word(0x5020, 0x1234)
        self.cpu_test_run(start=0x4000, end=None, mem=[0xFC, 0x50, 0x20]) # LDD $5020 (Extended)
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)


if __name__ == '__main__':
    log.setLevel(
        1
#        10 # DEBUG
#         20 # INFO
#         30 # WARNING
#         40 # ERROR
#        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    # XXX: Disable hacked XRoar trace
    import cpu6809; cpu6809.trace_file = None

    unittest.main(
        argv=(
            sys.argv[0],
            "Test6809_Store.test_STS_indexed",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
