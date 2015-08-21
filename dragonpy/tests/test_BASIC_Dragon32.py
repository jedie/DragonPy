#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test CPU with BASIC Interpreter from Dragon32 ROM.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import sys
import unittest
import logging

from dragonlib.utils.logging_utils import setup_logging
from dragonpy.tests.test_base import Test6809_Dragon32_Base


log = logging.getLogger(__name__)


class Test_Dragon32_BASIC(Test6809_Dragon32_Base):
#    @classmethod
#    def setUpClass(cls):
#        cls.UNITTEST_CFG_DICT.update({
#            "trace":True,
#        })
#        super(Test_Dragon32_BASIC, cls).setUpClass()

    def test_print01(self):
        self.periphery.add_to_input_queue('? "FOO"\r')
        op_call_count, cycles, output = self._run_until_OK(max_ops=57000)
        print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['? "FOO"', 'FOO', 'OK']
        )
        self.assertEqual(op_call_count, 56143)
        self.assertEqual(cycles, 316192) # TODO: cycles are probably not set corrent in CPU, yet!

    def test_poke(self):
        self.periphery.add_to_input_queue('POKE &H05ff,88\r')
        op_call_count, cycles, output = self._run_until_OK(max_ops=114000)
#        print op_call_count, cycles, output
        self.assertEqual(output,
            ['POKE &H05FF,88', 'OK', 'X']
        )

    def test_code_load01(self):
        output = self.machine.get_basic_program()
        self.assertEqual(output, [])

        self.periphery.add_to_input_queue(
            '10A=1\r'
            '20B=2\r'
            'LIST\r'
        )
        op_call_count, cycles, output = self._run_until_OK(max_ops=143000)
#        print op_call_count, cycles, output
        self.assertEqual(output,
            ['10A=1', '20B=2', 'LIST', '10 A=1', '20 B=2', 'OK']
        )
        output = self.machine.get_basic_program()
        self.assertEqual(output, ['10 A=1', '20 B=2'])

    def test_code_save01(self):
        output = self.machine.get_basic_program()
        self.assertEqual(output, [])

        self.machine.inject_basic_program(
            '10 ?123\n'
            '20 PRINT "FOO"\n'
        )

        # Check the lising
        self.periphery.add_to_input_queue('LIST\r')
        op_call_count, cycles, output = self._run_until_OK(max_ops=4000000)
#        print op_call_count, cycles, output
        self.assertEqual(output,
            ['LIST', '10 ?123', '20 PRINT "FOO"', 'OK']
        )

    @unittest.expectedFailure # TODO:
    def test_tokens_in_string(self):
        self.periphery.add_to_input_queue(
            # "10 PRINT ' FOR NEXT COMMENT\r"
            "10 PRINT ' FOR NEXT\r"
            'LIST\r'
        )
        op_call_count, cycles, output = self._run_until_OK(max_ops=1430000)
        print(op_call_count, cycles, output)
        self.assertEqual(output,
            ['10A=1', '20B=2', 'LIST', '10 A=1', '20 B=2', 'OK']
        )
        output = self.machine.get_basic_program()
        self.assertEqual(output, ['10 A=1', '20 B=2'])


