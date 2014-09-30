#!/usr/bin/env python
# encoding:utf8

"""
    unittests for BASIC parser
    ==========================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import logging
import sys
import unittest

from dragonlib.core.basic_parser import BASICParser


log = logging.getLogger(__name__)


class TestBASICParser(unittest.TestCase):
    def setUp(self):
        self.parser = BASICParser()

    def assertParser(self, ascii_listing, reference, print_parsed_lines=False):
        '''
        parse the given ASCII Listing and compare it with the reference.

        Used a speacial representation of the parser result for a human
        readable compare. Force using of """...""" to supress escaping apostrophe
        '''
        parsed_lines = self.parser.parse(ascii_listing)

        string_dict = {}
        for line_no, code_objects in list(parsed_lines.items()):
            string_dict[line_no] = [repr(code_object) for code_object in code_objects]

        if print_parsed_lines:
            print("-" * 79)
            print("parsed lines:", parsed_lines)
            print("-" * 79)
            print("reference:", reference)
            print("-" * 79)

        self.assertEqual(string_dict, reference)

    def test_only_code(self):
        ascii_listing = """
            10 CLS
            20 PRINT
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:CLS>""",
                ],
                20: [
                    """<CODE:PRINT>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_string(self):
        ascii_listing = '10 A$="A STRING"'
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:A$=>""",
                    """<STRING:"A STRING">""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_strings(self):
        ascii_listing = """
            10 A$="1":B=2:C$="4":CLS:PRINT "ONLY CODE"
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:A$=>""",
                    """<STRING:"1">""",
                    """<CODE::B=2:C$=>""",
                    """<STRING:"4">""",
                    """<CODE::CLS:PRINT >""",
                    """<STRING:"ONLY CODE">""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_string_and_comment(self):
        ascii_listing = """
            10 A$="NO :'REM" ' BUT HERE!
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:A$=>""",
                    """<STRING:"NO :'REM">""",
                    """<CODE: '>""",
                    """<COMMENT: BUT HERE!>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_string_not_terminated(self):
        ascii_listing = """
            10 PRINT "NOT TERMINATED STRING
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:PRINT >""",
                    """<STRING:"NOT TERMINATED STRING>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_data(self):
        ascii_listing = """
            10 DATA 1,2,A,FOO
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:DATA>""",
                    """<DATA: 1,2,A,FOO>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_data_with_string1(self):
        ascii_listing = """
            10 DATA 1,2,"A","FOO BAR",4,5
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:DATA>""",
                    """<DATA: 1,2,"A","FOO BAR",4,5>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_data_string_colon(self):
        ascii_listing = """
            10 DATA "FOO : BAR"
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:DATA>""",
                    """<DATA: "FOO : BAR">""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_code_after_data(self):
        ascii_listing = """
            10 DATA "FOO : BAR":PRINT 123
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:DATA>""",
                    """<DATA: "FOO : BAR">""",
                    """<CODE::PRINT 123>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_comment(self):
        ascii_listing = """
            10 REM A COMMENT
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:REM>""",
                    """<COMMENT: A COMMENT>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_nothing_after_comment1(self):
        ascii_listing = """
            10 REM
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:REM>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_nothing_after_comment2(self):
        ascii_listing = """
            10 '
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:'>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_no_code_after_comment(self):
        ascii_listing = """
            10 REM FOR "FOO : BAR":PRINT 123
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:REM>""",
                    """<COMMENT: FOR "FOO : BAR":PRINT 123>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_comment2(self):
        ascii_listing = """
            10 A=2 ' FOR "FOO : BAR":PRINT 123
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:A=2 '>""",
                    """<COMMENT: FOR "FOO : BAR":PRINT 123>""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_no_comment(self):
        ascii_listing = """
            10 B$="'"
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:B$=>""",
                    """<STRING:"'">""",
                ],
            },
            #             print_parsed_lines=True
        )

    def test_spaces_after_line_no(self):
        ascii_listing = """
            10 FOR I=1 TO 3:
            20     PRINT I
            30 NEXT
        """
        self.assertParser(ascii_listing,
            {
                10: [
                    """<CODE:FOR I=1 TO 3:>""",
                ],
                20: [
                    """<CODE:    PRINT I>""",
                ],
                30: [
                    """<CODE:NEXT>""",
                ],
            },
#             print_parsed_lines=True
        )


if __name__ == "__main__":
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
#         level=1 # hardcore debug ;)
#         level=10  # DEBUG
#         level=20  # INFO
#         level=30  # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    unittest.main(
        argv=(
            sys.argv[0],
#             "TestBASICParser.test_spaces_after_line_no",
        ),
        #         verbosity=1,
        verbosity=2,
        #         failfast=True,
    )
    print(" --- END --- ")
