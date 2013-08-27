
"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


class CfgDragon32(object):
    """
    Der maximal von der CPU adressierbare Speicherbereich von 64 kB (hexadezimal: $FFFF Bytes) unterteilt sich beim
    Dragon 32 im Wesentlichen in vier verschiedene Sektionen:
    32 kB RAM ($0000-$7FFF),
    16 kB ROM ($8000-$BFFF), ein etwa
    16 kB umfassender freier Speicherblock ($C000-$FEFF) und
    Sonderspeicher mit u.a. Hardwareregistern des 6883-SAM und der beiden PIAs ($FF00-$FFFF).
    """
    RAM_START = 0x0000
    RAM_SIZE = 0x7FFF
    RAM_END = RAM_START + RAM_SIZE

    ROM_START = 0x8000
    ROM_SIZE = 0x4000
    ROM_END = ROM_START + ROM_SIZE
