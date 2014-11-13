#!/usr/bin/env python

"""
    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import itertools
import logging
import operator
import sys
import unittest

from dragonlib.utils.unittest_utils import TextTestRunner2
from dragonpy.tests.test_base import BaseCPUTestCase


log = logging.getLogger("DragonPy")


class Test6809_BranchInstructions(BaseCPUTestCase):
    """
    Test branch instructions
    """
    def test_BCC_no(self):
        self.cpu.cc.C = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x24, 0xf4, # BCC -12
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

    def test_BCC_yes(self):
        self.cpu.cc.C = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x24, 0xf4, # BCC -12    ; ea = $1002 + -12 = $ff6
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)

    def test_LBCC_no(self):
        self.cpu.cc.C = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x24, 0x07, 0xe4, # LBCC +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_LBCC_yes(self):
        self.cpu.cc.C = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x24, 0x07, 0xe4, # LBCC +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)

    def test_BCS_no(self):
        self.cpu.cc.C = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x25, 0xf4, # BCS -12
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

    def test_BCS_yes(self):
        self.cpu.cc.C = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x25, 0xf4, # BCS -12    ; ea = $1002 + -12 = $ff6
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)

    def test_LBCS_no(self):
        self.cpu.cc.C = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x25, 0x07, 0xe4, # LBCS +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_LBCS_yes(self):
        self.cpu.cc.C = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x25, 0x07, 0xe4, # LBCS +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)

    def test_BEQ_no(self):
        self.cpu.cc.Z = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x27, 0xf4, # BEQ -12
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

    def test_BEQ_yes(self):
        self.cpu.cc.Z = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x27, 0xf4, # BEQ -12    ; ea = $1002 + -12 = $ff6
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)

    def test_LBEQ_no(self):
        self.cpu.cc.Z = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x27, 0x07, 0xe4, # LBEQ +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_LBEQ_yes(self):
        self.cpu.cc.Z = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x27, 0x07, 0xe4, # LBEQ +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)

    def test_BGE_LBGE(self):
        for n, v in itertools.product(list(range(2)), repeat=2): # -> [(0, 0), (0, 1), (1, 0), (1, 1)]
            # print n, v, (n ^ v) == 0, n == v
            self.cpu.cc.N = n
            self.cpu.cc.V = v
            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x2c, 0xf4, # BGE -12    ; ea = $1002 + -12 = $ff6
            ])
#            print "%s - $%04x" % (self.cpu.cc.get_info, self.cpu.program_counter)
            if not operator.xor(n, v): # same as: (n ^ v) == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x10, 0x2c, 0x07, 0xe4, # LBGE +2020    ; ea = $1004 + 2020 = $17e8
            ])
            if (n ^ v) == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_BGT_LBGT(self):
        for n, v, z in itertools.product(list(range(2)), repeat=3):
            # -> [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ..., (1, 1, 1)]
            # print n, v, (n ^ v) == 0, n == v
            self.cpu.cc.N = n
            self.cpu.cc.V = v
            self.cpu.cc.Z = z
            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x2e, 0xf4, # BGT -12    ; ea = $1002 + -12 = $ff6
            ])
            if n == v and z == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x10, 0x2e, 0x07, 0xe4, # LBGT +2020    ; ea = $1004 + 2020 = $17e8
            ])
            if n == v and z == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_BHI_LBHI(self):
        for c, z in itertools.product(list(range(2)), repeat=2): # -> [(0, 0), (0, 1), (1, 0), (1, 1)]
            self.cpu.cc.C = c
            self.cpu.cc.Z = z
            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x22, 0xf4, # BHI -12    ; ea = $1002 + -12 = $ff6
            ])
#            print "%s - $%04x" % (self.cpu.cc.get_info, self.cpu.program_counter)
            if c == 0 and z == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x10, 0x22, 0x07, 0xe4, # LBHI +2020    ; ea = $1004 + 2020 = $17e8
            ])
            if c == 0 and z == 0:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_BHS_no(self):
        self.cpu.cc.Z = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x2f, 0xf4, # BHS -12
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

    def test_BHS_yes(self):
        self.cpu.cc.Z = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x2f, 0xf4, # BHS -12    ; ea = $1002 + -12 = $ff6
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)

    def test_LBHS_no(self):
        self.cpu.cc.Z = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x2f, 0x07, 0xe4, # LBHS +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_LBHS_yes(self):
        self.cpu.cc.Z = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x2f, 0x07, 0xe4, # LBHS +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)

    def test_BPL_no(self):
        self.cpu.cc.N = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x2a, 0xf4, # BPL -12
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

    def test_BPL_yes(self):
        self.cpu.cc.N = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x2a, 0xf4, # BPL -12    ; ea = $1002 + -12 = $ff6
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)

    def test_LBPL_no(self):
        self.cpu.cc.N = 1
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x2a, 0x07, 0xe4, # LBPL +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)

    def test_LBPL_yes(self):
        self.cpu.cc.N = 0
        self.cpu_test_run2(start=0x1000, count=1, mem=[
            0x10, 0x2a, 0x07, 0xe4, # LBPL +2020    ; ea = $1004 + 2020 = $17e8
        ])
        self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)

    def test_BLT_LBLT(self):
        for n, v in itertools.product(list(range(2)), repeat=2): # -> [(0, 0), (0, 1), (1, 0), (1, 1)]
            self.cpu.cc.N = n
            self.cpu.cc.V = v
            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x2d, 0xf4, # BLT -12    ; ea = $1002 + -12 = $ff6
            ])
#            print "%s - $%04x" % (self.cpu.cc.get_info, self.cpu.program_counter)
            if operator.xor(n, v): # same as: n ^ v == 1
                self.assertEqualHex(self.cpu.program_counter.get(), 0xff6)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1002)

            self.cpu_test_run2(start=0x1000, count=1, mem=[
                0x10, 0x2d, 0x07, 0xe4, # LBLT +2020    ; ea = $1004 + 2020 = $17e8
            ])
            if operator.xor(n, v):
                self.assertEqualHex(self.cpu.program_counter.get(), 0x17e8)
            else:
                self.assertEqualHex(self.cpu.program_counter.get(), 0x1004)


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log,
#         level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test6809_BranchInstructions",
#            "Test6809_BranchInstructions.test_BLT_LBLT",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
