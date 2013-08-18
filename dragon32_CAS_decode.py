#!/usr/bin/env python2

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

    Spec links:
        http://www.onastick.clara.net/cosio.htm
        http://www.cs.unc.edu/~yakowenk/coco/text/tapeformat.html
        http://dragon32.info/info/basicfmt.html

    Many thanks to the people from:
        http://www.python-forum.de/viewtopic.php?f=1&t=32102 (de)
        http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4231 (en)

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import collections
import wave
import sys
import struct
import time

# own modules
from utils import ProcessInfo, human_duration
from basic_tokens import BASIC_TOKENS, FUNCTION_TOKEN


ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz

LEADER_BYTE = "10101010" # 0x55
SYNC_BYTE = "00111100" # 0x3C

# Block types:
FILENAME_BLOCK = 0x00
DATA_BLOCK = 0x01
EOF_BLOCK = 0xff

BLOCK_TYPE_DICT = {
    FILENAME_BLOCK: "filename block",
    DATA_BLOCK: "data block",
    EOF_BLOCK: "end-of-file block",
}

WAVE_READ_SIZE = 1024 # How many frames should be read from WAVE file at once?
MIN_TOGGLE_COUNT = 3 # How many samples must be in pos/neg to count a cycle?

DISPLAY_BLOCK_COUNT = 8 # How many bit block should be printet in one line?


def iter_steps(g, steps):
    """
    iterate over 'g' in blocks with a length of the given 'step' count.

    >>> for v in iter_steps([1,2,3,4,5], steps=2): v
    [1, 2]
    [3, 4]
    [5]
    >>> for v in iter_steps([1,2,3,4,5,6,7,8,9], steps=3): v
    [1, 2, 3]
    [4, 5, 6]
    [7, 8, 9]

                                 12345678        12345678
                                         12345678
    >>> bits = [int(i) for i in "0101010101010101111000"]
    >>> for v in iter_steps(bits, steps=8): v
    [0, 1, 0, 1, 0, 1, 0, 1]
    [0, 1, 0, 1, 0, 1, 0, 1]
    [1, 1, 1, 0, 0, 0]
    """
    values = []
    for value in g:
        values.append(value)
        if len(values) == steps:
            yield list(values)
            values = []
    if values:
        yield list(values)


def iter_window(g, window_size):
    """
    interate over 'g' bit-by-bit and yield a window with the given 'window_size' width.

    >>> for v in iter_window([1,2,3,4], window_size=2): v
    [1, 2]
    [2, 3]
    [3, 4]
    >>> for v in iter_window([1,2,3,4,5], window_size=3): v
    [1, 2, 3]
    [2, 3, 4]
    [3, 4, 5]

    >>> for v in iter_window([1,2,3,4], window_size=2):
    ...    v
    ...    v.append(True)
    [1, 2]
    [2, 3]
    [3, 4]
    """
    values = collections.deque(maxlen=window_size)
    for value in g:
        values.append(value)
        if len(values) == window_size:
            yield list(values)


def count_sign(values):
    """
    >>> count_sign([3,-1,-2])
    (1, 2)
    >>> count_sign([0,-1])
    (0, 1)
    """
    positive_count = 0
    negative_count = 0
    for value in values:
        if value > 0:
            positive_count += 1
        elif value < 0:
            negative_count += 1
    return positive_count, negative_count


def iter_wave_values(wavefile):
    samplewidth = wavefile.getsampwidth() # i.e 1 for 8-bit samples, 2 for 16-bit samples
    print "samplewidth:", samplewidth
    nchannels = wavefile.getnchannels() # typically 1 for mono, 2 for stereo
    print "channels:", nchannels

    assert nchannels == 1, "Only MONO files are supported, yet!"

    frame_count = wavefile.getnframes() # number of audio frames

    # FIXME
    if samplewidth == 1:
        struct_unpack_str = "b"
    elif samplewidth == 2:
        struct_unpack_str = "<h"
    else:
        raise NotImplementedError("Only sample width 2 or 1 are supported, yet!")
    print "struct_unpack_str:", struct_unpack_str

    frame_no = 0
    while True:
        frames = wavefile.readframes(WAVE_READ_SIZE)
        if not frames:
            break

        for frame in frames:
            frame_no += 1
            frame = struct.unpack(struct_unpack_str, frame)[0]
            yield frame_no, frame




def iter_bits(wavefile, even_odd):
    framerate = wavefile.getframerate() # frames / second
    print "Framerate:", framerate
    frame_count = wavefile.getnframes()
    print "Numer of audio frames:", frame_count

    in_positive = even_odd
    in_negative = not even_odd
    toggle_count = 0 # Counter for detect a complete cycle
    previous_frame_no = 0
    bit_count = 0

    process_info = ProcessInfo(frame_count, use_last_rates=4)
    start_time = time.time()
    next_status = start_time + 0.25

    def _print_status(frame_no, framerate):
        ms = float(frame_no) / framerate
        rest, eta, rate = process_info.update(frame_no)
        sys.stdout.write(
            "\r%i frames readed. Position in WAV: %s - eta: %s (rate: %iFrames/sec)" % (
                frame_no, human_duration(ms), eta, rate
            )
        )

    window_values = collections.deque(maxlen=MIN_TOGGLE_COUNT)
    for frame_no, value in iter_wave_values(wavefile):
        window_values.append(value)
        if len(window_values) >= MIN_TOGGLE_COUNT:
            positive_count, negative_count = count_sign(window_values)

            # print window_values, positive_count, negative_count
            if not in_positive and positive_count == MIN_TOGGLE_COUNT and negative_count == 0:
                # go into a positive sinus area
                in_positive = True
                in_negative = False
                toggle_count += 1
            elif not in_negative and negative_count == MIN_TOGGLE_COUNT and positive_count == 0:
                # go into a negative sinus area
                in_negative = True
                in_positive = False
                toggle_count += 1

            if toggle_count >= 2:
                # a single sinus cycle complete
                toggle_count = 0

                frame_count = frame_no - previous_frame_no
                hz = framerate / frame_count

                dst_one = abs(ONE_HZ - hz)
                dst_nul = abs(NUL_HZ - hz)
                if dst_one < dst_nul:
                    bit_count += 1
                    yield 1
                else:
                    bit_count += 1
                    yield 0

                # ms=float(frame_no)/framerate
                # print "***", bit, hz, "Hz", "%0.5fms" % ms
                previous_frame_no = frame_no

                if time.time() > next_status:
                    next_status = time.time() + 1
                    _print_status(frame_no, framerate)

    _print_status(frame_no, framerate)
    print
    duration = time.time() - start_time
    rate = bit_count / duration / 8 / 1024
    print "%i bits decoded in %s (%.1fKBytes/s)" % (bit_count, human_duration(duration), rate)
    print
    print


def count_continuous_pattern(bits, pattern):
    """
    count 'pattern' matches without ceasing.

    >>> bit_str = (
    ... "00111100"
    ... "00111100"
    ... "0101")
    >>> pos = count_continuous_pattern([int(i) for i in bit_str], "00111100")
    >>> bit_str[pos*8:]
    '0101'
    >>> pos
    2

    >>> count_continuous_pattern([1,1,1,2,3], "1")
    3

    >>> count_continuous_pattern([1,2,3], "99")
    0

    >>> count_continuous_pattern([0,1,0,1], "01")
    2
    """
    pattern_len = len(pattern)
    pattern = [int(i) for i in pattern]
    for count, data in enumerate(iter_steps(bits, pattern_len), 1):
        if data != pattern:
            count -= 1
            break
    return count


def find_iter_window(bit_list, pattern):
    """
    Search for 'pattern' in bit-by-bit steps (iter window)
    and return the number of bits before the 'pattern' match.

    Useable for slicing all bits before the first 'pattern' match:

    >>> bit_str = "111010111"
    >>> pos = find_iter_window([int(i) for i in bit_str], "010")
    >>> bit_str[pos:]
    '010111'
    >>> pos
    3

    >>> find_iter_window([1,1,1], "0")
    0
    >>> find_iter_window([1,0,0], "1")
    0
    >>> find_iter_window([0,1,0], "1")
    1
    >>> find_iter_window([0,0,1], "1")
    2
    """
    pattern_len = len(pattern)
    pattern = [int(i) for i in pattern]
    for pos, data in enumerate(iter_window(bit_list, pattern_len)):
        if data == pattern:
            return pos
    return 0


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


def print_block_bit_list(block_bit_list):
    in_line_count = 0

    line = ""
    for no, block in enumerate(block_bit_list, -DISPLAY_BLOCK_COUNT + 1):
        line += "%s " % list2str(block)
        in_line_count += 1
        if in_line_count >= DISPLAY_BLOCK_COUNT:
            in_line_count = 0
            print "%4s - %s" % (no, line)
            line = ""
    if in_line_count > 0:
        print

def print_bitlist(bit_list):
    block_bit_list = iter_steps(bit_list, steps=8)
    print_block_bit_list(block_bit_list)


def list2str(l):
    """
    >>> list2str([0, 0, 0, 1, 0, 0, 1, 0])
    '00010010'
    """
    return "".join([str(c) for c in l])


def bits2byte_no(bits):
    """
    >>> c = bits2byte_no([0, 0, 0, 1, 0, 0, 1, 0])
    >>> c
    72
    >>> chr(c)
    'H'

    >>> bits2byte_no([0, 0, 1, 1, 0, 0, 1, 0])
    76
    """
    bits = bits[::-1]
    bits = list2str(bits)
    return int(bits, 2)

def byte_list2bit_list(data):
    """
    >>> data = (0x0,0x1e,0x8b,0x20,0x49,0x0)
    >>> byte_list2bit_list(data)
    ['00000000', '01111000', '11010001', '00000100', '10010010', '00000000']
    """
    bit_list = []
    for char in data:
        bits = '{0:08b}'.format(char)
        bits = bits[::-1]
        bit_list.append(bits)
    return bit_list

def block2bytes(block_bit_list):
    bytes = "".join([chr(bits2byte_no(block)) for block in block_bit_list])
    return bytes


def print_block_table(block_bit_list):
    for block in block_bit_list:
        byte_no = bits2byte_no(block)
        character = chr(byte_no)
        print "%s %4s %3s %s" % (
            list2str(block), hex(byte_no), byte_no, repr(character)
        )


def print_as_hex(block_bit_list):
    line=""
    for block in block_bit_list:
        byte_no = bits2byte_no(block)
        character = chr(byte_no)
        line += hex(byte_no)
    print line


def print_as_hex_list(block_bit_list):
    line=[]
    for block in block_bit_list:
        byte_no = bits2byte_no(block)
        character = chr(byte_no)
        line.append(hex(byte_no))
    print ",".join(line)


def get_block_info(bit_list):
    leader_pos = find_iter_window(bit_list, LEADER_BYTE) # Search for LEADER_BYTE in bit-by-bit steps
    print "Start leader '%s' found at position: %i" % (LEADER_BYTE, leader_pos)

    # Cut bits before the first 01010101 start leader
    print "bits before header:", repr(list2str(bit_list[:leader_pos]))
    bit_list = bit_list[leader_pos:]

    leader_count = count_continuous_pattern(bit_list, LEADER_BYTE)
    print "Found %i leader bytes" % leader_count
    if leader_count == 0:
        print "WARNING: leader bytes not found! Maybe 'even_odd' bool wrong???"
    to_cut = leader_count * 8
    bit_list = bit_list[to_cut:]

    sync_pos = find_iter_window(bit_list, SYNC_BYTE) # Search for SYNC_BYTE in bit-by-bit steps
    print "Find sync byte after %i Bits" % sync_pos
    to_cut = sync_pos + 8 # Bits before sync byte + sync byte
    bit_list = bit_list[to_cut:]

    bit_list, bytes = pop_bytes_from_bit_list(bit_list, count=2)

    block_type = bits2byte_no(bytes[0])
    block_length = bits2byte_no(bytes[1])

    return bit_list, block_type, block_length


class CodeLine(object):
    def __init__(self, pre_bytes, line_no, code):
        assert isinstance(line_no, int), "Line number not integer, it's: %s" % repr(line_no)
        self.pre_bytes = pre_bytes
        self.line_no = line_no
        self.code = code

    def __repr__(self):
        return "<CodeLine pre bytes: %s line no: %s code: %s>" % (
            repr(self.pre_bytes), repr(self.line_no), repr(self.code)
        )


class FileContent(object):
    """
    Content (all data blocks) of a cassette file.
    """
    def __init__(self):
        self.code_lines = []

    def add_data_block(self, block_length, block_bit_list):
        """
        >>> fc = FileContent()
        >>> data = (
        ... 0x1e,0x12,0x0,0xa,0x80,0x20,0x49,0x20,0xcb,0x20,0x31,0x20,0xbc,0x20,0x31,0x30,0x0,0x1e,0x29,0x0,0x14,0x87,0x20,0x49,0x3b,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22,0x0,0x1e,0x31,0x0,0x1e,0x8b,0x20,0x49,0x0,0x0,0x0
        ... )
        >>> bit_list=byte_list2bit_list(data)
        >>> fc.add_data_block(0, bit_list)
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10
        20 PRINT I;"HELLO WORLD!"
        30 NEXT I

        >>> fc = FileContent()
        >>> data = (
        ... 0x1e,0x4a,0x0,
        ... 0x1e,0x58,0xcb,0x58,0xc3,0x4c,0xc5,0xff,0x88,0x28,0x52,0x29,0x3a,0x59,0xcb,0x59,0xc3,0x4c,0xc5,0xff,0x89,0x28,0x52,0x29,
        ... 0x0,0x0,0x0
        ... )
        >>> bit_list=byte_list2bit_list(data)
        >>> fc.add_data_block(0, bit_list)
        >>> fc.print_code_lines()
        30 X=X+L*SIN(R):Y=Y+L*COS(R)
        """
        in_code_line = False
        func_token = False
        pre_bytes = []
        line_no = None
        code_line = ""

        raw_bytes = [bits2byte_no(bit_block) for bit_block in block_bit_list]
        for index, byte_no in enumerate(raw_bytes):
#             print index, hex(byte_no)
            if byte_no == 0x00:
                if in_code_line:
                    # print "Add code line", repr(pre_bytes), repr(line_no), repr(code_line)
                    code_line_obj = CodeLine(pre_bytes, line_no, code_line)
                    self.code_lines.append(code_line_obj)
                    pre_bytes = []
                    line_no = None
                    code_line = ""
                    in_code_line = False
                else:
                    if raw_bytes[index:] == [0, 0]:
                        # Next two bytes are 0x00 0x00 -> end of data delimiter
                        break
                    in_code_line = True
            else:
                if in_code_line:
                    if line_no is None:
                        line_no = byte_no
                        continue

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
                    code_line += character
                else:
                    pre_bytes.append(byte_no)

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
    def __init__(self, file_block_bit_list):
#         print_block_bit_list(block_bit_list)
#         print_block_table(block_bit_list)

        self.data = block2bytes(block_bit_list)
        self.filename = self.data[:8]

        self.file_content = FileContent()

    def add_data_block(self, block_length, block_bit_list):
        print_as_hex_list(block_bit_list)
        self.file_content.add_data_block(block_length, block_bit_list)
        print "*"*79
        self.file_content.print_code_lines()
        print "*"*79

    def __repr__(self):
        return "<BlockFile '%s' raw data: %s>" % (self.filename, repr(self.data))


class Cassette(object):
    def __init__(self):
        self.files = []
        self.current_file = None

    def add_block(self, block_type, block_length, block_bit_list):
        if block_type == EOF_BLOCK:
            return
        elif block_type == FILENAME_BLOCK:
            self.current_file = CassetteFile(block_bit_list)
            print "Add file %s" % repr(self.current_file)
            self.files.append(self.current_file)
        elif block_type == DATA_BLOCK:
            self.current_file.add_data_block(block_length, block_bit_list)
        else:
            raise TypeError("Block type %s unkown!" & hex(block_type))





if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
    #~ sys.exit()


    # created by Xroar Emulator
#     FILENAME = "HelloWorld1 xroar.wav"
#     even_odd = False

    # created by origin Dragon 32 machine
#     FILENAME = "HelloWorld1 origin.wav" # 109922 frames, 2735 bits (raw)
#     even_odd = True

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
    #     http://archive.worldofdragon.org/archive/index.php?dir=Tapes/Dragon/wav/
#     FILENAME = "Quickbeam Software - Duplicas v3.0.wav" # binary!
#     even_odd = False

    FILENAME = "Dragon Data Ltd - Examples from the Manual - 39~58 [run].wav"
    even_odd = False

#     FILENAME = "1_MANIA.WAV" # 148579 frames, 4879 bits (raw)
#     FILENAME = "2_DBJ.WAV" # TODO
#     even_odd = False


    print "Read '%s'..." % FILENAME
    wavefile = wave.open(FILENAME, "r")

    print "read..."
    bit_list = list(iter_bits(wavefile, even_odd))

    # print "-"*79
    # print_bitlist(bit_list)
    # print "-"*79
    # print_block_table(bit_list)
    # print "-"*79
    # sys.exit()

    cassette = Cassette()

    while True:
        print "_"*79
        bit_list, block_type, block_length = get_block_info(bit_list)
        try:
            block_type_name = BLOCK_TYPE_DICT[block_type]
        except KeyError:
            print "ERROR: Block type %s unknown in BLOCK_TYPE_DICT!" % hex(block_type)
            print "Maybe 'even_odd' bool wrong???"
            print "-"*79
            print "Debug bitlist:"
            print_bitlist(bit_list)
            print "-"*79
            sys.exit(-1)


        print "*** block type: 0x%x (%s)" % (block_type, block_type_name)
        print "*** block length:", block_length

        if block_type == EOF_BLOCK:
            print "EOF-Block found"
            break

        bit_list, block_bit_list = pop_bytes_from_bit_list(bit_list, count=block_length)

#         print_block_table(block_bit_list)
#         print_block_bit_list(block_bit_list)

        cassette.add_block(block_type, block_length, block_bit_list)
        print "="*79


