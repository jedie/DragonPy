#!/usr/bin/env python
# encoding:utf-8

"""
    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import time
import sys

XROAR_TRACE = os.path.expanduser("~/xroar_trace.txt")

class XroarTraceFilter(object):
    def __init__(self, filename):
        self.filename = filename
        self.addr_stat = self.stat_trace()

    def stat_trace(self):
        print "Analyze %s..." % self.filename
        stat = {}
        next_update = time.time() + 1
        with open(self.filename, "r") as f:
            for line in f:
                if time.time() > next_update:
                    print "Analyzed %i lines..." % len(stat)
    #                 sys.stdout.write(".")
    #                 sys.stdout.flush()
                    next_update = time.time() + 1

                addr = line.split("|", 1)[0]
                stat.setdefault(addr, 0)
                stat[addr] += 1

        print "Analyzed %i lines, complete." % len(stat)
        print
        return stat

    def display_addr_stat(self, display_max=None):
        for no, data in enumerate(sorted(self.addr_stat.items(), key=lambda x: x[1], reverse=True)):
            if display_max and no >= display_max:
                break
            print "Address: %s exist %s times" % data

    def filter(self, max_count=10):
        with open(self.filename, "r") as f:
            skip_count = 0
            for line in f:
                addr = line.split("|", 1)[0]
                addr_count = self.addr_stat[addr]
                if addr_count > max_count:
                    skip_count += 1
                    continue
                if skip_count != 0:
                    print "... [Skip %i lines] ..." % skip_count
                    skip_count = 0
                print line.strip()



xt = XroarTraceFilter(XROAR_TRACE)
xt.display_addr_stat(
    display_max=100
)
xt.filter(
    max_count=10
)


