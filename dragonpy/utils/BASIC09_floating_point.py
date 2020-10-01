#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import decimal
import math

from dragonlib.utils.byte_word_values import signed16, unsigned8


class BASIC09FloatingPoint:
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
        for __ in range(byte_count):
            current_byte = 0
            for bit_no in reversed(list(range(8))):
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
        print(f"Float value was: {self.value}")
        print(f"\texponent......: dez.: {self.exponent} hex: ${self.exponent:02x}")
        print(f"\texponent byte.: dez.: {self.exponent_byte} hex: ${self.exponent_byte:02x}")
        print(f"\tmantissa value: dez.: {self.mantissa}")
        print("\tmantissa bytes: dez.: {} hex: {}".format(
            repr(self.mantissa_bytes),
            ", ".join(["$%02x" % i for i in self.mantissa_bytes])
        ))
        print(f"\tmatissa-sign..: hex: ${self.mantissa_sign:02x}")
        byte_list = self.get_bytes()
        print(f"\tbinary........: hex: {', '.join([('$%02x' % i) for i in byte_list])}")
        print("\texponent |            mantissa             | mantissa-sign")
        print("\t" + " ".join(
            [f'{i:08b}' for i in byte_list]
        ))
        print()

    def __repr__(self):
        return f"<BinaryFloatingPoint {self.value:f}: {', '.join([('$%02x' % i) for i in self.get_bytes()])}>"


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
    areas += ["..."] + list(range(0x7f, 0x82))  # sign change in 8 Bit range
    areas += ["..."] + list(range(0xfe, 0x101))  # end of 8 Bit range
    areas += ["..."] + list(range(0x7ffe, 0x8003))  # sign change in 16 Bit range
    areas += ["..."] + list(range(0xfffd, 0x10000))  # end of 16 Bit range

    for test_value in areas:
        if test_value == "...":
            print("\n...\n")
            continue
        fp = BASIC09FloatingPoint(test_value)
        print(f"${test_value:x} (dez.: {test_value}) -> {' '.join([('$%02x' % i) for i in fp.get_bytes()])}")
