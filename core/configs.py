# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect
import struct

class ConfigDict(dict):
    DEFAULT = None
    def register(self, name, cls, default=False):
        dict.__setitem__(self, name, cls)
        if default:
            assert self.DEFAULT is None
            self.DEFAULT = name

configs = ConfigDict()



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

    # XXX: use multiprocessing send instead of struct
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

    # http address/port number for the CPU control server
    CPU_CONTROL_ADDR = "127.0.0.1"
    CPU_CONTROL_PORT = 6809

    # How many ops should be execute before make a control server update cycle?
    BURST_COUNT = 10000

    def __init__(self, cmd_args):
        assert self.RAM_SIZE == (self.RAM_END - self.RAM_START) + 1
        assert self.ROM_SIZE == (self.ROM_END - self.ROM_START) + 1

        self.bus_addr_areas = AddressAreas(self.BUS_ADDR_AREAS)

        # print CPU cycle/sec while running
        self.display_cycle = cmd_args.display_cycle

        # Compare with XRoar/v09 trace file? (see README)
        self.compare_trace = cmd_args.compare_trace

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

#         "--cfg=Simple6809",
        "--cfg=sbc09",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd=".").wait()

if __name__ == "__main__":
    test_run()
