#!/usr/bin/env python
# encoding:utf-8

"""
    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import unittest
import itertools

from cpu6809 import CPU
from Dragon32.config import Dragon32Cfg
from Dragon32.mem_info import DragonMemInfo
from tests.test_base import TextTestRunner2, BaseTestCase, UnittestCmdArgs


log = logging.getLogger("DragonPy")


class BaseDragon32TestCase(BaseTestCase):
    # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4462
    INITIAL_SYSTEM_STACK_ADDR = 0x7f36
    INITIAL_USER_STACK_ADDR = 0x82ec

    def setUp(self):
        cmd_args = UnittestCmdArgs
        cfg = Dragon32Cfg(cmd_args)
        self.assertFalse(cfg.use_bus)
        cfg.mem_info = DragonMemInfo(log.debug)
        self.cpu = CPU(cfg)

        self.cpu._system_stack_pointer.set(self.INITIAL_SYSTEM_STACK_ADDR)
        self.cpu.user_stack_pointer.set(self.INITIAL_USER_STACK_ADDR)


class Test6809_AddressModes(BaseTestCase):
    def test_base_page_direct01(self):
        self.cpu.memory.load(0x1000, [0x12, 0x34, 0xf])
        self.cpu.program_counter = 0x1000
        self.cpu.direct_page.set(0xab)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHex(ea, 0xab12)

        ea = self.cpu.get_ea_direct()
        self.assertEqualHex(ea, 0xab34)

        self.cpu.direct_page.set(0x0)
        ea = self.cpu.get_ea_direct()
        self.assertEqualHex(ea, 0xf)


class Test6809_Register(BaseTestCase):
    def test_registerA(self):
        for i in xrange(255):
            self.cpu.accu_a.set(i)
            t = self.cpu.accu_a.get()
            self.assertEqual(i, t)

    def test_register_8bit_overflow(self):
        self.cpu.accu_a.set(0xff)
        a = self.cpu.accu_a.get()
        self.assertEqualHex(a, 0xff)

        self.cpu.accu_a.set(0x100)
        a = self.cpu.accu_a.get()
        self.assertEqualHex(a, 0)

        self.cpu.accu_a.set(0x101)
        a = self.cpu.accu_a.get()
        self.assertEqualHex(a, 0x1)

    def test_register_8bit_negative(self):
        self.cpu.accu_a.set(0)
        t = self.cpu.accu_a.get()
        self.assertEqualHex(t, 0)

        self.cpu.accu_a.set(-1)
        t = self.cpu.accu_a.get()
        self.assertEqualHex(t, 0xff)

        self.cpu.accu_a.set(-2)
        t = self.cpu.accu_a.get()
        self.assertEqualHex(t, 0xfe)

    def test_register_16bit_overflow(self):
        self.cpu.index_x.set(0xffff)
        x = self.cpu.index_x.get()
        self.assertEqual(x, 0xffff)

        self.cpu.index_x.set(0x10000)
        x = self.cpu.index_x.get()
        self.assertEqual(x, 0)

        self.cpu.index_x.set(0x10001)
        x = self.cpu.index_x.get()
        self.assertEqual(x, 1)

    def test_register_16bit_negative1(self):
        self.cpu.index_x.set(-1)
        x = self.cpu.index_x.get()
        self.assertEqualHex(x, 0xffff)

        self.cpu.index_x.set(-2)
        x = self.cpu.index_x.get()
        self.assertEqualHex(x, 0xfffe)

    def test_register_16bit_negative2(self):
        self.cpu.index_x.set(0)
        x = self.cpu.index_x.decrement()
        self.assertEqualHex(x, 0x10000 - 1)

        self.cpu.index_x.set(0)
        x = self.cpu.index_x.decrement(2)
        self.assertEqualHex(x, 0x10000 - 2)


class Test6809_ZeroFlag(BaseTestCase):
    def test_DECA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x1, # LDA $01
            0x4A, #      DECA
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_DECB(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0xC6, 0x1, # LDB $01
            0x5A, #      DECB
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_ADDA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0xff, # LDA $FF
            0x8B, 0x01, # ADDA #1
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_CMPA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x00, # LDA $00
            0x81, 0x00, # CMPA %00
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_COMA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0xFF, # LDA $FF
            0x43, #       COMA
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_NEGA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0xFF, # LDA $FF
            0x40, #       NEGA
        ])
        self.assertEqual(self.cpu.cc.Z, 0)

    def test_ANDA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0xF0, # LDA $F0
            0x84, 0x0F, # ANDA $0F
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_TFR(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x04, # LDA $04
            0x1F, 0x8a, # TFR A,CCR
        ])
        self.assertEqual(self.cpu.cc.Z, 1)

    def test_CLRA(self):
        self.assertEqual(self.cpu.cc.Z, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x4F, # CLRA
        ])
        self.assertEqual(self.cpu.cc.Z, 1)



class Test6809_CarryFlag(BaseTestCase):
    def test_LSRA(self):
        self.assertEqual(self.cpu.cc.C, 0)
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x99, # LDA $99
            0x44, #       LSRA
        ])
        self.assertEqual(self.cpu.cc.C, 1)



class Test6809_CC(BaseTestCase):
    """
    condition code register tests
    """
    def test_defaults(self):
        status_byte = self.cpu.cc.get()
        self.assertEqual(status_byte, 0)

    def test_from_to(self):
        for i in xrange(256):
            self.cpu.cc.set(i)
            status_byte = self.cpu.cc.get()
            self.assertEqual(status_byte, i)

    def test_set_register01(self):
        self.cpu.set_register(0x00, 0x1e12)
        self.assertEqual(self.cpu.accu_a.get(), 0x1e)
        self.assertEqual(self.cpu.accu_b.get(), 0x12)

    def test_AND(self):
        excpected_values = range(0, 128)
        excpected_values += range(0, 128)
        excpected_values += range(0, 4)

        for i in xrange(260):
            self.cpu.accu_a.set(i)
            self.cpu.cc.set(0x0e) # Set affected flags: ....NZV.
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x84, 0x7f, # ANDA #$7F
            ])
            r = self.cpu.accu_a.get()
            excpected_value = excpected_values[i]
#             print i, r, excpected_value, self.cpu.cc.get_info, self.cpu.cc.get()

            # test AND result
            self.assertEqual(r, excpected_value)

            # test all CC flags
            if r == 0:
                self.assertEqual(self.cpu.cc.get(), 4)
            else:
                self.assertEqual(self.cpu.cc.get(), 0)

    def test_LSL(self):
        excpected_values = range(0, 255, 2)
        excpected_values += range(0, 255, 2)
        excpected_values += range(0, 8, 2)

        for i in xrange(260):
            self.cpu.accu_a.set(i)
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x48, # LSLA/ASLA
            ])
            r = self.cpu.accu_a.get()
            excpected_value = excpected_values[i]
#             print "{0:08b} -> {1:08b}".format(i, r), self.cpu.cc.get_info, i, r, self.cpu.cc.get()

            # test LSL result
            self.assertEqual(r, excpected_value)

            # test negative
            if 128 <= r <= 255:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if 64 <= i <= 191:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if 128 <= i <= 255:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)


class Test6809_Ops(BaseTestCase):
    def test_TFR01(self):
        self.cpu.index_x.set(512) # source
        self.assertEqual(self.cpu.index_y.get(), 0) # destination

        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x1f, # TFR
            0x12, # from index register X (0x01) to Y (0x02)
        ])
        self.assertEqual(self.cpu.index_y.get(), 512)

    def test_TFR02(self):
        self.cpu.accu_b.set(0x55) # source
        self.assertEqual(self.cpu.cc.get(), 0) # destination

        self.cpu_test_run(start=0x1000, end=0x1002, mem=[
            0x1f, # TFR
            0x9a, # from accumulator B (0x9) to condition code register CC (0xa)
        ])
        self.assertEqual(self.cpu.cc.get(), 0x55) # destination

    def test_TFR03(self):
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x10, 0x8e, 0x12, 0x34, # LDY Y=$1234
            0x1f, 0x20, # TFR  Y,D
        ])
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234) # destination

    def test_CMPU_immediate(self):
        u = 0x80
        self.cpu.user_stack_pointer.set(u)
        for m in xrange(0x7e, 0x83):
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x11, 0x83, # CMPU (immediate word)
                0x00, m # the word that CMP reads
            ])
            r = u - m
            """
            80 - 7e = 02 -> ........
            80 - 7f = 01 -> ........
            80 - 80 = 00 -> .....Z..
            80 - 81 = -1 -> ....N..C
            80 - 82 = -2 -> ....N..C
            """
#             print "%02x - %02x = %02x -> %s" % (
#                 u, m, r, self.cpu.cc.get_info
#             )

            # test negative: 0x01 <= a <= 0x80
            if r < 0:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            self.assertEqual(self.cpu.cc.V, 0)

            # test carry is set if r=1-255 (hex: r=$01 - $ff)
            if r < 0:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_CMPA_immediate_byte(self):
        a = 0x80
        self.cpu.accu_a.set(a)
        for m in xrange(0x7e, 0x83):
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x81, m # CMPA (immediate byte)
            ])
            r = a - m
            """
            80 - 7e = 02 -> ......V.
            80 - 7f = 01 -> ......V.
            80 - 80 = 00 -> .....Z..
            80 - 81 = -1 -> ....N..C
            80 - 82 = -2 -> ....N..C
            """
#             print "%02x - %02x = %02x -> %s" % (
#                 a, m, r, self.cpu.cc.get_info
#             )

            # test negative: 0x01 <= a <= 0x80
            if r < 0:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if r > 0:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry is set if r=1-255 (hex: r=$01 - $ff)
            if r < 0:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_CMPX_immediate_word(self):
        x = 0x80
        self.cpu.index_x.set(x)
        for m in xrange(0x7e, 0x83):
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x8c, 0x00, m # CMPX (immediate word)
            ])
            r = x - m
            """
            80 - 7e = 02 -> ........
            80 - 7f = 01 -> ........
            80 - 80 = 00 -> .....Z..
            80 - 81 = -1 -> ....N..C
            80 - 82 = -2 -> ....N..C
            """
#             print "%02x - %02x = %02x -> %s" % (
#                 x, m, r, self.cpu.cc.get_info
#             )

            # test negative: 0x01 <= a <= 0x80
            if r < 0:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            self.assertEqual(self.cpu.cc.V, 0)

            # test carry is set if r=1-255 (hex: r=$01 - $ff)
            if r < 0:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_LSLA(self):
        for a1 in xrange(256):
            self.cpu.accu_a.set(a1)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x48, #       LSLA
            ])
            a2 = self.cpu.accu_a.get()
#             print "%02x %s > LSLA > %02x %s -> %s" % (
#                 a1, '{0:08b}'.format(a1),
#                 a2, '{0:08b}'.format(a2),
#                 self.cpu.cc.get_info
#             )

            r = a1 << 1 # shift left
            r = r & 0xff # wrap around
            self.assertEqualHex(a2, r)

            # test negative
            if r >= 0x80:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if 0x40 <= a1 <= 0xbf:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if a1 < 0x80: # if Bit 7 set
                self.assertEqual(self.cpu.cc.C, 0)
            else:
                self.assertEqual(self.cpu.cc.C, 1)

    def assertROL(self, src, dst, source_carry):
            src_bit_str = '{0:08b}'.format(src)
            dst_bit_str = '{0:08b}'.format(dst)
#             print "%02x %s > ROLA > %02x %s -> %s" % (
#                 src, src_bit_str,
#                 dst, dst_bit_str,
#                 self.cpu.cc.get_info
#             )

            # Carry was cleared and moved into bit 0
            excpeted_bits = "%s%s" % (src_bit_str[1:], source_carry)
            self.assertEqual(dst_bit_str, excpeted_bits)

            # test negative
            if dst >= 0x80:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if dst == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            source_bit6 = 0 if src & 2 ** 6 == 0 else 1
            source_bit7 = 0 if src & 2 ** 7 == 0 else 1
            if source_bit6 == source_bit7: # V = bit 6 XOR bit 7
                self.assertEqual(self.cpu.cc.V, 0)
            else:
                self.assertEqual(self.cpu.cc.V, 1)

            # test carry
            if 0x80 <= src <= 0xff: # if bit 7 was set
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_ROL_with_clear_carry(self):
        for a in xrange(256):
            self.cpu.cc.set(0x00) # clear all CC flags
            a = self.cpu.accu_a.set(a)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x49, # ROLA
            ])
            r = self.cpu.accu_a.get()
            self.assertROL(a, r, source_carry=0)

            # test half carry is uneffected!
            self.assertEqual(self.cpu.cc.H, 0)

    def test_ROL_with_set_carry(self):
        for a in xrange(256):
            self.cpu.cc.set(0xff) # set all CC flags
            a = self.cpu.accu_a.set(a)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x49, #       ROLA
            ])
            r = self.cpu.accu_a.get()
            self.assertROL(a, r, source_carry=1)

            # test half carry is uneffected!
            self.assertEqual(self.cpu.cc.H, 1)

    def test_ABX_01(self):
        self.cpu.cc.set(0xff)
        self.cpu.accu_b.set(0x0f)
        self.cpu.index_x.set(0x00f0)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x3A, # ABX
        ])
        self.assertEqualHex(self.cpu.index_x.get(), 0x00ff)
        self.assertEqualHex(self.cpu.cc.get(), 0xff)

        self.cpu.cc.set(0x00)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x3A, # ABX
        ])
        self.assertEqualHex(self.cpu.index_x.get(), 0x010E)
        self.assertEqualHex(self.cpu.cc.get(), 0x00)


class Test6809_TestInstructions(BaseTestCase):
    def assertTST(self, i):
        if 128 <= i <= 255: # test negative
            self.assertEqual(self.cpu.cc.N, 1)
        else:
            self.assertEqual(self.cpu.cc.N, 0)

        if i == 0: # test zero
            self.assertEqual(self.cpu.cc.Z, 1)
        else:
            self.assertEqual(self.cpu.cc.Z, 0)

        # test overflow
        self.assertEqual(self.cpu.cc.V, 0)

        # test not affected flags:
        self.assertEqual(self.cpu.cc.E, 1)
        self.assertEqual(self.cpu.cc.F, 1)
        self.assertEqual(self.cpu.cc.H, 1)
        self.assertEqual(self.cpu.cc.I, 1)
        self.assertEqual(self.cpu.cc.C, 1)

    def test_TST_direct(self):
        for i in xrange(255):
            self.cpu.accu_a.set(i)
            self.cpu.cc.set(0xff) # Set all CC flags

            self.cpu.memory.write_byte(address=0x00, value=i)

            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x0D, 0x00 # TST $00
            ])
            self.assertTST(i)

    def test_TST_extended(self):
        for i in xrange(255):
            self.cpu.accu_a.set(i)
            self.cpu.cc.set(0xff) # Set all CC flags

            self.cpu.memory.write_byte(address=0x1234, value=i)

            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x7D, 0x12, 0x34 # TST $1234
            ])
            self.assertTST(i)

    def test_TSTA(self):
        for i in xrange(255):
            self.cpu.accu_a.set(i)
            self.cpu.cc.set(0xff) # Set all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x4D # TSTA
            ])
            self.assertTST(i)

    def test_TSTB(self):
        for i in xrange(255):
            self.cpu.accu_b.set(i)
            self.cpu.cc.set(0xff) # Set all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x5D # TSTB
            ])
            self.assertTST(i)






class Test6809_Ops2(BaseTestCase):
    def test_TFR_CC_B(self):
        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x7E, 0x40, 0x04, # JMP $4004
            0xfe, # $12 value for A
            0xB6, 0x40, 0x03, # LDA $4003
            0x8B, 0x01, # ADDA 1
            0x1F, 0xA9, # TFR CC,B
            0xF7, 0x50, 0x01, # STB $5001
            0xB7, 0x50, 0x00, # STA $5000
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0xff)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x8) # N=1
        self.assertEqualHex(self.cpu.memory.read_byte(0x5000), 0xff) # A
        self.assertEqualHex(self.cpu.memory.read_byte(0x5001), 0x8) # B == CC

    def test_LD16_ST16_CLR(self):
        self.cpu.accu_d.set(0)
        self.cpu_test_run(start=0x4000, end=None, mem=[0xCC, 0x12, 0x34]) # LDD $1234 (Immediate)
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)

        self.cpu_test_run(start=0x4000, end=None, mem=[0xFD, 0x50, 0x00]) # STD $5000 (Extended)
        self.assertEqualHex(self.cpu.memory.read_word(0x5000), 0x1234)

        self.cpu_test_run(start=0x4000, end=None, mem=[0x4F]) # CLRA
        self.assertEqualHex(self.cpu.accu_d.get(), 0x34)

        self.cpu_test_run(start=0x4000, end=None, mem=[0x5F]) # CLRB
        self.assertEqualHex(self.cpu.accu_d.get(), 0x0)

        self.cpu_test_run(start=0x4000, end=None, mem=[0xFC, 0x50, 0x00]) # LDD $5000 (Extended)
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)


class Test6809_Stack(BaseDragon32TestCase):
    def test_PushPullSytemStack_01(self):
        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR
        )

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x1a, # LDA A=$1a
            0x34, 0x02, # PSHS A
        ])

        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR - 1 # Byte added
        )

        self.assertEqualHex(self.cpu.accu_a.get(), 0x1a)

        self.cpu.accu_a.set(0xee)

        self.assertEqualHex(self.cpu.accu_b.get(), 0x00)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x35, 0x04, # PULS B  ;  B gets the value from A = 1a
        ])

        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR # Byte removed
        )

        self.assertEqualHex(self.cpu.accu_a.get(), 0xee)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x1a)

    def test_PushPullSystemStack_02(self):
        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR
        )

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0xab, # LDA A=$ab
            0x34, 0x02, # PSHS A
            0x86, 0x02, # LDA A=$02
            0x34, 0x02, # PSHS A
            0x86, 0xef, # LDA A=$ef
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0xef)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x35, 0x04, # PULS B
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0xef)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x02)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x35, 0x02, # PULS A
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0xab)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x02)

        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR
        )

    def test_PushPullSystemStack_03(self):
        self.assertEqualHex(
            self.cpu.system_stack_pointer,
            self.INITIAL_SYSTEM_STACK_ADDR
        )

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0xcc, 0x12, 0x34, # LDD D=$1234
            0x34, 0x06, # PSHS B,A
            0xcc, 0xab, 0xcd, # LDD D=$abcd
            0x34, 0x06, # PSHS B,A
            0xcc, 0x54, 0x32, # LDD D=$5432
        ])
        self.assertEqualHex(self.cpu.accu_d.get(), 0x5432)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x35, 0x06, # PULS B,A
        ])
        self.assertEqualHex(self.cpu.accu_d.get(), 0xabcd)
        self.assertEqualHex(self.cpu.accu_a.get(), 0xab)
        self.assertEqualHex(self.cpu.accu_b.get(), 0xcd)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x35, 0x06, # PULS B,A
        ])
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)


class Test6809_Code(BaseTestCase):
    """
    Test with some small test codes
    """
    def test_code01(self):
        self.cpu.memory.load(
            0x2220, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        )

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0x86, 0x22, #       LDA $22    ; Immediate
            0x8E, 0x22, 0x22, # LDX $2222  ; Immediate
            0x1F, 0x89, #       TFR A,B    ; Inherent (Register)
            0x5A, #             DECB       ; Inherent (Implied)
            0xED, 0x84, #       STD ,X     ; Indexed (non indirect)
            0x4A, #             DECA       ; Inherent (Implied)
            0xA7, 0x94, #       STA [,X]   ; Indexed (indirect)
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0x21)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x21)
        self.assertEqualHex(self.cpu.accu_d.get(), 0x2121)
        self.assertEqualHex(self.cpu.index_x.get(), 0x2222)
        self.assertEqualHex(self.cpu.index_y.get(), 0x0000)
        self.assertEqualHex(self.cpu.direct_page.get(), 0x00)

        self.assertMemory(
            start=0x2220,
            mem=[0xFF, 0x21, 0x22, 0x21, 0xFF, 0xFF]
        )

    def test_code02(self):
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x10, 0x8e, 0x30, 0x00, #       2000|       LDY $3000
            0xcc, 0x10, 0x00, #             2004|       LDD $1000
            0xed, 0xa4, #                   2007|       STD ,Y
            0x86, 0x55, #                   2009|       LDA $55
            0xA7, 0xb4, #                   200B|       STA ,[Y]
        ])
        self.assertEqualHex(self.cpu.cc.get(), 0x00)
        self.assertMemory(
            start=0x1000,
            mem=[0x55]
        )

    def test_code_LEAU_01(self):
        self.cpu.user_stack_pointer.set(0xff)
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0x33, 0x41, #                  0000|            LEAU   1,U
        ])
        self.assertEqualHex(self.cpu.user_stack_pointer.get(), 0x100)

    def test_code_LEAU_02(self):
        self.cpu.user_stack_pointer.set(0xff)
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0xCE, 0x00, 0x00, #                       LDU   #$0000
            0x33, 0xC9, 0x1A, 0xBC, #                 LEAU  $1abc,U
        ])
        self.assertEqualHex(self.cpu.user_stack_pointer.get(), 0x1abc)

    def test_code_LDU_01(self):
        self.cpu.user_stack_pointer.set(0xff)
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0xCE, 0x12, 0x34, #                       LDU   #$0000
        ])
        self.assertEqualHex(self.cpu.user_stack_pointer.get(), 0x1234)

    def test_code_ORA_01(self):
        self.cpu.cc.set(0xff)
        self.cpu.accu_a.set(0x12)
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0x8A, 0x21, #                             ORA   $21
        ])
        self.assertEqualHex(self.cpu.accu_a.get(), 0x33)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0)

    def test_code_ORCC_01(self):
        self.cpu.cc.set(0x12)
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0x1A, 0x21, #                             ORCC   $21
        ])
        self.assertEqualHex(self.cpu.cc.get(), 0x33)



class TestSimple6809ROM(BaseTestCase):
    """
    use routines from Simple 6809 ROM code
    """
    def _is_carriage_return(self, a, pc):
        self.cpu.accu_a.set(a)
        self.cpu_test_run2(start=0x4000, count=3, mem=[
            # origin start address in ROM: $db16
            0x34, 0x02, # PSHS A
            0x81, 0x0d, # CMPA #000d(CR)       ; IS IT CARRIAGE RETURN?
            0x27, 0x0b, # BEQ  NEWLINE         ; YES
        ])
        self.assertEqualHex(self.cpu.program_counter, pc)

    def test_is_not_carriage_return(self):
        self._is_carriage_return(a=0x00, pc=0x4006)

    def test_is_carriage_return(self):
        self._is_carriage_return(a=0x0d, pc=0x4011)


if __name__ == '__main__':
    log.setLevel(
#         1
#        10 # DEBUG
#         20 # INFO
#         30 # WARNING
#         40 # ERROR
        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    # XXX: Disable hacked XRoar trace
    import cpu6809; cpu6809.trace_file = None

    unittest.main(
        argv=(
            sys.argv[0],
#             "Test6809_Register"
#             "Test6809_ZeroFlag",
#             "Test6809_CarryFlag",
#             "Test6809_CC.test_INC_memory",
#             "Test6809_CC.test_INCB",
#             "Test6809_Ops",
#             "Test6809_Ops.test_CMPA_immediate_byte",
#              "Test6809_Ops.test_CMPX_immediate_word",
#             "Test6809_Ops.test_LSLA",
#             "Test6809_Ops.test_ROL_with_clear_carry",
#             "Test6809_Ops.test_ROL_with_set_carry",
#              "Test6809_TestInstructions",
#             "Test6809_AddressModes",
#             "Test6809_Ops2",
#             "Test6809_Ops2.test_TFR_CC_B",
#              "Test6809_Stack",
#              "Test6809_Stack.test_PushPullSystemStack_03",
#             "TestSimple6809ROM",
#             "Test6809_Code",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
