#!/usr/bin/env python2
# encoding:utf-8

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time
import collections
import itertools
import logging


LOG_FORMATTER = logging.Formatter("") # %(asctime)s %(message)s")
LOG_LEVEL_DICT = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration("type error")
    Traceback (most recent call last):
    ...
    TypeError: human_duration() argument must be integer or float

    >>> human_duration(0.01)
    u'10.0 ms'
    >>> human_duration(0.9)
    u'900.0 ms'
    >>> human_duration(65.5)
    u'1.1 min'
    >>> human_duration((60 * 60)-1)
    u'59.0 min'
    >>> human_duration(60*60)
    u'1.0 hours'
    >>> human_duration(1.05*60*60)
    u'1.1 hours'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    u'2.5 years'
    """
    if not isinstance(t, (int, float)):
        raise TypeError("human_duration() argument must be integer or float")

    chunks = (
      (60 * 60 * 24 * 365, u'years'),
      (60 * 60 * 24 * 30, u'months'),
      (60 * 60 * 24 * 7, u'weeks'),
      (60 * 60 * 24, u'days'),
      (60 * 60, u'hours'),
    )

    if t < 1:
        return u"%.1f ms" % round(t * 1000, 1)
    if t < 60:
        return u"%.1f sec" % round(t, 1)
    if t < 60 * 60:
        return u"%.1f min" % round(t / 60, 1)

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return u"%(number).1f %(type)s" % {'number': count, 'type': name}


class ProcessInfo(object):
    """
    >>> p = ProcessInfo(100)
    >>> p.update(1)[0]
    99
    >>> p = ProcessInfo(100)
    >>> p.update(0)
    (100, u'-', 0.0)
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
            return self.total, u"-", 0.0
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

# def match_count(g, pattern):
#     """
#     >>> match_count([, pattern)
#     """
#     # Searching for lead-in byte
#     leader_pos = find_iter_window(bit_list, LEAD_IN_PATTERN) # Search for LEAD_IN_PATTERN in bit-by-bit steps
#     print "Start leader '%s' found at position: %i" % (LEAD_IN_PATTERN, leader_pos)
#
#     # Cut bits before the first 01010101 start leader
#     print "bits before header:", repr(list2str(bit_list[:leader_pos]))
#     bit_list = bit_list[leader_pos:]
#
#     # count lead-in byte matches without ceasing to get faster to the sync-byte
#     leader_count = count_continuous_pattern(bit_list, LEAD_IN_PATTERN)

def diff_info(data):
    """
    >>> diff_info([5,5,10,10,5,5,10,10])
    (0, 15)
    >>> diff_info([5,10,10,5,5,10,10,5])
    (15, 0)
    """
    def get_diff(l):
        diff = 0
        for no1, no2 in iter_steps(l, steps=2):
            diff += abs(no1 - no2)
        return diff

    data1 = data[2:]
    diff1 = get_diff(data1)

    data2 = data[1:-1]
    diff2 = get_diff(data2)

    return diff1, diff2


def iter_pare_sum(data):
    """
    >>> def g(data):
    ...     for no, i in enumerate(data): yield (no, i)

    >>> l = [5,5,10,10,5,5,10,10,5,5,10,10,10,10,5,5,5,5]
    >>> len(l)
    18
    >>> list(iter_pare_sum(g(l)))
    [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10), (16, 10)]


    >>> l = [5,10,10,5,5,10,10,5,5,10,10,10,10,5,5,5,5]
    >>> len(l)
    17
    >>> list(iter_pare_sum(g(l)))
    [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10), (16, 10)]
    [(2, 20), (4, 10), (6, 20), (8, 10), (10, 20), (12, 20), (14, 10)]
    """
    for previous, current, next_value in itertools.islice(iter_window(data, window_size=3), 0, None, 2):
        # ~ print previous, current, next_value
        diff1 = abs(previous[1] - current[1])
        diff2 = abs(current[1] - next_value[1])

        if diff1 < diff2:
            yield (current[0], previous[1] + current[1])
        else:
            yield (current[0], current[1] + next_value[1])


def list2str(l):
    """
    >>> list2str([0, 0, 0, 1, 0, 0, 1, 0])
    '00010010'
    """
    return "".join([str(c) for c in l])

def print_block_bit_list(block_bit_list, display_block_count=8):
    in_line_count = 0

    line = ""
    for no, block in enumerate(block_bit_list, -display_block_count + 1):
        line += "%s " % list2str(block)
        in_line_count += 1
        if in_line_count >= display_block_count:
            in_line_count = 0
            print "%4s - %s" % (no, line)
            line = ""
    if in_line_count > 0:
        print

def print_bitlist(bit_list):
    block_bit_list = iter_steps(bit_list, steps=8)
    print_block_bit_list(block_bit_list)


class TextLevelMeter(object):
    """
    >>> tl = TextLevelMeter(255, 9)
    >>> tl.feed(0)
    '|   *   |'
    >>> tl.feed(128)
    '|   | * |'
    >>> tl.feed(255)
    '|   |  *|'
    >>> tl.feed(-128)
    '| * |   |'
    >>> tl.feed(-255)
    '|*  |   |'

    >>> tl = TextLevelMeter(255, 74)
    >>> tl.feed(0)
    '|                                   *                                   |'
    >>> tl.feed(128)
    '|                                   |                 *                 |'
    >>> tl.feed(255)
    '|                                   |                                  *|'
    >>> tl.feed(-128)
    '|                 *                 |                                   |'
    >>> tl.feed(-255)
    '|*                                  |                                   |'
    """
    def __init__(self, max_value, width):
        self.max_value = max_value

        fill_len = int(round(((width - 3) / 2)))
        fill = " " * fill_len
        self.source_msg = "|" + fill + "|" + fill + "|"

        self.offset = fill_len + 1
        self.max_width = fill_len

    def feed(self, value):
        value = int(round(
            float(value) / self.max_value * self.max_width + self.offset
        ))
        return self.source_msg[:value] + "*" + self.source_msg[value + 1:]


if __name__ == "__main__":
    import doctest
    print doctest.testmod()


    # ~ import math

    # ~ count = 32
    # ~ max_value = 255
    # ~ width = 79

    # ~ tl = TextLevelMeter(max_value, width)
    # ~ for index in xrange(0, count + 1):
        # ~ angle = 360.0 / count * index
        # ~ y = math.sin(math.radians(angle)) * max_value
        # ~ y = round(y)
        # ~ print tl.feed(y)
    # ~ #     print "%i - %.1f� %i" % (index, angle, y)
