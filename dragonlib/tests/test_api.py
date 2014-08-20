#!/usr/bin/env python
# encoding:utf-8

"""
    Dragon Lib unittests
    ~~~~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import pprint
import sys
import unittest

from dragonlib.api import Dragon32API
from dragonlib.core.basic import BasicLine
from dragonlib.tests.test_base import BaseTestCase
from dragonlib.utils.logging_utils import log, setup_logging, log_program_dump


class BaseDragon32ApiTestCase(BaseTestCase):
    def setUp(self):
        self.dragon32api = Dragon32API()

    def assertEqualProgramDump(self, first, second, msg=None):
        first = self.dragon32api.pformat_program_dump(first)
        second = self.dragon32api.pformat_program_dump(second)
        self.assertEqual(first, second, msg)

    def _prepare_text(self, txt):
        """
        prepare the multiline, indentation text.
        from python-creole
        """
        # txt = unicode(txt)
        txt = txt.splitlines()
        assert txt[0] == "", "First assertion line must be empty! Is: %s" % repr(txt[0])
        txt = txt[1:]  # Skip the first line

        # get the indentation level from the first line
        count = False
        for count, char in enumerate(txt[0]):
            if char != " ":
                break

        assert count != False, "second line is empty!"

        # remove indentation from all lines
        txt = [i[count:].rstrip(" ") for i in txt]

        # ~ txt = re.sub("\n {2,}", "\n", txt)
        txt = "\n".join(txt)

        # strip *one* newline at the begining...
        if txt.startswith("\n"):
            txt = txt[1:]
        # and strip *one* newline at the end of the text
        if txt.endswith("\n"):
            txt = txt[:-1]
        # ~ print(repr(txt))
        # ~ print("-"*79)

        return unicode(txt)  # turn to unicode, for better assertEqual error messages


class Dragon32BASIC_LowLevel_ApiTest(BaseDragon32ApiTestCase):
    def setUp(self):
        super(Dragon32BASIC_LowLevel_ApiTest, self).setUp()
        self.token_util = self.dragon32api.listing.token_util
        self.basic_line = BasicLine(self.token_util)

    def test_load_from_dump(self):
        dump = (
            0x1e, 0x07,  # next_address
            0x00, 0x0a,  # 10
            0xa0,  # CLS
            0x00,  # end of line
            0x00, 0x00  # program end
        )
        basic_lines = self.dragon32api.listing.dump2basic_lines(dump, program_start=0x1e01)
        ascii_listing = basic_lines[0].get_content()
        self.assertEqual(ascii_listing, "10 CLS")
        self.assertEqual(len(basic_lines), 1)

    def test_tokens2ascii(self):
        self.basic_line.token_load(
            line_number=50,
            tokens=(0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30, 0x00)
        )
        code = self.basic_line.get_content()
        self.assertEqual(code,
            '50 I$ = INKEY$:IF I$="" THEN 50'
        )

    def test_ascii2tokens01(self):
        basic_lines = self.dragon32api.listing.ascii_listing2basic_lines(
            '10 CLS'
        )
        tokens = basic_lines[0].get_tokens()
        self.assertHexList(tokens, [
            0x0a,  # 10
            0xa0,  # CLS
        ])
        self.assertEqual(len(basic_lines), 1)

    def test_ascii2tokens02(self):
        basic_lines = self.dragon32api.listing.ascii_listing2basic_lines(
            '50 I$ = INKEY$:IF I$="" THEN 50'
        )
        tokens = basic_lines[0].get_tokens()
        self.assertHexList(tokens, [
            0x32,  # 50
            # I$ = INKEY$:IF I$="" THEN 50
            0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a, 0x3a, 0x85, 0x20, 0x49, 0x24, 0xcb, 0x22, 0x22, 0x20, 0xbf, 0x20, 0x35, 0x30,
        ])
        self.assertEqual(len(basic_lines), 1)

    def test_format_tokens(self):
        tokens = (0x49, 0x24, 0x20, 0xcb, 0x20, 0xff, 0x9a)  # I$ = INKEY$
        formated_tokens = self.token_util.pformat_tokens(tokens)
        self.assertEqual(formated_tokens, [
            "\t  $49 -> 'I'",
            "\t  $24 -> '$'",
            "\t  $20 -> ' '",
            "\t  $cb -> '='",
            "\t  $20 -> ' '",
            "\t$ff9a -> 'INKEY$'",
        ])


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
        program_dump = self.dragon32api.ascii_listing2program_dump(basic_program_ascii)
#         print "\n".join(self.dragon32api.pformat_program_dump(program_dump))        
        self.assertEqualProgramDump(program_dump, self.DUMP)

    def test_ascii2RAM01(self):
        tokens = self.dragon32api.ascii_listing2program_dump("10 CLS")
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(tokens, (
            0x1e, 0x07,  # next_address
            0x00, 0x0a,  # 10
            0xa0,  # CLS
            0x00,  # end of line
            0x00, 0x00  # program end
        ))

    def test_ascii2RAM02(self):
        tokens = self.dragon32api.ascii_listing2program_dump(
            "10 A=1\n"
            "20 B=2\n"
        )
#        log_hexlist(ram_content)
#        log_hexlist(dump)
        self.assertEqualProgramDump(tokens, (
            0x1e, 0x09,  # next_address
            0x00, 0x0a, # 10
            0x41, 0xcb, 0x31,  # A=1
            0x00,  # end of line
            0x1e, 0x11,  # next_address
            0x00, 0x14, # 20
            0x42, 0xcb, 0x32,  # B=2
            0x00,  # end of line
            0x00, 0x00  # program end
        ))

    def test_listing2program_strings_dont_in_comment(self):
        """
        TODO: Don't replace tokens in comments

        NOTE: The REM shortcut >'< would be replace by >:'< internally from
        the BASIC Interpreter.

        See also:
        http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4310&p=11632#p11630
        """
        program_dump = self.dragon32api.ascii_listing2program_dump(
            "10 :'IF THEN ELSE"
        )
        print "\n".join(
            self.dragon32api.pformat_program_dump(program_dump)
        )
        self.assertEqualProgramDump(program_dump, (
            0x1e, 0x14, # next address
            0x00, 0x0a, # 10
            0x3a, # :
            0x83, # '
            0x49, 0x46, # I, F
            0x20, # " "
            0x54, 0x48, 0x45, 0x4e, # T, H, E, N
            0x20, # " "
            0x45, 0x4c, 0x53, 0x45, # E, L, S, E
            0x00, # end of line
            0x00, 0x00, # program end
        ))

    def test_listing2program_strings_dont_in_strings(self):
        """
        Don't replace tokens in strings
        """
        program_dump = self.dragon32api.ascii_listing2program_dump(
            '10 PRINT"FOR NEXT'
        )
        log_program_dump(program_dump)
        print "\n".join(
            self.dragon32api.pformat_program_dump(program_dump)
        )
        self.assertEqualProgramDump(program_dump, (
            0x1e, 0x10,  # start address
            0x00,  # line start
            0x0a,  # 10
            0x87,  # PRINT
            0x22,  # "
            0x46, 0x4f, 0x52,  # F, O, R
            0x20,  # " "
            0x4e, 0x45, 0x58, 0x54,  # N, E, X, T
            0x00,  # end of line
            0x00, 0x00,  # program end
        ))


class RenumTests(BaseDragon32ApiTestCase):
    def test_renum01(self):
        old_listing = self._prepare_text("""
            1 PRINT "ONE"
            11 GOTO 12
            12 PRINT "FOO":GOSUB 15
            14 IF A=1 THEN 20 ELSE 1
            15 PRINT "BAR"
            16 RESUME
            20 PRINT "END?"
        """)
#         print old_listing
#         print "-"*79
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 PRINT "ONE"
            20 GOTO 30
            30 PRINT "FOO":GOSUB 50
            40 IF A=1 THEN 70 ELSE 10
            50 PRINT "BAR"
            60 RESUME
            70 PRINT "END?"
        """))

    def test_missing_number01(self):
        old_listing = self._prepare_text("""
            1 GOTO 2
            2 GOTO 123 ' 123 didn't exists
            3 IF A=1 THEN 456 ELSE 2 ' 456 didn't exists
        """)
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 GOTO 20
            20 GOTO 123 ' 123 didn't exists
            30 IF A=1 THEN 456 ELSE 20 ' 456 didn't exists
        """))

    def test_on_goto(self):
        old_listing = self._prepare_text("""
            1 ON X GOTO 2,3
            2 ?"A"
            3 ?"B"
        """)
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 ON X GOTO 20,30
            20 ?"A"
            30 ?"B"
        """))

    def test_on_goto_spaces(self):
        old_listing = self._prepare_text("""
            1 ON X GOTO 2,30 , 4,  555
            2 ?"A"
            30 ?"B"
            4 ?"C"
            555 ?"D"
        """)
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 ON X GOTO 20,30,40,50
            20 ?"A"
            30 ?"B"
            40 ?"C"
            50 ?"D"
        """))

    def test_on_goto_space_after(self):
        old_listing = self._prepare_text("""
            1 ON X GOTO 1,2 ' space before comment?
            2 ?"A"
        """)
#         print old_listing
#         print "-"*79
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 ON X GOTO 10,20 ' space before comment?
            20 ?"A"
        """))

    def test_on_gosub_dont_exists(self):
        old_listing = self._prepare_text("""
            1 ON X GOSUB 1,2,3
            2 ?"A"
        """)
#         print old_listing
#         print "-"*79
        new_listing = self.dragon32api.renum_ascii_listing(old_listing)
#         print new_listing
        self.assertEqual(new_listing, self._prepare_text("""
            10 ON X GOSUB 10,20,3
            20 ?"A"
        """))


if __name__ == '__main__':
    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50  # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
            #             "Dragon32BASIC_HighLevel_ApiTest",
        ),
        #         verbosity=1,
        verbosity=2,
        failfast=True,
    )
