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


class Test6809_Arithmetic(BaseTestCase):
    def test_ADDA_extended01(self):
        self.cpu_test_run(start=0x1000, end=0x1003, mem=[
            0xbb, # ADDA extended
            0x12, 0x34 # word to add on accu A
        ])
        self.assertEqual(self.cpu.cc.Z, 1)
        self.assertEqual(self.cpu.cc.get(), 0x04)
        self.assertEqual(self.cpu.accu_a.get(), 0x00)

    def test_ADDA_immediate(self):
        # expected values are: 1 up to 255 then wrap around to 0 and up to 4
        excpected_values = range(1, 256)
        excpected_values += range(0, 5)

        self.cpu.accu_a.set(0x00) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x8B, 0x01, # ADDA #$1 Immediate
            ])
            a = self.cpu.accu_a.get()
            excpected_value = excpected_values[i]
#             print i, a, excpected_value, self.cpu.cc.get_info

            # test ADDA result
            self.assertEqual(a, excpected_value)

            # test half carry
            if a % 16 == 0:
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

    def test_ADDA1(self):
        for i in xrange(260):
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x8B, 0x01, # ADDA   #$01
            ])
            r = self.cpu.accu_a.get()
#             print "$%02x > ADD 1 > $%02x | CC:%s" % (
#                 i, r, self.cpu.cc.get_info
#             )

            # test INC value from RAM
            self.assertEqualHex(i + 1 & 0xff, r) # expected values are: 1 up to 255 then wrap around to 0 and up to 4

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
            if r == 0x80:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

    def test_ADDD1(self):
        areas = range(0, 3) + ["..."] + range(0x7ffd, 0x8002) + ["..."] + range(0xfffd, 0x10002)
        for i in areas:
            if i == "...":
#                 print "..."
                continue
            self.cpu.accu_d.set(i)
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0xc3, 0x00, 0x01, # ADDD   #$01
            ])
            r = self.cpu.accu_d.get()
#             print "%5s $%04x > ADDD 1 > $%04x | CC:%s" % (
#                 i, i, r, self.cpu.cc.get_info
#             )

            # test INC value from RAM
            self.assertEqualHex(i + 1 & 0xffff, r)

            # test negative
            if 0x8000 <= r <= 0xffff:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow
            if r == 0x8000:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

    def test_DECA(self):
        for a in xrange(256):
            self.cpu.cc.set(0x00)
            self.cpu.accu_a.set(a)
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x4a, # DECA
            ])
            r = self.cpu.accu_a.get()
#             print "%03s - a=%02x r=%02x -> %s" % (
#                 a, a, r, self.cpu.cc.get_info
#             )
#             continue

            excpected_value = a - 1 & 0xff

            # test result
            self.assertEqual(r, excpected_value)

            # test half carry and carry is uneffected!
            self.assertEqual(self.cpu.cc.H, 0)
            self.assertEqual(self.cpu.cc.C, 0)

            # test negative:
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
            if a == 0x80:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)


    def test_NEGA(self):
        """
        Example assembler code to test NEGA

        CLRB        ; B is always 0
        TFR B,U     ; clear U
loop:
        TFR U,A     ; for next NEGA
        TFR B,CC    ; clear CC
        NEGA
        LEAU 1,U    ; inc U
        JMP loop


0000   5F                     CLRB   ; B is always 0
0001   1F 93                  TFR   B,U   ; clear U
0003                LOOP:
0003   1F 38                  TFR   U,A   ; for next NEGA
0005   1F 9A                  TFR   B,CC   ; clear CC
0007   40                     NEGA
0008   33 41                  LEAU   1,U   ; inc U
000A   0E 03                  JMP   loop

        """
        excpected_values = [0] + range(255, 0, -1)

        for a in xrange(256):
            self.cpu.cc.set(0x00)

            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x86, a, # LDA   #$i
                0x40, # NEGA (inherent)
            ])
            r = self.cpu.accu_a.get()
#            print "%03s - a=%02x r=%02x -> %s" % (
#                a, a, r, self.cpu.cc.get_info
#            )

            excpected_value = excpected_values[a]

            """
            xroar NEG CC - input for NEG values:
            H = uneffected
            N = dez: 1-128      | hex: $01 - $80
            Z = dez: 0          | hex: $00
            V = dez: 128        | hex: $80
            C = dez: 1-255      | hex: $01 - $ff
            """

            # test NEG result
            self.assertEqual(r, excpected_value)

            # test half carry is uneffected!
            self.assertEqual(self.cpu.cc.H, 0)

            # test negative: 0x01 <= a <= 0x80
            if 1 <= a <= 128:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero | a==0 and r==0
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow | a==128 and r==128
            if r == 128:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry is set if r=1-255 (hex: r=$01 - $ff)
            if r >= 1:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_NEG_memory(self):
        excpected_values = [0] + range(255, 0, -1)
        address = 0x10

        for a in xrange(256):
            self.cpu.cc.set(0x00)

            self.cpu.memory.write_byte(address, a)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0x00, address, # NEG address
            ])
            r = self.cpu.memory.read_byte(address)
#             print "%03s - a=%02x r=%02x -> %s" % (
#                 a, a, r, self.cpu.cc.get_info
#             )

            excpected_value = excpected_values[a]

            # test NEG result
            self.assertEqual(r, excpected_value)

            # test half carry is uneffected!
            self.assertEqual(self.cpu.cc.H, 0)

            # test negative: 0x01 <= a <= 0x80
            if 1 <= a <= 128:
                self.assertEqual(self.cpu.cc.N, 1)
            else:
                self.assertEqual(self.cpu.cc.N, 0)

            # test zero | a==0 and r==0
            if r == 0:
                self.assertEqual(self.cpu.cc.Z, 1)
            else:
                self.assertEqual(self.cpu.cc.Z, 0)

            # test overflow | a==128 and r==128
            if r == 128:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

            # test carry is set if r=1-255 (hex: r=$01 - $ff)
            if r >= 1:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)

    def test_INC_memory(self):
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
#             print "%5s $%02x > INC > $%02x | CC:%s" % (
#                 i, i, r, self.cpu.cc.get_info
#             )

            # test INC value from RAM
            self.assertEqualHex(r, excpected_value)
            self.assertEqualHex(i + 1 & 0xff, r)

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
            if r in (0x80, 0x00):
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

    def test_INCB(self):
        # expected values are: 1 up to 255 then wrap around to 0 and up to 4
        excpected_values = range(1, 256)
        excpected_values += range(0, 5)

        for i in xrange(260):
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x5c, # INCB
            ])
            r = self.cpu.accu_b.get()
            excpected_value = excpected_values[i]
#             print i, r, excpected_value, self.cpu.cc.get_info

            # test INC value from RAM
            self.assertEqual(r, excpected_value)
            self.assertEqualHex(i + 1 & 0xff, r)

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
            if r in (0x80, 0x00):
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

    def test_INC_not_affected_flags1(self):
        self.cpu.memory.write_byte(0x0100, 0x00) # start value

        self.cpu.cc.set(0x00) # Clear all CC flags
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0x7c, 0x01, 0x00, # INC $0100
        ])
        r = self.cpu.memory.read_byte(0x0100)
        self.assertEqual(r, 0x01)

        # half carry bit is not affected in INC
        self.assertEqual(self.cpu.cc.H, 0)

        # carry bit is not affected in INC
        self.assertEqual(self.cpu.cc.C, 0)

    def test_INC_not_affected_flags2(self):
        self.cpu.memory.write_byte(0x0100, 0x00) # start value

        self.cpu.cc.set(0xff) # Set all CC flags
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0x7c, 0x01, 0x00, # INC $0100
        ])
        r = self.cpu.memory.read_byte(0x0100)
        self.assertEqual(r, 0x01)

        # half carry bit is not affected in INC
        self.assertEqual(self.cpu.cc.H, 1)

        # carry bit is not affected in INC
        self.assertEqual(self.cpu.cc.C, 1)

    def test_SUBA_immediate(self):
        # expected values are: 254 down to 0 than wrap around to 255 and down to 252
        excpected_values = range(254, -1, -1)
        excpected_values += range(255, 250, -1)

        self.cpu.accu_a.set(0xff) # start value
        for i in xrange(260):
            self.cpu.cc.set(0x00) # Clear all CC flags
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x80, 0x01, # SUBA #$01
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
#             "Test6809_Arithmetic",
#             "Test6809_Arithmetic.test_ADDA1",
#             "Test6809_Arithmetic.test_ADDD1",
#             "Test6809_Arithmetic.test_DECA",
#             "Test6809_Arithmetic.test_NEG_memory",
#            "Test6809_Arithmetic.test_NEGA",
            "Test6809_Arithmetic.test_INC_memory",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
