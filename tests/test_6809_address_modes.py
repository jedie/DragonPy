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

import logging
import sys
import unittest

from tests.test_base import TextTestRunner2, BaseTestCase


log = logging.getLogger("DragonPy")


class Test6809_AddressModes_LowLevel(BaseTestCase):
    def test_base_page_direct01(self):
        self.cpu.memory.load(0x1000, [0x12, 0x34, 0x0f])
        self.cpu.program_counter = 0x1000
        self.cpu.direct_page.set(0xab)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHexWord(ea, 0xab12)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHexWord(ea, 0xab34)

        self.cpu.direct_page.set(0x0)
        ea = self.cpu.get_ea_direct()
        self.assertEqualHexByte(ea, 0xf)

class Test6809_AddressModes_Indexed(BaseTestCase):
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
            "Test6809_AddressModes_Indexed",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
