"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect


class BaseConfig(object):
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
    max Memory is 64KB ($FFFF Bytes)

    32 kB RAM ($0000-$7FFF)
    16 kB ROM ($8000-$BFFF)
    ~16 kB free/reseved ($C000-$FEFF)
    $FF00-$FFFF 6883-SAM / PIA
    """
    RAM_START = 0x0000
    RAM_END = 0x7FFF
    RAM_SIZE = 0x7FFF # 32767 Bytes

    ROM_START = 0x8000
    ROM_END = 0xBFFF
    ROM_SIZE = 0x3FFF # 16383 Bytes

    STACK_PAGE = 0x100

    # see http://dragon32.info/info/romref.html

#     RESET_VECTOR = 0xB3B4 # RESET interrupt service routine (CoCo $a027)
    RESET_VECTOR = 0xB3BA # Cold start routine - clears lo mem, inits BASIC
#     RESET_VECTOR = 0xB39B # Called after Hardware init routine, following a RESET Inits stack, checks for Cold/warm start

    def __init__(self):
        self.rom = "d32.rom"
        self.ram = None
        self.bus = None
        self.pc = None

        assert self.RAM_SIZE == (self.RAM_END - self.RAM_START)
        assert self.ROM_SIZE == (self.ROM_END - self.ROM_START)



if __name__ == "__main__":
    cfg = Dragon32Cfg()
    cfg.print_debug_info()
