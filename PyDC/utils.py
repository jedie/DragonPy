#!/usr/bin/env python2

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import time


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
        current_rate = float(count) / current_duration
        self.rate_info.append(current_rate)
        self.rate_info = self.rate_info[-self.use_last_rates:]
        smoothed_rate = sum(self.rate_info) / len(self.rate_info)
        rest = self.total - count
        try:
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


if __name__ == "__main__":
    import doctest
    print doctest.testmod()
