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


def unsigned8(x):
    """ convert a signed 8-Bit value into a unsigned value """
    if x < 0:
        x = x + 0x0100 # 0x100 == 2**8 == 256
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
        return self.value # e.g.: r = operand.set(a + 1)
    def get(self):
        return self.value

    # FIXME:
    def decrement(self, value=1):
        return self.set(self.value - value)
    def increment(self, value=1):
        return self.set(self.value + value)

    def __str__(self):
        return "<%s:$%x>" % (self.name, self.value)
    __repr__ = __str__


class ValueStorage8Bit(ValueStorage):
    def set(self, v):
        if v > 0xff:
            log.info(" **** Value $%x is to big for %s (8-bit)" % (v, self.name))
            v = v & 0xff
            log.info(" ^^^^ Value %s (8-bit) wrap around to $%x" % (self.name, v))
        elif v < 0:
            log.info(" **** %s value $%x is negative" % (self.name, v))
            v = 0x100 + v
            log.info(" **** Value %s (8-bit) wrap around to $%x" % (self.name, v))
        self.value = v
        return self.value # e.g.: r = operand.set(a + 1)
    def __str__(self):
        return "%s=%02x" % (self.name, self.value)


class ValueStorage16Bit(ValueStorage):
    def set(self, v):
        if v > 0xffff:
            log.info(" **** Value $%x is to big for %s (16-bit)" % (v, self.name))
            v = v & 0xffff
            log.info(" ^^^^ Value %s (16-bit) wrap around to $%x" % (self.name, v))
        elif v < 0:
            log.info(" **** %s value $%x is negative" % (self.name, v))
            v = 0x10000 + v
            log.info(" **** Value %s (16-bit) wrap around to $%x" % (self.name, v))
        self.value = v
        return self.value # e.g.: r = operand.set(a + 1)
    def __str__(self):
        return "%s=%04x" % (self.name, self.value)



def _register_bit(key):
    def set_flag(self, value):
        assert value in (0, 1)
        self._register[key] = value
    def get_flag(self):
        return self._register[key]
    return property(get_flag, set_flag)


def cc_value2txt(status):
    """
    >>> cc_value2txt(0x50)
    '.F.I....'
    >>> cc_value2txt(0x54)
    '.F.I.Z..'
    >>> cc_value2txt(0x59)
    '.F.IN..C'
    """
    return "".join(
        ["." if status & x == 0 else char for char, x in zip("EFHINZVC", (128, 64, 32, 16, 8, 4, 2, 1))]
    )


class ConditionCodeRegister(object):
    """ CC - 8 bit condition code register bits """

    def __init__(self, *cmd_args, **kwargs):
        self.name = "CC"
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

    @property
    def get_info(self):
        return cc_value2txt(self.get())

    ####

    def set_H8(self, a, b, r):
        self.H = 1 if (a ^ b ^ r) & 0x10 else 0
        log.debug("\tSet H half-carry flag to %i: (%i ^ %i ^ %i) & 16 = %i" % (
            self.H, a, b, r, (a ^ b ^ r) & 0x10
        ))

    def set_Z8(self, r):
        self.Z = 1 if r & 0xff == 0 else 0

    def set_Z16(self, r):
        self.Z = 1 if r & 0xffff == 0 else 0

    def set_N8(self, r):
#         self.N = 1 if signed8(r) < 0 else 0
        self.N = 1 if 127 < r < 256 else 0
        log.debug("\tSet N negative flag to %i: 127 < %i < 256 = %s" % (
            self.N, r, repr(127 < r < 256)
        ))

    def set_N16(self, r):
        self.N = 1 if signed16(r) < 0 else 0

    def set_C8(self, r):
        """
        Carry flag:
        CC.C = 0 - result in range 0-255
        CC.C = 1 - result out of range
        """
        if self.C == 0 and (r > 255 or r < 0):
            self.C = 1

        self.C = 1 if r & 0x100 else 0
        log.debug("\tSet C 8bit carry flag to %i: %i & 256 = %i" % (
            self.C, r, r & 0x100
        ))

    def set_C16(self, r):
        self.C = 1 if r & 0x10000 else 0

    def set_V8(self, a, b, r): # FIXME
#         if self.V == 0 and ((a ^ b ^ r ^ (r >> 1)) & 0x80):
#             self.V = 1
#         log.debug("\tSet V overflow flag to %i: ((%i ^ %i ^ %i ^ (%i >> 1)) & 128) = %i" % (
#             self.V, a, b, r, r, ((a ^ b ^ r ^ (r >> 1)) & 0x80)
#         ))
        if self.V == 0 and (r > 255 or r < 0):
            self.V = 1
        log.debug("\tSet V overflow flag to %i" % (
            self.V,
        ))

    def set_V16(self, a, b, r):
        if self.V == 0 and ((a ^ b ^ r ^ (r >> 1)) & 0x8000):
            self.V = 1

    ####

    def clear_NZVC(self):
        self.N = 0
        self.Z = 0
        self.V = 0
        self.C = 0

    def clear_HNZVC(self):
        self.H = 0
        self.N = 0
        self.Z = 0
        self.V = 0
        self.C = 0

    ####

    def update_NZ_8(self, r):
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

    def update_NZV_8(self, a, b, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.set_V8(a, b, r)

    def update_NZVC_8(self, a, b, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.set_V8(a, b, r)
        self.set_C8(r)

    def update_NZVC_16(self, a, b, r):
        self.set_N16(r)
        self.set_Z16(r)
        self.set_V16(a, b, r)
        self.set_C16(r)

    def update_HNZVC_8(self, a, b, r):
        self.set_H8(a, b, r)
        self.set_N8(r)
        self.set_Z8(r)
        self.set_V8(a, b, r)
        self.set_C8(r)


class ConcatenatedAccumulator(object):
    """
    6809 has register D - 16 bit concatenated reg. (A + B)
    """
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

    def __str__(self):
        return "%s=%04x" % (self.name, self.get())

# def get_6809_registers():
#
#     return d
