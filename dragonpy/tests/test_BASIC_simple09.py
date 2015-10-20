#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test CPU with BASIC Interpreter from simple6809 ROM.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging
import sys
import unittest

from dragonpy.tests.test_base import Test6809_BASIC_simple6809_Base
from dragonpy.utils.BASIC09_floating_point import BASIC09FloatingPoint


log = logging.getLogger("DragonPy")


class Test_simple6809_BASIC(Test6809_BASIC_simple6809_Base):
    def test_print01(self):
        self.periphery.add_to_input_queue('? "FOO"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['? "FOO"\r\n', 'FOO\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1085)
        self.assertEqual(cycles, 7354) # TODO: cycles are probably not set corrent in CPU, yet!

    def test_print02(self):
        self.periphery.add_to_input_queue('PRINT "BAR"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['PRINT "BAR"\r\n', 'BAR\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1424)

    def test_print03(self):
        self.periphery.add_to_input_queue('PRINT 0\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['PRINT 0\r\n', ' 0 \r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1366)

    def test_print04(self):
        self.periphery.add_to_input_queue('PRINT 4\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['PRINT 4\r\n', ' 4 \r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 3184)

    def test_STR(self):
        self.periphery.add_to_input_queue(
            'A=0\r\n'
            '? "A="+STR$(A)\r\n'
        )
        op_call_count, cycles, output = self._run_until_OK(
            OK_count=2, max_ops=20000
        )
        print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['A=0\r\n', 'OK\r\n', '? "A="+STR$(A)\r\n', 'A= 0\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 11229)

    def test_print_string_variable(self):
        self.periphery.add_to_input_queue(
            'A$="B"\r\n'
            '?A$\r\n'
        )
        op_call_count, cycles, output = self._run_until_OK(
            OK_count=2, max_ops=8500
        )
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['A$="B"\r\n', 'OK\r\n', '?A$\r\n', 'B\r\n', 'OK\r\n']
        )

    def test_TM_Error(self):
        self.periphery.add_to_input_queue('X="Y"\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=3500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['X="Y"\r\n', '?TM ERROR\r\n', 'OK\r\n']
        )


class Test_simple6809_BASIC_Float1(Test6809_BASIC_simple6809_Base):
    def test_print_float(self):
        self.periphery.add_to_input_queue('?2.5\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=5500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?2.5\r\n', ' 2.5 \r\n', 'OK\r\n']
        )

    def test_print_negative_float(self):
        self.periphery.add_to_input_queue('?-3.4\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=6300)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?-3.4\r\n', '-3.4 \r\n', 'OK\r\n']
        )

    def test_print_rounded_float(self):
        self.periphery.add_to_input_queue('?1.123456789\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=15000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?1.123456789\r\n', ' 1.12345679 \r\n', 'OK\r\n']
        )

    def test_division1(self):
        self.periphery.add_to_input_queue('?6/2\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=4500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?6/2\r\n', ' 3 \r\n', 'OK\r\n']
        )

    def test_division2(self):
        self.periphery.add_to_input_queue('?3/2\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=4500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?3/2\r\n', ' 1.5 \r\n', 'OK\r\n']
        )

    def test_division3(self):
        self.periphery.add_to_input_queue('?5/3\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=5100)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?5/3\r\n', ' 1.66666667 \r\n', 'OK\r\n']
        )

    def test_multiply1(self):
        self.periphery.add_to_input_queue('?3*2\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=4500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?3*2\r\n', ' 6 \r\n', 'OK\r\n']
        )

    def test_multiply2(self):
        self.periphery.add_to_input_queue('?8*-3\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=5100)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?8*-3\r\n', '-24 \r\n', 'OK\r\n']
        )

class Test_simple6809_BASIC_NumericFunctions(Test6809_BASIC_simple6809_Base):
    def test_ABS(self):
        self.periphery.add_to_input_queue('?ABS(-2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=7900)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?ABS(-2)\r\n', ' 2 \r\n', 'OK\r\n']
        )

    def test_ATN(self):
        self.periphery.add_to_input_queue('?ATN(2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=17200)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?ATN(2)\r\n', ' 1.10714872 \r\n', 'OK\r\n']
        )

    def test_COS(self):
        self.periphery.add_to_input_queue('?COS(3)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=15000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?COS(3)\r\n', '-.989992497 \r\n', 'OK\r\n']
        )

    def test_EXP(self):
        self.periphery.add_to_input_queue('?EXP(10)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=14000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?EXP(10)\r\n', ' 22026.4658 \r\n', 'OK\r\n']
        )

    def test_FIX(self):
        self.periphery.add_to_input_queue('?FIX(-7.4)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=11000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?FIX(-7.4)\r\n', '-7 \r\n', 'OK\r\n']
        )

    def test_INT(self):
        self.periphery.add_to_input_queue('?INT(-7.4)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=11000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?INT(-7.4)\r\n', '-8 \r\n', 'OK\r\n']
        )

    def test_LOG(self):
        self.periphery.add_to_input_queue('?LOG(2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=13000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?LOG(2)\r\n', ' .693147181 \r\n', 'OK\r\n']
        )

    def test_PEEK(self):
        addr = 0x03FE
        value = 0x5b
        self.cpu.memory.write_byte(addr, value)
        self.periphery.add_to_input_queue('?PEEK(%s)\r\n' % addr)
        op_call_count, cycles, output = self._run_until_OK(max_ops=9000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output, [
            '?PEEK(%i)\r\n' % addr,
            ' %i \r\n' % value,
            'OK\r\n'
        ])

    def test_POKE(self):
        addr = 0x03FE
        value = 12
        self.cpu.memory.write_byte(addr, 0xff)
        self.periphery.add_to_input_queue('POKE%i,%i\r\n' % (addr, value))
        op_call_count, cycles, output = self._run_until_OK(max_ops=4600)
#         print(op_call_count, cycles, output)
        self.assertEqual(output, [
            'POKE%i,%i\r\n' % (addr, value),
            'OK\r\n'
        ])
        self.assertEqualHexByte(self.cpu.memory.read_byte(addr), value)

    def test_RND(self): # FIXME: How to test is better?
        self.periphery.add_to_input_queue('?RND(1)\r\n') # will always return 1
        op_call_count, cycles, output = self._run_until_OK(max_ops=9000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?RND(1)\r\n', ' 1 \r\n', 'OK\r\n']
        )

    def test_SGN(self):
        self.periphery.add_to_input_queue('?SGN(10):?SGN(0):?SGN(-3)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=21000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output, [
            '?SGN(10):?SGN(0):?SGN(-3)\r\n',
            ' 1 \r\n', ' 0 \r\n', '-1 \r\n',
            'OK\r\n'
        ])

    def test_SIN(self):
        self.periphery.add_to_input_queue('?SIN(12)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=15000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?SIN(12)\r\n', '-.536572917 \r\n', 'OK\r\n']
        )

    def test_SQR(self):
        self.periphery.add_to_input_queue('?SQR(2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=20000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?SQR(2)\r\n', ' 1.41421356 \r\n', 'OK\r\n']
        )

    def test_TAN(self):
        self.periphery.add_to_input_queue('?TAN(5)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=20400)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?TAN(5)\r\n', '-3.38051501 \r\n', 'OK\r\n']
        )

    def test_CHR(self):
        self.periphery.add_to_input_queue('?CHR$(64)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=6000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?CHR$(64)\r\n', '@\r\n', 'OK\r\n']
        )

    def test_HEX(self):
        self.periphery.add_to_input_queue('?HEX$(30)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=6100)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?HEX$(30)\r\n', '1E\r\n', 'OK\r\n']
        )

    def test_STR(self):
        self.periphery.add_to_input_queue('?STR$(12.34)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=12000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?STR$(12.34)\r\n', ' 12.34\r\n', 'OK\r\n']
        )

    def test_LEFT(self):
        self.periphery.add_to_input_queue('?LEFT$("ABCD",2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=8000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?LEFT$("ABCD",2)\r\n', 'AB\r\n', 'OK\r\n']
        )

    def test_MID(self):
        self.periphery.add_to_input_queue('?MID$("ABCDE",2,3)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=10000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?MID$("ABCDE",2,3)\r\n', 'BCD\r\n', 'OK\r\n']
        )

    def test_RIGHT(self):
        self.periphery.add_to_input_queue('?RIGHT$("ABCD",2)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=8000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?RIGHT$("ABCD",2)\r\n', 'CD\r\n', 'OK\r\n']
        )

    def test_STRING(self):
        self.periphery.add_to_input_queue('?STRING$(4,"*")\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=8000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?STRING$(4,"*")\r\n', '****\r\n', 'OK\r\n']
        )

    def test_ASC(self):
        self.periphery.add_to_input_queue('X$="@":?ASC(X$)\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=15000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['X$="@":?ASC(X$)\r\n', ' 64 \r\n', 'OK\r\n']
        )

    def test_INSTR(self):
        self.periphery.add_to_input_queue('?INSTR(2,"ABCDABCD","A")\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=13000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?INSTR(2,"ABCDABCD","A")\r\n', ' 5 \r\n', 'OK\r\n']
        )

    def test_LEN(self):
        self.periphery.add_to_input_queue('?LEN("FOO")\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=7500)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?LEN("FOO")\r\n', ' 3 \r\n', 'OK\r\n']
        )

    def test_VAL(self):
        self.periphery.add_to_input_queue('?VAL("12")\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=8000)
#         print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['?VAL("12")\r\n', ' 12 \r\n', 'OK\r\n']
        )



class Test_simple6809_BASIC_Float2(Test6809_BASIC_simple6809_Base):
    def assertFPA(self, value, start, end):
        reference = BASIC09FloatingPoint(value)
        reference_bytes = reference.get_bytes()
        ram = self.cpu.memory.ram._mem[start:end + 1]
        if not ram == reference_bytes:
            self.cpu.memory.ram.print_dump(start, end)
            reference.print_values()
            self.assertEqual(ram, reference_bytes)

    def assertFPA0(self, value):
        """ test if the given value is in Floating Point Memory Accumulator 0 """
        self.assertFPA(value, 0x004f, 0x0054)

    def assertFPA1(self, value):
        """ test if the given value is in Floating Point Memory Accumulator 1 """
        self.assertFPA(value, 0x005c, 0x0061)

    def test_transfer_fpa0_to_fpa1(self):
        self.cpu.memory.load(0x004f, data=[
            0x12, # FPA 0 - exponent
            0x34, # FPA 0 - MS
            0x56, # FPA 0 - NMS
            0x78, # FPA 0 - NLS
            0x9a, # FPA 0 - LS
            0xbc, # FPA 0 - sign
        ])
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0xBD, 0xee, 0xa8, # JSR   $eea8  ; Move FPA0 to FPA1
        ])
#        self.cpu.memory.ram.print_dump(0x004f, 0x0054)  # FPA0 # FPA0
#        self.cpu.memory.ram.print_dump(0x005c, 0x0061) # FPA1
        self.assertEqual(
            self.cpu.memory.get(start=0x004f, end=0x0055),
            self.cpu.memory.get(start=0x005c, end=0x0062)
        )

    def test_ACCD_to_FPA0(self):
#        areas = range(0x10000) # Takes very long ;)

        # 16 Bit test values
        areas = list(range(0, 3))
        areas += ["..."] + list(range(0x7f, 0x82)) # sign change in 8 Bit range
        areas += ["..."] + list(range(0xfe, 0x101)) # end of 8 Bit range
        areas += ["..."] + list(range(0x7ffe, 0x8003)) # sign change in 16 Bit range
        areas += ["..."] + list(range(0xfffd, 0x10000)) # end of 16 Bit range

        failed = []
        ok = []
        for test_value in areas:
            if test_value == "...":
#                print "\n...\n"
                continue
#            print "\n$%04x (dez.: %i):" % (test_value, test_value),

            self.cpu.accu_d.set(test_value)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0xBD, 0xE7, 0x78, # JSR $e778 = CONVERT THE VALUE IN ACCD INTO A FLOATING POINT NUMBER IN FPA0
            ])
#            self.cpu.memory.ram.print_dump(0x004f, 0x0054)  # FPA0

            ram = self.cpu.memory.get(start=0x004f, end=0x0055)

            fp = BASIC09FloatingPoint(test_value)
#            fp.print_values()
            reference = fp.get_bytes()

            self.assertEqual(ram, reference)

            if not ram == reference:
                failed.append(test_value)
#                print "*** ERROR:"
#                print "in RAM...:", ", ".join(["$%02x" % i for i in ram])
#                print "Reference:", ", ".join(["$%02x" % i for i in reference])
#                fp.print_values()
            else:
                ok.append(test_value)
#                print "*** OK"

#            print
#            print "-"*79
#            print

#        print
#        print "OK:" , ok # [0, 1, 2, 127, 128, 129, 254, 255, 256, 32766, 32767]
#        print "Failed:", failed # [32768, 32769, 32770, 65533, 65534, 65535]


    def test_FPA0_to_D(self):
        # 16 Bit test values
        areas = list(range(0, 2))
        areas += ["..."] + list(range(0x7f, 0x82)) # sign change in 8 Bit range
        areas += ["..."] + list(range(0xfe, 0x101)) # end of 8 Bit range
        areas += ["..."] + list(range(0x7fff, 0x8002)) # sign change in 16 Bit range
        areas += ["..."] + list(range(0xfffd, 0x10000)) # end of 16 Bit range

        for test_value in areas:
            if test_value == "...":
#                print "\n...\n"
                continue

            # Set FPA0 via python float implementation
            fp = BASIC09FloatingPoint(test_value)
            self.cpu.memory.load(0x004f, fp.get_bytes())

            self.cpu_test_run(start=0x0000, end=None, mem=[
                0xBD, 0xe6, 0x82, #             JSR   $e682 - CONVERT FPA0 TO A TWO BYTE INTEGER to D
            ])
            d = self.cpu.accu_d.value
#            print "dez.: %i -> %i | hex: %04x -> %04x" % (d, test_value, d, test_value)
            self.assertEqual(d, test_value)

    def test_ACCB_to_FPA0_to_ACCD(self):
        """
        Convert a number vial CPU accu B with the BASIC routine into the
        BASIC floting point number. Then, convert the Float into CPU accu D
        and compare.
        """
        # 8 Bit test values
        areas = list(range(0, 3))
        areas += ["..."] + list(range(0x7f, 0x82)) # sign change in 8 Bit range
        areas += ["..."] + list(range(0xfe, 0x100)) # end of 8 Bit range

        for test_value in areas:
            if test_value == "...":
#                print "\n...\n"
                continue

            self.cpu.accu_b.set(test_value)
            self.cpu_test_run(start=0x0100, end=None, mem=[
                0xC6, test_value, # 0000  LDB  #$..
                0xBD, 0xE7, 0x77, # 0002  JSR  $e777 - CONVERT THE VALUE IN ACCB INTO A FP NUMBER IN FPA0
                0xBD, 0xE9, 0x92, # 0005  JSR  $e992 - CONVERT FPA0 TO INTEGER IN ACCD
            ])
            d = self.cpu.accu_d.value
#            print "dez.: %i -> %i | hex: %04x -> %04x" % (d, test_value, d, test_value)
            self.assertEqual(d, test_value)

    def test_ACCB_to_FPA0(self):
#        areas = range(0x100) # Takes long ;)

        # 8 Bit test values
        areas = list(range(0, 3))
        areas += ["..."] + list(range(0x7f, 0x82)) # sign change in 8 Bit range
        areas += ["..."] + list(range(0xfe, 0x100)) # end of 8 Bit range

#        areas = [55]

        failed = []
        ok = []
        for test_value in areas:
            if test_value == "...":
#                print "\n...\n"
                continue
#            print "$%02x (dez.: %i):" % (test_value, test_value)

            self.cpu_test_run(start=0x0000, end=None, mem=[
                0xC6, test_value, #  LDB  #$..
                0xBD, 0xE7, 0x77, #  JSR  $e777 - CONVERT THE VALUE IN ACCB INTO A FP NUMBER IN FPA0
            ])
#            self.cpu.memory.ram.print_dump(0x004f, 0x0054)  # FPA0

            ram = self.cpu.memory.get(start=0x004f, end=0x0055)

            fp = BASIC09FloatingPoint(test_value)
#            fp.print_values()
            reference = fp.get_bytes()

            self.assertEqual(ram, reference)

            if not ram == reference:
                failed.append(test_value)
#                print "*** ERROR:"
#                print "in RAM...:", ", ".join(["$%02x" % i for i in ram])
#                print "Reference:", ", ".join(["$%02x" % i for i in reference])
            else:
                ok.append(test_value)
#                print "*** OK"

            self.cpu_test_run(start=0x0000, end=None, mem=[
                0xBD, 0xE9, 0x92, #             JSR   $e992 - CONVERT FPA0 TO INTEGER IN ACCD
            ])
            d = self.cpu.accu_d.value
            self.assertEqual(d, test_value)

#            print
#            print "-"*79
#            print
#        print "OK:" , ok
#        print "Failed:", failed


'''
WIP:
    def test_divide_FPA0_by_10(self): # FIXME!
        """
        dividend / divisor = quotient
        """
        dividend = 0x5

        self.cpu.accu_d.set(dividend)
        self.cpu_test_run(start=0x0300, end=None, mem=[
            0xBD, 0xE7, 0x78, # JSR   $e778  ; Convert D to a float in FPA0
        ])
        self.assertFPA0(dividend) # Test if value is in FPA0

        from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log, level=20)
        self.cpu_test_run(start=0x0300, end=None, mem=[
            0xBD, 0xed, 0xcb, # JSR   $edcb  ; DIVIDE FPA0 BY 10
        ])

        self.cpu.memory.ram.print_dump(0x004f, 0x0054) # FPA0
        self.cpu.memory.ram.print_dump(0x005c, 0x0062) # FPA1

        BASIC09FloatingPoint(5).print_values()
        BASIC09FloatingPoint(10).print_values()
        BASIC09FloatingPoint(5.0 / 10).print_values()



    def test_division(self): # FIXME!
        """
        dividend / divisor = quotient
        """
        dividend = 0x5
        divisor = 0x3

        self.cpu.accu_d.set(dividend) # stored in FPA0 and moved to FPA1
        self.cpu_test_run(start=0x0300, end=None, mem=[
            0xBD, 0xE7, 0x78, # 0300  JSR   $e778  ; Convert D to a float in FPA0
        ])
        self.assertFPA0(dividend) # Test if value is in FPA0


#        self.cpu_test_run(start=0x0300, end=None, mem=[
#            0xBD, 0xEE, 0xA8, # 0303  JSR   $eea8  ; Move FPA0 to FPA1
#        ])
#        self.assertFPA1(dividend) # Test if value is in FPA1

        from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log, level=20)
#        self.cpu.index_x.set(divisor)
        self.cpu.accu_d.set(divisor)
        self.cpu_test_run(start=0x0300, end=None, mem=[
            0xBD, 0xed, 0xd8, # 0306  JSR   $edd8  ; divide X by FPA0
        ])

#        self.cpu.accu_d.set(divisor) # stored in FPA0
#        self.cpu_test_run(start=0x0300, end=None, mem=[
#            0xBD, 0xE7, 0x78, # 0300  JSR   $e778  ; Convert D to a float in FPA0
#        ])
#        self.assertFPA0(divisor) # Test if value is in FPA0
#
#        from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log, level=20)
##        self.cpu_test_run2(start=0x0306, count=100, mem=[
#        self.cpu_test_run(start=0x0300, end=None, mem=[
#            0xBD, 0xed, 0xdc, # 0306  JSR   $edda  ; divide FPA1 by FPA0
#        ])

        self.cpu.memory.ram.print_dump(0x004f, 0x0054) # FPA0
        self.cpu.memory.ram.print_dump(0x005c, 0x0062) # FPA1

        BASIC09FloatingPoint(5).print_values()
        BASIC09FloatingPoint(3).print_values()
        BASIC09FloatingPoint(5.0 / 3.0).print_values()
'''


