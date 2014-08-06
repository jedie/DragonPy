#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.utils.logging_utils import log

class DragonTextDisplayBase(object):
    """
    Every stuff with is GUI independent.

    Text mode:
    32 rows x 16 columns
    """
    def __init__(self, memory):
        self.memory = memory
        
        self.charmap = get_charmap_dict()
        self.rows = 32
        self.columns = 16

        self.display_offset = 0x0400
        self.display_ram = [None] * self.display_offset # empty Offset
        self.display_ram += [0x00] * (0x200+1)
        
        self.memory.add_read_byte_callback(self.read_byte, 0x0400, 0x0600)
        self.memory.add_read_word_callback(self.read_word, 0x0400, 0x0600)
        self.memory.add_write_byte_callback(self.write_byte, 0x0400, 0x0600)
        self.memory.add_write_word_callback(self.write_word, 0x0400, 0x0600)

    def read_byte(self, cpu_cycles, op_address, address):
        value = self.display_ram[address]
#         char, color = self.charmap[value]
#         log.critical(
#             "%04x| *** Display read $%02x ***%s*** %s from $%04x",
#             op_address, value, repr(char), color, address
#         )
        return value

    def read_word(self, cpu_cycles, op_address, address):
        # 6809 is Big-Endian
        return self.display_ram[address + 1] + (self.display_ram[address] << 8)

    def write_byte(self, cpu_cycles, op_address, address, value):
        char, color = self.charmap[value]
#         log.critical(
#             "%04x| *** Display write $%02x ***%s*** %s at $%04x",
#             op_address, value, repr(char), color, address
#         )
        self.render_char(char, color, address)
        self.display_ram[address] = value

    def write_word(self, cpu_cycles, op_address, address, value):
        # 6809 is Big-Endian
        self.write_byte(cpu_cycles, op_address, address, value >> 8)
        self.write_byte(cpu_cycles, op_address, address + 1, value & 0xff)

