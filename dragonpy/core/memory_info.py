#!/usr/bin/env python

"""
    DragonPy - base memory info
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import sys

class BaseMemoryInfo(object):
    def __init__(self, out_func):
        self.out_func = out_func

    def get_shortest(self, addr):
        shortest = None
        size = sys.maxsize
        for start, end, txt in self.MEM_INFO:
            if not start <= addr <= end:
                continue

            current_size = abs(end - start)
            if current_size < size:
                size = current_size
                shortest = start, end, txt

        if shortest is None:
            return "$%x: UNKNOWN" % addr

        start, end, txt = shortest
        if start == end:
            return "$%x: %s" % (addr, txt)
        else:
            return "$%x: $%x-$%x - %s" % (addr, start, end, txt)

    def __call__(self, addr, info="", shortest=True):
        if shortest:
            mem_info = self.get_shortest(addr)
            if info:
                self.out_func("%s: %s" % (info, mem_info))
            else:
                self.out_func(mem_info)
            return

        mem_info = []
        for start, end, txt in self.MEM_INFO:
            if start <= addr <= end:
                mem_info.append(
                    (start, end, txt)
                )

        if not mem_info:
            self.out_func("%s $%x: UNKNOWN" % (info, addr))
        else:
            self.out_func("%s $%x:" % (info, addr))
            for start, end, txt in mem_info:
                if start == end:
                    self.out_func(" * $%x - %s" % (start, txt))
                else:
                    self.out_func(" * $%x-$%x - %s" % (start, end, txt))
