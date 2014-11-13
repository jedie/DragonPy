#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Register changed Ops: TFR, EXG

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
import sys
import unittest

from dragonlib.utils.unittest_utils import TextTestRunner2
from dragonpy.tests.test_base import BaseCPUTestCase


log = logging.getLogger("DragonPy")


class Test6809_TFR(BaseCPUTestCase):
    def test_TFR_A_B(self):
        self.cpu.accu_a.set(0x12)
        self.cpu.accu_b.set(0x34)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1F, 0x89, # TFR A,B
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x12)
        self.assertEqualHexByte(self.cpu.accu_b.get(), 0x12)

    def test_TFR_B_A(self):
        self.cpu.accu_a.set(0x12)
        self.cpu.accu_b.set(0x34)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1F, 0x98, # TFR B,A
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x34)
        self.assertEqualHexByte(self.cpu.accu_b.get(), 0x34)

    def test_TFR_X_U(self):
        """
        LDX #$1234
        LDU #$abcd
        TFR X,U
        STX $20
        STU $30
        """
        self.cpu.index_x.set(0x1234)
        self.cpu.user_stack_pointer.set(0xabcd)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1F, 0x13, # TFR X,U
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), 0x1234)
        self.assertEqualHexWord(self.cpu.user_stack_pointer.get(), 0x1234)

    def test_TFR_CC_X(self):
        """
        transfer 8 bit register in a 16 bit register
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.cc.set(0x34)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x1F, 0xA1, # TFR CC,X
        ])
        self.assertEqualHexByte(self.cpu.cc.get(), 0x34)
        self.assertEqualHexWord(self.cpu.index_x.get(), 0xff34)

    def test_TFR_CC_A(self):
        """
        transfer 8 bit register in a 16 bit register
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.accu_a.set(0xab)
        self.cpu.cc.set(0x89)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x1F, 0xA8, # TFR CC,A
        ])
        self.assertEqualHexByte(self.cpu.cc.get(), 0x89)
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x89)

    def test_TFR_Y_B(self):
        """
        transfer 16 bit register in a 8 bit register
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.index_y.set(0x1234)
        self.cpu.accu_b.set(0xab)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x1F, 0x29, # TFR Y,B
        ])
        self.assertEqualHexWord(self.cpu.index_y.get(), 0x1234)
        self.assertEqualHexByte(self.cpu.accu_b.get(), 0x34)

    def test_TFR_undefined_A(self):
        """
        transfer undefined register in a 8 bit register
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.accu_a.set(0x12)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x1F, 0x68, # TFR undefined,A
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0xff)


class Test6809_EXG(BaseCPUTestCase):
    def test_EXG_A_B(self):
        self.cpu.accu_a.set(0xab)
        self.cpu.accu_b.set(0x12)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1E, 0x89, # EXG A,B
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x12)
        self.assertEqualHexByte(self.cpu.accu_b.get(), 0xab)

    def test_EXG_X_Y(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #       LDX   #$abcd     ; set X to $abcd
            0x10, 0x8E, 0x80, 0x4F, # LDY   #$804f     ; set Y to $804f
            0x1E, 0x12, #             EXG   X,Y        ; y,x=x,y
            0x9F, 0x20, #             STX   $20        ; store X to $20
            0x10, 0x9F, 0x40, #       STY   $40        ; store Y to $40
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x20), 0x804f) # X
        self.assertEqualHexWord(self.cpu.memory.read_word(0x40), 0xabcd) # Y

    def test_EXG_A_X(self):
        """
        exange 8 bit register with a 16 bit register
        TODO: verify this behaviour on real hardware!
        """
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x86, 0x56, #             LDA   #$56
            0x8E, 0x12, 0x34, #       LDX   #$1234
            0x1E, 0x81, #             EXG   A,X
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x34)
        self.assertEqualHexWord(self.cpu.index_x.get(), 0xff56)

    def test_EXG_A_CC(self):
        """
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.accu_a.set(0x1f)
        self.cpu.cc.set(0xe2)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1E, 0x8A, # EXG A,CC
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0xe2)
        self.assertEqualHexByte(self.cpu.cc.get(), 0x1f)

    def test_EXG_X_CC(self):
        """
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.index_x.set(0x1234)
        self.cpu.cc.set(0x56)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1E, 0x1A, # EXG X,CC
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), 0xff56)
        self.assertEqualHexByte(self.cpu.cc.get(), 0x34)

    def test_EXG_undefined_to_X(self):
        """
        TODO: verify this behaviour on real hardware!
        """
        self.cpu.index_x.set(0x1234)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x1E, 0xd1, # EXG undefined,X
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), 0xffff)



if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log,
        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
#        level=50 # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test6809_TFR",
#             "Test6809_TFR.test_TFR_CC_A",
#            "Test6809_EXG",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
