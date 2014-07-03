# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from dragonpy.core.configs import BaseConfig
from dragonpy.Simple6809.mem_info import get_simple6809_meminfo
from dragonpy.Simple6809.periphery_simple6809 import Simple6809Periphery


class Simple6809Cfg(BaseConfig):
    """
    DragonPy config for Grant Searle's Simple 6809 design
    More info read ./Simple6809/README.creole
    """
    RAM_START = 0x0000
    RAM_END = 0x03FF # 1KB
    # RAM_END = 0x07FF # 2KB
    # RAM_END = 0x0FFF # 4KB
    # RAM_END = 0x1FFF # 8KB
    # RAM_END = 0x3FFF # 16KB
    # RAM_END = 0x7FFF # 32KB

    ROM_START = 0xC000
    ROM_END = 0xFFFF
    ROM_SIZE = 0x4000 # 16384 Bytes

    RESET_VECTOR = 0xBFFE

    BUS_ADDR_AREAS = (
        (0xa000, 0xbfef, "RS232 interface"),
        (0xbff0, 0xbfff, "Interrupt vectors"),
    )

    DEFAULT_ROM = os.path.join("Simple6809", "ExBasROM.bin")

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        self.RAM_SIZE = (self.RAM_END - self.RAM_START) + 1
        super(Simple6809Cfg, self).__init__(cmd_args)

#         if self.verbosity <= logging.INFO:
        self.mem_info = get_simple6809_meminfo()

        self.periphery_class = Simple6809Periphery


