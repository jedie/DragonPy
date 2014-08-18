#!/usr/bin/env python
# encoding:utf-8

"""
    Dragon Lib unittests
    ~~~~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

class BaseTestCase(unittest.TestCase):
    """
    Only some special assertments.
    """
    def assertHexList(self, first, second, msg=None):
        first = ["$%x" % value for value in first]
        second = ["$%x" % value for value in second]
        self.assertEqual(first, second, msg)

    def assertEqualHex(self, hex1, hex2, msg=None):
        first = "$%x" % hex1
        second = "$%x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

    def assertIsByteRange(self, value):
        self.assertTrue(0x0 <= value, "Value (dez: %i - hex: %x) is negative!" % (value, value))
        self.assertTrue(0xff >= value, "Value (dez: %i - hex: %x) is greater than 0xff!" % (value, value))

    def assertIsWordRange(self, value):
        self.assertTrue(0x0 <= value, "Value (dez: %i - hex: %x) is negative!" % (value, value))
        self.assertTrue(0xffff >= value, "Value (dez: %i - hex: %x) is greater than 0xffff!" % (value, value))

    def assertEqualHexByte(self, hex1, hex2, msg=None):
        self.assertIsByteRange(hex1)
        self.assertIsByteRange(hex2)
        first = "$%02x" % hex1
        second = "$%02x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

    def assertEqualHexWord(self, hex1, hex2, msg=None):
        self.assertIsWordRange(hex1)
        self.assertIsWordRange(hex2)
        first = "$%04x" % hex1
        second = "$%04x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

