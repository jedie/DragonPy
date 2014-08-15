#!/usr/bin/env python
# encoding:utf-8

"""
    Dragon Lib unittests
    ~~~~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import unittest

from dragonlib.api import Dragon32API
from dragonlib.core.basic import BasicLine
from dragonlib.tests.test_base import BaseTestCase
from dragonlib.utils.logging_utils import log, setup_logging


class BaseDragon32ApiTestCase(BaseTestCase):
    def setUp(self):
        self.dragon32api = Dragon32API()


class Dragon32BASIC_LowLevel_ApiTest(BaseDragon32ApiTestCase):
    def setUp(self):
        super(Dragon32BASIC_LowLevel_ApiTest, self).setUp()
        self.token_util = self.dragon32api.listing.token_util
        self.basic_line = BasicLine(self.token_util)

    def test_load_from_dump(self):
        dump=(
            0x1e, 0x07, # next_address
            0x00,
            0x0a, # 10
            0xa0, # CLS
            0x00, # end of line
            0x00, 0x00 # program end
        )
        basic_lines = self.dragon32api.listing.dump2basic_lines(dump, program_start=0x1e01)
        ascii_listing = basic_lines[0].get_ascii()
        self.assertEqual(ascii_listing, "10 CLS")
        self.assertEqual(len(basic_lines), 1)

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
        basic_lines = self.dragon32api.listing.ascii_listing2basic_lines(
            '10 CLS'
        )
        tokens = basic_lines[0].get_tokens()
        self.assertHexList(tokens, [
            0x0a, # 10
            0xa0, # CLS
        ])
        self.assertEqual(len(basic_lines), 1)

    def test_ascii2tokens02(self):
        basic_lines = self.dragon32api.listing.ascii_listing2basic_lines(
            '50 I$ = INKEY$:IF I$="" THEN 50'
        )
        tokens = basic_lines[0].get_tokens()
        self.assertHexList(tokens, [
            0x32, # 50
            # I$ = INKEY$:IF I$="" THEN 50
            0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30,
        ])
        self.assertEqual(len(basic_lines), 1)


class Dragon32BASIC_HighLevel_ApiTest(BaseDragon32ApiTestCase):
    DUMP = (0x1e, 0x07, 0x00, 0x0a, 0xa0, 0x00, 0x1e, 0x1a, 0x00, 0x14, 0x80, 0x20, 0x49, 0x20, 0xcb, 0x20, 0x30, 0x20, 0xbc, 0x20, 0x32, 0x35, 0x35, 0x3a, 0x00, 0x1e, 0x2d, 0x00, 0x1e, 0x93, 0x20, 0x31, 0x30, 0x32, 0x34, 0xc3, 0x28, 0x49, 0xc5, 0x32, 0x29, 0x2c, 0x49, 0x00, 0x1e, 0x35, 0x00, 0x28, 0x8b, 0x20, 0x49, 0x00, 0x1e, 0x4e, 0x00, 0x32, 0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00, 0x00, 0x00)
    LISTING = [
            '10 CLS',
            '20 FOR I = 0 TO 255:',
            '30 POKE 1024+(I*2),I',
            '40 NEXT I',
            '50 I$ = INKEY$:IF I$="" THEN 50'
        ]

    def test_program_dump2ascii(self):
        listing = self.dragon32api.program_dump2ascii_lines(self.DUMP)
        self.assertEqual(listing, self.LISTING)

    def test_ascii_listing2tokens(self):
        basic_program_ascii = "\n".join(self.LISTING)
        tokens = self.dragon32api.ascii_listing2program_dump(basic_program_ascii)
        self.assertEqualProgramDump(tokens, self.DUMP)

    def test_ascii2RAM01(self):
        tokens = self.dragon32api.ascii_listing2program_dump("10 CLS")
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(tokens, (
            0x1e, 0x07, # next_address
            0x00,
            0x0a, # 10
            0xa0, # CLS
            0x00, # end of line
            0x00, 0x00 # program end
        ))

    def test_ascii2RAM02(self):
        tokens = self.dragon32api.ascii_listing2program_dump(
            "10 A=1\n"
            "20 B=2\n"
        )
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(tokens, (
            0x1e, 0x09,# next_address
            0x00, # line start
            0x0a, 0x41, 0xcb, 0x31, # 10 A=1
            0x00, # end of line
            0x1e, 0x11,# next_address
            0x00, # line start
            0x14, 0x42, 0xcb, 0x32, # 20 B=2
            0x00, # end of line
            0x00, 0x00 # program end
        ))



if __name__ == '__main__':
    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test_Dragon32_BASIC.test_code_load02",
        ),
#         verbosity=1,
        verbosity=2,
        failfast=True,
    )