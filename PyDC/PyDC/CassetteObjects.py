#!/usr/bin/env python2
# coding: utf-8

"""
    PyDC - Cassette Objects
    =======================

    Python objects to hold the content of a Cassette.

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys

# own modules
from basic_tokens import bytes2codeline
from configs import Dragon32Config
from utils import get_word, codepoints2string, string2codepoint, LOG_LEVEL_DICT, \
    LOG_FORMATTER, codepoints2bitstream, pformat_codepoints



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
        return string2codepoint(self.get_ascii_codeline())

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
            line_number, code = line.split(" ", 1)
            line_number = int(line_number)
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
            print "\nERROR: Block length value %i is not equal to parsed bytes!" % block_length

    def get_as_codepoints(self):
        result = []
        delim = list(string2codepoint("\r"))[0]
        for code_line in self.code_lines:
            result.append(delim)
            result += list(code_line.get_as_codepoints())
        result.append(delim)

        result += self.cfg.BASIC_CODE_END
        log.debug("code: %s" % repr(result))
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
        self.file_content = FileContent(self.cfg)
        self.file_content.create_from_bas(file_content)

    def create_from_wave(self, codepoints):

        log.debug("filename data: %s" % pformat_codepoints(codepoints))

        raw_filename = codepoints[:8]

        self.filename = codepoints2string(raw_filename).rstrip()
        print "\nFilename: %s" % repr(self.filename)

#         print "file meta:"
#         print_codepoint_stream(codepoints)

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

        ascii_flag = codepoints[9]
        log.info("Raw ASCII flag is: %s" % repr(ascii_flag))
        if ascii_flag == self.cfg.BASIC_TOKENIZED:
            self.is_tokenized = True
        elif ascii_flag == self.cfg.BASIC_ASCII:
            self.is_tokenized = False
        else:
            raise NotImplementedError("Unknown BASIC type: '%s'" % hex(ascii_flag))

        log.info("ASCII flag: %s" % self.cfg.BASIC_TYPE_DICT[ascii_flag])

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
        codepoints = []
        codepoints += list(string2codepoint(self.filename.ljust(8, " ")))
        codepoints.append(self.cfg.FTYPE_BASIC) # one byte file type
        codepoints.append(self.cfg.BASIC_ASCII) # one byte ASCII flag
        codepoints.append(0x00) # one byte gap flag (00=no gaps, FF=gaps)
        # FIXME, see: http://five.pairlist.net/pipermail/coco/2013-August/070938.html
        codepoints += [0x0c, 0x00] # two bytes machine code starting address
        codepoints += [0x0c, 0x00] # two bytes machine code loading address
        log.debug("filename block: %s" % pformat_codepoints(codepoints))
        return codepoints

    def get_code_block_as_codepoints(self):
        return self.file_content.get_as_codepoints()

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

    def add_from_bas(self, filename):
        with open(filename, "r") as f:
            file_content = f.read()

        self.current_file = CassetteFile(self.cfg)
        self.current_file.create_from_bas(filename, file_content)
        self.files.append(self.current_file)

    def add_from_cas(self, source_filepath):
        log.debug("Open %s..." % repr(source_filepath))

        class CasStream(object):
            def __init__(self, source_filepath):
                self.source_filepath = source_filepath
                self.f = open(source_filepath, "rb")
                self.pos = 0

            def __iter__(self):
                return self
            def next(self):
                self.last_byte = self.f.read(1)
                if self.last_byte == "":
                    raise StopIteration
                self.pos += 1
                self.last_codepoint = ord(self.last_byte)
                return (self.pos, self.last_codepoint)

        cas_stream = CasStream(source_filepath)

        leadin_count = None
#         for i in iter(cas_stream.next, self.cfg.LEAD_BYTE_CODEPOINT):
#             print i
#             break

        log.debug("Count leading byte.")
#         for leadin_count, leadin_byte in iter(cas_stream.next, self.cfg.LEAD_BYTE_CODEPOINT):
        for leadin_count, leadin_byte in cas_stream:
            if leadin_byte != self.cfg.LEAD_BYTE_CODEPOINT:
                break

        if leadin_count is None:
            log.error("Leadin byte not found in file!")
            sys.exit(-1)
        log.info("%s x leadin bytes found." % leadin_count)

#         sync_byte = cas_stream.next()
        sync_byte = cas_stream.last_codepoint
        if sync_byte != self.cfg.SYNC_BYTE_CODEPOINT:
            log.error("Sync byte wrong. Get %s but excepted %s" % (
                repr(sync_byte), hex(self.cfg.SYNC_BYTE_CODEPOINT)
            ))
        else:
            log.debug("Sync byte, ok.")

        raise TODO


    def add_block(self, block_type, block_length, block_codepoints):
        if block_type == self.cfg.EOF_BLOCK:
            return
        elif block_type == self.cfg.FILENAME_BLOCK:
            self.current_file = CassetteFile(self.cfg)
            self.current_file.create_from_wave(block_codepoints)
            log.info("Add file %s" % repr(self.current_file))
            self.files.append(self.current_file)
        elif block_type == self.cfg.DATA_BLOCK:
            self.current_file.add_block_data(block_length, block_codepoints)
        else:
            raise TypeError("Block type %s unkown!" & hex(block_type))

    def print_debug_info(self):
        print "There exists %s files:" % len(self.files)
        for file_obj in self.files:
            file_obj.print_debug_info()

    def block2codepoint_stream(self, block_type, block_codepoints):
        log.debug("yield %sx lead byte %s" % (
            self.cfg.LEAD_BYTE_LEN, hex(self.cfg.LEAD_BYTE_CODEPOINT)
        ))
        leadin = [self.cfg.LEAD_BYTE_CODEPOINT for _ in xrange(self.cfg.LEAD_BYTE_LEN)]
        yield leadin

        log.debug("yield sync byte %s" % hex(self.cfg.SYNC_BYTE_CODEPOINT))
        if self.wav:
            log.debug("wave pos: %s" % self.wav.pformat_pos())
        yield self.cfg.SYNC_BYTE_CODEPOINT

        log.debug("yield block type '%s'" % self.cfg.BLOCK_TYPE_DICT[block_type])
        yield block_type

        block_length = len(block_codepoints)
        log.debug("yield block length %s (%sBytes)" % (hex(block_length), block_length))
        yield block_length

        if not block_codepoints:
            # EOF block
            # FIXME checksum
            checksum = block_type
            checksum += block_length
            checksum = checksum & 0xFF
            log.debug("yield calculated checksum %s" % hex(checksum))
            yield checksum
            log.debug("yield magic byte %s" % hex(self.cfg.MAGIC_BYTE))
            yield self.cfg.MAGIC_BYTE # 0x55
        else:
            log.debug("content of '%s':" % self.cfg.BLOCK_TYPE_DICT[block_type])
            log.debug("-"*79)
            log.debug(pformat_codepoints(block_codepoints))
            log.debug("-"*79)
            checksum = 0x00
            yield block_codepoints
#             for codepoint in block_codepoints:
#                 checksum += codepoint
#                 yield codepoint

            checksum += block_type
            checksum += block_length
            checksum = checksum & 0xFF
            log.debug("yield calculated checksum %s" % hex(checksum))
            yield checksum
            log.debug("yield magic byte %s" % hex(self.cfg.MAGIC_BYTE))
            yield self.cfg.MAGIC_BYTE # 0x55

    def codepoint_stream(self):
        for file_obj in self.files:
            # yield filename
            for codepoints in self.block2codepoint_stream(
                    block_type=self.cfg.FILENAME_BLOCK,
                    block_codepoints=file_obj.get_filename_block_as_codepoints()
                ):
                yield codepoints

            if self.wav:
                self.wav.write_silence(sec=2)

            # yield file content
            for codepoints in self.block2codepoint_stream(
                block_type=self.cfg.DATA_BLOCK,
                block_codepoints=file_obj.get_code_block_as_codepoints()
                ):
                yield codepoints

            if self.wav:
                self.wav.write_silence(sec=2)

        # yield EOF
        for codepoints in self.block2codepoint_stream(
                block_type=self.cfg.EOF_BLOCK,
                block_codepoints=[]
            ):
            yield codepoints

        if self.wav:
            self.wav.write_silence(sec=2)

    def write_wave(self, wav):
        self.wav = wav # Bitstream2Wave instance
        for codepoint in self.codepoint_stream():
            if isinstance(codepoint, (tuple, list)):
                for item in codepoint:
                    assert isinstance(item, int), "Codepoint %s is not int/hex" % repr(codepoint)
            else:
                assert isinstance(codepoint, int), "Codepoint %s is not int/hex" % repr(codepoint)
            wav.write_codepoint(codepoint)

    def write_cas(self, destination_file):
        log.info("Create %s..." % repr(destination_file))
        with open(destination_file, "wb") as f:
            for codepoint in self.codepoint_stream():
                if isinstance(codepoint, (tuple, list)):
                    for item in codepoint:
                        f.write(chr(item))
                else:
                    f.write(chr(codepoint))
        print "\nFile %s saved." % repr(destination_file)

    def save_bas(self, destination_file):
        dest_filename, dest_ext = os.path.splitext(destination_file)
        for file_obj in self.files:

            bas_filename = file_obj.filename # Filename from CSAVE argument

            out_filename = "%s_%s.bas" % (dest_filename, bas_filename)
            log.info("Create %s..." % repr(out_filename))
            with open(out_filename, "w") as f:
                for line in file_obj.file_content.get_ascii_codeline():
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

#     # bas -> wav
#     subprocess.Popen([sys.executable, "../PyDC_cli.py",
#         "--verbosity=10",
# #         "--verbosity=5",
# #         "--logfile=5",
# #         "--log_format=%(module)s %(lineno)d: %(message)s",
# #         "../test_files/HelloWorld1.bas", "--dst=../test.wav"
#         "../test_files/HelloWorld1.bas", "--dst=../test.cas"
#     ]).wait()
#
#     print "\n"*3
#     print "="*79
#     print "\n"*3

#     # wav -> bas
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
#         "--verbosity=10",
        "--verbosity=7",
#         "../test.wav", "--dst=../test.bas",
        "../test.cas", "--dst=../test.bas",
#         "../test_files/HelloWorld1 origin.wav", "--dst=../test_files/HelloWorld1.bas",
    ]).wait()

    print "-- END --"


