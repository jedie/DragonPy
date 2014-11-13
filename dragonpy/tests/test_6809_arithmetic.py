#!/usr/bin/env python
# encoding:utf-8

"""
    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from dragonlib.utils.unittest_utils import TextTestRunner2
from dragonlib.utils import six
xrange = six.moves.xrange

import logging
import sys
import unittest

from dragonpy.tests.test_base import BaseCPUTestCase


log = logging.getLogger("DragonPy")


class Test6809_Arithmetic(BaseCPUTestCase):
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
        excpected_values = list(range(1, 256))
        excpected_values += list(range(0, 5))

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
        areas = list(range(0, 3)) + ["..."] + list(range(0x7ffd, 0x8002)) + ["..."] + list(range(0xfffd, 0x10002))
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
        excpected_values = [0] + list(range(255, 0, -1))

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
        excpected_values = [0] + list(range(255, 0, -1))
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
        excpected_values = list(range(1, 256))
        excpected_values += list(range(0, 5))

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
            if r == 0x80:
                self.assertEqual(self.cpu.cc.V, 1)
            else:
                self.assertEqual(self.cpu.cc.V, 0)

    def test_INCB(self):
        # expected values are: 1 up to 255 then wrap around to 0 and up to 4
        excpected_values = list(range(1, 256))
        excpected_values += list(range(0, 5))

        for i in xrange(260):
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x5c, # INCB
            ])
            r = self.cpu.accu_b.get()
            excpected_value = excpected_values[i]
#             print "%5s $%02x > INC > $%02x | CC:%s" % (
#                 i, i, r, self.cpu.cc.get_info
#             )

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
            if r == 0x80:
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
        excpected_values = list(range(254, -1, -1))
        excpected_values += list(range(255, 250, -1))

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

    def test_SUBA_indexed(self):
        self.cpu.memory.load(0x1234, [0x12, 0xff])
        self.cpu.system_stack_pointer.set(0x1234)
        self.cpu.accu_a.set(0xff) # start value
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0xa0, 0xe0, # SUBA ,S+
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0xed) # $ff - $12 = $ed
        self.assertEqualHexWord(self.cpu.system_stack_pointer.get(), 0x1235)

        self.cpu_test_run(start=0x1000, end=None, mem=[
            0xa0, 0xe0, # SUBA ,S+
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0xed - 0xff & 0xff) # $ee
        self.assertEqualHexWord(self.cpu.system_stack_pointer.get(), 0x1236)

    def test_DEC_extended(self):
        # expected values are: 254 down to 0 than wrap around to 255 and down to 252
        excpected_values = list(range(254, -1, -1))
        excpected_values += list(range(255, 250, -1))

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

    def test_DECA(self):
        for a in xrange(256):
            self.cpu.cc.set(0x00)
            self.cpu.accu_a.set(a)
            self.cpu_test_run(start=0x1000, end=None, mem=[
                0x4a, # DECA
            ])
            r = self.cpu.accu_a.get()
#            print "%03s - %02x > DEC > %02x | CC:%s" % (
#                a, a, r, self.cpu.cc.get_info
#            )
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

    def test_SBCA_immediate_01(self):
        a = 0x80
        self.cpu.cc.set(0x00) # CC:........
        self.cpu.accu_a.set(a)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x82, 0x40, # SBC
        ])
        r = self.cpu.accu_a.get()
#        print "%02x > SBC > %02x | CC:%s" % (
#            a, r, self.cpu.cc.get_info
#        )
        self.assertEqualHex(r, 0x80 - 0x40 - 0x00)
        self.assertEqual(self.cpu.cc.get_info, "......V.")

    def test_SBCA_immediate_02(self):
        a = 0x40
        self.cpu.cc.set(0xff) # CC:EFHINZVC
        self.cpu.accu_a.set(a)
        self.cpu_test_run(start=0x1000, end=None, mem=[
            0x82, 0x20, # SBC
        ])
        r = self.cpu.accu_a.get()
#        print "%02x > SBC > %02x | CC:%s" % (
#            a, r, self.cpu.cc.get_info
#        )
        self.assertEqualHex(r, 0x40 - 0x20 - 0x01)
        # half-carry is undefined
        self.assertEqual(self.cpu.cc.get_info, "EFHI....")

    def test_ORCC(self):
        a_areas = list(range(0, 3)) + ["..."] + list(range(0x7e, 0x83)) + ["..."] + list(range(0xfd, 0x100))
        b_areas = list(range(0, 3)) + ["..."] + list(range(0x7e, 0x83)) + ["..."] + list(range(0xfd, 0x100))
        for a in a_areas:
            if a == "...":
#                print "..."
                continue
            for b in b_areas:
                if b == "...":
#                    print "..."
                    continue
                self.cpu.cc.set(a)
                self.cpu_test_run(start=0x1000, end=None, mem=[
                    0x1a, b # ORCC $a
                ])
                r = self.cpu.cc.get()
                expected_value = a | b
#                print "%02x OR %02x = %02x | CC:%s" % (
#                    a, b, r, self.cpu.cc.get_info
#                )
                self.assertEqualHex(r, expected_value)

    def test_ANDCC(self):
        a_areas = list(range(0, 3)) + ["..."] + list(range(0x7e, 0x83)) + ["..."] + list(range(0xfd, 0x100))
        b_areas = list(range(0, 3)) + ["..."] + list(range(0x7e, 0x83)) + ["..."] + list(range(0xfd, 0x100))
        for a in a_areas:
            if a == "...":
#                print "..."
                continue
            for b in b_areas:
                if b == "...":
#                    print "..."
                    continue
                self.cpu.cc.set(a)
                self.cpu_test_run(start=0x1000, end=None, mem=[
                    0x1c, b # ANDCC $a
                ])
                r = self.cpu.cc.get()
                expected_value = a & b
#                print "%02x AND %02x = %02x | CC:%s" % (
#                    a, b, r, self.cpu.cc.get_info
#                )
                self.assertEqualHex(r, expected_value)

    def test_ABX(self):
        self.cpu.cc.set(0xff)

        x_areas = list(range(0, 3)) + ["..."] + list(range(0x7ffd, 0x8002)) + ["..."] + list(range(0xfffd, 0x10000))
        b_areas = list(range(0, 3)) + ["..."] + list(range(0x7e, 0x83)) + ["..."] + list(range(0xfd, 0x100))

        for x in x_areas:
            if x == "...":
#                print "..."
                continue
            for b in b_areas:
                if b == "...":
#                    print "..."
                    continue
                self.cpu.index_x.set(x)
                self.cpu.accu_b.set(b)
                self.cpu_test_run(start=0x1000, end=None, mem=[
                    0x3a, # ABX (inherent)
                ])
                r = self.cpu.index_x.get()
                expected_value = x + b & 0xffff
#                print "%04x + %02x = %04x | CC:%s" % (
#                    x, b, r, self.cpu.cc.get_info
#                )
                self.assertEqualHex(r, expected_value)

                # CC complet uneffected:
                self.assertEqualHex(self.cpu.cc.get(), 0xff)

    def test_XOR(self):
        print("TODO!!!")

#    def setUp(self):
#        cmd_args = UnittestCmdArgs
#        cmd_args.trace = True # enable Trace output
#        cfg = TestCfg(cmd_args)
#        self.cpu = CPU(cfg)
#        self.cpu.cc.set(0x00)

    def test_DAA(self):
        self.cpu_test_run(start=0x0100, end=None, mem=[
            0x86, 0x67, #  LDA   #$67     ; A=$67
            0x8b, 0x75, #  ADDA  #$75     ; A=$67+$75 = $DC
            0x19, #        DAA   19       ; A=67+75=142 -> $42
        ])
        self.assertEqualHexByte(self.cpu.accu_a.get(), 0x42)
        self.assertEqual(self.cpu.cc.C, 1)

    def test_DAA2(self):
        for add in xrange(0xff):
            self.cpu.cc.set(0x00)
            self.cpu.accu_a.set(0x01)
            self.cpu_test_run(start=0x0100, end=None, mem=[
                0x8b, add, #  ADDA  #$1
                0x19, #       DAA
            ])
            r = self.cpu.accu_a.get()
#            print "$01 + $%02x = $%02x > DAA > $%02x | CC:%s" % (
#                add, (1 + add), r, self.cpu.cc.get_info
#            )

            # test half carry
            if add & 0x0f == 0x0f:
                self.assertEqual(self.cpu.cc.H, 1)
            else:
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

            # is undefined?
            # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4896
#            # test overflow
#            if r == 128:
#                self.assertEqual(self.cpu.cc.V, 1)
#            else:
#                self.assertEqual(self.cpu.cc.V, 0)

            # test carry
            if add >= 0x99:
                self.assertEqual(self.cpu.cc.C, 1)
            else:
                self.assertEqual(self.cpu.cc.C, 0)


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test6809_Arithmetic",
#             "Test6809_Arithmetic.test_DAA2",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
