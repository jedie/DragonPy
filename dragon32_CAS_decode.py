#!/usr/bin/env python2

"""
    Convert dragon 32 Cassetts WAV files into plain text.
    =====================================================

    In current state only the bits would be decoded, yet!

    TODO:
        detect even_odd startpoint!

    Interesting links:
        http://www.onastick.clara.net/cosio.htm
        http://www.cs.unc.edu/~yakowenk/coco/text/tapeformat.html

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

MIN_TOGGLE_COUNT = 3 # How many samples must be in pos/neg to count a cycle?

DISPLAY_BLOCK_COUNT = 8 # How many bit block should be printet in one line?

BASIC_TOKENS = {
    128: " FOR ", # 0x80
    129: " GO ", # 0x81
    130: " REM ", # 0x82
    131: "'", # 0x83
    132: " ELSE ", # 0x84
    133: " IF ", # 0x85
    134: " DATA ", # 0x86
    135: " PRINT ", # 0x87
    136: " ON ", # 0x88
    137: " INPUT ", # 0x89
    138: " END ", # 0x8a
    139: " NEXT ", # 0x8b
    140: " DIM ", # 0x8c
    141: " READ ", # 0x8d
    142: " LET ", # 0x8e
    143: " RUN ", # 0x8f
    144: " RESTORE ", # 0x90
    145: " RETURN ", # 0x91
    146: " STOP ", # 0x92
    147: " POKE ", # 0x93
    148: " CONT ", # 0x94
    149: " LIST ", # 0x95
    150: " CLEAR ", # 0x96
    151: " NEW ", # 0x97
    152: " DEF ", # 0x98
    153: " CLOAD ", # 0x99
    154: " CSAVE ", # 0x9a
    155: " OPEN ", # 0x9b
    156: " CLOSE ", # 0x9c
    157: " LLIST ", # 0x9d
    158: " SET ", # 0x9e
    159: " RESET ", # 0x9f
    160: " CLS ", # 0xa0
    161: " MOTOR ", # 0xa1
    162: " SOUND ", # 0xa2
    163: " AUDIO ", # 0xa3
    164: " EXEC ", # 0xa4
    165: " SKIPF ", # 0xa5
    166: " DELETE ", # 0xa6
    167: " EDIT ", # 0xa7
    168: " TRON ", # 0xa8
    169: " TROFF ", # 0xa9
    170: " LINE ", # 0xaa
    171: " PCLS ", # 0xab
    172: " PSET ", # 0xac
    173: " PRESET ", # 0xad
    174: " SCREEN ", # 0xae
    175: " PCLEAR ", # 0xaf
    176: " COLOR ", # 0xb0
    177: " CIRCLE ", # 0xb1
    178: " PAINT ", # 0xb2
    179: " GET ", # 0xb3
    180: " PUT ", # 0xb4
    181: " DRAW ", # 0xb5
    182: " PCOPY ", # 0xb6
    183: " PMODE ", # 0xb7
    184: " PLAY ", # 0xb8
    185: " DLOAD ", # 0xb9
    186: " RENUM ", # 0xba
    187: " TAB(", # 0xbb
    188: " TO ", # 0xbc
    189: " SUB ", # 0xbd
    190: " FN ", # 0xbe
    191: " THEN ", # 0xbf
    192: " NOT ", # 0xc0
    193: " STEP ", # 0xc1
    194: " OFF ", # 0xc2
    195: "+", # 0xc3
    196: "-", # 0xc4
    197: "*", # 0xc5
    198: "/", # 0xc6
    199: "^", # 0xc7
    200: " AND ", # 0xc8
    201: " OR ", # 0xc9
    202: ">", # 0xca
    203: "=", # 0xcb
    204: "<", # 0xcc
    205: " USING ", # 0xcd
}

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

    for frame_no in xrange(frame_count):
        frame = wavefile.readframes(1)
        if not frame:
            break

        frame = struct.unpack(struct_unpack_str, frame)[0]

        yield frame_no, frame


def iter_bits(wavefile, even_odd):
    framerate = wavefile.getframerate() # frames / second
    print "Framerate:", framerate

    in_positive = even_odd
    in_negative = not even_odd
    toggle_count = 0 # Counter for detect a complete cycle
    previous_frame_no = 0

    window_values = collections.deque(maxlen=MIN_TOGGLE_COUNT)
    for frame_no, value in iter_wave_values(wavefile):
        # ms=float(frame_no)/framerate
        # print "%i %0.5fms %i" % (frame_no, ms, value)

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
                    yield 1
                else:
                    yield 0

                # ms=float(frame_no)/framerate
                # print "***", bit, hz, "Hz", "%0.5fms" % ms
                previous_frame_no = frame_no


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


def block2bytes(block_bit_list):
    bytes = "".join([chr(bits2byte_no(block)) for block in block_bit_list])
    return bytes


def block2ascii(block_bit_list):
    for block in block_bit_list:
        byte_no = bits2byte_no(block)

        if byte_no in BASIC_TOKENS:
            character = BASIC_TOKENS[byte_no]
        else:
            character = chr(byte_no)

        print "%s %4s %3s %s" % (
            list2str(block), hex(byte_no), byte_no, repr(character)
        )


def get_block_info(bit_list):
    leader_pos = find_iter_window(bit_list, LEADER_BYTE) # Search for LEADER_BYTE in bit-by-bit steps
    print "Start leader '%s' found at position: %i" % (LEADER_BYTE, leader_pos)

    # Cut bits before the first 01010101 start leader
    print "bits before header:", repr(list2str(bit_list[:leader_pos]))
    bit_list = bit_list[leader_pos:]

    leader_count = count_continuous_pattern(bit_list, LEADER_BYTE)
    print "Found %i leader bytes" % leader_count
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


class FilenameBlock(object):
    """
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
    def __init__(self, block_bit_list):
        print_block_bit_list(block_bit_list)
        block2ascii(block_bit_list)

        self.data = block2bytes(block_bit_list)
        self.filename = self.data[:8]

    def __repr__(self):
        return "<BlockFile '%s' raw data: %s>" % (self.filename, repr(self.data))


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
#     sys.exit()


    # created by Xroar Emulator
    FILENAME = "HelloWorld1 xroar.wav"
    even_odd = False

    # created by origin Dragon 32 machine
#     FILENAME = "HelloWorld1 origin.wav"
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

    print "Read '%s'..." % FILENAME
    wavefile = wave.open(FILENAME, "r")

    frame_count = wavefile.getnframes()
    print "Numer of audio frames:", frame_count

    print "read..."
    bit_list = list(iter_bits(wavefile, even_odd))
    print "%i bits decoded." % len(bit_list)
    print


    # print "-"*79
    # print_bitlist(bit_list)
    # print "-"*79
    # block2ascii(bit_list)
    # print "-"*79
    # sys.exit()

    while True:
        print "="*79
        bit_list, block_type, block_length = get_block_info(bit_list)
        print "*** block type: 0x%x (%s)" % (block_type, BLOCK_TYPE_DICT[block_type])
        print "*** block length:", block_length

        if block_type == EOF_BLOCK:
            print "end of file."
            break

        bit_list, block_bit_list = pop_bytes_from_bit_list(bit_list, count=block_length)

        if block_type == FILENAME_BLOCK:
            file_block = FilenameBlock(block_bit_list)
            print repr(file_block)
            continue

        print_block_bit_list(block_bit_list)
        print "-"*79
        block2ascii(block_bit_list)
        print "="*79


