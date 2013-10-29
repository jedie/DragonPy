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
import struct

from Dragon32_mem_info import get_dragon_meminfo
from components.periphery_dragon import Dragon32Periphery
from components.periphery_simple6809 import Simple6809Periphery
from Simple6809.mem_info import get_simple6809_meminfo
from sbc09.mem_info import get_sbc09_meminfo
from sbc09.periphery import SBC09Periphery



class DummyMemInfo(object):
    def get_shortest(self, *args):
        return ">>mem info not active<<"
    def __call__(self, *args):
        return ">>mem info not active<<"


class AddressAreas(dict):
    """
    Hold information about memory address areas which accessed via bus.
    e.g.:
        Interrupt vectors
        Text screen
        Serial/parallel devices
    """
    def __init__(self, areas):
        super(AddressAreas, self).__init__()
        for start_addr, end_addr, txt in areas:
            self.add_area(start_addr, end_addr, txt)

    def add_area(self, start_addr, end_addr, txt):
        for addr in xrange(start_addr, end_addr + 1):
            dict.__setitem__(self, addr, txt)


class BaseConfig(object):

    # for sending a bytes/words via socket bus I/O:
    STRUCT_TO_PERIPHERY_FORMAT = (# For sending data to periphery
        "<" # little-endian byte order
        "I" # CPU cycles - unsigned int (integer with size: 4)
        "I" # op code address - unsigned int (integer with size: 4)
        "B" # action: 0 = read, 1 = write - unsigned char (integer with size: 1)
        "B" # structure: 0 = byte, 1 = word - unsigned char (integer with size: 1)
        "H" # Address - unsigned short (integer with size: 2)
        "H" # Bytes/Word to write - unsigned short (integer with size: 2)
    )
    BUS_ACTION_READ = 0
    BUS_ACTION_WRITE = 1
    BUS_STRUCTURE_BYTE = 0
    BUS_STRUCTURE_WORD = 1
    STRUCT_TO_PERIPHERY_LEN = struct.calcsize(STRUCT_TO_PERIPHERY_FORMAT)

    # Sending responses from periphery back to memory/cpu
    STRUCT_TO_MEMORY_FORMAT = "<H"
    STRUCT_MEMORY_LEN = struct.calcsize(STRUCT_TO_MEMORY_FORMAT)

    # How many ops should be execute before make a control server update cycle?
    BURST_COUNT = 10000

    def __init__(self, cmd_args):
        assert self.RAM_SIZE == (self.RAM_END - self.RAM_START) + 1
        assert self.ROM_SIZE == (self.ROM_END - self.ROM_START) + 1

        self.bus_addr_areas = AddressAreas(self.BUS_ADDR_AREAS)

        # socket address for internal bus I/O:
        if cmd_args.bus_socket_host and cmd_args.bus_socket_port:
            self.use_bus = True
            self.bus_socket_addr = (cmd_args.bus_socket_host, cmd_args.bus_socket_port)
        else:
            self.use_bus = False

        if cmd_args.ram:
            self.ram = cmd_args.ram
        else:
            self.ram = None

        if cmd_args.rom:
            self.rom = cmd_args.rom
        else:
            self.rom = self.DEFAULT_ROM

        self.verbosity = cmd_args.verbosity

        if cmd_args.max:
            self.max_cpu_cycles = cmd_args.max
        else:
            self.max_cpu_cycles = None

        if cmd_args.area_debug_active:
            # FIXME: How do this in a easier way?
            level, area = cmd_args.area_debug_active.split(":")
            level = int(level)
            start, end = area.split("-")
            start = start.strip()
            end = end.strip()
            start = int(start, 16)
            end = int(end, 16)
            self.area_debug = (level, start, end)
        else:
            self.area_debug = None

        self.area_debug_cycles = cmd_args.area_debug_cycles

        self.mem_info = DummyMemInfo()

    def _get_initial_Memory(self, size):
        return [0x00] * size

    def get_initial_RAM(self):
        return self._get_initial_Memory(self.RAM_SIZE)

    def get_initial_ROM(self):
        return self._get_initial_Memory(self.ROM_SIZE)


#     def get_initial_ROM(self):
#         start=cfg.ROM_START, size=cfg.ROM_SIZE
#         self.start = start
#         self.end = start + size
#         self._mem = [0x00] * size

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

    DEFAULT_ROM = "d32.rom"

    def __init__(self, cmd_args):
        super(Dragon32Cfg, self).__init__(cmd_args)

        if self.verbosity <= logging.INFO:
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

    RESET_VECTOR = 0xBFFE

    BUS_ADDR_AREAS = (
        (0xa000, 0xbfef, "RS232 interface"),
        (0xbff0, 0xbfff, "Interrupt vectors"),
    )

    DEFAULT_ROM = os.path.join("Simple6809", "ExBasROM.bin")

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        super(Simple6809Cfg, self).__init__(cmd_args)

#         if self.verbosity <= logging.INFO:
        self.mem_info = get_simple6809_meminfo()

        self.periphery_class = Simple6809Periphery


class SBC09Cfg(BaseConfig):
    """
    DragonPy config for Lennart's 6809 single board computer

        Buggy machine language monitor and rudimentary O.S. version 1.0

    More info read ./sbc09/README.creole
    """
    RAM_START = 0x0000
    RAM_END = 0x7FFF
    RAM_SIZE = 0x8000 # 32768 Bytes

    ROM_START = 0x8000
    ROM_END = 0xFFFF
    ROM_SIZE = 0x4000 # 16384 Bytes

    RESET_VECTOR = 0xFFFE

    BUS_ADDR_AREAS = (
        (0xe000, 0xe001, "RS232 interface"), # emulated serial port (ACIA)
        (0xFFF2, 0xFFFE, "Interrupt vectors"),
    )

    DEFAULT_ROM = os.path.join("sbc09", "sbc09", "v09.rom") # Source for this is monitor.asm

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        super(SBC09Cfg, self).__init__(cmd_args)

#         if self.verbosity <= logging.INFO:
        self.mem_info = get_sbc09_meminfo()

        self.periphery_class = SBC09Periphery


DEFAULT_CFG = Dragon32Cfg.__name__



def test_run():
    import sys, subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",

#         "--verbosity=5",
        "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL

#         "--cfg=Simple6809Cfg",
        "--cfg=SBC09Cfg",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd=".").wait()

if __name__ == "__main__":
    test_run()
