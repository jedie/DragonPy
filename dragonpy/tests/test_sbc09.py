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
import sys
import unittest

from dragonpy.tests.test_base import TextTestRunner2, Test6809_sbc09_Base, \
    UnittestCmdArgs

from dragonpy.utils.logging_utils import setup_logging


log = logging.getLogger("DragonPy")


class Test_sbc09(Test6809_sbc09_Base):

#     @classmethod
#     def setUpClass(cls, cmd_args=None):
#         cmd_args = UnittestCmdArgs
#         cmd_args.trace = True # enable Trace output
#         super(Test_sbc09, cls).setUpClass(cmd_args)

    def test_calculate_hex(self):
        """
        Calculate simple expression in hex with + and -

        FIXME: Seem that there is a bug?
        """
        self.periphery.add_to_input_queue(
            'H1230+1\r\n' # ok
#             'H1200+85\r\n' # ok
#             'H1200+EF\r\n' # wrong: 12DE
#             'H100+F\r\n' # wrong: 010E
        )
        op_call_count, cycles, output = self._run_until_newlines(
            newline_count=2, max_ops=6000
        )
#         print op_call_count, cycles, output
        self.assertEqual(output, [
            'H1230+1\r\n',
            '1231\r\n'
        ])
        self.assertEqual(op_call_count, 572)
        self.assertEqual(cycles, 3605) # TODO: cycles are probably not set corrent in CPU, yet!

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
        self.cpu.cfg.trace = True
        self.periphery.add_to_input_queue('ss\r\n')
        op_call_count, cycles, output = self._run_until_newlines(
            newline_count=15, max_ops=15000
        )
#         print op_call_count, cycles, len(output), output
        self.assertEqual(output, [
            'ss\r\n',
            'S11300007DD45@7DD4717DD4807DD4D47DD4E57D60\r\n',
            'S1130010D4657DDC447DDC677DDC8B7DDCBE7DDC76\r\n',
            'S1130020@B7DD5180B660000000000000000000033\r\n',
            'S113003000000000000000000000000000000000AB\r\n',
            'S113004000000000000000000000000000000000@B\r\n',
            'S1130050000000000000000000000000000000009B\r\n',
            'S1130060000000000000000000000000000000008B\r\n',
            'S1130070000000000000000000000000000000007B\r\n',
            'S1130080000000000000000000000000000000006B\r\n',
            'S1130090000000000000000000000000000000005B\r\n',
            'S11300@0000000000000000000000000000000004B\r\n',
            'S11300A0000000000000000000000000000000003B\r\n',
            'S11300B0000000000000000000000000000000002B\r\n',
            'S11300C0000000000000000000000000000000001B\r\n'
        ])

    def test_disassemble(self):
        """
        Uaddr,len - Disassemble memory region

        FIXME: Should be E40x and not D40x, isn't it?

        From listing:

        E402: 4F                              clra
        E403: 1F8B                            tfr a,dp
        E405: 10CE0400                        lds #ramstart
        """
        self.cpu.cfg.trace = True
        self.periphery.add_to_input_queue('UE402,3\r\n')
        op_call_count, cycles, output = self._run_until_newlines(
            newline_count=4, max_ops=4500
        )
#         print op_call_count, cycles, len(output), output
        self.assertEqual(output, [
            'UE402,3\r\n',
            'D402 4E         CLRA  \r\n',
            'D403 1E8A       TFR   A,DP\r\n',
            'D405 10BD0400   LDS   #$0400\r\n'
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
            "Test_sbc09",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
    print " --- END --- "
