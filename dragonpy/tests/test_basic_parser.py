#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import unittest

from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.basic_editor.parser import BasicListing, BasicTokenUtil, BasicLine, \
    log_program_dump
from dragonpy.tests.test_base import BaseTestCase
from dragonpy.utils.logging_utils import log, setup_logging, log_hexlist


class Dragon32BasicLineTest(BaseTestCase):
    def setUp(self):
        super(Dragon32BasicLineTest, self).setUp()
        token_util = BasicTokenUtil(Dragon32Cfg.BASIC_TOKENS)
        self.basic_line = BasicLine(token_util)

    def test_tokens2ascii(self):
        self.basic_line.token_load(
            line_number=50,
            tokens=(0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00)
        )
        code = self.basic_line.get_ascii()
        self.assertEqual(code,
            '50 I$ = INKEY$:IF I$="" THEN 50'
        )

    def test_ascii2tokens01(self):
        self.basic_line.ascii_load('10 CLS')
        tokens = self.basic_line.get_tokens()
        self.assertHexList(tokens, [
            0x0a, # 10
            0xa0, # CLS
        ])

    def test_ascii2tokens02(self):
        self.basic_line.ascii_load('50 I$ = INKEY$:IF I$="" THEN 50')
        tokens = self.basic_line.get_tokens()
        self.assertHexList(tokens, [
            0x32, # 50
            # I$ = INKEY$:IF I$="" THEN 50
            0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30,
        ])

class Dragon32BasicParserTest(BaseTestCase):
    def setUp(self):
        super(Dragon32BasicParserTest, self).setUp()
        self.listing = BasicListing(Dragon32Cfg.BASIC_TOKENS)

    def test_tokens2ascii(self):
        program_start = 0x1e01
        program_end = 0x1e12
        dump = (0x1e, 0x07, 0x00, 0x0a, 0xa0, 0x00, 0x1e, 0x1a, 0x00, 0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a, 0x00, 0x1e, 0x2d, 0x00, 0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49, 0x00, 0x1e, 0x35, 0x00, 0x28, 0x8b, 0x20, 0x49, 0x00, 0x1e, 0x4e, 0x00, 0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00, 0x00, 0x00)
        self.listing.load_from_dump(dump, program_start, program_end)
        #self.listing.debug_listing()
        ascii_lines = self.listing.get_ascii()
        self.assertEqual(ascii_lines, [
            '10 CLS',
            '20 FOR I = 0 TO 255:',
            '30 POKE 1024+(I*2),I',
            '40 NEXT I',
            '50 I$ = INKEY$:IF I$="" THEN 50'
        ])

    def test_ascii2tokens(self):
        txt = "\n".join([
            "10 CLS",
            "20 FOR I = 0 TO 255:",
            "30 POKE 1024+(I*2),I",
            "40 NEXT I",
            "50 I$ = INKEY$:IF I$="" THEN 50"
        ])
        self.listing.parse_ascii(txt)
        self.listing.debug_listing()

    def test_ascii2RAM01(self):
        txt = "10 CLS"
        self.listing.parse_ascii(txt)
        ram_content = self.listing.get_ram_content(program_start=0x1e01)
        dump = (
            0x1e, 0x07, # next_address
            0x00,
            0x0a, # 10
            0xa0, # CLS
            0x00, # end of line
            0x00, 0x00 # program end
        )
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(ram_content, dump)

    def test_ascii2RAM02(self):
        txt = """\
10 A=1
20 B=2
"""
        self.listing.parse_ascii(txt)
        ram_content = self.listing.get_ram_content(program_start=0x1e01)
        dump = (
            0x1e, 0x09,# next_address
            0x00, # line start
            0x0a, 0x41, 0xcb, 0x31, # 10 A=1
            0x00, # end of line
            0x1e, 0x11,# next_address
            0x00, # line start
            0x14, 0x42, 0xcb, 0x32, # 20 B=2
            0x00, # end of line
            0x00, 0x00 # program end
        )
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(ram_content, dump)

    def test_ascii2RAM03(self):
        txt = """\
10 CLS
20 FOR I = 0 TO 255:
30 POKE 1024+(I*2),I
40 NEXT I
50 I$ = INKEY$:IF I$="" THEN 50"""
        self.listing.parse_ascii(txt)
        ram_content = self.listing.get_ram_content(program_start=0x1e01)
        dump = (
            0x1e, 0x07,
            0x00,
            # 10 CLS
            0x0a, 0xa0,
            0x00,
            0x1e, 0x1a,
            0x00,
            # 20 FOR I = 0 TO 255:
            0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a,
            0x00,
            0x1e, 0x2d,
            0x00,
            # 30 POKE 1024+(I*2),I
            0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49,
            0x00,
            0x1e, 0x35,
            0x00,
            # 40 NEXT I
            0x28, 0x8b, 0x20, 0x49,
            0x00,
            0x1e, 0x4e,
            0x00,
            # 50 I$ = INKEY$:IF I$="" THEN 50
            0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30,
            0x00,
            0x00, 0x00
        )
        log_program_dump(ram_content)
        log_program_dump(dump)
        self.assertEqualProgramDump(ram_content, dump)



#        program_start = 0x1e01
#        program_end = 0x1e12
#
#        self.listing.load_from_dump(dump, program_start, program_end)
#        #self.listing.debug_listing()
#        ascii_lines = self.listing.get_ascii()
#        self.assertEqual(ascii_lines, [
#            '10 CLS',
#            '20 FOR I = 0 TO 255:',
#            '30 POKE 1024+(I*2),I',
#            '40 NEXT I',
#            '50 I$ = INKEY$:IF I$="" THEN 50'
#        ])

if __name__ == '__main__':
    setup_logging(log,
#         level=1 # hardcore debug ;)
#        level=10 # DEBUG
#         level=20 # INFO
#         level=30 # WARNING
#         level=40 # ERROR
        level=50  # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#             "Test6809_Program.test_division",

        ),
#        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#        failfast=True,
    )
