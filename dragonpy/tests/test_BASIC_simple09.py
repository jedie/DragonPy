#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test CPU with BASIC Interpreter from simple6809 ROM.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import unittest

from dragonpy.tests.test_base import TextTestRunner2, Test6809_BASIC_simple6809_Base


from dragonpy.utils.BASIC09_floating_point import BASIC09FloatingPoint



log = logging.getLogger("DragonPy")


class Test_simple6809_BASIC(Test6809_BASIC_simple6809_Base):
    def test_print01(self):
        self.assertEqual(self.cpu.get_info,
            "cc=54 a=0d b=00 dp=00 x=deae y=0000 u=deab s=0334"
        )
        self.assertEqual(self.cpu.cc.get_info, ".F.I.Z..")
        self.assertEqual(self.cpu.program_counter, 57131)

        self.periphery.add_to_input_queue('? "FOO"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['? "FOO"\r\n', 'FOO\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1085)
        self.assertEqual(cycles, 7354) # TODO: cycles are probably not set corrent in CPU, yet!

    def test_print02(self):
        self.assertEqual(self.cpu.get_info,
            "cc=54 a=0d b=00 dp=00 x=deae y=0000 u=deab s=0334"
        )
        self.assertEqual(self.cpu.cc.get_info, ".F.I.Z..")
        self.assertEqual(self.cpu.program_counter, 57131)

        self.periphery.add_to_input_queue('PRINT "BAR"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['PRINT "BAR"\r\n', 'BAR\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1424)

    def test_print03(self):
        self.periphery.add_to_input_queue('PRINT 0\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['PRINT 0\r\n', ' 0 \r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1366)

    def test_STR(self):
        self.periphery.add_to_input_queue(
            'A=0\r\n'
            '? "A="+STR$(A)\r\n'
        )
        op_call_count, cycles, output = self._run_until_OK(
            OK_count=2, max_ops=12000
        )
#         print op_call_count, cycles, output
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
        print op_call_count, cycles, output
        self.assertEqual(output,
            ['A$="B"\r\n', 'OK\r\n', '?A$\r\n', 'B\r\n', 'OK\r\n']
        )

    def test_TM_Error(self):
        self.periphery.add_to_input_queue('X="Y"\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=3500)
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['X="Y"\r\n', '?TM ERROR\r\n', 'OK\r\n']
        )

#    def test_PRINT04(self):  # will faile, yet...
#        self.periphery.add_to_input_queue('?5/3\r\n')
#        op_call_count, cycles, output = self._run_until_OK(max_ops=100000)
##         print op_call_count, cycles, output
#        self.assertEqual(output,
#            ['?2\r\n', ' 2 \r\n', 'OK\r\n']
#        )

#     def test_MUL(self): # will faile, yet...
#         self.periphery.add_to_input_queue('?2*3\r\n')
#         op_call_count, cycles, output = self._run_until_OK()
# #         print op_call_count, cycles, output
#         self.assertEqual(output,
#             ['?2*3\r\n', ' 6\r\n', 'OK\r\n']
#         )

    def test_transfer_fpa0_to_fpa1(self):
        self.cpu.memory.ram.load(0x004f, data=[
            0x12, # FPA 0 - exponent
            0x34, # FPA 0 - MS
            0x56, # FPA 0 - NMS
            0x78, # FPA 0 - NLS
            0x9a, # FPA 0 - LS
            0xbc, # FPA 0 - sign
        ])
        self.cpu_test_run(start=0x0000, end=None, mem=[
            0xBD, 0xee, 0xa8, # JSR   $eea8
        ])
#        self.cpu.memory.ram.print_dump(0x004f, 0x0054) # FPA0
#        self.cpu.memory.ram.print_dump(0x005c, 0x0061) # FPA1
        self.assertEqual(
            self.cpu.memory.ram._mem[0x004f:0x0055],
            self.cpu.memory.ram._mem[0x005c:0x0062],
        )

    def test_ACCD_to_FPA0(self): # FIXME!
#        areas = range(0x10000) # Takes very long ;)

        # 16 Bit test values
        areas = range(0, 3)
        areas += ["..."] + range(0x7f, 0x82) # sign change in 8 Bit range
        areas += ["..."] + range(0xfe, 0x101) # end of 8 Bit range
        areas += ["..."] + range(0x7ffe, 0x8003) # sign change in 16 Bit range
        areas += ["..."] + range(0xfffd, 0x10000) # end of 16 Bit range

#        areas = [0x0100]

        print areas
        failed = []
        ok = []
        for test_value in areas:
            if test_value == "...":
                print "\n...\n"
                continue
            print "\n$%04x (dez.: %i):" % (test_value, test_value),

            self.cpu.accu_d.set(test_value)
            self.cpu_test_run(start=0x0000, end=None, mem=[
                0xBD, 0xE7, 0x78, # JSR $e778 = CONVERT THE VALUE IN ACCD INTO A FLOATING POINT NUMBER IN FPA0
            ])
#            self.cpu.memory.ram.print_dump(0x004f, 0x0054)

            ram = self.cpu.memory.ram._mem[0x004f:0x0055]

            fp = BASIC09FloatingPoint(test_value)
#            fp.print_values()
            reference = fp.get_bytes()

#            self.assertEqual(ram, reference)

            if not ram == reference:
                failed.append(test_value)
                print "*** ERROR:"
                print "in RAM...:", ", ".join(["$%02x" % i for i in ram])
                print "Reference:", ", ".join(["$%02x" % i for i in reference])
                fp.print_values()
            else:
                ok.append(test_value)
                print "*** OK"

            # Will only work from $0-$ff, after this -> ?FC ERROR IN 0
#            self.cpu_test_run(start=0x0000, end=None, mem=[
#                0xBD, 0xE9, 0x92, #             JSR   $e992 - CONVERT FPA0 TO INTEGER IN ACCD
#            ])
#            d = self.cpu.accu_d.get()
#            print "dez.: %i -> %i | hex: %04x -> %04x" % (d, test_value, d, test_value)
#            self.assertEqual(d, test_value)

#            print
#            print "-"*79
#            print

        print
        print "OK:" , ok # [0, 1, 2, 127, 128, 129, 254, 255, 256, 32766, 32767]
        print "Failed:", failed # [32768, 32769, 32770, 65533, 65534, 65535]


    def test_ACCB_to_FPA0_to_ACCD(self):
        """
        Convert a number vial CPU accu B with the BASIC routine into the
        BASIC floting point number. Then, convert the Float into CPU accu D
        and compare.
        """
        areas = range(0, 2) + ["..."] + range(0x7f, 0x82) + ["..."] + range(0xfd, 0x100)
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
            d = self.cpu.accu_d.get()
#            print "dez.: %i -> %i | hex: %04x -> %04x" % (d, test_value, d, test_value)
            self.assertEqual(d, test_value)

    def test_ACCB_to_FPA0(self):
#        areas = range(0x100) # Takes long ;)

        # 8 Bit test values
        areas = range(0, 3)
        areas += ["..."] + range(0x7f, 0x82) # sign change in 8 Bit range
        areas += ["..."] + range(0xfe, 0x100) # end of 8 Bit range

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
#            self.cpu.memory.ram.print_dump(0x004f, 0x0054)

            ram = self.cpu.memory.ram._mem[0x004f:0x0055]

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
            d = self.cpu.accu_d.get()
            self.assertEqual(d, test_value)

#            print
#            print "-"*79
#            print
#        print "OK:" , ok
#        print "Failed:", failed


#    def test_floating_point_routines01(self):
#        # $ee5d = "FPA0 load: MOVE (X) TO FPA0"
#
#        self.periphery.add_to_input_queue('F=6\r\n')
#        try:
#            op_call_count, cycles, output = self._run_until_OK(max_ops=5000)
#            print op_call_count, cycles, output
#        except Exception, err:
#            print "Abort: %s" % err
#
#        self.cpu.memory.ram.print_dump(0x004f, 0x0054)
#        return
#
#        self.cpu_test_run(start=0x0100, end=None, mem=[
#            #                        FLOAD: EQU   $ee5d
##            0x8E, 0x61, 0x00, #             LDX   #$6100
#            0xBD, 0xee, 0x5d, #       JSR   FLOAD
#        ])


if __name__ == '__main__':
    log.setLevel(
#        1
#        10 # DEBUG
#        20 # INFO
#        30 # WARNING
#        40 # ERROR
        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test_simple6809_BASIC.test_PRINT04",
#            "Test_simple6809_BASIC.test_ACCD_to_FPA0",
#            "Test_simple6809_BASIC.test_transfer_fpa0_to_fpa1",
#            "Test_simple6809_BASIC.test_ACCB_to_FPA0_to_ACCD",
            "Test_simple6809_BASIC.test_ACCB_to_FPA0",
#            "Test_simple6809_BASIC.test_floating_point_routines01",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
