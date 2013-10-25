#!/usr/bin/env python

"""
    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import unittest

from configs import Dragon32Cfg
from cpu6809 import CPU
from Dragon32_mem_info import DragonMemInfo
from test_base import TextTestRunner2


class UnittestCmdArgs(object):
    bus_socket_host = None
    bus_socket_port = None
    ram = None
    rom = None
    verbosity = None
    max = None
    area_debug_active = None
    area_debug_cycles = None


class BaseTestCase(unittest.TestCase):
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

    def cpu_test_run(self, start, end, mem):
        for cell in mem:
            self.assertLess(-1, cell, "$%x < 0" % cell)
            self.assertGreater(0x100, cell, "$%x > 0xff" % cell)
        self.cpu.memory.load(start, mem)
        if end is None:
            end = start + len(mem)
        self.cpu.test_run(start, end)

    def cpu_test_run2(self, start, count, mem):
        for cell in mem:
            self.assertLess(-1, cell, "$%x < 0" % cell)
            self.assertGreater(0x100, cell, "$%x > 0xff" % cell)
        self.cpu.memory.load(start, mem)
        self.cpu.test_run2(start, count)

    def assertEqualHex(self, first, second):
        msg = "$%x != $%x" % (first, second)
        self.assertEqual(first, second, msg)


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

    def test_ADDA(self):
        # expected values are: 1 up to 255 then wrap around to 0 and up to 4
        excpected_values = range(1, 256)
        excpected_values += range(0, 5)

        half_carry = (# range(0, 255, 16)
            0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240
        )

        self.cpu.accu_a.set(0x00) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x8B, 0x01, # ADDA #1
            ])
            a = self.cpu.accu_a.get()
            excpected_value = excpected_values[i]
#             print i, a, excpected_value, self.cpu.cc.get_info

            # test ADDA result
            self.assertEqual(a, excpected_value)

            # test half carry
            if a in half_carry:
                self.assertEqual(self.cpu.cc.H, 1)
            else:
                self.assertEqual(self.cpu.cc.H, 0)

            # test negative
            if 128 <= a <= 255:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if a == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if a == 128:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if a == 0:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_INC(self):
        # expected values are: 1 up to 255 then wrap around to 0 and up to 4
        excpected_values = range(1, 256)
        excpected_values += range(0, 5)

        self.cpu.memory.write_byte(0x4500, 0x0) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x7c, 0x45, 0x00, # INC $4500
            ])
            r = self.cpu.memory.read_byte(0x4500)
            excpected_value = excpected_values[i]
#             print i, r, excpected_value, self.cpu.cc.get_info

            # test INC value from RAM
            self.assertEqual(r, excpected_value)

            # half carry bit is not affected in INC
            self.assertEqual(self.cpu.cc.H, 0)

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
            if r == 128:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # carry bit is not affected in INC
            self.assertEqual(self.cpu.cc.C, 0)

    def test_SUBA(self):
        # expected values are: 254 down to 0 than wrap around to 255 and down to 252
        excpected_values = range(254, -1, -1)
        excpected_values += range(255, 250, -1)

        self.cpu.accu_a.set(0xff) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x80, 0x01, # SUBA #1
            ])
            a = self.cpu.accu_a.get()
            excpected_value = excpected_values[i]
#             print i, a, excpected_value, self.cpu.cc.get_info

            # test SUBA result
            self.assertEqual(a, excpected_value)

            # test half carry
            # XXX: half carry is "undefined" in SUBA!
            self.assertEqual(self.cpu.cc.H, 0)

            # test negative
            if 128 <= a <= 255:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if a == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if a == 127: # V ist set if SUB $80 to $7f
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if a == 0xff: # C is set if SUB $00 to $ff
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_DEC(self):
        # expected values are: 254 down to 0 than wrap around to 255 and down to 252
        excpected_values = range(254, -1, -1)
        excpected_values += range(255, 250, -1)

        self.cpu.memory.write_byte(0x4500, 0xff) # start value
        self.cpu.accu_a.set(0xff) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x7A, 0x45, 0x00, # DEC $4500
            ])
            r = self.cpu.memory.read_byte(0x4500)
            excpected_value = excpected_values[i]
#             print i, r, excpected_value, self.cpu.cc.get_info

            # test DEC result
            self.assertEqual(r, excpected_value)

            # half carry bit is not affected in DEC
            self.assertEqual(self.cpu.cc.H, 0)

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
            if r == 127: # V is set if SUB $80 to $7f
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # carry bit is not affected in DEC
            self.assertEqual(self.cpu.cc.C, 0)

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

    def test_ADDA_extended01(self):
        self.cpu_test_run(start=0x1000, end=0x1003, mem=[
            0xbb, # ADDA extended
            0x12, 0x34 # word to add on accu A
        ])
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.get(), 0x04)
        self.assertEqual(self.cpu.accu_a.get(), 0x00)

    def test_CMPX_extended(self):
        """
        Compare M:M+1 from X
        Addressing Mode: extended
        """
        self.cpu.accu_a.set(0x0) # source

        self.cpu_test_run(start=0x1000, end=0x1003, mem=[
            0xbc, # CMPX extended
            0x10, 0x20 # word to add on accu A
        ])
        self.assertEqual(self.cpu.cc.get(), 0x04)
        self.assertEqual(self.cpu.cc.C, 1)

    def test_NEGA_01(self):
        self.cpu.accu_a.set(0x0) # source

        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x40, # NEGA (inherent)
        ])
        self.assertEqual(self.cpu.accu_a.get(), 0x0)
        self.assertEqual(self.cpu.cc.N, 0)
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.V, 0)
        self.assertEqual(self.cpu.cc.C, 0)

    def test_NEGA_02(self):
        self.cpu.accu_a.set(0x80) # source: 0x80 == 128 signed: -128 $-80

        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x40, # NEGA (inherent)
        ])
        self.assertEqual(self.cpu.accu_a.get(), 0x80)
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 1) # FIXME
        self.assertEqual(self.cpu.cc.C, 0)

    def test_NEGA_03(self):
        self.cpu.accu_a.set(0x1) # source: signed: 1 == unsigned: 1

        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x40, # NEGA (inherent)
        ])
        self.assertEqual(self.cpu.accu_a.get(), 0xff) # signed: -1 -> unsigned: 255 == 0xff
        self.assertEqual(self.cpu.cc.N, 1)
        self.assertEqual(self.cpu.cc.Z, 0)
        self.assertEqual(self.cpu.cc.V, 0) # FIXME
        self.assertEqual(self.cpu.cc.C, 0)


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

class Test6809_Stack(BaseTestCase):
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
    log = logging.getLogger("DragonPy")
    log.setLevel(
#         10 # DEBUG
#         20 # INFO
        30 # WARNING
#         40 # ERROR
#         50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    # XXX: Disable hacked XRoar trace
    import cpu6809; cpu6809.trace_file = None

    unittest.main(
        argv=(
            sys.argv[0],
#             "Test6809_Register"
#             "Test6809_CC",
#             "Test6809_CC.test_ADDA",
#             "Test6809_CC.test_INC",
#             "Test6809_CC.test_SUBA",
#             "Test6809_CC.test_DEC",
#             "Test6809_Ops",
#             "Test6809_Ops.test_TFR03",
#             "Test6809_Ops.test_CMPX_extended",
#             "Test6809_Ops.test_NEGA_02",
#             "Test6809_AddressModes",
#             "Test6809_Ops2",
#             "Test6809_Ops2.test_TFR_CC_B",
#              "Test6809_Stack",
#              "Test6809_Stack.test_PushPullSystemStack_03",
            "TestSimple6809ROM",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
