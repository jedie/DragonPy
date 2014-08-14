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

import logging
import sys
import unittest

from dragonpy.tests.test_base import TextTestRunner2, Test6809_Dragon32_Base
from dragonpy.utils.logging_utils import log
from dragonpy.utils.logging_utils import setup_logging


class Test_Dragon32_BASIC(Test6809_Dragon32_Base):
#    @classmethod
#    def setUpClass(cls):
#        cls.UNITTEST_CFG_DICT.update({
#            "trace":True,
#        })
#        super(Test_Dragon32_BASIC, cls).setUpClass()

    def test_print01(self):
        self.periphery.add_to_input_queue('? "FOO"\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=57000)
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['? "FOO"', 'FOO', 'OK']
        )
        self.assertEqual(op_call_count, 56137)
        self.assertEqual(cycles, 316144) # TODO: cycles are probably not set corrent in CPU, yet!

    def test_poke(self):
        self.periphery.add_to_input_queue('POKE &H05ff,88\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=114000)
#        print op_call_count, cycles, output
        self.assertEqual(output,
            [u'POKE &H05FF,88', u'OK', u'X']
        )
    
    def test_code_load(self):
        self.periphery.add_to_input_queue(
            '10A=1\r\n'
            '20B=2\r\n'
            'LIST\r\n'
        )
        op_call_count, cycles, output = self._run_until_OK(max_ops=143000)
#        print op_call_count, cycles, output
        self.assertEqual(output,
            [u'10A=1', u'20B=2', u'LIST', u'10 A=1', u'20 B=2', u'OK']
        )
        output = self.request_comm.get_basic_program()
        self.assertEqual(output, ['10 A=1', '20 B=2'])



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
            "Test_Dragon32_BASIC.test_code_load",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
        failfast=True,
    )
