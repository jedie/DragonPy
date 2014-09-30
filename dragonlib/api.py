#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from dragonlib.CoCo.basic_tokens import COCO_BASIC_TOKENS
from dragonlib.core.basic import BasicListing, RenumTool, BasicTokenUtil,\
    BasicLine
from dragonlib.core.basic_parser import BASICParser
from dragonlib.dragon32.basic_tokens import DRAGON32_BASIC_TOKENS
import logging

log=logging.getLogger(__name__)


DRAGON32 = "Dragon32"
COCO2B = "CoCo"


class BaseAPI(object):
    RENUM_REGEX = r"""
        (?P<statement> GOTO|GOSUB|THEN|ELSE ) (?P<space>\s*) (?P<no>[\d*,\s*]+)
    """
    
    def __init__(self):
        self.listing = BasicListing(self.BASIC_TOKENS)
        self.renum_tool = RenumTool(self.RENUM_REGEX)
        self.token_util = BasicTokenUtil(self.BASIC_TOKENS)

    def program_dump2ascii_lines(self, dump, program_start=None):
        """
        convert a memory dump of a tokensized BASIC listing into
        ASCII listing list.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
        return self.listing.program_dump2ascii_lines(dump, program_start)
    
    def parse_ascii_listing(self, basic_program_ascii):
        parser = BASICParser()
        parsed_lines = parser.parse(basic_program_ascii)
        if not parsed_lines:
            log.critical("No parsed lines %s from %s ?!?" % (
                repr(parsed_lines), repr(basic_program_ascii)
            ))
        log.info("Parsed BASIC: %s", repr(parsed_lines))
        return parsed_lines

    def ascii_listing2program_dump(self, basic_program_ascii, program_start=None):
        """
        convert a ASCII BASIC program listing into tokens.
        This tokens list can be used to insert it into the
        Emulator RAM.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
            
        parsed_lines = self.parse_ascii_listing(basic_program_ascii)
         
        basic_lines = []       
        for line_no, code_objects in sorted(parsed_lines.items()):
            basic_line = BasicLine(self.token_util)
            basic_line.code_objects_load(line_no,code_objects)
            basic_lines.append(basic_line)
         
        return self.listing.basic_lines2program_dump(basic_lines, program_start)          

    def pformat_tokens(self, tokens):
        """
        format a tokenized BASIC program line. Useful for debugging.
        returns a list of formated string lines.
        """
        return self.listing.token_util.pformat_tokens(tokens)

    def pformat_program_dump(self, program_dump, program_start=None):
        """
        format a BASIC program dump. Useful for debugging.
        returns a list of formated string lines.
        """
        if program_start is None:
            program_start = self.DEFAULT_PROGRAM_START
        return self.listing.pformat_program_dump(program_dump, program_start)

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


class CoCoAPI(Dragon32API):
    """
    http://sourceforge.net/p/toolshed/code/ci/default/tree/cocoroms/dragon_equivs.asm
    """
    CONFIG_NAME = COCO2B
    MACHINE_NAME = "CoCo"
    BASIC_TOKENS = COCO_BASIC_TOKENS

