#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonlib.core.basic import BasicListing
from dragonlib.dragon32.basic_tokens import DRAGON32_BASIC_TOKENS
from dragonlib.utils.logging_utils import log


DRAGON32 = "Dragon32"


class BaseAPI(object):
    def program_dump2ascii_lines(self, dump, program_start=None):
        """
        convert a memory dump of a tokensized BASIC listing into
        ASCII listing list.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
        return self.listing.program_dump2ascii_lines(dump, program_start)

    def ascii_listing2program_dump(self, basic_program_ascii, program_start=None):
        """
        convert a ASCII BASIC program listing into tokens.
        This tokens list can be used to insert it into the
        Emulator RAM.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
        return self.listing.ascii_listing2program_dump(basic_program_ascii, program_start)


class Dragon32API(BaseAPI):
    CONFIG_NAME = DRAGON32
    MACHINE_NAME = "Dragon 32"
    BASIC_TOKENS = DRAGON32_BASIC_TOKENS
    
    # Default memory location of BASIC listing start
    DEFAULT_PROGRAM_START = 0x1e01

    def __init__(self):
        self.listing = BasicListing(self.BASIC_TOKENS)


if __name__ == "__main__":
    program_start = 0x1e01
    program_end = 0x1e12
    dump = (0x1e, 0x07, 0x00, 0x0a, 0xa0, 0x00, 0x1e, 0x1a, 0x00, 0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a, 0x00, 0x1e, 0x2d, 0x00, 0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49, 0x00, 0x1e, 0x35, 0x00, 0x28, 0x8b, 0x20, 0x49, 0x00, 0x1e, 0x4e, 0x00, 0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00, 0x00, 0x00)

    dragon32 = Dragon32API()
    print dragon32.program_dump2ascii_lines(dump)


#    listing.load_from_dump(dump, program_start, program_end)
#    listing.debug_listing()

    txt = """\
10 CLS ' FOR I = 0 TO 255:
20 FOR I = 0 TO 255:
30 POKE 1024+(I*2),I
40 NEXT I
50 I$ = INKEY$:IF I$="" THEN 50"""
    listing.ascii_listing2basic_lines(txt)
    listing.debug_listing()
