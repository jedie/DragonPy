#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonpy.Dragon32.basic_tokens import BASIC_TOKENS
from dragonpy.utils.logging_utils import log


class BasicLine(object):
    def __init__(self, basic_token_dict, line_number, line_code):
        self.basic_token_dict = basic_token_dict
        self.line_number = line_number
        self.line_code = line_code
    
    def token2ascii(self, value):
        try:
            result = self.basic_token_dict[value]
        except KeyError:
            result = chr(value)
        return result
    
    def get_ascii(self, code=None):
        if code is None: # start
            code = self.line_code
            
        line = "%i " % self.line_number
        old_value=None
        for value in code:
            if value == 0xff:
                old_value=value
                continue
            if old_value is not None:
                value = (old_value << 8) + value
                old_value = None
            line += self.token2ascii(value)
        return line
    
    def debug_line(self):
        log.critical(self.get_ascii())

class BasicListing(object):
    def __init__(self, basic_token_dict):
        self.basic_token_dict = basic_token_dict
        self.lines = []

    def load_from_dump(self, dump, program_start, program_end):
        log.critical("progam start $%04x - end $%04x", program_start, program_end)
        next_address = (dump[0] << 8) + dump[1]
        log.critical("next_address: $%04x", next_address)
        if next_address == 0x0000:
            # program end
            return
        line_number = (dump[2] << 8) + dump[3]
        log.critical("line_number: %i", line_number)
        length = next_address - program_start
        log.critical("length: %i", length)
        line_code = dump[4:length]
        log.critical("line_code: %s", ",".join(["$%02x" % i for i in line_code]))
        
        self.lines.append(
            BasicLine(self.basic_token_dict, line_number, line_code)
        )
        self.load_from_dump(dump[length:], next_address, program_end)

    def get_ascii(self):
        listing = []
        for line in self.lines:
            listing.append(line.get_ascii())
        return listing

    def debug_listing(self):
        for line in self.lines:
            line.debug_line()


if __name__ == "__main__":
    from dragonpy.Dragon32.config import Dragon32Cfg
    
    listing = BasicListing(Dragon32Cfg.BASIC_TOKENS)

    
    program_start=0x1e01
    program_end=0x1e12

    """
    10 CLS
    20 FOR I = 0 TO 255:
    30 POKE 1024+(I*2),I
    40 NEXT I
    50 I$ = INKEY$:IF I$="" THEN 50
    """
    dump = (0x1e, 0x07, 0x00, 0x0a, 0xa0, 0x00, 0x1e, 0x1a, 0x00, 0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a, 0x00, 0x1e, 0x2d, 0x00, 0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49, 0x00, 0x1e, 0x35, 0x00, 0x28, 0x8b, 0x20, 0x49, 0x00, 0x1e, 0x4e, 0x00, 0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00, 0x00, 0x00)

    listing.load_from_dump(dump, program_start, program_end)
    listing.debug_listing()
