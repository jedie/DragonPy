"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


class Dragon32Cfg(object):
    """
    max Memory is 64KB ($FFFF Bytes)

    32 kB RAM ($0000-$7FFF)
    16 kB ROM ($8000-$BFFF)
    ~16 kB free/reseved ($C000-$FEFF)
    $FF00-$FFFF 6883-SAM / PIA
    """
    RAM_START = 0x0000
    RAM_SIZE = 0x7FFF
    RAM_END = RAM_START + RAM_SIZE

    ROM_START = 0x8000
    ROM_SIZE = 0x4000
    ROM_END = ROM_START + ROM_SIZE

    def __init__(self):
        self.rom = "d32.rom"
        self.ram = None
        self.bus = None
        self.pc = None

