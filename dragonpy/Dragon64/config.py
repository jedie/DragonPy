# coding: utf-8

"""
    Dragon 64 config
    ================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import logging

from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon64.mem_info import get_dragon_meminfo
from dragonpy.Dragon32.periphery_dragon import Dragon32Periphery


class Dragon64Cfg(Dragon32Cfg):
    RAM_START = 0x0000
#     RAM_END = 0x07FF # 2KB
#     RAM_END = 0x0FFF # 4KB
#     RAM_END = 0x1FFF # 8KB
    RAM_END = 0x3FFF # 16KB
#     RAM_END = 0x7FFF # 32KB

    ROM_START = 0x8000
    ROM_END = 0xFFFF
    ROM_SIZE = 0x8000 # 32768 Bytes

    DEFAULT_ROM = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "d64.rom"
    )

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        self.RAM_SIZE = (self.RAM_END - self.RAM_START) + 1
        super(Dragon64Cfg, self).__init__(cmd_args)

        if self.verbosity <= logging.ERROR:
            self.mem_info = get_dragon_meminfo()

        self.periphery_class = Dragon32Periphery

    def get_initial_RAM(self):
        """
        init the Dragon RAM
        See: http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4444
        """
        mem_FF = [0xff for _ in xrange(4)]
        mem_00 = [0x00 for _ in xrange(4)]

        mem = []
        for _ in xrange(self.RAM_SIZE / 8):
            mem += mem_FF
            mem += mem_00

        return mem


config = Dragon64Cfg
