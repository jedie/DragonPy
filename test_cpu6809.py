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
from cpu6809 import CPU, Memory

class TextTestResult2(unittest.TextTestResult):
    def startTest(self, test):
        if not self.showAll:
            super(TextTestResult2, self).startTest(test)
            return

        print
        print "_"*70
        self.showAll = False
        print self.getDescription(test), "..."
        super(TextTestResult2, self).startTest(test)
        self.showAll = True


class TextTestRunner2(unittest.TextTestRunner):
    resultclass = TextTestResult2


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        cfg = Dragon32Cfg()
        self.memory = Memory(cfg)
        self.cpu = CPU(cfg, self.memory)


class Test6809_CC(BaseTestCase):
    """
    condition code register tests
    """
    def test_defaults(self):
        status_byte = self.cpu.status_as_byte()
        self.assertEqual(status_byte, 0)

    def test_from_to(self):
        for i in xrange(256):
            self.cpu.status_from_byte(i)
            status_byte = self.cpu.status_as_byte()
            self.assertEqual(status_byte, i)

    def test_set_register01(self):
        self.cpu.set_register(0x00, 0x1e12)
        self.assertEqual(self.cpu.accumulator_a, 0x1e)
        self.assertEqual(self.cpu.accumulator_b, 0x12)


class Test6809_Ops(BaseTestCase):
    def test_TFR01(self):
        self.cpu.index_x = 512 # source
        self.assertEqual(self.cpu.index_y, 0) # destination

        self.memory.load(0x1000, [
            0x1f, # TFR
            0x12, # from index register X (0x01) to Y (0x02)
            0x1f, # TFR
            0x9a, # from accumulator B (0x09) to condition code register CC (0x9a)
        ])
        self.cpu.test_run(start=0x1000, end=0x1002)

        self.assertEqual(self.cpu.index_y, 512)

    def test_TFR02(self):
        self.cpu.accumulator_b = 0x55 # source
        self.assertEqual(self.cpu.status_as_byte(), 0) # destination

        self.memory.load(0x1000, [
            0x1f, # TFR
            0x9a, # from accumulator B (0x09) to condition code register CC (0x9a)
        ])
        self.cpu.test_run(start=0x1000, end=0x1002)
        self.assertEqual(self.cpu.status_as_byte(), 0x55) # destination





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
#             "Test6809_Ops.test_TFR02",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
        failfast=True,
    )
