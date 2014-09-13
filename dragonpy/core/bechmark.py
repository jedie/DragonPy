#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from dragonlib.utils import six
xrange = six.moves.xrange

import binascii
import io
import locale
import string
import time
import unittest
import logging

from dragonlib.utils import six
from dragonpy.tests.test_6809_program import Test6809_Program, \
    Test6809_Program_Division2
from dragonpy.utils.humanize import locale_format_number


log = logging.getLogger(__name__)


class Test6809_Program2(Test6809_Program):
    def runTest(self):
        pass

    def bench(self, loops, multiply, func, msg):
        print("\n%s benchmark" % msg)

        self.setUp()
        self.cpu.cycles = 0

        txt = string.printable

        if six.PY3:
            txt = bytes(txt, encoding="UTF-8")

        txt = txt * multiply

        print("\nStart %i %s loops with %i Bytes test string..." % (
            loops, msg, len(txt)
        ))

        start_time = time.time()
        for __ in xrange(loops):
            self._crc32(txt)
        duration = time.time() - start_time

        print("%s benchmark runs %s CPU cycles in %.2f sec" % (
            msg, locale_format_number(self.cpu.cycles), duration
        ))

        return duration, self.cpu.cycles

    def crc32_benchmark(self, loops):
        return self.bench(loops, 10, self._crc32, "CRC32")

    def crc16_benchmark(self, loops):
        return self.bench(loops, 20, self._crc16, "CRC16")



def run_benchmark(loops):
    total_duration = 0
    total_cycles = 0
    bench_class = Test6809_Program2()

    #--------------------------------------------------------------------------

    duration, cycles = bench_class.crc16_benchmark(loops)
    total_duration += duration
    total_cycles += cycles

    #--------------------------------------------------------------------------

    duration, cycles = bench_class.crc32_benchmark(loops)
    total_duration += duration
    total_cycles += cycles

    #--------------------------------------------------------------------------
    print("-"*79)
    print("\nTotal of %i benchmak loops run in %.2f sec %s CPU cycles." % (
        loops, total_duration, locale_format_number(total_cycles)
    ))
    print("\tavg.: %s CPU cycles/sec" % locale_format_number(total_cycles / total_duration))


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    # will be done in CLI:
    locale.setlocale(locale.LC_ALL, '') # For Formating cycles/sec number

    run_benchmark(
        loops=1
#        loops=2
#        loops=10
    )
    print(" --- END --- ")
