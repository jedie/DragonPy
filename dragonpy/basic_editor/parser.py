#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import re

from dragonpy.Dragon32.basic_tokens import BASIC_TOKENS
from dragonpy.utils.logging_utils import log


class BasicTokenUtil(object):
    def __init__(self, basic_token_dict):
        self.basic_token_dict = basic_token_dict
        self.ascii2token_dict = dict([
            (code,token)
            for token,code in basic_token_dict.items()
        ])
        
        regex = "(%s)" % "|".join([
            re.escape(statement)
            for statement in self.basic_token_dict.values()
        ])
        print regex
        self.regex = re.compile(regex)
        
    def token2ascii(self, value):
        try:
            result = self.basic_token_dict[value]
        except KeyError:
            result = chr(value)
        return result
    
    def ascii2token(self, ascii_code, debug=False):
        log.critical(repr(ascii_code))
        parts = self.regex.split(ascii_code)
        log.critical(repr(parts))
        tokens = []
        for part in parts:
            if not part:
                continue

            if part in self.ascii2token_dict:
                new_token = self.ascii2token_dict[part]
                log.critical("\t%r -> %x", part, new_token)
                if new_token > 0xff:
                    tokens.append(new_token >> 8)
                    tokens.append(new_token & 0xff)
                else:
                    tokens.append(new_token)
            else:
                new_tokens = [ord(char) for char in part]
                log.critical("\t%s -> %s", repr(part),
                    ",".join(["$%02x" % t for t in new_tokens])
                )
                tokens += new_tokens
        return tokens

class BasicLine(object):
    def __init__(self, token_util):
        self.token_util=token_util
        self.line_number=None
        self.line_code=None
    
    def token_load(self, line_number, tokens):
        self.line_number = line_number
        assert tokens[-1] == 0x00, "line code %s doesn't ends with \\x00: %s" % (
            repr(tokens), repr(tokens[-1])
        )
        self.line_code = tokens[:-1] # rstrip \x00        
    
    def ascii_load(self, line_ascii):
        line_number, ascii_code = line_ascii.split(" ", 1)
        self.line_number = int(line_number)
        self.line_code = self.token_util.ascii2token(ascii_code)   
    
    def get_tokens(self):
        return tuple(
            [self.line_number, ord(" ")] + self.line_code + [0x00]
        )

    def get_ascii(self, code=None, debug=False):
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
            code = self.token_util.token2ascii(value)
            if debug:
                log.critical("\t%s -> %s", hex(value), repr(code))
            line += code
        return line
    
    def debug_line(self):
        log.critical(self.get_ascii(debug=True))


class BasicListing(object):
    def __init__(self, basic_token_dict):
        self.token_util = BasicTokenUtil(basic_token_dict)
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
        tokens = dump[4:length]
        log.critical("tokens: %s", ",".join(["$%02x" % i for i in tokens]))
        
        basic_line = BasicLine(self.token_util)
        basic_line.token_load(line_number, tokens)
        self.lines.append(basic_line)
        
        self.load_from_dump(dump[length:], next_address, program_end)

    def get_ascii(self):
        listing = []
        for line in self.lines:
            listing.append(line.get_ascii())
        return listing

    def parse_ascii(self, txt):
        for line in txt.splitlines():
            basic_line = BasicLine(self.token_util)
            basic_line.ascii_load(line)
            self.lines.append(basic_line)

    def debug_listing(self):
        for line in self.lines:
            line.debug_line()


if __name__ == "__main__":
    from dragonpy.Dragon32.config import Dragon32Cfg
    
    listing = BasicListing(Dragon32Cfg.BASIC_TOKENS)

    program_start=0x1e01
    program_end=0x1e12
    dump = (0x1e, 0x07, 0x00, 0x0a, 0xa0, 0x00, 0x1e, 0x1a, 0x00, 0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a, 0x00, 0x1e, 0x2d, 0x00, 0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49, 0x00, 0x1e, 0x35, 0x00, 0x28, 0x8b, 0x20, 0x49, 0x00, 0x1e, 0x4e, 0x00, 0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00, 0x00, 0x00)
#    listing.load_from_dump(dump, program_start, program_end)
#    listing.debug_listing()

    txt = """\
10 CLS ' FOR I = 0 TO 255:
20 FOR I = 0 TO 255:
30 POKE 1024+(I*2),I
40 NEXT I
50 I$ = INKEY$:IF I$="" THEN 50"""
    listing.parse_ascii(txt)
    listing.debug_listing()
