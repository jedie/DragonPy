#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    6809 is Big-Endian
    some code is from XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging


log = logging.getLogger("DragonPy")


class Accumulators(object):
    def __init__(self, cpu):
        self.cpu = cpu
        self._A = 0 # A - 8 bit accumulator
        self._B = 0 # B - 8 bit accumulator
        # D - 16 bit concatenated reg. (A + B)

    def _check(self, value, txt):
        if value > 0xff:
            log.warning(" **** Set cc overflow from 8-bit accumulator %s, value: $%x" % (txt, value))
            self.cpu.cc.V = 1 # set Overflow flag
            value = value & 0xff
            log.warning(" ^^^^ Value for %s truncated to $%x" % (txt, value))
        return value

    def get_A(self):
        return self._A
    def set_A(self, value):
        self._A = self._check(value, "A")
    A = property(get_A, set_A)

    def get_B(self):
        return self._B
    def set_B(self, value):
        self._B = self._check(value, "B")
    B = property(get_B, set_B)

    def get_D(self):
        return self._A * 256 + self._B
    def set_D(self, value):
        self.set_A(value >> 8)
        self.set_B(value & 0xff)
        if value > 0xffff:
            log.warning(" **** Set cc overflow from 16-bit accumulator D, value: $%x" % value)
            self.cpu.cc.V = 1 # set Overflow flag
            value = value & 0xffff
            log.warning(" ^^^^ Value for D truncated to $%x" % value)
    D = property(get_D, set_D)


