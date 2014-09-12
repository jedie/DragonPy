#!/usr/bin/env python
# encoding:utf8

"""
    BASIC parser
    ============

    Note:
        The parser does only split into:
            * line number
            * Code parts
            * DATA
            * Strings
            * Comments

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import re

import logging

log = logging.getLogger(__name__)


CODE_TYPE_CODE = "CODE"
CODE_TYPE_DATA = "DATA"
CODE_TYPE_STRING = "STRING"
CODE_TYPE_COMMENT = "COMMENT"


class BaseCode(object):
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "<%s:%s>" % (self.PART_TYPE, self.content)


class BASIC_Code(BaseCode):
    PART_TYPE = CODE_TYPE_CODE


class BASIC_Data(BaseCode):
    PART_TYPE = CODE_TYPE_DATA


class BASIC_String(BaseCode):
    PART_TYPE = CODE_TYPE_STRING


class BASIC_Comment(BaseCode):
    PART_TYPE = CODE_TYPE_COMMENT


class ParsedBASIC(dict):
    """
    Normal dict with special __repr__
    """
    def pformat(self):
        '''
        Manually pformat to force using """...""" and supress escaping apostrophe
        '''
        result = "{\n"
        indent1 = " " * 4
        indent2 = " " * 8
        for line_no, code_objects in sorted(self.items()):
            result += '%s%i: [\n' % (indent1, line_no)
            for code_object in code_objects:
                result += '%s"""<%s:%s>""",\n' % (
                    indent2, code_object.PART_TYPE, code_object.content
                )
            result += '%s],\n' % indent1
        result += "}"

        return result

    def __repr__(self):
        return self.pformat()


class BASICParser(object):
    """
    Split BASIC sourcecode into:
        * line number
        * Code parts
        * DATA
        * Strings
        * Comments
    """
    def __init__(self):
        self.regex_line_no = re.compile(
            # Split the line number from the code
            "^\s*(?P<no>\d+)\s?(?P<content>.+)\s*$",
            re.MULTILINE
        )
        self.regex_split_all = re.compile(
            # To split a code line for parse CODE, DATA, STRING or COMMENT
            r""" ( " | DATA | REM | ') """,
            re.VERBOSE | re.MULTILINE
        )
        self.regex_split_data = re.compile(
            # To consume the complete DATA until " or :
            r""" ( " | : ) """,
            re.VERBOSE | re.MULTILINE
        )
        self.regex_split_string = re.compile(
            # To consume a string
            r""" ( " ) """,
            re.VERBOSE | re.MULTILINE
        )

    def parse(self, ascii_listing):
        """
        parse the given ASCII BASIC listing.
        Return a ParsedBASIC() instance.
        """
        self.parsed_lines = ParsedBASIC()
        for match in self.regex_line_no.finditer(ascii_listing):
            log.info("_" * 79)
            log.info("parse line >>>%r<<<", match.group())
            line_no = int(match.group("no"))
            line_content = match.group("content")

            self.line_data = []
            self._parse_code(line_content)
            log.info("*** line %s result: %r", line_no, self.line_data)

            self.parsed_lines[line_no] = self.line_data

        return self.parsed_lines

    def _parse_data(self, line, old_data=""):
        """
        Parse a DATA section until : or \n but exclude : in a string part.
        e.g.:
            10 DATA 1,"FOO:BAR",2:PRINT "NO DATA"
        """
        log.debug("*** parse DATA: >>>%r<<< old data: >>>%r<<<", line, old_data)
        parts = self.regex_split_data.split(line, maxsplit=1)
        if len(parts) == 1:  # end
            return old_data + parts[0], None

        pre, match, post = parts
        log.debug("\tpre: >>>%r<<<", pre)
        pre = old_data + pre
        log.debug("\tmatch: >>>%r<<<", match)
        log.debug("\tpost: >>>%r<<<", post)
        if match == ":":
            return old_data, match + post
        elif match == '"':
            string_part, rest = self._parse_string(post)
            return self._parse_data(rest, old_data=pre + match + string_part)

        raise RuntimeError("Wrong Reg.Exp.? match is: %r" % match)

    def _parse_string(self, line):
        """
        Consume the complete string until next " or \n
        """
        log.debug("*** parse STRING: >>>%r<<<", line)
        parts = self.regex_split_string.split(line, maxsplit=1)
        if len(parts) == 1:  # end
            return parts[0], None

        pre, match, post = parts
        log.debug("\tpre: >>>%r<<<", pre)
        log.debug("\tmatch: >>>%r<<<", match)
        log.debug("\tpost: >>>%r<<<", post)
        pre = pre + match
        log.debug("Parse string result: %r,%r", pre, post)
        return pre, post

    def _parse_code(self, line):
        """
        parse the given BASIC line and branch into DATA, String and
        consume a complete Comment
        """
        log.debug("*** parse CODE: >>>%r<<<", line)
        parts = self.regex_split_all.split(line, maxsplit=1)
        if len(parts) == 1:  # end
            self.line_data.append(BASIC_Code(parts[0]))
            return
        pre, match, post = parts
        log.debug("\tpre: >>>%r<<<", pre)
        log.debug("\tmatch: >>>%r<<<", match)
        log.debug("\tpost: >>>%r<<<", post)

        if match == '"':
            log.debug("%r --> parse STRING", match)
            self.line_data.append(BASIC_Code(pre))
            string_part, rest = self._parse_string(post)
            self.line_data.append(BASIC_String(match + string_part))
            if rest:
                self._parse_code(rest)
            return

        self.line_data.append(BASIC_Code(pre + match))

        if match == "DATA":
            log.debug("%r --> parse DATA", match)
            data_part, rest = self._parse_data(post)
            self.line_data.append(BASIC_Data(data_part))
            if rest:
                self._parse_code(rest)
            return
        elif match in ("'", "REM"):
            log.debug("%r --> consume rest of the line as COMMENT", match)
            if post:
                self.line_data.append(BASIC_Comment(post))
            return

        raise RuntimeError("Wrong Reg.Exp.? match is: %r" % match)


if __name__ == "__main__":
    import unittest
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log,
#        level=1 # hardcore debug ;)
#         level=10  # DEBUG
#         level=20  # INFO
        level=30  # WARNING
#         level=40 # ERROR
#         level=50 # CRITICAL/FATAL
    )

    unittest.main(
        module="dragonlib.tests.test_basic_parser",
        verbosity=2,
        #         failfast=True,
    )
    print(" --- END --- ")
