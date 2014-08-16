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

from dragonlib.utils.logging_utils import log, log_program_dump
from dragonpy.utils.byte_word_values import word2bytes



class BasicTokenUtil(object):
    def __init__(self, basic_token_dict):
        self.basic_token_dict = basic_token_dict
        self.ascii2token_dict = dict([
            (code, token)
            for token, code in basic_token_dict.items()
        ])

        regex = "(%s)" % "|".join([
            re.escape(statement)
            for statement in self.basic_token_dict.values()
        ])
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
        self.token_util = token_util
        self.line_number = None
        self.line_code = None

    def token_load(self, line_number, tokens):
        self.line_number = line_number
        assert tokens[-1] == 0x00, "line code %s doesn't ends with \\x00: %s" % (
            repr(tokens), repr(tokens[-1])
        )
        self.line_code = tokens[:-1] # rstrip \x00

    def ascii_load(self, line_ascii):
        try:
            line_number, ascii_code = line_ascii.split(" ", 1)
        except ValueError as err:
            msg = "Error split line number and code in line: %r (Origin error: %s)" % (
                line_ascii, err
            )
            raise ValueError(msg)
        self.line_number = int(line_number)
        self.line_code = self.token_util.ascii2token(ascii_code)

    def get_tokens(self):
        return [self.line_number] + self.line_code

    def get_content(self, code=None, debug=False):
        if code is None: # start
            code = self.line_code

        line = "%i " % self.line_number
        old_value = None
        for value in code:
            if value == 0xff:
                old_value = value
                continue
            if old_value is not None:
                value = (old_value << 8) + value
                old_value = None
            code = self.token_util.token2ascii(value)
            if debug:
                log.critical("\t%s -> %s", hex(value), repr(code))
            line += code
        return line

    def log_line(self):
        log.critical("%r -> %s" % (
            self.get_content(debug=True), " ".join(["$%02x" % v for v in self.get_tokens()])
        ))


class BasicListing(object):
    def __init__(self, basic_token_dict):
        self.token_util = BasicTokenUtil(basic_token_dict)

    def dump2basic_lines(self, dump, program_start, basic_lines=None):
        if basic_lines is None:
            basic_lines = []

        log.critical("progam start $%04x", program_start)
        next_address = (dump[0] << 8) + dump[1]
        log.critical("next_address: $%04x", next_address)
        if next_address == 0x0000:
            # program end
            log.critical("return: %s", repr(basic_lines))
            return basic_lines
        line_number = (dump[2] << 8) + dump[3]
        log.critical("line_number: %i", line_number)
        length = next_address - program_start
        log.critical("length: %i", length)
        tokens = dump[4:length]
        log.critical("tokens: %s", ",".join(["$%02x" % i for i in tokens]))

        basic_line = BasicLine(self.token_util)
        basic_line.token_load(line_number, tokens)
        basic_lines.append(basic_line)

        return self.dump2basic_lines(dump[length:], next_address, basic_lines)

    def basic_lines2program_dump(self, basic_lines, program_start):
        program_dump = []
        current_address = program_start
        count = len(basic_lines)
        for no, line in enumerate(basic_lines, 1):
            line.log_line()
            line_tokens = [0x00] + line.get_tokens() + [0x00]

            current_address += len(line_tokens) + 2
            program_dump += word2bytes(current_address)
            if no == count: # It's the last line
                line_tokens += [0x00, 0x00]
            program_dump += line_tokens

        return program_dump

    def ascii_listing2basic_lines(self, txt):
        basic_lines = []
        for line in txt.splitlines():
            line = line.strip()
            if line:
                basic_line = BasicLine(self.token_util)
                basic_line.ascii_load(line)
                basic_lines.append(basic_line)
        return basic_lines

    def debug_listing(self, basic_lines):
        for line in basic_lines:
            line.log_line()

    def log_ram_content(self, program_start, level=99):
        ram_content = self.basic_lines2program_dump(program_start)
        log_program_dump(ram_content, level)

    def ascii_listing2program_dump(self,basic_program_ascii, program_start):
        basic_lines = self.ascii_listing2basic_lines(basic_program_ascii)
        self.debug_listing(basic_lines)
        return self.basic_lines2program_dump(basic_lines, program_start)

    def program_dump2ascii_lines(self, dump, program_start):
        basic_lines = self.dump2basic_lines(dump, program_start)
        log.critical("basic_lines: %s", repr(basic_lines))
        ascii_lines = []
        for line in basic_lines:
            ascii_lines.append(line.get_content())
        return ascii_lines
