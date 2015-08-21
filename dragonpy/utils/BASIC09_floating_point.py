#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import six
xrange = six.moves.xrange

import math
import decimal

from dragonlib.utils.byte_word_values import unsigned8, signed16


class BASIC09FloatingPoint(object):
    """
    Calucalte the representation of a float value in the BASIC09
    FPA memory accumulator.

    exponent.........: 1Byte =   8 Bits
    mantissa/fraction: 4Bytes = 32 Bits
    sign of mantissa.: 1Byte =   8 Bits (0x00 positive, 0xff negative)

    exponent most significant bit is the sign: 1=positive 0=negative
    """
    def __init__(self, value):
        value = signed16(value)
        self.value = decimal.Decimal(value)
        self.mantissa, self.exponent = math.frexp(value)

        if self.value == 0:
            # As in BASIC09 Implementation (other wise exponent is $80)
            self.exponent_byte = 0x00
        else:
            self.exponent_byte = unsigned8(self.exponent - 128)

        if self.mantissa >= 0:
            self.mantissa_sign = 0x00
        else:
            self.mantissa_sign = 0xff
        self.mantissa_bytes = self.mantissa2bytes(self.mantissa)

    def mantissa2bytes(self, value, byte_count=4):
        value = decimal.Decimal(abs(value))
        result = []
        pos = 0
        for __ in xrange(byte_count):
            current_byte = 0
            for bit_no in reversed(range(8)):
                pos += 1
                bit_value = decimal.Decimal(1.0) / decimal.Decimal(2) ** decimal.Decimal(pos)
                if value >= bit_value:
                    value -= bit_value
                    current_byte += 2 ** bit_no
            result.append(current_byte)
        return result

    def get_bytes(self):
        return [self.exponent_byte] + self.mantissa_bytes + [self.mantissa_sign]

    def print_values(self):
        print("Float value was: %s" % self.value)
        print("\texponent......: dez.: %s hex: $%02x" % (self.exponent, self.exponent))
        print("\texponent byte.: dez.: %s hex: $%02x" % (
            self.exponent_byte, self.exponent_byte
        ))
        print("\tmantissa value: dez.: %s" % (self.mantissa))
        print("\tmantissa bytes: dez.: %s hex: %s" % (
            repr(self.mantissa_bytes),
            ", ".join(["$%02x" % i for i in self.mantissa_bytes])
        ))
        print("\tmatissa-sign..: hex: $%02x" % self.mantissa_sign)
        byte_list = self.get_bytes()
        print("\tbinary........: hex: %s" % (
            ", ".join(["$%02x" % i for i in byte_list])
        ))
        print("\texponent |            mantissa             | mantissa-sign")
        print("\t" + " ".join(
            ['{0:08b}'.format(i) for i in byte_list]
        ))
        print()

    def __repr__(self):
        return "<BinaryFloatingPoint %f: %s>" % (
            self.value, ", ".join(["$%02x" % i for i in self.get_bytes()])
        )


if __name__ == "__main__":
    # Examples:
#    BASIC09FloatingPoint(54).print_values()
#    BASIC09FloatingPoint(-54).print_values()
#    BASIC09FloatingPoint(5.5).print_values()
#    BASIC09FloatingPoint(-5.5).print_values()
#    BASIC09FloatingPoint(0).print_values()
#    BASIC09FloatingPoint(10.14 ** 38).print_values()
#    BASIC09FloatingPoint(10.14 ** -38).print_values()

#    areas = xrange(0x100)

#    areas = range(0, 3) + ["..."] + range(0x7e, 0x83) + ["..."] + range(0xfd, 0x100)

    # 16 Bit test values
    areas = list(range(0, 3))
    areas += ["..."] + list(range(0x7f, 0x82)) # sign change in 8 Bit range
    areas += ["..."] + list(range(0xfe, 0x101)) # end of 8 Bit range
    areas += ["..."] + list(range(0x7ffe, 0x8003)) # sign change in 16 Bit range
    areas += ["..."] + list(range(0xfffd, 0x10000)) # end of 16 Bit range

    for test_value in areas:
        if test_value == "...":
            print("\n...\n")
            continue
        fp = BASIC09FloatingPoint(test_value)
        print("$%x (dez.: %s) -> %s" % (
            test_value, test_value,
            " ".join(["$%02x" % i for i in fp.get_bytes()])
        ))
