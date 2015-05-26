
"""
    VectrexPy - Vectrex emulator in Python
    =======================================

    :copyleft: 2013-2014 by the VectrexPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from MC6809.core.memory_info import BaseMemoryInfo
from dragonpy.utils.humanize import nice_hex
import logging

log=logging.getLogger(__name__)


class VectrexMemInfo(BaseMemoryInfo):
    MEM_INFO = (
        # TODO: Add info from:
        # * http://www.playvectrex.com/designit/chrissalo/appendixa.htm#Other
        # * http://www.playvectrex.com/designit/chrissalo/appendixb.htm

        (0x0000, 0x7FFF , "Cartridge ROM"),
        (0x8000, 0xC7FF , "Unmapped space"),
        (0xC800, 0xCFFF , "RAM"),
        (0xD000, 0xD7FF , "6522 interface adapter"),
        (0xD800, 0xDFFF , "6522 / RAM ?!?"),
        (0xE000, 0xEFFF , "ROM - builtin Mine storm game"),
        (0xF000, 0xFFFF , "ROM - vectrex BIOS Executive"),

        (0xbff0, 0xbfff, "6809 interrupt vectors mapped to $fff0-$ffff by SAM"),
        (0xbff0, 0xfff1, "Reserved     ($0000)"),
        (0xbff2, 0xbff3, "SWI3 vector  ($0100)"),
        (0xbff4, 0xbff5, "SWI2 vector  ($0103)"),
        (0xbff6, 0xbff7, "FIRQ vector  ($010f)"),
        (0xbff8, 0xbff9, "IRQ vector   ($010c)"),
        (0xbffa, 0xbffb, "SWI vector   ($0106)"),
        (0xbffc, 0xbffd, "NMI vector   ($0109)"),
        (0xbffe, 0xbfff, "RESET vector ($b3b4)"),
    )


def print_out(txt):
    print(txt)


def get_vectrex_meminfo():
    return VectrexMemInfo(log.debug)


if __name__ == "__main__":
#     mem_info = VectrexMemInfo(print_out)
#
#     # 0xaf-0xaf - TRON/TROFF trace flag - non zero for TRON
#     mem_info(0xaf)
#     mem_info(0xaf, shortest=False)
#     print
#
#     # 5x entries
#     mem_info(0xbff0)
#     mem_info(0xbff0, shortest=False)
#     print
#
#     # 0xf-0x18 - Temporary results
#     mem_info(0xf)
#     mem_info(0xf, shortest=False)
#     print
#     mem_info(0x10)
#     mem_info(0x10, shortest=False)
#     print
#     mem_info(0x18)
#     mem_info(0x18, shortest=False)
#     print
#
#     print "\n --- END --- \n"
    for s, e, txt in VectrexMemInfo.MEM_INFO:
        if s == e:
            addr = nice_hex(s)
        else:
            addr = "%s-%s" % (nice_hex(s), nice_hex(e))

        print("%-11s ; %s" % (addr, txt))
