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


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        cfg = Dragon32Cfg()
        cfg.mem_info = DragonMemInfo(log.debug)
        self.cpu = CPU(cfg)

    def cpu_test_run(self, start, end, mem):
        for cell in mem:
            self.assertLess(-1, cell, "$%x < 0" % cell)
            self.assertGreater(0x100, cell, "$%x > 0xff" % cell)
        self.cpu.memory.load(start, mem)
        if end is None:
            end = start + len(mem)
        self.cpu.test_run(start, end)

    def assertEqualHex(self, first, second):
        msg = "$%x != $%x" % (first, second)
        self.assertEqual(first, second, msg)


class Test6809_AddressModes(BaseTestCase):
    def test_base_page_direct01(self):
        self.cpu.memory.load(0x1000, [0x12, 0x34, 0xf])
        self.cpu.program_counter = 0x1000
        self.cpu.direct_page = 0xab

        value = self.cpu.direct()
        self.assertEqual(hex(value), hex(0xab12))

        value = self.cpu.direct()
        self.assertEqual(hex(value), hex(0xab34))

        self.cpu.direct_page = 0x0
        value = self.cpu.direct()
        self.assertEqual(hex(value), hex(0xf))


class Test6809_Register(BaseTestCase):
    def test_registerA(self):
        for i in xrange(255):
            self.cpu.accu_a.set(i)
            t = self.cpu.accu_a.get()
            self.assertEqual(i, t)

    def test_registerA_overflow(self):
        self.cpu.accu_a.set(256)
        t = self.cpu.accu_a.get()
        self.assertEqual(0, t)

        self.cpu.accu_a.set(257)
        t = self.cpu.accu_a.get()
        self.assertEqual(1, t)


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

    def test_Overflow01(self):
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x86, 0x80, # LDA #-128
            0x80, 0x01, # SUBA #1
        ])
        self.assertEqual(self.cpu.accu_a.get(), 0x7f) # $7f == signed: 127 == unsigned: 127
        self.assertEqual(self.cpu.cc.N, 0) # N - 0x08 - bit 3 - Negative result (twos complement)
        self.assertEqual(self.cpu.cc.Z, 0) # Z - 0x04 - bit 2 - Zero result
        self.assertEqual(self.cpu.cc.V, 1) # V - 0x02 - bit 1 - Overflow
        self.assertEqual(self.cpu.cc.C, 0) # C - 0x01 - bit 0 - Carry (or borrow)

    def test_Overflow02(self):
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x86, 0x7F, # LDA #+127
            0x8B, 0x01, # ADDA #1
        ])
        self.assertEqual(self.cpu.accu_a.get(), 0x80) # $80 == signed: -128 == unsigned: 128
        self.assertEqual(self.cpu.cc.N, 1) # N - 0x08 - bit 3 - Negative result (twos complement)
        self.assertEqual(self.cpu.cc.Z, 0) # Z - 0x04 - bit 2 - Zero result
        self.assertEqual(self.cpu.cc.V, 1) # V - 0x02 - bit 1 - Overflow
        self.assertEqual(self.cpu.cc.C, 0) # C - 0x01 - bit 0 - Carry (or borrow)


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
        self.cpu.index_y = 0x12 # source
        self.cpu.program_counter = 0 # destination

        self.cpu_test_run(start=0x1000, end=0x12, mem=[
            0x9E, 0x12, # LDX $12 (direct)
            0x1f, # TFR
            0x15, # from X (0x1) to PC (0x5)
        ])
        self.assertEqual(self.cpu.program_counter, 0x12) # destination

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



#     @opcode(0xbb)
#     def ADDA_extended(self):
#         """
#         A = A + M
#         """
#         self.cycles += 5
#         value = self.read_pc_word()
#         log.debug("%s - 0xbb ADDA extended: Add %s to accu A: %s" % (
#             hex(self.program_counter), hex(value), hex(self.accu_a)
#         ))
#         self.accu_a += value

class Test6809_Ops2(BaseTestCase):
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

    def test_print(self):
#         self.cpu_test_run(start=0x1000, end=None, mem=[
#             0x86, 0x12, # LDA A=$12
#             0xC6, 0x34, # LDB B=$34
#
#             0xB7, 0x06, 0x00, # STA 0x0600 (extended) ($0600-1dff = Available graphics pages w/o DOS)
#             0xF7, 0x06, 0x01, # STB 0x0601 (extended)
#
#             0xFC, 0x06, 0x00, # LDD 0x0600 (extended)
#         ])
#         self.assertEqualHex(self.cpu.memory.read_word(0x0600), 0x1234)
#         self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)
#         self.assertEqualHex(self.cpu.accu_a.get(), 0x12)
#         self.assertEqualHex(self.cpu.accu_b.get(), 0x34)

        self.cpu_test_run(start=0x4000, end=None, mem=[
            0xCC, 0x12, 0x34, # LDD $1234        ; $5858 == 22616
#             0xBD, 0x95, 0x7A, # JSR 38266        ; OUTPUT D REGISTER
            0x7E, 0x95, 0x7A, # JMP 38266        ; OUTPUT D REGISTER
        ])
        self.assertEqualHex(self.cpu.accu_d.get(), 0x1234)
        self.assertEqualHex(self.cpu.accu_a.get(), 0x12)
        self.assertEqualHex(self.cpu.accu_b.get(), 0x34)



if __name__ == '__main__':
    log = logging.getLogger("DragonPy")
    log.setLevel(
#         logging.ERROR
#         logging.INFO
#         logging.WARNING
        logging.DEBUG
    )
    log.addHandler(logging.StreamHandler())



    unittest.main(
        argv=(
            sys.argv[0],
#             "Test6809_Register"
#             "Test6809_CC",
#             "Test6809_Ops",
#             "Test6809_Ops.test_TFR02",
#             "Test6809_Ops.test_CMPX_extended",
#             "Test6809_Ops.test_NEGA_02",
#             "Test6809_AddressModes",
            "Test6809_Ops2",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
