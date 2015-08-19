#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging

log=logging.getLogger(__name__)
from dragonpy.Dragon32.periphery_dragon import Dragon32Periphery


class CoCoPeriphery(Dragon32Periphery):
    """
    Some documentation links:

    http://www.cs.unc.edu/~yakowenk/coco/text/history.html
    http://sourceforge.net/p/toolshed/code/ci/default/tree/cocoroms/bas.asm
    http://www.lomont.org/Software/Misc/CoCo/Lomont_CoCoHardware_2.pdf
    """
    def __init__(self, cfg, cpu, memory, display_callback, user_input_queue):
        super(CoCoPeriphery, self).__init__(cfg, cpu, memory, display_callback, user_input_queue)
#         self.read_byte_func_map.update({
#             0xc000: self.no_dos_rom,
#         })
        self.memory.add_read_word_callback(self.read_NMI, 0xfffc)
        self.memory.add_write_word_callback(self.write_word_info, 0xfffc)
        self.memory.add_write_word_callback(self.write_word_info, 0xfffe)

    def read_NMI(self, cpu_cycles, op_address, address):
        log.critical("%04x| TODO: read NMI" % op_address)
        return 0x0000

    def write_word_info(self, cpu_cycles, op_address, address, value):
        log.critical("%04x| write word $%04x to $%04x ?!?!" % (
            op_address, value, address
        ))


#------------------------------------------------------------------------------


