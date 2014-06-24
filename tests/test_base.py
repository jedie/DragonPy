#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import unittest

from cpu_utils.MC6809_registers import ConditionCodeRegister, ValueStorage8Bit
import logging


class BaseTestCase(unittest.TestCase):
    def assertEqualHex(self, hex1, hex2, msg=None):
        first = "$%x" % hex1
        second = "$%x" % hex2
        self.assertEqual(first, second, msg)


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


class TestCPU(object):
    def __init__(self):
        self.accu_a = ValueStorage8Bit("A", 0) # A - 8 bit accumulator
        self.accu_b = ValueStorage8Bit("B", 0) # B - 8 bit accumulator
        # 8 bit condition code register bits: E F H I N Z V C
        self.cc = ConditionCodeRegister()
