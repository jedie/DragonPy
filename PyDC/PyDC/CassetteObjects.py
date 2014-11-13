#!/usr/bin/env python2
# coding: utf-8

"""
    PyDC - Cassette Objects
    =======================

    Python objects to hold the content of a Cassette.

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import itertools
import logging
import os
import sys

# own modules
from basic_tokens import bytes2codeline
from dragonlib.utils import get_word, codepoints2string, string2codepoint, LOG_LEVEL_DICT, \
    LOG_FORMATTER, pformat_codepoints
from wave2bitstream import Wave2Bitstream, Bitstream2Wave
from bitstream_handler import BitstreamHandler, CasStream, BytestreamHandler
from PyDC.utils import iter_steps


log = logging.getLogger("PyDC")


class CodeLine(object):
    def __init__(self, line_pointer, line_no, code):
        assert isinstance(line_no, int), "Line number not integer, it's: %s" % repr(line_no)
        self.line_pointer = line_pointer
        self.line_no = line_no
        self.code = code

    def get_ascii_codeline(self):
        return "%i %s" % (self.line_no, self.code)

    def get_as_codepoints(self):
        return tuple(string2codepoint(self.get_ascii_codeline()))

    def __repr__(self):
        return "<CodeLine pointer: %s line no: %s code: %s>" % (
            repr(self.line_pointer), repr(self.line_no), repr(self.code)
        )


class FileContent(object):
    """
    Content (all data blocks) of a cassette file.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.code_lines = []

    def create_from_bas(self, file_content):
        for line in file_content.splitlines():
            if not line:
                # Skip empty lines (e.g. XRoar need a empty line at the end)
                continue

            try:
                line_number, code = line.split(" ", 1)
            except ValueError:
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    "Error split line: %s (line: %s)" % (evalue, repr(line))
                )
                raise etype, evalue, etb
            line_number = int(line_number)

            if self.cfg.case_convert:
                code = code.upper()

            self.code_lines.append(
                CodeLine(None, line_number, code)
            )

    def add_block_data(self, block_length, data):
        """
        add a block of tokenized BASIC source code lines.

        >>> cfg = Dragon32Config
        >>> fc = FileContent(cfg)

        >>> block = [
        ... 0x1e,0x12,0x0,0xa,0x80,0x20,0x49,0x20,0xcb,0x20,0x31,0x20,0xbc,0x20,0x31,0x30,0x0,
        ... 0x0,0x0]
        >>> len(block)
        19
        >>> fc.add_block_data(19,iter(block))
        19 Bytes parsed
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10

        >>> block = iter([
        ... 0x1e,0x29,0x0,0x14,0x87,0x20,0x49,0x3b,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22,0x0,
        ... 0x0,0x0])
        >>> fc.add_block_data(999,block)
        25 Bytes parsed
        ERROR: Block length value 999 is not equal to parsed bytes!
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10
        20 PRINT I;"HELLO WORLD!"

        >>> block = iter([
        ... 0x1e,0x31,0x0,0x1e,0x8b,0x20,0x49,0x0,
        ... 0x0,0x0])
        >>> fc.add_block_data(10,block)
        10 Bytes parsed
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10
        20 PRINT I;"HELLO WORLD!"
        30 NEXT I


        Test function tokens in code

        >>> fc = FileContent(cfg)
        >>> data = iter([
        ... 0x1e,0x4a,0x0,0x1e,0x58,0xcb,0x58,0xc3,0x4c,0xc5,0xff,0x88,0x28,0x52,0x29,0x3a,0x59,0xcb,0x59,0xc3,0x4c,0xc5,0xff,0x89,0x28,0x52,0x29,0x0,
        ... 0x0,0x0
        ... ])
        >>> fc.add_block_data(30, data)
        30 Bytes parsed
        >>> fc.print_code_lines()
        30 X=X+L*SIN(R):Y=Y+L*COS(R)


        Test high line numbers

        >>> fc = FileContent(cfg)
        >>> data = [
        ... 0x1e,0x1a,0x0,0x1,0x87,0x20,0x22,0x4c,0x49,0x4e,0x45,0x20,0x4e,0x55,0x4d,0x42,0x45,0x52,0x20,0x54,0x45,0x53,0x54,0x22,0x0,
        ... 0x1e,0x23,0x0,0xa,0x87,0x20,0x31,0x30,0x0,
        ... 0x1e,0x2d,0x0,0x64,0x87,0x20,0x31,0x30,0x30,0x0,
        ... 0x1e,0x38,0x3,0xe8,0x87,0x20,0x31,0x30,0x30,0x30,0x0,
        ... 0x1e,0x44,0x27,0x10,0x87,0x20,0x31,0x30,0x30,0x30,0x30,0x0,
        ... 0x1e,0x50,0x80,0x0,0x87,0x20,0x33,0x32,0x37,0x36,0x38,0x0,
        ... 0x1e,0x62,0xf9,0xff,0x87,0x20,0x22,0x45,0x4e,0x44,0x22,0x3b,0x36,0x33,0x39,0x39,0x39,0x0,0x0,0x0
        ... ]
        >>> len(data)
        99
        >>> fc.add_block_data(99, iter(data))
        99 Bytes parsed
        >>> fc.print_code_lines()
        1 PRINT "LINE NUMBER TEST"
        10 PRINT 10
        100 PRINT 100
        1000 PRINT 1000
        10000 PRINT 10000
        32768 PRINT 32768
        63999 PRINT "END";63999
        """

#         data = list(data)
# #         print repr(data)
#         print_as_hex_list(data)
#         print_codepoint_stream(data)
#         sys.exit()

        # create from codepoint list a iterator
        data = iter(data)

        byte_count = 0
        while True:
            try:
                line_pointer = get_word(data)
            except (StopIteration, IndexError), err:
                log.error("No line pointer information in code line data. (%s)" % err)
                break
#             print "line_pointer:", repr(line_pointer)
            byte_count += 2
            if not line_pointer:
                # arrived [0x00, 0x00] -> end of block
                break

            try:
                line_number = get_word(data)
            except (StopIteration, IndexError), err:
                log.error("No line number information in code line data. (%s)" % err)
                break
#             print "line_number:", repr(line_number)
            byte_count += 2

#             data = list(data)
#             print_as_hex_list(data)
#             print_codepoint_stream(data)
#             data = iter(data)

            # get the code line:
            # new iterator to get all characters until 0x00 arraived
            code = iter(data.next, 0x00)

            code = list(code) # for len()
            byte_count += len(code) + 1 # from 0x00 consumed in iter()

#             print_as_hex_list(code)
#             print_codepoint_stream(code)

            # convert to a plain ASCII string
            code = bytes2codeline(code)

            self.code_lines.append(
                CodeLine(line_pointer, line_number, code)
            )

        print "%i Bytes parsed" % byte_count
        if block_length != byte_count:
            print "ERROR: Block length value %i is not equal to parsed bytes!" % block_length

    def add_ascii_block(self, block_length, data):
        """
        add a block of ASCII BASIC source code lines.

        >>> data = [
        ... 0xd,
        ... 0x31,0x30,0x20,0x50,0x52,0x49,0x4e,0x54,0x20,0x22,0x54,0x45,0x53,0x54,0x22,
        ... 0xd,
        ... 0x32,0x30,0x20,0x50,0x52,0x49,0x4e,0x54,0x20,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22,
        ... 0xd
        ... ]
        >>> len(data)
        41
        >>> fc = FileContent(Dragon32Config)
        >>> fc.add_ascii_block(41, iter(data))
        41 Bytes parsed
        >>> fc.print_code_lines()
        10 PRINT "TEST"
        20 PRINT "HELLO WORLD!"
        """
        data = iter(data)

        data.next() # Skip first \r
        byte_count = 1 # incl. first \r
        while True:
            code = iter(data.next, 0xd) # until \r
            code = "".join([chr(c) for c in code])

            if not code:
                log.warning("code ended.")
                break

            byte_count += len(code) + 1 # and \r consumed in iter()

            try:
                line_number, code = code.split(" ", 1)
            except ValueError, err:
                print "\nERROR: Splitting linenumber in %s: %s" % (repr(code), err)
                break

            try:
                line_number = int(line_number)
            except ValueError, err:
                print "\nERROR: Part '%s' is not a line number!" % repr(line_number)
                continue

            self.code_lines.append(
                CodeLine(None, line_number, code)
            )

        print "%i Bytes parsed" % byte_count
        if block_length != byte_count:
            log.error(
                "Block length value %i is not equal to parsed bytes!" % block_length
            )

    def get_as_codepoints(self):
        result = []
        delim = list(string2codepoint("\r"))[0]
        for code_line in self.code_lines:
            result.append(delim)
            result += list(code_line.get_as_codepoints())
        result.append(delim)
#         log.debug("-"*79)
#         for line in pformat_codepoints(result):
#             log.debug(repr(line))
#         log.debug("-"*79)
        return result

    def get_ascii_codeline(self):
        for code_line in self.code_lines:
            yield code_line.get_ascii_codeline()

    def print_code_lines(self):
        for code_line in self.code_lines:
            print "%i %s" % (code_line.line_no, code_line.code)

    def print_debug_info(self):
        print "\tcode lines:"
        print "-"*79
        self.print_code_lines()
        print "-"*79


class CassetteFile(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.is_tokenized = False
        self.ascii_flag = None
        self.gap_flag = None # one byte gap flag (0x00=no gaps, 0xFF=gaps)

    def create_from_bas(self, filename, file_content):
        filename2 = os.path.split(filename)[1]
        filename2 = filename2.upper()
        filename2 = filename2.rstrip()
        filename2 = filename2.replace(" ", "_")
        # TODO: remove non ASCII!
        filename2 = filename2[:8]

        log.debug("filename '%s' from: %s" % (filename2, filename))

        self.filename = filename2

        self.file_type = self.cfg.FTYPE_BASIC # BASIC programm (0x00)

        # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4231&p=9723#p9723
        self.ascii_flag = self.cfg.BASIC_ASCII
        self.gap_flag = self.cfg.GAPS # ASCII File is GAP, tokenized is no gaps

        self.file_content = FileContent(self.cfg)
        self.file_content.create_from_bas(file_content)

    def create_from_wave(self, codepoints):

        log.debug("filename data: %s" % pformat_codepoints(codepoints))

        raw_filename = codepoints[:8]

        self.filename = codepoints2string(raw_filename).rstrip()
        print "\nFilename: %s" % repr(self.filename)

        self.file_type = codepoints[8]

        if not self.file_type in self.cfg.FILETYPE_DICT:
            raise NotImplementedError(
                "Unknown file type %s is not supported, yet." % hex(self.file_type)
            )

        log.info("file type: %s" % self.cfg.FILETYPE_DICT[self.file_type])

        if self.file_type == self.cfg.FTYPE_DATA:
            raise NotImplementedError("Data files are not supported, yet.")
        elif self.file_type == self.cfg.FTYPE_BIN:
            raise NotImplementedError("Binary files are not supported, yet.")

        self.ascii_flag = codepoints[9]
        log.info("Raw ASCII flag is: %s" % repr(self.ascii_flag))
        if self.ascii_flag == self.cfg.BASIC_TOKENIZED:
            self.is_tokenized = True
        elif self.ascii_flag == self.cfg.BASIC_ASCII:
            self.is_tokenized = False
        else:
            raise NotImplementedError("Unknown BASIC type: '%s'" % hex(self.ascii_flag))

        log.info("ASCII flag: %s" % self.cfg.BASIC_TYPE_DICT[self.ascii_flag])

        self.gap_flag = codepoints[10]
        log.info("gap flag is %s (0x00=no gaps, 0xff=gaps)" % hex(self.gap_flag))

        # machine code starting/loading address
        if self.file_type != self.cfg.FTYPE_BASIC: # BASIC programm (0x00)
            codepoints = iter(codepoints)

            self.start_address = get_word(codepoints)
            log.info("machine code starting address: %s" % hex(self.start_address))

            self.load_address = get_word(codepoints)
            log.info("machine code loading address: %s" % hex(self.load_address))
        else:
            # not needed in BASIC files
            # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4341&p=9109#p9109
            pass

        self.file_content = FileContent(self.cfg)

    def add_block_data(self, block_length, codepoints):
        if self.is_tokenized:
            self.file_content.add_block_data(block_length, codepoints)
        else:
            self.file_content.add_ascii_block(block_length, codepoints)

        print "*"*79
        self.file_content.print_code_lines()
        print "*"*79

    def get_filename_block_as_codepoints(self):
        """
        TODO: Support tokenized BASIC. Now we only create ASCII BASIC.
        """
        codepoints = []
        codepoints += list(string2codepoint(self.filename.ljust(8, " ")))
        codepoints.append(self.cfg.FTYPE_BASIC) # one byte file type
        codepoints.append(self.cfg.BASIC_ASCII) # one byte ASCII flag

        # one byte gap flag (0x00=no gaps, 0xFF=gaps)
        # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4231&p=9110#p9110
        codepoints.append(self.gap_flag)

        # machine code starting/loading address
        if self.file_type != self.cfg.FTYPE_BASIC: # BASIC programm (0x00)
            codepoints = iter(codepoints)

            self.start_address = get_word(codepoints)
            log.info("machine code starting address: %s" % hex(self.start_address))

            self.load_address = get_word(codepoints)
            log.info("machine code loading address: %s" % hex(self.load_address))
        else:
            # not needed in BASIC files
            # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4341&p=9109#p9109
            pass

        log.debug("filename block: %s" % pformat_codepoints(codepoints))
        return codepoints

    def get_code_block_as_codepoints(self):
        result = self.file_content.get_as_codepoints()

        # XXX: Is a code block end terminator needed?
        # e.g.:
#         if self.is_tokenized:
#             result += [0x00, 0x00]
#         else:
#             result.append(0x0d) # 0x0d == \r

        return result

    def print_debug_info(self):
        print "\tFilename: '%s'" % self.filename
        print "\tfile type: %s" % self.cfg.FILETYPE_DICT[self.file_type]
        print "\tis tokenized:", self.is_tokenized
        self.file_content.print_debug_info()

    def __repr__(self):
        return "<BlockFile '%s'>" % (self.filename,)


class Cassette(object):
    """
    >>> d32cfg = Dragon32Config()
    >>> c = Cassette(d32cfg)
    >>> c.add_from_bas("../test_files/HelloWorld1.bas")
    >>> c.print_debug_info() # doctest: +NORMALIZE_WHITESPACE
    There exists 1 files:
        Filename: 'HELLOWOR'
        file type: BASIC programm (0x00)
        is tokenized: False
        code lines:
    -------------------------------------------------------------------------------
    10 FOR I = 1 TO 10
    20 PRINT I;"HELLO WORLD!"
    30 NEXT I
    -------------------------------------------------------------------------------
    >>> c.pprint_codepoint_stream()
    255 x LEAD_BYTE_CODEPOINT
    0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55 0x55
    1x SYNC_BYTE_CODEPOINT
     0x3c
    block type filename block (0x00)
     0x0
    block length: 0xa
     0xa
    yield block data
     0x48 0x45 0x4c 0x4c 0x4f 0x57 0x4f 0x52 0x0 0xff
    block type data block (0x01)
     0x1
    block length: 0x36
     0x36
    yield block data
     0x31 0x30 0x20 0x46 0x4f 0x52 0x20 0x49 0x20 0x3d 0x20 0x31 0x20 0x54 0x4f 0x20 0x31 0x30 0x32 0x30 0x20 0x50 0x52 0x49 0x4e 0x54 0x20 0x49 0x3b 0x22 0x48 0x45 0x4c 0x4c 0x4f 0x20 0x57 0x4f 0x52 0x4c 0x44 0x21 0x22 0x33 0x30 0x20 0x4e 0x45 0x58 0x54 0x20 0x49 0x0 0x0
    block type end-of-file block (0xff)
     0xff
    block length: 0x0
     0x0
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.files = []
        self.current_file = None
        self.wav = None # Bitstream2Wave instance only if write_wave() used!

        # temp storage for code block
        self.buffer = []
        self.buffered_block_length = 0

    def add_from_wav(self, source_file):
        bitstream = iter(Wave2Bitstream(source_file, self.cfg))

        # store bitstream into python objects
        bh = BitstreamHandler(self, self.cfg)
        bh.feed(bitstream)

    def add_from_cas(self, source_file):
        cas_stream = CasStream(source_file)
        bh = BytestreamHandler(self, self.cfg)
        bh.feed(cas_stream)

    def add_from_bas(self, filename):
        with open(filename, "r") as f:
            file_content = f.read()

        self.current_file = CassetteFile(self.cfg)
        self.current_file.create_from_bas(filename, file_content)
        self.files.append(self.current_file)

    def buffer2file(self):
        """
        add the code buffer content to CassetteFile() instance
        """
        if self.current_file is not None and self.buffer:
            self.current_file.add_block_data(self.buffered_block_length, self.buffer)
            self.buffer = []
            self.buffered_block_length = 0

    def buffer_block(self, block_type, block_length, block_codepoints):

        block = tuple(itertools.islice(block_codepoints, block_length))
        log.debug("pprint block: %s" % pformat_codepoints(block))

        if block_type == self.cfg.EOF_BLOCK:
            self.buffer2file()
            return
        elif block_type == self.cfg.FILENAME_BLOCK:
            self.buffer2file()
            self.current_file = CassetteFile(self.cfg)
            self.current_file.create_from_wave(block)
            log.info("Add file %s" % repr(self.current_file))
            self.files.append(self.current_file)
        elif block_type == self.cfg.DATA_BLOCK:
            # store code until end marker
            self.buffer += block
            self.buffered_block_length += block_length
        else:
            raise TypeError("Block type %s unkown!" & hex(block_type))

    def print_debug_info(self):
        print "There exists %s files:" % len(self.files)
        for file_obj in self.files:
            file_obj.print_debug_info()

    def block2codepoint_stream(self, file_obj, block_type, block_codepoints):
        if file_obj.gap_flag == self.cfg.GAPS:
            # file has gaps (e.g. ASCII BASIC)
            log.debug("File has GAP flag set:")
            log.debug("yield %sx bit-sync bytes %s",
                self.cfg.LEAD_BYTE_LEN, hex(self.cfg.LEAD_BYTE_CODEPOINT)
            )
            leadin = [self.cfg.LEAD_BYTE_CODEPOINT for _ in xrange(self.cfg.LEAD_BYTE_LEN)]
            yield leadin

        log.debug("yield 1x leader byte %s", hex(self.cfg.LEAD_BYTE_CODEPOINT))
        yield self.cfg.LEAD_BYTE_CODEPOINT

        log.debug("yield sync byte %s" % hex(self.cfg.SYNC_BYTE_CODEPOINT))
        if self.wav:
            log.debug("wave pos: %s" % self.wav.pformat_pos())
        yield self.cfg.SYNC_BYTE_CODEPOINT

        log.debug("yield block type '%s'" % self.cfg.BLOCK_TYPE_DICT[block_type])
        yield block_type

        codepoints = tuple(block_codepoints)
        block_length = len(codepoints)
        assert block_length <= 255
        log.debug("yield block length %s (%sBytes)" % (hex(block_length), block_length))
        yield block_length

        if not codepoints:
            # EOF block
            # FIXME checksum
            checksum = block_type
            checksum += block_length
            checksum = checksum & 0xFF
            log.debug("yield calculated checksum %s" % hex(checksum))
            yield checksum
        else:
            log.debug("content of '%s':" % self.cfg.BLOCK_TYPE_DICT[block_type])
            log.debug("-"*79)
            log.debug(repr("".join([chr(i) for i in codepoints])))
            log.debug("-"*79)

            yield codepoints

            checksum = sum([codepoint for codepoint in codepoints])
            checksum += block_type
            checksum += block_length
            checksum = checksum & 0xFF
            log.debug("yield calculated checksum %s" % hex(checksum))
            yield checksum

        log.debug("yield 1x tailer byte %s", hex(self.cfg.LEAD_BYTE_CODEPOINT))
        yield self.cfg.LEAD_BYTE_CODEPOINT

    def codepoint_stream(self):
        if self.wav:
            self.wav.write_silence(sec=0.1)

        for file_obj in self.files:
            # yield filename
            for codepoints in self.block2codepoint_stream(file_obj,
                    block_type=self.cfg.FILENAME_BLOCK,
                    block_codepoints=file_obj.get_filename_block_as_codepoints()
                ):
                yield codepoints

            if self.wav:
                self.wav.write_silence(sec=0.1)

            # yield file content
            codepoints = file_obj.get_code_block_as_codepoints()

            for raw_codepoints in iter_steps(codepoints, 255):
#                 log.debug("-"*79)
#                 log.debug("".join([chr(i) for i in raw_codepoints]))
#                 log.debug("-"*79)

                # Add meta information
                codepoint_stream = self.block2codepoint_stream(file_obj,
                    block_type=self.cfg.DATA_BLOCK, block_codepoints=raw_codepoints
                )
                for codepoints2 in codepoint_stream:
                    yield codepoints2

                if self.wav:
                    self.wav.write_silence(sec=0.1)

        # yield EOF
        for codepoints in self.block2codepoint_stream(file_obj,
                block_type=self.cfg.EOF_BLOCK,
                block_codepoints=[]
            ):
            yield codepoints

        if self.wav:
            self.wav.write_silence(sec=0.1)

    def write_wave(self, destination_file):
        wav = Bitstream2Wave(destination_file, self.cfg)
        for codepoint in self.codepoint_stream():
            if isinstance(codepoint, (tuple, list)):
                for item in codepoint:
                    assert isinstance(item, int), "Codepoint %s is not int/hex" % repr(codepoint)
            else:
                assert isinstance(codepoint, int), "Codepoint %s is not int/hex" % repr(codepoint)
            wav.write_codepoint(codepoint)

        wav.close()

    def write_cas(self, destination_file):
        log.info("Create %s..." % repr(destination_file))

        def _write(f, codepoint):
            try:
                f.write(chr(codepoint))
            except ValueError, err:
                log.error("Value error with %s: %s" % (repr(codepoint), err))
                raise

        with open(destination_file, "wb") as f:
            for codepoint in self.codepoint_stream():
                if isinstance(codepoint, (tuple, list)):
                    for item in codepoint:
                        _write(f, item)
                else:
                    _write(f, codepoint)

        print "\nFile %s saved." % repr(destination_file)

    def write_bas(self, destination_file):
        dest_filename = os.path.splitext(destination_file)[0]
        for file_obj in self.files:

            bas_filename = file_obj.filename # Filename from CSAVE argument

            out_filename = "%s_%s.bas" % (dest_filename, bas_filename)
            log.info("Create %s..." % repr(out_filename))
            with open(out_filename, "w") as f:
                for line in file_obj.file_content.get_ascii_codeline():
                    if self.cfg.case_convert:
                        line = line.lower()
                    f.write("%s\n" % line)
            print "\nFile %s saved." % repr(out_filename)

    def pprint_codepoint_stream(self):
        log_level = LOG_LEVEL_DICT[3]
        log.setLevel(log_level)

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(LOG_FORMATTER)
        log.addHandler(handler)

        for codepoint in self.codepoint_stream():
            try:
                print hex(codepoint),
            except TypeError, err:
                raise TypeError(
                    "\n\nERROR with '%s': %s" % (repr(codepoint), err)
                )



if __name__ == "__main__":
#     import doctest
#     print doctest.testmod(
#         verbose=False
#         # verbose=True
#     )
#     sys.exit()

    import subprocess

    # bas -> wav
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
#         "--verbosity=10",
        "--verbosity=5",
#         "--logfile=5",
#         "--log_format=%(module)s %(lineno)d: %(message)s",
#         "../test_files/HelloWorld1.bas", "--dst=../test.wav"
        "../test_files/HelloWorld1.bas", "--dst=../test.cas"
    ]).wait()

#     print "\n"*3
#     print "="*79
#     print "\n"*3
#
# #     # wav -> bas
#     subprocess.Popen([sys.executable, "../PyDC_cli.py",
# #         "--verbosity=10",
#         "--verbosity=7",
# #         "../test.wav", "--dst=../test.bas",
# #         "../test.cas", "--dst=../test.bas",
# #         "../test_files/HelloWorld1 origin.wav", "--dst=../test_files/HelloWorld1.bas",
#         "../test_files/LineNumber Test 02.wav", "--dst=../test.bas",
#     ]).wait()
#
#     print "-- END --"


