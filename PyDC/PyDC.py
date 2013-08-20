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

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import collections
import wave
import sys
import time
import array
import functools
import itertools

try:
    import audioop
except ImportError, err:
    # e.g. PyPy, see: http://bugs.pypy.org/msg4430
    print "Can't use audioop:", err
    audioop = None

# own modules
from utils import ProcessInfo, human_duration, average
from basic_tokens import BASIC_TOKENS, FUNCTION_TOKEN


BIT_ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
BIT_NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz
MAX_HZ_VARIATION = 1000 # How much Hz can signal scatter to match 1 or 0 bit ?

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

# WAVE_RESAMPLE = 22050 # Downsample wave file to this sample rate
# WAVE_RESAMPLE = 11025 # Downsample wave file to this sample rate
# WAVE_RESAMPLE = 8000 # Downsample wave file to this sample rate

WAVE_RESAMPLE = None # Don't change sample rate

WAVE_READ_SIZE = 16 * 1024 # How many frames should be read from WAVE file at once?
WAV_ARRAY_TYPECODE = {
    1: "b", #  8-bit wave file
    2: "h", # 16-bit wave file
    4: "l", # 32-bit wave file TODO: Test it
}
MIN_TOGGLE_COUNT = 4 # How many samples must be in pos/neg to count a cycle?

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


def iter_wave_values(wavefile):
    """
    generator that yield integers for WAVE files.

    returned sample values are in this ranges:
         8-bit:        -255..255
        16-bit:      -32768..32768
        32-bit: -2147483648..2147483647
    """
    nchannels = wavefile.getnchannels() # typically 1 for mono, 2 for stereo
    assert nchannels == 1, "Only MONO files are supported, yet!"
    samplewidth = wavefile.getsampwidth() # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples

    try:
        typecode = WAV_ARRAY_TYPECODE[samplewidth]
    except KeyError:
        raise NotImplementedError(
            "Only %s wave files are supported, yet!" % ", ".join(["%sBit" % (i * 8) for i in WAV_ARRAY_TYPECODE.keys()])
        )

    def _print_status(frame_no, framerate):
        ms = float(frame_no) / framerate
        rest, eta, rate = process_info.update(frame_no)
        sys.stdout.write(
            "\r%i frames (wav pos:%s) eta: %s (rate: %iFrames/sec)   " % (
                frame_no, human_duration(ms), eta, rate
            )
        )

    framerate = wavefile.getframerate() # frames / second
    frame_count = wavefile.getnframes()

    process_info = ProcessInfo(frame_count, use_last_rates=4)
    start_time = time.time()
    next_status = start_time + 0.25

    new_rate = None
    if audioop is not None and WAVE_RESAMPLE is not None and framerate > WAVE_RESAMPLE:
        new_rate = WAVE_RESAMPLE
        print "resample from %iHz/sec. to %sHz/sec" % (framerate, new_rate)
        framerate = WAVE_RESAMPLE

    frame_no = 0
    ratecv_state = None

    get_wave_block_func = functools.partial(wavefile.readframes, WAVE_READ_SIZE)
    for frames in iter(get_wave_block_func, ""):

        if new_rate is not None:
            # downsample the wave file
            # FIXME! See: http://www.python-forum.de/viewtopic.php?f=11&t=6118&p=244377#p244377
            print "before:", len(frames), new_rate
            frames, ratecv_state = audioop.ratecv(
                frames, samplewidth, nchannels, framerate, new_rate, ratecv_state, 1, 1
            )
            print "after:", len(frames), new_rate

        if time.time() > next_status:
            next_status = time.time() + 1
            _print_status(frame_no, framerate)

        for value in array.array(typecode, frames):
            frame_no += 1
            yield frame_no, value

    _print_status(frame_no, framerate)
    print


MIN_SAMPLE_VALUE = 5
def count_sign(values, min_value):
    """
    >>> count_sign([3,-1,-2], 0)
    (1, 2)
    >>> count_sign([3,-1,-2], 2)
    (1, 0)
    >>> count_sign([0,-1],0)
    (0, 1)
    """
    positive_count = 0
    negative_count = 0
    for value in values:
        if value > min_value:
            positive_count += 1
        elif value < -min_value:
            negative_count += 1
    return positive_count, negative_count


def samples2bits(samples, framerate, frame_count, even_odd):
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
            "\r%i frames (wav pos:%s) eta: %s (rate: %iFrames/sec)   " % (
                frame_no, human_duration(ms), eta, rate
            )
        )

    window_values = collections.deque(maxlen=MIN_TOGGLE_COUNT)

    # Fill window deque
    for frame_no, value in samples[:MIN_TOGGLE_COUNT]:
        window_values.append(value)

    bit_one_min_hz = BIT_ONE_HZ - MAX_HZ_VARIATION
    bit_one_max_hz = BIT_ONE_HZ + MAX_HZ_VARIATION

    bit_nul_min_hz = BIT_NUL_HZ - MAX_HZ_VARIATION
    bit_nul_max_hz = BIT_NUL_HZ + MAX_HZ_VARIATION

    one_hz_count = 0
    one_hz_min = sys.maxint
    one_hz_avg = None
    one_hz_max = 0
    nul_hz_count = 0
    nul_hz_min = sys.maxint
    nul_hz_avg = None
    nul_hz_max = 0

    old_status = (-1, -1)
    for frame_no, value in samples[MIN_TOGGLE_COUNT:]:
        window_values.append(value)

        new_status = count_sign(window_values, MIN_SAMPLE_VALUE)
        if new_status == old_status:
            # ignore the frame if status not changed
#             print new_status, "skip"
            continue
        positive_count, negative_count = old_status = new_status

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
        else:
#             print "wrong:", positive_count, negative_count
            continue

        if toggle_count >= 2:
            # a single sinus cycle complete
            toggle_count = 0

            frame_count = frame_no - previous_frame_no
            previous_frame_no = frame_no
            hz = framerate / frame_count
#             print "%sHz" % hz

            if hz > bit_one_min_hz and hz < bit_one_max_hz:
#                 print "bit 1"
                bit_count += 1
                yield 1
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif hz > bit_nul_min_hz and hz < bit_nul_max_hz:
#                 print "bit 0"
                bit_count += 1
                yield 0
                nul_hz_count += 1
                if hz < nul_hz_min:
                    nul_hz_min = hz
                if hz > nul_hz_max:
                    nul_hz_max = hz
                nul_hz_avg = average(nul_hz_avg, hz, nul_hz_count)
            else:
                print "Skip signal with %sHz." % hz
                continue

            if time.time() > next_status:
                next_status = time.time() + 1
                _print_status(frame_no, framerate)

    _print_status(frame_no, framerate)
    print
    duration = time.time() - start_time
    rate = bit_count / duration / 8 / 1024
    print "%i bits decoded from %i audio samples in %s (%.1fKBytes/s)" % (
        bit_count, frame_no, human_duration(duration), rate
    )
    print
    print "Bit 1: %s-%sHz avg: %.1fHz variation: %sHz" % (
        one_hz_min, one_hz_max, one_hz_avg, one_hz_max - one_hz_min
    )
    print "Bit 0: %s-%sHz avg: %.1fHz variation: %sHz" % (
        nul_hz_min, nul_hz_max, nul_hz_avg, nul_hz_max - nul_hz_min
    )


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
    line = ""
    for block in block_bit_list:
        byte_no = bits2byte_no(block)
        character = chr(byte_no)
        line += hex(byte_no)
    print line


def print_as_hex_list(block_bit_list):
    line = []
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


def to16bit(values):
    """
    >>> v = to16bit([0x1e, 0x12])
    >>> v
    7698
    >>> hex(v)
    '0x1e12'
    """
    return (values[0] << 8) | values[1]


def get_until(g, until):
    """
    >>> g=iter([1,2,3,4,5])
    >>> r=get_until(g, 3)
    >>> list(r)
    [1, 2]
    """
    while True:
        item = g.next()
        if item == until:
            raise StopIteration()
        yield item


def get_16bit_char(g):
    """
    >>> g=iter([0x1e, 0x12])
    >>> v=get_16bit_char(g)
    >>> v
    7698
    >>> hex(v)
    '0x1e12'
    """
    values = itertools.islice(g, 2)
    values = list(values)
    return to16bit(values)


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

    def add_data_block(self, block_length, block_bit_list):
        """
        >>> fc = FileContent()

        >>> block = byte_list2bit_list([
        ... 0x1e,0x12,0x0,0xa,0x80,0x20,0x49,0x20,0xcb,0x20,0x31,0x20,0xbc,0x20,0x31,0x30,0x0,
        ... 0x0,0x0])
        >>> fc.add_data_block(0,block)
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10

        >>> block = byte_list2bit_list([
        ... 0x1e,0x29,0x0,0x14,0x87,0x20,0x49,0x3b,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22,0x0,
        ... 0x0,0x0])
        >>> fc.add_data_block(0,block)
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10
        20 PRINT I;"HELLO WORLD!"

        >>> block = byte_list2bit_list([
        ... 0x1e,0x31,0x0,0x1e,0x8b,0x20,0x49,0x0,
        ... 0x0,0x0])
        >>> fc.add_data_block(0,block)
        >>> fc.print_code_lines()
        10 FOR I = 1 TO 10
        20 PRINT I;"HELLO WORLD!"
        30 NEXT I


        Test function tokens in code

        >>> fc = FileContent()
        >>> data = (
        ... 0x1e,0x4a,0x0,0x1e,0x58,0xcb,0x58,0xc3,0x4c,0xc5,0xff,0x88,0x28,0x52,0x29,0x3a,0x59,0xcb,0x59,0xc3,0x4c,0xc5,0xff,0x89,0x28,0x52,0x29,0x0,
        ... 0x0,0x0
        ... )
        >>> bit_list=byte_list2bit_list(data)
        >>> fc.add_data_block(0, bit_list)
        >>> fc.print_code_lines()
        30 X=X+L*SIN(R):Y=Y+L*COS(R)


        Test high line numbers

        >>> fc = FileContent()
        >>> data = (
        ... 0x1e,0x1a,0x0,0x1,0x87,0x20,0x22,0x4c,0x49,0x4e,0x45,0x20,0x4e,0x55,0x4d,0x42,0x45,0x52,0x20,0x54,0x45,0x53,0x54,0x22,0x0,
        ... 0x1e,0x23,0x0,0xa,0x87,0x20,0x31,0x30,0x0,
        ... 0x1e,0x2d,0x0,0x64,0x87,0x20,0x31,0x30,0x30,0x0,
        ... 0x1e,0x38,0x3,0xe8,0x87,0x20,0x31,0x30,0x30,0x30,0x0,
        ... 0x1e,0x44,0x27,0x10,0x87,0x20,0x31,0x30,0x30,0x30,0x30,0x0,
        ... 0x1e,0x50,0x80,0x0,0x87,0x20,0x33,0x32,0x37,0x36,0x38,0x0,
        ... 0x1e,0x62,0xf9,0xff,0x87,0x20,0x22,0x45,0x4e,0x44,0x22,0x3b,0x36,0x33,0x39,0x39,0x39,0x0,0x0,0x0
        ... )
        >>> bit_list=byte_list2bit_list(data)
        >>> fc.add_data_block(0, bit_list)
        >>> fc.print_code_lines()
        1 PRINT "LINE NUMBER TEST"
        10 PRINT 10
        100 PRINT 100
        1000 PRINT 1000
        10000 PRINT 10000
        32768 PRINT 32768
        63999 PRINT "END";63999
        """
        data = iter([bits2byte_no(bit_block) for bit_block in block_bit_list])
        while True:
            line_pointer = list(itertools.islice(data, 2))
            if line_pointer == [0x00, 0x00]:
                # end of block
                break
            line_pointer = to16bit(line_pointer)

            line_number = get_16bit_char(data)

            code = get_until(data, 0x00)
            code = bytes2codeline(code)

            self.code_lines.append(
                CodeLine(line_pointer, line_number, code)
            )

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
        print_block_table(block_bit_list)
        print_as_hex_list(file_block_bit_list)

        self.data = block2bytes(block_bit_list)
        self.filename = self.data[:8]

        self.file_type = self.data[8]
        print "file type:", repr(self.file_type),
#         if self.file_type == 0x00:
#             print "BASIC programm"
#         if self.file_type == 0x00:

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

#     even_odd = False # correct:
#     Bit 1 min: 1696Hz avg: 2058.3Hz max: 2205Hz variation: 509Hz
#     Bit 0 min: 595Hz avg: 1090.4Hz max: 1160Hz Variation: 565Hz
#     4760 Bits: 2243 positive bits and 2517 negative bits

#     even_odd = True # wrong:
#     Bit 1 min: 1470Hz avg: 1487.5Hz max: 2205Hz variation: 735Hz
#     Bit 0 min: 689Hz avg: 1332.3Hz max: 1378Hz Variation: 689Hz
#     4760 Bits: 2404 positive bits and 2356 negative bits



    # created by origin Dragon 32 machine
    # 16Bit 44.1KHz mono
#     FILENAME = "HelloWorld1 origin.wav" # 109922 frames, 2735 bits (raw)
#     even_odd = True # correct:
    # Bit 1 min: 1764Hz avg: 2013.9Hz max: 2100Hz variation: 336Hz
    # Bit 0 min: 595Hz avg: 1090.2Hz max: 1336Hz Variation: 741Hz
    # 2710 Bits: 1217 positive bits and 1493 negative bits

#     even_odd = False # wrong:
    # Bit 1 min: 1422Hz avg: 1461.5Hz max: 2100Hz variation: 678Hz
    # Bit 0 min: 459Hz avg: 1265.1Hz max: 1378Hz Variation: 919Hz
    # 2712 Bits: 1723 positive bits and 989 negative bits



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


#     FILENAME = "Dragon Data Ltd - Examples from the Manual - 39~58 [run].wav"
#     even_odd = False # correct:
    # Bit 1 min: 1696Hz avg: 2004.0Hz max: 2004Hz variation: 308Hz
    # Bit 0 min: 1025Hz avg: 1025.0Hz max: 1025Hz Variation: 0Hz
    # 155839 Bits: 73776 positive bits and 82063 negative bits

#     even_odd = True # wrong:
    # Bit 1 min: 2004Hz avg: 2004.5Hz max: 2940Hz variation: 936Hz
    # Bit 0 min: 1025Hz avg: 1330.1Hz max: 1378Hz Variation: 353Hz
    # 155840 Bits: 4018 positive bits and 151822 negative bits


#     FILENAME = "1_MANIA.WAV" # 148579 frames, 4879 bits (raw)
#     FILENAME = "2_DBJ.WAV" # TODO
#     even_odd = False

    # BASIC file with high line numbers:
    FILENAME = "LineNumber Test 01.wav"
    even_odd = True


    print "Read '%s'..." % FILENAME
    wavefile = wave.open(FILENAME, "r")

    framerate = wavefile.getframerate() # frames / second
    print "Framerate:", framerate
    frame_count = wavefile.getnframes()
    print "Number of audio frames:", frame_count
    nchannels = wavefile.getnchannels() # typically 1 for mono, 2 for stereo
    print "channels:", nchannels
    assert nchannels == 1, "Only MONO files are supported, yet!"
    samplewidth = wavefile.getsampwidth() # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples
    print "samplewidth: %i (%sBit wave file)" % (samplewidth, samplewidth * 8)

    start_time = time.time()
    print "Read wave file...",
    wave_samples = list(iter_wave_values(wavefile))
    print "DONE in %s" % human_duration(time.time() - start_time)

    print "Convert WAVE samples to binary data..."
    bit_generator = samples2bits(wave_samples, framerate, frame_count, even_odd)
    bit_list = array.array('B', bit_generator) # 1.1sec 17KB/s

    print_bit_list_stats(bit_list)

#     print "-"*79
#     print_bitlist(bit_list)
#     print "-"*79
#     print_block_table(bit_list)
#     print "-"*79
#     sys.exit()

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


