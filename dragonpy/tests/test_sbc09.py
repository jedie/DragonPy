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

from dragonpy.tests.test_base import TextTestRunner2, Test6809_sbc09_Base


from dragonpy.utils.BASIC09_floating_point import BASIC09FloatingPoint
from dragonpy.utils.logging_utils import setup_logging



log = logging.getLogger("DragonPy")


class Test_sbc09(Test6809_sbc09_Base):
    def test_dump_registers(self):
        print "TODO: SBC09 unittests!"
        return
        self.periphery.add_to_input_queue('r\r\n')
        op_call_count, cycles, output = self._run_until_OK(max_ops=2000)
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['? "FOO"\r\n', 'FOO\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1085)
        self.assertEqual(cycles, 7354) # TODO: cycles are probably not set corrent in CPU, yet!


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
