#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - Humanize
    ===================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals



def byte2bit_string(data):
    """
    >>> byte2bit_string(0x1b)
    '00011011'
    """
    return '{0:08b}'.format(data)


def nice_hex(v):
    """
    >>> nice_hex(0x1)
    '$01'
    >>> nice_hex(0x123)
    '$0123'
    """
    if v < 0x100:
        return "$%02x" % v
    if v < 0x10000:
        return "$%04x" % v
    return "$%x" % v


def hex_repr(d):
    """
    >>> hex_repr({"A":0x1,"B":0xabc})
    'A=$01 B=$0abc'
    """
    txt = []
    for k, v in sorted(d.items()):
        if isinstance(v, int):
            txt.append("%s=%s" % (k, nice_hex(v)))
        else:
            txt.append("%s=%s" % (k, v))
    return " ".join(txt)


def cc_value2txt(status):
    """
    >>> cc_value2txt(0x50)
    '.F.I....'
    >>> cc_value2txt(0x54)
    '.F.I.Z..'
    >>> cc_value2txt(0x59)
    '.F.IN..C'
    """
    return "".join([
        "." if status & x == 0 else char
        for char, x in zip("EFHINZVC", (128, 64, 32, 16, 8, 4, 2, 1))
    ])


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(verbose=0))
