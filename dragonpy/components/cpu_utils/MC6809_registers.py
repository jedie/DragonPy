#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    some code is borrowed from:
    XRoar emulator by Ciaran Anscomb (GPL license) more info, see README

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from dragonpy.utils.humanize import cc_value2txt
import logging

log=logging.getLogger(__name__)


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


class UndefinedRegister(ValueStorage):
    # used in TFR and EXG
    WIDTH = 16 # 16 Bit
    name = "undefined!"
    value = 0xffff
    def __init__(self):
        pass
    def set(self, v):
        log.warning("Set value to 'undefined' register!")
        pass

    def get(self):
        return 0xffff


class ValueStorage8Bit(ValueStorage):
    WIDTH = 8 # 8 Bit

    def set(self, v):
        if v > 0xff:
#            log.info(" **** Value $%x is to big for %s (8-bit)", v, self.name)
            v = v & 0xff
#            log.info(" ^^^^ Value %s (8-bit) wrap around to $%x", self.name, v)
        elif v < 0:
#            log.info(" **** %s value $%x is negative", self.name, v)
            v = 0x100 + v
#            log.info(" **** Value %s (8-bit) wrap around to $%x", self.name, v)
        self.value = v
        return self.value # e.g.: r = operand.set(a + 1)
    def __str__(self):
        return "%s=%02x" % (self.name, self.value)


class ValueStorage16Bit(ValueStorage):
    WIDTH = 16 # 16 Bit

    def set(self, v):
        if v > 0xffff:
#            log.info(" **** Value $%x is to big for %s (16-bit)", v, self.name)
            v = v & 0xffff
#            log.info(" ^^^^ Value %s (16-bit) wrap around to $%x", self.name, v)
        elif v < 0:
#            log.info(" **** %s value $%x is negative", self.name, v)
            v = 0x10000 + v
#            log.info(" **** Value %s (16-bit) wrap around to $%x", self.name, v)
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


class ConditionCodeRegister(object):
    """ CC - 8 bit condition code register bits """

    WIDTH = 8 # 8 Bit

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
        """
        >>> cc=ConditionCodeRegister()
        >>> cc.set(0xa1)
        >>> cc.get_info
        'E.H....C'
        """
        return cc_value2txt(self.get())

    def __str__(self):
        return "%s=%s" % (self.name, self.get_info)

    ####

    """
    #define SET_Z(r)          ( REG_CC |= ((r) ? 0 : CC_Z) )
    #define SET_N8(r)         ( REG_CC |= (r&0x80)>>4 )
    #define SET_N16(r)        ( REG_CC |= (r&0x8000)>>12 )
    #define SET_H(a,b,r)      ( REG_CC |= ((a^b^r)&0x10)<<1 )
    #define SET_C8(r)         ( REG_CC |= (r&0x100)>>8 )
    #define SET_C16(r)        ( REG_CC |= (r&0x10000)>>16 )
    #define SET_V8(a,b,r)     ( REG_CC |= ((a^b^r^(r>>1))&0x80)>>6 )
    #define SET_V16(a,b,r)    ( REG_CC |= ((a^b^r^(r>>1))&0x8000)>>14 )
    """

    def set_H(self, a, b, r):
        if self.H == 0:
            r2 = (a ^ b ^ r) & 0x10
            self.H = 0 if r2 == 0 else 1
#            log.debug("\tset_H(): set half-carry flag to %i: ($%02x ^ $%02x ^ $%02x) & 0x10 = $%02x",
#                self.H, a, b, r, r2
#            )
#        else:
#            log.debug("\rset_H(): leave old value 1")

    def set_Z8(self, r):
        if self.Z == 0:
            r2 = r & 0xff
            self.Z = 1 if r2 == 0 else 0
#            log.debug("\tset_Z8(): set zero flag to %i: $%02x & 0xff = $%02x",
#                self.Z, r, r2
#            )
#        else:
#            log.debug("\tset_Z8(): leave old value 1")

    def set_Z16(self, r):
        if self.Z == 0:
            r2 = r & 0xffff
            self.Z = 1 if r2 == 0 else 0
#            log.debug("\tset_Z16(): set zero flag to %i: $%04x & 0xffff = $%04x",
#                self.Z, r, r2
#            )
#        else:
#            log.debug("\tset_Z16(): leave old value 1")

    def set_N8(self, r):
        if self.N == 0:
            r2 = r & 0x80
            self.N = 0 if r2 == 0 else 1
#            log.debug("\tset_N8(): set negative flag to %i: ($%02x & 0x80) = $%02x",
#                self.N, r, r2
#            )
#        else:
#            log.debug("\tset_N8(): leave old value 1")

    def set_N16(self, r):
        if self.N == 0:
            r2 = r & 0x8000
            self.N = 0 if r2 == 0 else 1
#            log.debug("\tset_N16(): set negative flag to %i: ($%04x & 0x8000) = $%04x",
#                self.N, r, r2
#            )
#        else:
#            log.debug("\tset_N16(): leave old value 1")

    def set_C8(self, r):
        if self.C == 0:
            r2 = r & 0x100
            self.C = 0 if r2 == 0 else 1
#            log.debug("\tset_C8(): carry flag to %i: ($%02x & 0x100) = $%02x",
#                self.C, r, r2
#            )
#         else:
#            log.debug("\tset_C8(): leave old value 1")

    def set_C16(self, r):
        if self.C == 0:
            r2 = r & 0x10000
            self.C = 0 if r2 == 0 else 1
#            log.debug("\tset_C16(): carry flag to %i: ($%04x & 0x10000) = $%04x",
#                self.C, r, r2
#            )
#         else:
#            log.debug("\tset_C16(): leave old value 1")

    def set_V8(self, a, b, r):
        if self.V == 0:
            r2 = (a ^ b ^ r ^ (r >> 1)) & 0x80
            self.V = 0 if r2 == 0 else 1
#            log.debug("\tset_V8(): overflow flag to %i: (($%02x ^ $%02x ^ $%02x ^ ($%02x >> 1)) & 0x80) = $%02x",
#                self.V, a, b, r, r, r2
#            )
#         else:
#            log.debug("\tset_V8(): leave old value 1")

    def set_V16(self, a, b, r):
        if self.V == 0:
            r2 = (a ^ b ^ r ^ (r >> 1)) & 0x8000
            self.V = 0 if r2 == 0 else 1
#            log.debug("\tset_V16(): overflow flag to %i: (($%04x ^ $%04x ^ $%04x ^ ($%04x >> 1)) & 0x8000) = $%04x",
#                self.V, a, b, r, r, r2
#            )
#         else:
#            log.debug("\tset_V16(): leave old value 1")

    ####

    def clear_NZ(self):
#        log.debug("\tclear_NZ()")
        self.N = 0
        self.Z = 0

    def clear_NZC(self):
#        log.debug("\tclear_NZC()")
        self.N = 0
        self.Z = 0
        self.C = 0

    def clear_NZV(self):
#        log.debug("\tclear_NZV()")
        self.N = 0
        self.Z = 0
        self.V = 0

    def clear_NZVC(self):
#        log.debug("\tclear_NZVC()")
        self.N = 0
        self.Z = 0
        self.V = 0
        self.C = 0

    def clear_HNZVC(self):
#        log.debug("\tclear_HNZVC()")
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

    def update_NZ_16(self, r):
        self.set_N16(r)
        self.set_Z16(r)

    def update_NZ0_8(self, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.V = 0

    def update_NZ0_16(self, r):
        self.set_N16(r)
        self.set_Z16(r)
        self.V = 0

    def update_NZC_8(self, r):
        self.set_N8(r)
        self.set_Z8(r)
        self.set_C8(r)

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
        self.set_H(a, b, r)
        self.set_N8(r)
        self.set_Z8(r)
        self.set_V8(a, b, r)
        self.set_C8(r)


class ConcatenatedAccumulator(object):
    """
    6809 has register D - 16 bit concatenated reg. (A + B)
    """
    WIDTH = 16 # 16 Bit

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


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
