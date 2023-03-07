#!/usr/bin/env python2

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import collections
import itertools
import logging
import math
import string
import time
import types
from collections.abc import Iterable


LOG_FORMATTER = logging.Formatter("")  # %(asctime)s %(message)s")
LOG_LEVEL_DICT = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}
LOG_LEVELS = sorted(LOG_LEVEL_DICT.keys())


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration("type error")
    Traceback (most recent call last):
    ...
    TypeError: human_duration() argument must be integer or float

    >>> human_duration(0.01)
    '10.0 ms'
    >>> human_duration(0.9)
    '900.0 ms'
    >>> human_duration(65.5)
    '1.1 min'
    >>> human_duration((60 * 60)-4)
    '59.9 min'
    >>> human_duration(60*60)
    '1.0 hours'
    >>> human_duration(1.05*60*60)
    '1.1 hours'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    '2.5 years'
    """
    if not isinstance(t, (int, float)):
        raise TypeError("human_duration() argument must be integer or float")

    chunks = (
        (60 * 60 * 24 * 365, 'years'),
        (60 * 60 * 24 * 30, 'months'),
        (60 * 60 * 24 * 7, 'weeks'),
        (60 * 60 * 24, 'days'),
        (60 * 60, 'hours'),
    )

    if t < 1:
        return f"{round(t * 1000, 1):.1f} ms"
    if t < 60:
        return f"{round(t, 1):.1f} sec"
    if t < 60 * 60:
        return f"{round(t / 60, 1):.1f} min"

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return f"{count:.1f} {name}"


class ProcessInfo:
    """
    >>> p = ProcessInfo(100)
    >>> p.update(1)[0]
    99
    >>> p = ProcessInfo(100)
    >>> p.update(0)
    (100, '-', 0.0)
    """

    def __init__(self, total, use_last_rates=4):
        self.total = total
        self.use_last_rates = use_last_rates
        self.last_count = 0
        self.last_update = self.start_time = time.time()
        self.rate_info = []

    def update(self, count):
        current_duration = time.time() - self.last_update
        try:
            current_rate = float(count) / current_duration
            self.rate_info.append(current_rate)
            self.rate_info = self.rate_info[-self.use_last_rates:]
            smoothed_rate = sum(self.rate_info) / len(self.rate_info)
            rest = self.total - count
            eta = rest / smoothed_rate
        except ZeroDivisionError:
            # e.g. called before a "count+=1"
            return self.total, "-", 0.0
        human_eta = human_duration(eta)
        return rest, human_eta, smoothed_rate


def average(old_avg, current_value, count):
    """
    Calculate the average. Count must start with 0

    >>> average(None, 3.23, 0)
    3.23
    >>> average(0, 1, 0)
    1.0
    >>> average(2.5, 5, 4)
    3.0
    """
    if old_avg is None:
        return current_value
    return (float(old_avg) * count + current_value) / (count + 1)


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


def count_continuous_pattern(bitstream, pattern):
    """
    >>> pattern = list(bytes2bit_strings("A"))
    >>> bitstream = bytes2bit_strings("AAAXXX")
    >>> count_continuous_pattern(bitstream, pattern)
    3

    >>> pattern = list(bytes2bit_strings("X"))
    >>> bitstream = bytes2bit_strings("AAAXXX")
    >>> count_continuous_pattern(bitstream, pattern)
    0
    """
    assert isinstance(bitstream, (Iterable, types.GeneratorType))
    assert isinstance(pattern, (list, tuple))

    window_size = len(pattern)
    count = -1
    for count, data in enumerate(iter_steps(bitstream, window_size), 1):
        #         print count, data, pattern
        if data != pattern:
            count -= 1
            break

    return count


class MaxPosArraived(Exception):
    pass


class PatternNotFound(Exception):
    pass


def find_iter_window(bitstream, pattern, max_pos=None):
    """
    >>> pattern = list(bytes2bit_strings("B"))
    >>> bitstream = bytes2bit_strings("AAABCCC")
    >>> find_iter_window(bitstream, pattern)
    24
    >>> "".join(list(bitstream2string(bitstream)))
    'CCC'

    >>> find_iter_window(bytes2bit_strings("HELLO!"), list(bytes2bit_strings("LO")))
    24

    >>> find_iter_window(bytes2bit_strings("HELLO!"), list(bytes2bit_strings("LO")), max_pos=16)
    Traceback (most recent call last):
    ...
    PyDC.PyDC.utils.MaxPosArraived: 17

    >>> find_iter_window(bytes2bit_strings("HELLO!"), list(bytes2bit_strings("X")))
    Traceback (most recent call last):
    ...
    PyDC.PyDC.utils.PatternNotFound: 40
    """
    assert isinstance(bitstream, (Iterable, types.GeneratorType))
    assert isinstance(pattern, (list, tuple))

    window_size = len(pattern)
    pos = -1
    for pos, data in enumerate(iter_window(bitstream, window_size)):
        #         print pos, data, pattern
        if data == pattern:
            return pos
        if max_pos is not None and pos > max_pos:
            raise MaxPosArraived(pos)
    raise PatternNotFound(pos)


def count_the_same(iterable, sentinel):
    """
    >>> count_the_same([0x55,0x55,0x55,0x55,0x3C,"foo","bar"],0x55)
    (4, 60)
    >>> 0x3C == 60
    True
    """
    count = 0
    x = None
    for count, x in enumerate(iterable):
        if x != sentinel:
            break
    return count, x


def diff_info(data):
    """
    >>> diff_info([5,5,10,10,5,5,10,10])
    (0, 15)
    >>> diff_info([5,10,10,5,5,10,10,5])
    (15, 0)
    """

    def get_diff(data):
        diff = 0
        for no1, no2 in iter_steps(data, steps=2):
            diff += abs(no1 - no2)
        return diff

    data1 = data[2:]
    diff1 = get_diff(data1)

    data2 = data[1:-1]
    diff2 = get_diff(data2)

    return diff1, diff2


# def iter_pare_sum(data):
#     """
#     >>> def g(data):
#     ...     for no, i in enumerate(data): yield (no, i)
#
#     >>> l = [5,5,10,10,5,5,10,10,5,5,10,10,10,10,5,5,5,5]
#     >>> len(l)
#     18
#     >>> list(iter_pare_sum(g(l)))
#     [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10), (16, 10)]
#
#
#     >>> l = [5,10,10,5,5,10,10,5,5,10,10,10,10,5,5,5,5]
#     >>> len(l)
#     17
#     >>> list(iter_pare_sum(g(l)))
#     [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10), (16, 10)]
#     [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10)]
#     """
#     for previous, current, next_value in itertools.islice(iter_window(data, window_size=3), 0, None, 2):
#         # print previous, current, next_value
#         diff1 = abs(previous[1] - current[1])
#         diff2 = abs(current[1] - next_value[1])
#
#         if diff1 < diff2:
#             yield (current[0], previous[1] + current[1])
#         else:
#             yield (current[0], current[1] + next_value[1])


class TextLevelMeter:
    """
    TODO: Fix DocTest:

    >> tl = TextLevelMeter(255, 9)
    >> tl.feed(0)
    '|   *   |'
    >> tl.feed(128)
    '|   | * |'
    >> tl.feed(255)
    '|   |  *|'
    >> tl.feed(-128)
    '| * |   |'
    >> tl.feed(-255)
    '|*  |   |'

    >> tl = TextLevelMeter(255, 74)
    >> tl.feed(0)
    '|                                   *                                   |'
    >> tl.feed(128)
    '|                                   |                 *                 |'
    >> tl.feed(255)
    '|                                   |                                  *|'
    >> tl.feed(-128)
    '|                 *                 |                                   |'
    >> tl.feed(-255)
    '|*                                  |                                   |'
    """

    def __init__(self, max_value, width):
        self.max_value = max_value

        fill_len = int(round((width - 3) / 2))
        fill = " " * fill_len
        self.source_msg = "|" + fill + "|" + fill + "|"

        self.offset = fill_len + 1
        self.max_width = fill_len

    def feed(self, value):
        value = int(round(
            float(value) / self.max_value * self.max_width + self.offset
        ))
        return self.source_msg[:value] + "*" + self.source_msg[value + 1:]


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


def list2str(data):
    """
    >>> list2str(['a', 'b', 1, 2, 3])
    'ab123'
    """
    return "".join([str(c) for c in data])


def string2codepoint(s):
    """
    >>> codepoints = list(string2codepoint("HELLO"))
    >>> codepoints
    [72, 69, 76, 76, 79]
    >>> ",".join([hex(c) for c in codepoints])
    '0x48,0x45,0x4c,0x4c,0x4f'
    >>> print_codepoint_stream(codepoints) # doctest: +NORMALIZE_WHITESPACE
       5 | 0x48 'H' | 0x45 'E' | 0x4c 'L' | 0x4c 'L' | 0x4f 'O' |
    """
    for char in s:
        yield ord(char)


def bits2codepoint(bits):
    """
    >>> c = bits2codepoint([0, 0, 0, 1, 0, 0, 1, 0])
    >>> c
    72
    >>> chr(c)
    'H'

    >>> bits2codepoint("00010010")
    72

    >>> bits2codepoint([0, 0, 1, 1, 0, 0, 1, 0])
    76
    """
    bit_string = "".join([str(c) for c in reversed(bits)])
    return int(bit_string, 2)


def bitstream2codepoints(bitstream):
    """
    >>> list(bitstream2codepoints([0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0]))
    [72, 65]

    >>> [chr(i) for i in bitstream2codepoints(bytes2bitstream("HALLO!"))]
    ['H', 'A', 'L', 'L', 'O', '!']
    """
    for bits in iter_steps(bitstream, 8):
        yield bits2codepoint(bits)


def bits2string(bits):
    """
    >>> bits2string([0, 0, 0, 1, 0, 0, 1, 0])
    'H'
    >>> bits2string("00010010")
    'H'
    """
    codepoint = bits2codepoint(bits)
    return chr(codepoint)


def bitstream2string(bitstream):
    """
    >>> list(bitstream2string([0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0]))
    ['H', 'A']

    >>> "".join(list(bitstream2string(bytes2bitstream("FooBar !"))))
    'FooBar !'
    """
    for bits in iter_steps(bitstream, 8):
        yield bits2string(bits)


def byte2bit_string(data):
    """
    >>> byte2bit_string("H")
    '00010010'

    >>> byte2bit_string(0x55)
    '10101010'
    """
    if isinstance(data, str):
        assert len(data) == 1
        data = ord(data)

    bits = f'{data:08b}'
    bits = bits[::-1]
    return bits


def codepoints2bitstream(codepoints):
    """
    >>> list(codepoints2bitstream([0x48,0x45]))
    [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0]
    >>> list(codepoints2bitstream(0x48))
    [0, 0, 0, 1, 0, 0, 1, 0]
    """
    if isinstance(codepoints, int):
        codepoints = [codepoints]
    for codepoint in codepoints:
        bit_string = byte2bit_string(codepoint)
        for bit in bit_string:
            yield int(bit)


def byte_list2bit_list(data):
    """
    generator that yield a list

    >>> list(byte_list2bit_list("HELLO!"))
    ['00010010', '10100010', '00110010', '00110010', '11110010', '10000100']

    >>> data = (0x0,0x1e,0x8b,0x20,0x49,0x0)
    >>> list(byte_list2bit_list(data))
    ['00000000', '01111000', '11010001', '00000100', '10010010', '00000000']
    """
    for char in data:
        yield byte2bit_string(char)


def bytes2bit_strings(data):
    """
    generator that yield a list

    >>> list(byte_list2bit_list("HELLO!"))
    ['00010010', '10100010', '00110010', '00110010', '11110010', '10000100']

    >>> data = (0x0,0x1e,0x8b,0x20,0x49,0x0)
    >>> list(byte_list2bit_list(data))
    ['00000000', '01111000', '11010001', '00000100', '10010010', '00000000']
    """
    for char in data:
        yield from byte2bit_string(char)


def bytes2bitstream(data):
    """
    >>> list(bytes2bitstream("H"))
    [0, 0, 0, 1, 0, 0, 1, 0]

    >>> list(bytes2bitstream("HA"))
    [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    """
    for bit_string in bytes2bit_strings(data):
        yield int(bit_string)


def print_codepoint_stream(codepoint_stream, display_block_count=8, no_repr=False):
    """
    >>> def g(txt):
    ...     for c in txt: yield ord(c)
    >>> codepoint_stream = g("HELLO!")
    >>> print_codepoint_stream(codepoint_stream)
    ... # doctest: +NORMALIZE_WHITESPACE
       6 | 0x48 'H' | 0x45 'E' | 0x4c 'L' | 0x4c 'L' | 0x4f 'O' | 0x21 '!' |
    """
    in_line_count = 0

    line = []
    for no, codepoint in enumerate(codepoint_stream, 1):
        r = repr(chr(codepoint))
        if "\\x" in r:  # FIXME
            txt = "%s %i" % (hex(codepoint), codepoint)
        else:
            txt = f"{hex(codepoint)} {r}"

        line.append(txt.center(8))

        in_line_count += 1
        if in_line_count >= display_block_count:
            in_line_count = 0
            print(f"{no:>4} | {' | '.join(line)} |")
            line = []
    if line:
        print(f"{no:>4} | {' | '.join(line)} |")

    if in_line_count > 0:
        print()


def print_as_hex_list(codepoint_stream):
    """
    >>> print_as_hex_list([70, 111, 111, 32, 66, 97, 114, 32, 33])
    0x46,0x6f,0x6f,0x20,0x42,0x61,0x72,0x20,0x21
    """
    print(",".join([hex(codepoint) for codepoint in codepoint_stream]))


def pformat_codepoints(codepoints):
    """
    >>> l = pformat_codepoints([13, 70, 111, 111, 32, 66, 97, 114, 32, 33, 13])
    >>> repr(l)
    "['\\\\r', 'Foo Bar !', '\\\\r']"
    """
    printable = string.printable.replace("\n", "").replace("\r", "")
    line = []
    strings = ""
    for codepoint in codepoints:
        char = chr(codepoint)
        if char in printable:
            strings += char
        else:
            if strings != "":
                line.append(strings)
                strings = ""
            line.append(char)
    return line


def print_block_bit_list(block_bit_list, display_block_count=8, no_repr=False):
    """
    >>> bit_list = (
    ... [0,0,1,1,0,0,1,0], # L
    ... [1,0,0,1,0,0,1,0], # I
    ... )
    >>> print_block_bit_list(bit_list)
    ... # doctest: +NORMALIZE_WHITESPACE
       2 - 00110010 10010010
           0x4c 'L' 0x49 'I'
    """
    def print_line(no, line, line_info):
        print(f"{no:>4} - {line}")
        if no_repr:
            return

        line = []
        for codepoint in line_info:
            r = repr(chr(codepoint))
            if "\\x" in r:  # FIXME
                txt = f"{hex(codepoint)}"
            else:
                txt = f"{hex(codepoint)} {r}"
            txt = txt.center(8)
            line.append(txt)

        print(f"       {' '.join(line)}")

    in_line_count = 0

    line = ""
    line_info = []
    for no, bits in enumerate(block_bit_list, 1):
        line += f"{''.join([str(c) for c in bits])} "

        codepoint = bits2codepoint(bits)
        line_info.append(codepoint)

        in_line_count += 1
        if in_line_count >= display_block_count:
            in_line_count = 0
            print_line(no, line, line_info)
            line_info = []
            line = ""
    if line:
        print_line(no, line, line_info)

    if in_line_count > 0:
        print()


def print_bitlist(bitstream, no_repr=False):
    """
    >>> bitstream = bytes2bitstream("Hallo World!")
    >>> print_bitlist(bitstream)
    ... # doctest: +NORMALIZE_WHITESPACE
       8 - 00010010 10000110 00110110 00110110 11110110 00000100 11101010 11110110
           0x48 'H' 0x61 'a' 0x6c 'l' 0x6c 'l' 0x6f 'o' 0x20 ' ' 0x57 'W' 0x6f 'o'
      12 - 01001110 00110110 00100110 10000100
           0x72 'r' 0x6c 'l' 0x64 'd' 0x21 '!'

    >>> bitstream = bytes2bitstream("Hallo World!")
    >>> print_bitlist(bitstream, no_repr=True)
    ... # doctest: +NORMALIZE_WHITESPACE
       8 - 00010010 10000110 00110110 00110110 11110110 00000100 11101010 11110110
      12 - 01001110 00110110 00100110 10000100
    """
    block_bit_list = iter_steps(bitstream, steps=8)
    print_block_bit_list(block_bit_list, no_repr=no_repr)


def get_word(byte_iterator):
    """
    return a uint16 value

    >>> g=iter([0x1e, 0x12])
    >>> v=get_word(g)
    >>> v
    7698
    >>> hex(v)
    '0x1e12'
    """
    byte_values = list(itertools.islice(byte_iterator, 2))
    try:
        word = (byte_values[0] << 8) | byte_values[1]
    except TypeError as err:
        raise TypeError(f"Can't build word from {repr(byte_values)}: {err}")
    return word


def codepoints2string(codepoints):
    """
    >>> codepoints = [ord(c) for c in "Foo Bar !"]
    >>> codepoints
    [70, 111, 111, 32, 66, 97, 114, 32, 33]
    >>> codepoints2string(codepoints)
    'Foo Bar !'
    """
    return "".join([chr(c) for c in codepoints])


def sinus_values(count, max_value):
    """
    >>> values = list(sinus_values(10, 32768))
    >>> len(values)
    10
    >>> values
    [0, 21063, 32270, 28378, 11207, -11207, -28378, -32270, -21063, 0]

    >>> tl = TextLevelMeter(32768, width=40)
    >>> for v in values:
    ...     tl.feed(v)
    '|                  *                  |'
    '|                  |           *      |'
    '|                  |                 *|'
    '|                  |               *  |'
    '|                  |     *            |'
    '|            *     |                  |'
    '|  *               |                  |'
    '|*                 |                  |'
    '|      *           |                  |'
    '|                  *                  |'
    """
    count -= 1
    for index in range(0, count + 1):
        angle = 360.0 / count * index
        y = math.sin(math.radians(angle)) * max_value
        y = int(round(y))
        yield y


def sinus_values_by_hz(framerate, hz, max_value):
    """
    Create sinus values with the given framerate and Hz.
    Note:
    We skip the first zero-crossing, so the values can be used directy in a loop.

    >>> values = sinus_values_by_hz(22050, 1200, 255)
    >>> len(values) # 22050 / 1200Hz = 18,375
    18
    >>> values
    (87, 164, 221, 251, 251, 221, 164, 87, 0, -87, -164, -221, -251, -251, -221, -164, -87, 0)

    >>> tl = TextLevelMeter(255, width=40)
    >>> for v in values:
    ...     tl.feed(v)
    '|                  |     *            |'
    '|                  |           *      |'
    '|                  |               *  |'
    '|                  |                 *|'
    '|                  |                 *|'
    '|                  |               *  |'
    '|                  |           *      |'
    '|                  |     *            |'
    '|                  *                  |'
    '|            *     |                  |'
    '|      *           |                  |'
    '|  *               |                  |'
    '|*                 |                  |'
    '|*                 |                  |'
    '|  *               |                  |'
    '|      *           |                  |'
    '|            *     |                  |'
    '|                  *                  |'

    >>> values = sinus_values_by_hz(44100, 1200, 255)
    >>> len(values) # 44100 / 1200Hz = 36,75
    37
    """
    count = int(round(float(framerate) / float(hz)))
    count += 1
    values = tuple(sinus_values(count, max_value))
    values = values[1:]
    return values


def hz2duration(hz, framerate):
    """
    >>> hz2duration(hz=1200, framerate=44100)
    37
    >>> hz2duration(hz=2400, framerate=44100)
    18
    """
    return int(round(float(framerate) / hz))


def duration2hz(duration, framerate):
    """
    >>> duration2hz(duration=37, framerate=44100)
    1192
    >>> duration2hz(duration=18, framerate=44100)
    2450
    """
    return int(round(float(framerate) / duration))


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
