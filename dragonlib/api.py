#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonlib.core.basic import BasicListing, RenumTool
from dragonlib.dragon32.basic_tokens import DRAGON32_BASIC_TOKENS
from dragonlib.utils.logging_utils import log


DRAGON32 = "Dragon32"


class BaseAPI(object):
    RENUM_REGEX = r"""
        (?P<statement> GOTO|GOSUB|THEN|ELSE ) (?P<space>\s*) (?P<no>\d+)
        |
        (?P<on_goto_statement> ON.+?GOTO|ON.+?GOSUB ) (?P<on_goto_space>\s*) (?P<on_goto_no>[\d*,\s*]+)
    """

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

    def format_tokens(self, tokens):
        """
        format a tokenized BASIC program line. Useful for debugging.
        returns a list of formated string lines.
        """
        return self.listing.token_util.format_tokens(tokens)

    def format_program_dump(self, program_dump, program_start=None):
        """
        format a BASIC program dump. Useful for debugging.
        returns a list of formated string lines.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
        return self.listing.format_program_dump(program_dump, program_start)

    def renum_ascii_listing(self, content):
        return self.renum_tool.renum(content)


class Dragon32API(BaseAPI):
    CONFIG_NAME = DRAGON32
    MACHINE_NAME = "Dragon 32"
    BASIC_TOKENS = DRAGON32_BASIC_TOKENS

    PROGRAM_START_ADDR = 0x0019
    VARIABLES_START_ADDR = 0x001B
    ARRAY_START_ADDR = 0x001D
    FREE_SPACE_START_ADDR = 0x001F

    # Default memory location of BASIC listing start
    DEFAULT_PROGRAM_START = 0x1E01

    def __init__(self):
        self.listing = BasicListing(self.BASIC_TOKENS)
        self.renum_tool = RenumTool(self.RENUM_REGEX)


