#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    some code is borrowed from:
    XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

log = logging.getLogger("DragonPy")


def signed8(x):
    """ convert to signed 8-bit """
    if x > 0x7f: # 0x7f ==  2**7-1 == 127
        x = x - 0x100 # 0x100 == 2**8 == 256
    return x


def signed16(x):
    """ convert to signed 16-bit """
    if x > 0x7fff: # 0x7fff ==  2**15-1 == 32767
        x = x - 0x10000 # 0x100 == 2**16 == 65536
    return x


class ValueStorage(object):
    def __init__(self, name, initial_value):
        self.name = name
        self.value = initial_value

    def set(self, v):
        self.value = v
    def get(self):
        return self.value

    def __str__(self):
        return "<%s:%s>" % (self.name, repr(self.value))
    __repr__ = __str__


class ValueStorage8Bit(ValueStorage):
    def set(self, v):
        if v > 0xff:
            log.warning(" **** Value $%x is to big for %s (8-bit)" % (v, self.name))
            v = v & 0xff
            log.warning(" ^^^^ Value for %s (8-bit) truncated to $%x" % (self.name, v))
        self.value = v
    def __str__(self):
        return "<%s (8-Bit):%s>" % (self.name, repr(self.value))


class ValueStorage16Bit(ValueStorage):
    def set(self, v):
        if v > 0xffff:
            log.warning(" **** Value $%x is to big for %s (16-bit)" % (v, self.name))
            v = v & 0xffff
            log.warning(" ^^^^ Value for %s (16-bit) truncated to $%x" % (self.name, v))
        self.value = v
    def __str__(self):
        return "<%s (8-Bit):%s>" % (self.name, repr(self.value))



def _register_bit(key):
    def set_flag(self, value):
        assert value in (0, 1)
        self._register[key] = value
    def get_flag(self):
        return self._register[key]
    return property(get_flag, set_flag)


class ConditionCodeRegister(object):
    """ CC - 8 bit condition code register bits """

    def __init__(self, *args, **kwargs):
        self._register = {}
        self.set(0x0) # create all keys in dict with value 0

    E = _register_bit("E") # E - 0x80 - bit 7 - Entire register state stacked
    F = _register_bit("F") # F - 0x40 - bit 6 - FIRQ interrupt masked
    H = _register_bit("H") # H - 0x20 - bit 5 - Half-Carry
    I = _register_bit("I") # I - 0x10 - bit 4 - IRQ interrupt masked
    N = _register_bit("N") # N - 0x08 - bit 3 - Negative result (twos complement)
    Z = _register_bit("Z") # Z - 0x04 - bit 2 - Zero result
    V = _register_bit("V") # V - 0x02 - bit 1 - Overflow
    C = _register_bit("C") # C - 0x01 - bit 0 - Carry (or borrow)

    ####

    def set(self, status):
        self.E, self.F, self.H, self.I, self.N, self.Z, self.V, self.C = \
            [0 if status & x == 0 else 1 for x in (128, 64, 32, 16, 8, 4, 2, 1)]

    def get(self):
        return self.C | \
            self.V << 1 | \
            self.Z << 2 | \
            self.N << 3 | \
            self.I << 4 | \
            self.H << 5 | \
            self.F << 6 | \
            self.E << 7

    ####

    def set_Z8(self, r):
        self.Z = 1 if r & 0xff == 0 else 0

    def set_Z16(self, r):
        self.Z = 1 if r & 0xffff == 0 else 0

    def set_N8(self, r):
        self.N = 1 if signed8(r) < 0 else 0

    def set_N16(self, r):
        self.N = 1 if signed16(r) < 0 else 0

    def set_H(self, a, b, r): # TODO: Add tests
        self.H = 1 if (a ^ b ^ r) & 0x10 else 0

    def set_C8(self, r):
        self.C = 1 if r & 0x100 else 0

    def set_C16(self, r):
        self.C = 1 if r & 0x10000 else 0

    def set_V8(self, a, b, r):
        if self.V == 0 and (a ^ b ^ r ^ (r >> 1)) & 0x80:
            self.V = 1

    def set_V16(self, a, b, r):
        if self.V == 0 and (a ^ b ^ r ^ (r >> 1)) & 0x8000:
            self.V = 1

    ####

#     def update_NZ8(self, r):
#         self.set_N8(r)
#         self.set_Z8(r)
#
#     def update_NZ16(self, r):
#         self.set_N16(r)
#         self.set_Z16(r)
#
#     def update_NZC8(self, r):
#         self.set_N8(r)
#         self.set_Z8(r)
#         self.set_C8(r)
#
#     def update_NZC16(self, r):
#         self.set_N16(r)
#         self.set_Z16(r)
#         self.set_C16(r)
#
#     def update_NZVC8(self, a, b, r): # FIXME
#         self.set_N8(r)
#         self.set_Z8(r)
#         self.set_V8(a, b, r)
#         self.set_C8(r)
#
#     def update_NZVC16(self, a, b, r): # FIXME
#         self.set_N16(r)
#         self.set_Z16(r)
#         self.set_V16(a, b, r)
#         self.set_C16(r)

    def update_NZ8(self, r):
        self.set_N8(r)
        self.set_Z8(r)

    def update_0100(self):
        """ CC bits "HNZVC": -0100 """
        self.N = 0
        self.Z = 1
        self.V = 0
        self.C = 0

    def update_NZ01_8(self, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.V = 0
        self.C = 1

    def update_NZ0_8(self, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.V = 0

    def update_NZ0_16(self, r):
        self.set_N16(r)
        self.set_Z16(r)
        self.V = 0

    def update_HNZVC(self, a, b, r):
        self.set_H(a, b, r)


class ConcatenatedAccumulator(object):
    def __init__(self, name, a, b):
        self.name = name
        self._a = a
        self._b = b

    def set(self, value):
        self._a.set(value >> 8)
        self._b.set(value & 0xff)

    def get(self):
        a = self._a.get()
        b = self._b.get()
        return a * 256 + b


def get_6809_registers():

    return d
