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
from dragonpy.tests.test_base import BaseCPUTestCase


log = logging.getLogger("DragonPy")


class Test6809_AddressModes_LowLevel(BaseCPUTestCase):
    def test_base_page_direct01(self):
        self.cpu.memory.load(0x1000, [0x12, 0x34, 0x0f])
        self.cpu.program_counter.set(0x1000)
        self.cpu.direct_page.set(0xab)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHexWord(ea, 0xab12)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHexWord(ea, 0xab34)

        self.cpu.direct_page.set(0x0)
        ea = self.cpu.get_ea_direct()
        self.assertEqualHexByte(ea, 0xf)

class Test6809_AddressModes_Indexed(BaseCPUTestCase):
    def test_5bit_signed_offset_01(self):
        self.cpu.index_x.set(0x0300)
        self.cpu.index_y.set(0x1234)
        self.cpu_test_run(start=0x1b5c, end=None, mem=[0x10, 0xAF, 0x04]) # STY 4,X
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0304), 0x1234) # $0300 + $04 = $0304

    def test_5bit_signed_offset_02(self):
        """
        LDX #$abcd
        LDY #$50
        STX -16,Y
        """
        self.cpu.index_x.set(0xabcd)
        self.cpu.index_y.set(0x0050)
        self.cpu_test_run(start=0x1b5c, end=None, mem=[0xAF, 0x30]) # STX -16,Y
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0040), 0xabcd) # $0050 + $-10 = $0040

    def test_increment_by_1(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #            0000| LDX   #$abcd    ;set X to $abcd
            0x10, 0x8E, 0x00, 0x50, #      0003| LDY   #$50      ;set Y to $0050
            0xAF, 0xA0, #                  0007| STX   ,Y+       ;store X at $50 and Y+1
            0x10, 0x9F, 0x58, #            0009| STY   $58       ;store Y at $58
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0050), 0xabcd)
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x0051)

    def test_increment_by_2(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #            0000| LDX   #$abcd    ;set X to $abcd
            0x10, 0x8E, 0x00, 0x50, #      0003| LDY   #$50      ;set Y to $0050
            0xAF, 0xA1, #                  0007| STX   ,Y++      ;store X at $50 and Y+2
            0x10, 0x9F, 0x58, #            0009| STY   $58       ;store Y at $58
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0050), 0xabcd)
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x0052)

    def test_decrement_by_1(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #            0000| LDX   #$abcd    ;set X to $abcd
            0x10, 0x8E, 0x00, 0x50, #      0003| LDY   #$50      ;set Y to $0050
            0xAF, 0xA2, #                  0007| STX   ,-Y       ;Y-1 and store X at $50-1
            0x10, 0x9F, 0x58, #            0009| STY   $58       ;store Y at $58
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x004f), 0xabcd) # 50-1
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x004f)

    def test_decrement_by_2(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #            0000| LDX   #$abcd    ;set X to $abcd
            0x10, 0x8E, 0x00, 0x50, #      0003| LDY   #$50      ;set Y to $0050
            0xAF, 0xA3, #                  0007| STX   ,--Y      ;Y-2 and store X at $50-1
            0x10, 0x9F, 0x58, #            0009| STY   $58       ;store Y at $58
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x004e), 0xabcd) # 50-2
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x004e)

    def test_no_offset(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x8E, 0xAB, 0xCD, #            0000| LDX   #$abcd    ;set X to $abcd
            0x10, 0x8E, 0x00, 0x50, #      0003| LDY   #$50      ;set Y to $0050
            0xAF, 0xA4, #                  0007| STX   ,Y        ;store X at $50
            0x10, 0x9F, 0x58, #            0009| STY   $58       ;store Y at $58
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0050), 0xabcd) # X
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x0050) # Y

    def test_B_offset(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xC6, 0x03, #             LDB   #$3        ; set B to $3
            0x8E, 0xAB, 0xCD, #       LDX   #$abcd     ; set X to $abcd
            0x10, 0x8E, 0x00, 0x50, # LDY   #$50       ; set Y to $50
            0xAF, 0xA5, #             STX   B,Y        ; store X at Y and B
            0x10, 0x9F, 0x58, #       STY   $58        ; store Y
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0050 + 0x03), 0xabcd) # 53
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x0050) # Y

    def test_A_offset(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x86, 0xFC, #             LDA   #$-4       ; set A to $-4
            0x8E, 0xAB, 0xCD, #       LDX   #$abcd     ; set X to $abcd
            0x10, 0x8E, 0x00, 0x50, # LDY   #$50       ; set Y to $50
            0xAF, 0xA6, #             STX   A,Y        ; store X at Y and A
            0x10, 0x9F, 0x58, #       STY   $58        ; store Y
        ])
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0050 - 0x04), 0xabcd) # 4c
        self.assertEqualHexWord(self.cpu.memory.read_word(0x0058), 0x0050) # Y

    def test_8bit_offset(self):
        x = 0xabcd
        y = 0x00d0
        offset = 0x80 # signed = $-80
        self.cpu.index_x.set(x)
        self.cpu.index_y.set(y)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xAF, 0xA8, offset, #       STX   $30,Y      ; store X at Y -80 = $50
        ])
        self.assertEqualHexWord(self.cpu.index_y.get(), y)
        self.assertEqualHexWord(self.cpu.memory.read_word(0x50), x) # $d0 + $-80 = $50

    def test_16bit_offset(self):
        """
        LDX #$abcd   ; set X to $abcd
        LDY #$804f   ; set Y to $804f
        STX $8001,Y  ; store X at Y + $-7fff
        STY $20      ; store Y at $20
        """
        x = 0xabcd
        y = 0x804f
        offset = 0x8001 # signed = $-7fff
        offset_hi, offset_lo = divmod(offset, 0x100)
        self.cpu.index_x.set(x)
        self.cpu.index_y.set(y)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xAF, 0xA9, offset_hi, offset_lo, # STX $8001,Y   ; store X at Y + $-7fff
        ])
        self.assertEqualHexWord(self.cpu.index_y.get(), y)
        self.assertEqualHexWord(self.cpu.memory.read_word(0x50), x) # $804f + $-7fff = $50

    def test_D_offset(self):
        """
        LDX #$abcd   ; set X to $abcd
        LDY #$804f   ; set Y to $804f
        LDD #$8001   ; set D to $8001 signed = $-7fff
        STX D,Y      ; store X at $50 (Y + D)
        STY $20      ; store Y at $20
        """
        x = 0xabcd
        y = 0x804f
        d = 0x8001 # signed = $-7fff
        self.cpu.index_x.set(x)
        self.cpu.index_y.set(y)
        self.cpu.accu_d.set(d)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xAF, 0xAB, # STX D,Y  ; store X at Y + D
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), x)
        # $804f + $-7fff = $50
        self.assertEqualHexWord(self.cpu.memory.read_word(0x50), x) # $804f + $-7fff = $50

    def test_pc_offset_8bit_positive(self):
        x = 0xabcd
        self.cpu.index_x.set(x)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xAF, 0x8C, 0x12, # STX 12,PC
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), x)
        # ea = pc($2003) + $12 = $2015
        self.assertEqualHexWord(self.cpu.memory.read_word(0x2015), x)

    def test_pc_offset_8bit_negative(self):
        a = 0x56
        self.cpu.accu_a.set(a)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0xA7, 0x8C, 0x80, # STA 12,PC
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), a)
        # ea = pc($1003) + $-80 = $f83
        self.assertEqualHexByte(self.cpu.memory.read_byte(0x0f83), a)

    def test_pc_offset_16bit_positive(self):
        x = 0xabcd
        self.cpu.index_x.set(x)
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0xAF, 0x8D, 0x0a, 0xb0, # STX 1234,PC
        ])
        self.assertEqualHexWord(self.cpu.index_x.get(), x)
        # ea = pc($2004) + $ab0 = $2ab4
        self.assertEqualHexWord(self.cpu.memory.read_word(0x2ab4), x)

    def test_pc_offset_16bit_negative(self):
        a = 0x56
        self.cpu.accu_a.set(a)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0xA7, 0x8D, 0xf0, 0x10, # STA 12,PC
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), a)
        # ea = pc($1004) + $-ff0 = $14
        self.assertEqualHexByte(self.cpu.memory.read_byte(0x0014), a)

    def test_indirect_addressing(self):
        print("TODO!!!")


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
#            "Test6809_AddressModes_Indexed.test_8bit_offset",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
