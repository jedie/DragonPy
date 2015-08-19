#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy
    ========

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import os
import sys

import logging

log=logging.getLogger(__name__)
from dragonpy.components.periphery import PeripheryBase
from dragonpy.vectrex.MOS6522 import MOS6522VIA


class VectrexPeripheryBase(PeripheryBase):
    """
    GUI independent stuff
    """
    def __init__(self, cfg, memory, user_input_queue):
        super(VectrexPeripheryBase, self).__init__(cfg, memory, user_input_queue)

        self.via = MOS6522VIA(cfg, memory)

        # $0000 - $7FFF Cartridge ROM
        self.memory.add_read_byte_callback(self.cartridge_rom, 0xC000)
        self.memory.add_read_word_callback(self.cartridge_rom, 0xC000)

        self.running = True

    def cartridge_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: $0000 - $7FFF Cartridge ROM. Send 0x00 back", op_address)
        return 0x00

#     def update(self, cpu_cycles):
#         #        log.critical("update pygame")
#         if not self.running:
#             return
#         if self.speaker:
#             self.speaker.update(cpu_cycles)


class VectrexPeriphery(VectrexPeripheryBase):
    def __init__(self, cfg, memory, display_queue, user_input_queue):
        super(VectrexPeriphery, self).__init__(cfg, memory, user_input_queue)

        # redirect writes to display RAM area 0x0400-0x0600 into display_queue:
        #DragonDisplayOutputHandler(display_queue, memory)

#------------------------------------------------------------------------------


