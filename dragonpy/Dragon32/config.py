# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import logging

from dragonpy.core.configs import BaseConfig

from dragonpy.Dragon32.periphery_dragon import Dragon32Periphery
from dragonpy.Dragon32.mem_info import get_dragon_meminfo


class Dragon32Cfg(BaseConfig):
    """
    see:
     * http://dragon32.info/info/memmap.html
     * http://dragon32.info/info/romref.html
    """
    RAM_START = 0x0000
#     RAM_END = 0x03FF # 1KB
#     RAM_END = 0x07FF # 2KB
    RAM_END = 0x0FFF # 4KB
    # RAM_END = 0x1FFF # 8KB
    # RAM_END = 0x3FFF # 16KB
    # RAM_END = 0x7FFF # 32KB

    ROM_START = 0x8000
    ROM_END = 0xBFFF
    ROM_SIZE = 0x4000 # 16384 Bytes

#     RESET_VECTOR = 0xB3B4 # RESET interrupt service routine (CoCo $a027)
#     RESET_VECTOR = 0xB3BA # Cold start routine - clears lo mem, inits BASIC
#     RESET_VECTOR = 0xB39B # Called after Hardware init routine, following a RESET Inits stack, checks for Cold/warm start
    RESET_VECTOR = 0xFFFE # RESET     ($b3b4; D64 64K mode $c000 - never accessed)
#     RESET_VECTOR = 0xFFFC

    BUS_ADDR_AREAS = (
        # TODO: Add all devices!
        (0xff00, 0xff04, "PIA 0 (Peripheral Interface Adaptor MC6821)"),
        (0xff04, 0xff07, "D64 ACIA serial port"),
        (0xff20, 0xff23, "PIA 1 (Peripheral Interface Adaptor MC6821)"),
        (0xffc0, 0xffdf, "SAM (Synchronous Address Multiplexer MC6883)"),
        (0xc000, 0xfeff, "DOS ROM / cartridge expansion port"),
        (0xfff0, 0xffff, "Interrupt vectors"),
    )

    DEFAULT_ROM = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "d32.rom"
    )

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        self.RAM_SIZE = (self.RAM_END - self.RAM_START) + 1
        super(Dragon32Cfg, self).__init__(cmd_args)

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


