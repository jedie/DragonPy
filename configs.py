"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect
import logging
import os

from Dragon32_mem_info import get_dragon_meminfo
from components.periphery_dragon import get_dragon_periphery
from components.periphery_simple6809 import get_simple6809_periphery

class DummyMemInfo(object):
    def get_shortest(self, *args):
        pass


class BaseConfig(object):
    def __init__(self, cmd_args):
        assert self.RAM_SIZE == (self.RAM_END - self.RAM_START) + 1
        assert self.ROM_SIZE == (self.ROM_END - self.ROM_START) + 1

        self.bus = cmd_args.bus
        if cmd_args.ram:
            self.ram = cmd_args.ram
        else:
            self.ram = None

        if cmd_args.rom:
            self.rom = cmd_args.rom
        else:
            self.rom = self.DEFAULT_ROM

        if cmd_args.pc:
            self.pc = cmd_args.pc
        else:
            self.pc = None

        self.verbosity = cmd_args.verbosity

        self.mem_info = DummyMemInfo()

    def print_debug_info(self):
        print "Config: '%s'" % self.__class__.__name__

        for name, value in inspect.getmembers(self): # , inspect.isdatadescriptor):
            if name.startswith("_"):
                continue
#             print name, type(value)
            if not isinstance(value, (int, basestring, list, tuple, dict)):
                continue
            if isinstance(value, (int,)):
                print "%20s = %-6s in hex: %7s" % (
                    name, value, hex(value)
                )
            else:
                print "%20s = %s" % (name, value)


class Dragon32Cfg(BaseConfig):
    """
    see:
     * http://dragon32.info/info/memmap.html
     * http://dragon32.info/info/romref.html
    """
    RAM_START = 0x0000
    RAM_END = 0x7FFF
    RAM_SIZE = 0x8000 # 32768 Bytes

    ROM_START = 0x8000
    ROM_END = 0xBFFF
    ROM_SIZE = 0x4000 # 16384 Bytes

    RESET_VECTOR = 0xB3B4 # RESET interrupt service routine (CoCo $a027)
#     RESET_VECTOR = 0xB3BA # Cold start routine - clears lo mem, inits BASIC
#     RESET_VECTOR = 0xB39B # Called after Hardware init routine, following a RESET Inits stack, checks for Cold/warm start
#     RESET_VECTOR = 0xFFFE # RESET     ($b3b4; D64 64K mode $c000 - never accessed)
#     RESET_VECTOR = 0xFFFC

    DEFAULT_ROM = "d32.rom"

    def __init__(self, cmd_args):
        super(Dragon32Cfg, self).__init__(cmd_args)

        if self.verbosity <= logging.DEBUG:
            self.mem_info = get_dragon_meminfo()

        self.periphery = get_dragon_periphery(self)


class Simple6809Cfg(BaseConfig):
    """
    DragonPy config for Grant Searle's Simple 6809 design
    More info read ./Simple6809/README.creole
    """
    RAM_START = 0x0000
    RAM_END = 0x7FFF
    RAM_SIZE = 0x8000 # 32768 Bytes

    ROM_START = 0xC000
    ROM_END = 0xFFFF
    ROM_SIZE = 0x4000 # 16384 Bytes

    RESET_VECTOR = 0x1bd8

    DEFAULT_ROM = os.path.join("Simple6809", "ExBasROM.bin")

    def __init__(self, cmd_args):
        super(Simple6809Cfg, self).__init__(cmd_args)

        self.periphery = get_simple6809_periphery(self)


DEFAULT_CFG = Dragon32Cfg.__name__


if __name__ == "__main__":
    cfg = Dragon32Cfg()
    cfg.print_debug_info()
