#!/usr/bin/env python2
# coding: utf-8

"""
    Convert dragon 32 Cassetts WAV files into plain text.
    =====================================================

    Currently ony supported:
        * BASIC programs in tokenised form

    TODO:
        - check BASIC programs in ASCII form: CSAVE "NAME",A
        - detect even_odd startpoint!
        - add cli
        - write .BAS file

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys
import itertools
import logging

log = logging.getLogger("PyDC")


# own modules
from basic_tokens import BASIC_TOKENS, FUNCTION_TOKEN
from utils import find_iter_window, iter_steps, MaxPosArraived, \
    print_bitlist, bits2codepoint, list2str, bitstream2codepoints, get_word, \
    print_codepoint_stream
from wave2bitstream import Wave2Bitstream


BIT_ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
BIT_NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz
MAX_HZ_VARIATION = 1000 # How much Hz can signal scatter to match 1 or 0 bit ?

# Normaly the Dragon LeadIn-Byte is 0x55: "10101010"
# but in worst-case the last null can consume the first
# null of the sync byte.
# We use a reversed version of the LeadIn-Byte to avoid this.
# LEAD_IN_PATTERN = "01010101"
LEAD_IN_PATTERN = [0, 1, 0, 1, 0, 1, 0, 1]
# LEAD_IN_PATTERN = "10101010" # 0x55

# SYNC_BYTE = "00111100" # 0x3C
SYNC_BYTE = [0, 0, 1, 1, 1, 1, 0, 0] # 0x3C

# Block types:
FILENAME_BLOCK = 0x00
DATA_BLOCK = 0x01
EOF_BLOCK = 0xff

BLOCK_TYPE_DICT = {
    FILENAME_BLOCK: "filename block",
    DATA_BLOCK: "data block",
    EOF_BLOCK: "end-of-file block",
}

DISPLAY_BLOCK_COUNT = 8 # How many bit block should be printet in one line?



MIN_SAMPLE_VALUE = 5



def pop_bytes_from_bit_list(bit_list, count):
    """
    >>> bit_str = (
    ... "00110011"
    ... "00001111"
    ... "01010101"
    ... "11001100")
    >>> bit_list = [int(i) for i in bit_str]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 1)
    >>> bytes
    [[0, 0, 1, 1, 0, 0, 1, 1]]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 2)
    >>> bytes
    [[0, 0, 0, 0, 1, 1, 1, 1], [0, 1, 0, 1, 0, 1, 0, 1]]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 1)
    >>> bytes
    [[1, 1, 0, 0, 1, 1, 0, 0]]
    """
    data_bit_count = count * 8

    data_bit_list = bit_list[:data_bit_count]
    data = list(iter_steps(data_bit_list, steps=8))

    bit_list = bit_list[data_bit_count:]
    return bit_list, data




def print_block_table(block_codepoints):
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        character = chr(byte_no)
        print "%s %4s %3s %s" % (
            list2str(block), hex(byte_no), byte_no, repr(character)
        )


def print_as_hex(block_codepoints):
    line = ""
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        character = chr(byte_no)
        line += hex(byte_no)
    print line


def print_as_hex_list(block_codepoints):
    line = []
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        character = chr(byte_no)
        line.append(hex(byte_no))
    print ",".join(line)




LEADER_MAX_POS = 8 * 256 # Max search window for get the Leader-Byte?

def get_block_info(bitstream):

#     bitstream = iter(itertools.islice(bitstream, 2500)) # TEST
#     for i in xrange(119):
#         next(bitstream)
#     print "-"*79
# #     print_bitlist(bitstream, no_repr=True)
#     print_bitlist(bitstream)
#     print "-"*79
#     sys.exit()

    """
    00111100
    00000000
    11110000
    00000100
    00000100


 240 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 248 - 00111100 00000000 11110000 00000100 00000100 00000100 00000100 00000100
 256 - 00000100 00000100 00000100 00000000 00000000 00000000 00000000 00000000
 264 - 00000000 00000000 11110000 10101010 10101010 10101010 10101010 10101010

 240 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
       0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U'
 248 - 00111100 00000000 11110000 00000100 00000100 00000100 00000100 00000100
       0x3c '<'   0x0      0xf    0x20 ' ' 0x20 ' ' 0x20 ' ' 0x20 ' ' 0x20 ' '
 256 - 00000100 00000100 00000100 00000000 00000000 00000000 00000000 00000000
       0x20 ' ' 0x20 ' ' 0x20 ' '   0x0      0x0      0x0      0x0      0x0
 264 - 00000000 00000000 11110000 10101010 10101010 10101010 10101010 10101010
         0x0      0x0      0xf    0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U' 0x55 'U'
    """

    # Searching for lead-in byte
#     try:
#
#         leader_pos = find_iter_window(bitstream, LEAD_IN_PATTERN, LEADER_MAX_POS)
#     except MaxPosArraived, err:
#         print "\nError: Leader-Byte not found in the first %i Bytes! (%s)" % (
#             LEADER_MAX_POS, err
#         )
#         sys.exit(-1)
#     else:
#         print "\nLeader-Byte '%s' found at %i Bytes" % (list2str(LEAD_IN_PATTERN), leader_pos)

#     print "-"*79
#     print_bitlist(bitstream, no_repr=True)
#     print "-"*79
#     sys.exit()

    try:
        sync_pos = find_iter_window(bitstream, SYNC_BYTE, LEADER_MAX_POS)
    except MaxPosArraived, err:
        print "\nError: Sync-Byte not found in the first %i Bytes! (%s)" % (
            LEADER_MAX_POS, err
        )
        sys.exit(-1)
    else:
        print "\nSync-Byte '%s' found at %i Bytes" % (list2str(SYNC_BYTE), sync_pos)

#     print "-"*79
#     print_bitlist(bitstream, no_repr=True)
#     print "-"*79
#     sys.exit()

    """
    00111100 00000000 111100000 00001000 00001000 00001000 00001000 00001000 00001000 00001000

    00111100
    00000000
    11110000
    00000100
    00000100

    0 00001000 00001000 00001000 00001000 00001000
    """

#     print "-"*79
#     print_bitlist(bitstream)
#     print "-"*79
#     sys.exit()

    codepoint_stream = bitstream2codepoints(bitstream)
#     print "-"*79
#     print_codepoint_stream(codepoint_stream)
#     print "-"*79

    block_type = get_word(codepoint_stream)
    print "raw block type:", repr(block_type), hex(block_type)
    block_length = get_word(codepoint_stream)
    print "raw block length:", repr(block_length)

#     sys.exit()

    return block_type, block_length




def bytes2codeline(raw_bytes):
    """
    >>> data = (0x87,0x20,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22)
    >>> bytes2codeline(data)
    'PRINT "HELLO WORLD!"'
    """
    code_line = ""
    func_token = False
    for byte_no in raw_bytes:
        if byte_no == 0xff: # Next byte is a function token
            func_token = True
            continue
        elif func_token == True:
            func_token = False
            character = FUNCTION_TOKEN[byte_no]
        elif byte_no in BASIC_TOKENS:
            character = BASIC_TOKENS[byte_no]
        else:
            character = chr(byte_no)
#         print byte_no, repr(character)
        code_line += character
    return code_line


class CodeLine(object):
    def __init__(self, line_pointer, line_no, code):
        assert isinstance(line_no, int), "Line number not integer, it's: %s" % repr(line_no)
        self.line_pointer = line_pointer
        self.line_no = line_no
        self.code = code

    def __repr__(self):
        return "<CodeLine pointer: %s line no: %s code: %s>" % (
            repr(self.line_pointer), repr(self.line_no), repr(self.code)
        )


class FileContent(object):
    """
    Content (all data blocks) of a cassette file.
    """
    def __init__(self):
        self.code_lines = []

    def add_block_data(self, block_length, data):
        """
        add a block of tokenized BASIC source code lines.

        >>> fc = FileContent()

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

        >>> fc = FileContent()
        >>> data = iter([
        ... 0x1e,0x4a,0x0,0x1e,0x58,0xcb,0x58,0xc3,0x4c,0xc5,0xff,0x88,0x28,0x52,0x29,0x3a,0x59,0xcb,0x59,0xc3,0x4c,0xc5,0xff,0x89,0x28,0x52,0x29,0x0,
        ... 0x0,0x0
        ... ])
        >>> fc.add_block_data(30, data)
        30 Bytes parsed
        >>> fc.print_code_lines()
        30 X=X+L*SIN(R):Y=Y+L*COS(R)


        Test high line numbers

        >>> fc = FileContent()
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
        byte_count = 0
        while True:
            line_pointer = get_word(data)
            byte_count += 2
            if not line_pointer:
                # arrived [0x00, 0x00] -> end of block
                break

            line_number = get_word(data)
            byte_count += 2

            # get the code line:
            # new iterator to get all characters until 0x00 arraived
            code = iter(data.next, 0x00)

            code = list(code) # for len()
            byte_count += len(code) + 1 # from 0x00 consumed in iter()

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
        >>> fc = FileContent()
        >>> fc.add_ascii_block(41, iter(data))
        41 Bytes parsed
        >>> fc.print_code_lines()
        10 PRINT "TEST"
        20 PRINT "HELLO WORLD!"
        """
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
                print "Error splitting linenumber in %s: %s" % (repr(code), err)
                break

            line_number = int(line_number)

            self.code_lines.append(
                CodeLine(None, line_number, code)
            )

        print "%i Bytes parsed" % byte_count
        if block_length != byte_count:
            print "ERROR: Block length value %i is not equal to parsed bytes!" % block_length

    def print_code_lines(self):
        for code_line in self.code_lines:
            print "%i %s" % (code_line.line_no, code_line.code)


class CassetteFile(object):
    """
    Representes a "file name block" and his "data block"

     5.1 An 8 byte program name
     5.2 A file ID byte where:
         00=BASIC program
         01=Data file
         03=Binary file
     5.3 An ASCII flag where:
         00=Binary file
         FF=ASCII file
     5.4 A gap flag to indicate whether the
         data stream is continuous (00) as
         in binary or BASIC files, or in blocks
         where the tape keeps stopping (FF) as
         in data files.
     5.5 Two bytes for the default EXEC address
         of a binary file.
     5.6 Two bytes for the default load address
         of a binary file.
    """
    def __init__(self, file_block_data):
#         print_block_codepoints(block_codepoints)
        print_block_table(block_codepoints)
        print_as_hex_list(file_block_data)

        self.filename = bit_blocks2string(block_codepoints[:8])

        byte_no_block = bit_blocks2codepoint(file_block_data[8:])
        print "file meta:", repr(byte_no_block)

        self.file_type = byte_no_block[0]
        print "file type:", repr(self.file_type)
        if self.file_type == 0x00:
            print "BASIC programm (0x00)"
        elif self.file_type == 0x01:
            print "Data file (0x01)"
            raise NotImplemented("Data files are not supported, yet.")
        elif self.file_type == 0xFF:
            print "Binary file (0xFF)"
            raise NotImplemented("Binary files are not supported, yet.")
        else:
            raise NotImplemented(
                "Unknown file type %s is not supported, yet." % hex(self.file_type)
            )

        ascii_flag = byte_no_block[1]
        print "ASCII Flag is:", repr(ascii_flag)
        if ascii_flag == 0x00:
            print "tokenized BASIC"
            self.is_tokenized = True
        elif ascii_flag == 0xff:
            print "ASCII BASIC"
            self.is_tokenized = False


        self.file_content = FileContent()

    def add_block_data(self, block_length, block_codepoints):
        print "raw data length: %iBytes" % len(block_codepoints)
#         print_as_hex_list(block_codepoints)
        data = iter([bits2codepoint(bit_block) for bit_block in block_codepoints])
        if self.is_tokenized:
            self.file_content.add_block_data(block_length, data)
        else:
            self.file_content.add_ascii_block(block_length, data)
        print "*"*79
        self.file_content.print_code_lines()
        print "*"*79

    def __repr__(self):
        return "<BlockFile '%s'>" % (self.filename,)


class Cassette(object):
    def __init__(self):
        self.files = []
        self.current_file = None

    def add_block(self, block_type, block_length, block_codepoints):
        if block_type == EOF_BLOCK:
            return
        elif block_type == FILENAME_BLOCK:
            self.current_file = CassetteFile(block_codepoints)
            print "Add file %s" % repr(self.current_file)
            self.files.append(self.current_file)
        elif block_type == DATA_BLOCK:
            self.current_file.add_block_data(block_length, block_codepoints)
        else:
            raise TypeError("Block type %s unkown!" & hex(block_type))


def print_bit_list_stats(bit_list):
    """
    >>> print_bit_list_stats([1,1,1,1,0,0,0,0])
    8 Bits: 4 positive bits and 4 negative bits
    """
    print "%i Bits:" % len(bit_list),
    positive_count = 0
    negative_count = 0
    for bit in bit_list:
        if bit == 1:
            positive_count += 1
        elif bit == 0:
            negative_count += 1
        else:
            raise TypeError("Not a bit: %s" % repr(bit))
    print "%i positive bits and %i negative bits" % (positive_count, negative_count)




if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
#     sys.exit()



    # created by Xroar Emulator
#     FILENAME = "HelloWorld1 xroar.wav" # 8Bit 22050Hz
#     Bit 1 min: 1696Hz avg: 2058.3Hz max: 2205Hz variation: 509Hz
#     Bit 0 min: 595Hz avg: 1090.4Hz max: 1160Hz Variation: 565Hz
#     4760 Bits: 2243 positive bits and 2517 negative bits



    # created by origin Dragon 32 machine
    # 16Bit 44.1KHz mono
    FILENAME = "HelloWorld1 origin.wav" # no sync neede
    # Bit 1 min: 1764Hz avg: 2013.9Hz max: 2100Hz variation: 336Hz
    # Bit 0 min: 595Hz avg: 1090.2Hz max: 1336Hz Variation: 741Hz
    # 2710 Bits: 1217 positive bits and 1493 negative bits



    """
    The origin BASIC code of the two WAV file is:

    10 FOR I = 1 TO 10
    20 PRINT I;"HELLO WORLD!"
    30 NEXT I

    The WAV files are here:
    https://github.com/jedie/python-code-snippets/raw/master/CodeSnippets/Dragon%2032/HelloWorld1%20origin.wav
    https://github.com/jedie/python-code-snippets/raw/master/CodeSnippets/Dragon%2032/HelloWorld1%20xroar.wav
    """


    # Test files from:
    # http://archive.worldofdragon.org/archive/index.php?dir=Tapes/Dragon/wav/
#     FILENAME = "Quickbeam Software - Duplicas v3.0.wav" # binary!


    # FILENAME = "Dragon Data Ltd - Examples from the Manual - 39~58 [run].wav"
    # Bit 1 min: 1696Hz avg: 2004.0Hz max: 2004Hz variation: 308Hz
    # Bit 0 min: 1025Hz avg: 1025.0Hz max: 1025Hz Variation: 0Hz
    # 155839 Bits: 73776 positive bits and 82063 negative bits

#     FILENAME = "1_MANIA.WAV" # 148579 frames, 4879 bits (raw)
#     FILENAME = "2_DBJ.WAV" # TODO

    # BASIC file with high line numbers:
#     FILENAME = "LineNumber Test 01.wav" # tokenized BASIC - no sync
#     FILENAME = "LineNumber Test 02.wav" # ASCII BASIC - no sync



    # log_level = LOG_LEVEL_DICT[3] # args.verbosity
    # log.setLevel(log_level)

    # logfilename = FILENAME + ".log" # args.logfile
    # if logfilename:
        # print "Log into '%s'" % logfilename
        # handler = logging.FileHandler(logfilename,
    # #         mode='a',
            # mode='w',
            # encoding="utf8"
        # )
        # handler.setFormatter(LOG_FORMATTER)
        # log.addHandler(handler)

    # if args.stdout_log:
    # handler = logging.StreamHandler()
    # handler.setFormatter(LOG_FORMATTER)
    # log.addHandler(handler)



    st = Wave2Bitstream(FILENAME,
        bit_nul_hz=1200, # "0" is a single cycle at 1200 Hz
        bit_one_hz=2400, # "1" is a single cycle at 2400 Hz
        hz_variation=450, # How much Hz can signal scatter to match 1 or 0 bit ?
    )
    bitstream = iter(st)
    bitstream.sync(32)
    bitstream = itertools.imap(lambda x: x[1], bitstream) # remove frame_no

    # bit_list = array.array('B', bitstream)

    # print "-"*79
    # print_bitlist(bit_list)
    # print "-"*79
#     print_block_table(bit_list)
#     print "-"*79
#     sys.exit()

    cassette = Cassette()

    while True:
        print "_"*79
        block_type, block_length = get_block_info(bitstream)

        print "*** block length:", block_length

        try:
            block_type_name = BLOCK_TYPE_DICT[block_type]
        except KeyError:
            print "ERROR: Block type %s unknown in BLOCK_TYPE_DICT!" % hex(block_type)
            print "-"*79
            print "Debug bitlist:"
            print_bitlist(bitstream)
            print "-"*79
            sys.exit(-1)


        print "*** block type: 0x%x (%s)" % (block_type, block_type_name)

        if block_type == EOF_BLOCK:
            print "EOF-Block found"
            break

        if block_length == 0:
            print "ERROR: block length == 0 ???"
            print "-"*79
            print "Debug bitlist:"
            print_bitlist(bitstream)
            print "-"*79
            sys.exit(-1)

        block_bits = itertools.islice(bitstream, block_length)
        block_codepoints = bitstream2codepoints(block_bits)
#         print "".join([chr(i) for i in block_codepoints])

        cassette.add_block(block_type, block_length, block_codepoints)
        print "="*79


