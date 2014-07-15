#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test CPU with BASIC Interpreter from sbc09 ROM.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import pprint
import sys
import unittest

from dragonpy.tests.test_base import TextTestRunner2, Test6809_sbc09_Base, \
    UnittestCmdArgs

from dragonpy.utils.logging_utils import setup_logging


log = logging.getLogger("DragonPy")


class Test_sbc09(Test6809_sbc09_Base):

#    @classmethod
#    def setUpClass(cls, cmd_args=None):
#        cmd_args = UnittestCmdArgs
#        cmd_args.trace = True # enable Trace output
#        super(Test_sbc09, cls).setUpClass(cmd_args)

    def test_calculate_hex_positive(self):
        """
        Calculate simple expression in hex with + and -
        """
        for i in xrange(20):
            self.setUp() # Reset CPU
            self.periphery.add_to_input_queue(
                 'H100+%X\r\n' % i
            )
            op_call_count, cycles, output = self._run_until_newlines(
                newline_count=2, max_ops=700
            )
#            print op_call_count, cycles, output
            self.assertEqual(output[1:], [
                '%04X\r\n' % (0x100 + i)
            ])

    def test_calculate_hex_negative(self):
        """
        Calculate simple expression in hex with + and -
        """
        for i in xrange(20):
            self.setUp() # Reset CPU
            self.periphery.add_to_input_queue(
                 'H100-%X\r\n' % i
            )
            op_call_count, cycles, output = self._run_until_newlines(
                newline_count=2, max_ops=700
            )
#            print op_call_count, cycles, output
            self.assertEqual(output[1:], [
                '%04X\r\n' % (0x100 - i)
            ])

    def test_dump_registers(self):
        self.periphery.add_to_input_queue('r\r\n')
        op_call_count, cycles, output = self._run_until_newlines(
            newline_count=3, max_ops=2200
        )
#         print op_call_count, cycles, output
        self.assertEqual(output, [
            'r\r\n',
            'X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00 \r\n',
            'P=0400 NEG   $00\r\n'
        ])

    def test_S_records(self):
        """ Dump memory region as Motorola S records """
        print "TODO!!!"
        return
        self.periphery.add_to_input_queue('ss\r\n')
        op_call_count, cycles, output = self._run_until_newlines(
#            newline_count=18,
            newline_count=4,
            max_ops=150000
        )
        print op_call_count, cycles, len(output), pprint.pformat(output)
        self.assertEqual(output, [
            'ss\r\n',
            "S11300007EE45A7EE4717EE4807EE4E47EE4F57E60\r\n",
            "S1130010E4657EED447EED677EED8C7EEDCF7EED76\r\n",
            "S1130020AC7EE5180C660000000000003000000003\r\n", # failed here is a 3 ?!?
            "S113003000000000000000000000000000000000BC\r\n",
            "S113004000000000000000000000000000000000AC\r\n",
            "S1130050000000000000000000000000000000009C\r\n",
            "S1130060000000000000000000000000000000008C\r\n",
            "S1130070000000000000000000000000000000007C\r\n",
            "S1130080000000000000000000000000000000006C\r\n",
            "S1130090000000000000000000000000000000005C\r\n",
            "S11300A0000000000000000000000000000000004C\r\n",
            "S11300B0000000000000000000000000000000003C\r\n",
            "S11300C0000000000000000000000000000000002C\r\n",
            "S11300D0000000000000000000000000000000001C\r\n",
            "S11300E0000000000000000000000000000000000C\r\n",
            "S11300F000000000000000000000000000000000FC\r\n",
            "S9030000FC\r\n",
        ])

    def test_disassemble(self):
        """
        Uaddr,len - Disassemble memory region

        From listing:

        02CF:                 * Monitor ROM starts here.
        02CF:                                 org $E400
        E400:
        E400: 1AFF            reset           orcc #$FF
        E402: 4F                              clra
        E403: 1F8B                            tfr a,dp
        E405: 10CE0400                        lds #ramstart
        E409: 8EE4FF                          ldx #intvectbl
        E40C: CE0280                          ldu #swi3vec
        E40F: C61B                            ldb #osvectbl-intvectbl
        E411: 8D37                            bsr blockmove
        E413: 8EE51A                          ldx #osvectbl
        E416: CE0000                          ldu #0
        E419: C624                            ldb #endvecs-osvectbl
        E41B: 8D2D                            bsr blockmove
        E41D: 8D33                            bsr initacia
        E41F: 1C00                            andcc #$0
        """
        self.cpu.cfg.trace = True
        self.periphery.add_to_input_queue('UE400,16\r\n')
        op_call_count, cycles, output = self._run_until_newlines(
            newline_count=11, max_ops=13600
        )
#        print op_call_count, cycles, len(output), pprint.pformat(output)
        self.assertEqual(output, [
            'UE400,16\r\n',
            'E400 1AFF       ORCC  #$FF\r\n',
            'E402 4F         CLRA  \r\n',
            'E403 1F8B       TFR   A,DP\r\n',
            'E405 10CE0400   LDS   #$0400\r\n',
            'E409 8EE520     LDX   #$E520\r\n',
            'E40C CE0280     LDU   #$0280\r\n',
            'E40F C61B       LDB   #$1B\r\n',
            'E411 8D37       BSR   $E44A\r\n',
            'E413 8EE53B     LDX   #$E53B\r\n',
            'E416 CE0000     LDU   #$0000\r\n'
        ])


if __name__ == '__main__':
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
#            "Create_sbc09_trace",
#            "Test_sbc09.test_S_records",
#            "Test_sbc09.test_calculate_hex_negative",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
    print " --- END --- "
