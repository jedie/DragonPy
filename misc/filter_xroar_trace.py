#!/usr/bin/env python
# encoding:utf-8

"""
    Filter Xroar trace files.

    see README for more information.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import time
import sys
import argparse


class XroarTraceFilter(object):
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile
        self.addr_stat = self.stat_trace()

    def stat_trace(self):
        print
        print "Read %s..." % self.infile.name
        print
        stat = {}
        next_update = time.time() + 1
        line_no = 0 # e.g. empty file
        for line_no, line in enumerate(self.infile):
            if time.time() > next_update:
                print "Analyzed %i op calls..." % line_no
                next_update = time.time() + 1

            addr = line.split("|", 1)[0]
            stat.setdefault(addr, 0)
            stat[addr] += 1

        print "Analyzed %i op calls, complete." % line_no
        print
        print "The tracefile contains %i unique addresses." % len(stat)
        print
        return stat

    def display_addr_stat(self, display_max=None):
        if display_max is None:
            print "List of all called addresses:"
        else:
            print "List of the %i most called addresses:" % display_max

        for no, data in enumerate(sorted(self.addr_stat.items(), key=lambda x: x[1], reverse=True)):
            if display_max is not None and no >= display_max:
                break
            print "Address: $%s called %s times." % data

    def filter(self, max_count=10):
        print
        print "Filter with %i:" % max_count

        to_stdout = self.outfile.name == "<stdout>" # FIXME
        if not to_stdout:
            print "Create file %r..." % self.outfile.name

        assert self.infile.name != self.outfile.name # FIXME

        total_skiped_lines = 0
        skip_count = 0
        self.infile.seek(0)
        for line in self.infile:
            addr = line.split("|", 1)[0]
            addr_count = self.addr_stat[addr]
            if addr_count > max_count:
                total_skiped_lines += 1
                skip_count += 1
                continue
            if skip_count != 0:
                self.outfile.write(
                    "... [Skip %i lines] ...\n" % skip_count
                )
                skip_count = 0
            self.outfile.write(line)

        if not to_stdout:
            self.outfile.close()

        print
        print "%i lines was filtered." % total_skiped_lines


def main(args):
    xt = XroarTraceFilter(args.infile, args.outfile)
    if "display" in args:
        xt.display_addr_stat(
            display_max=args.display
        )
    if args.filter:
        xt.filter(
            max_count=args.filter
        )


def get_cli_args():
    parser = argparse.ArgumentParser(description="Filter Xroar traces")
    parser.add_argument("infile",
        type=argparse.FileType("r"),
        help="Xroar trace file."
    )
    parser.add_argument("outfile", nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="If given: write output in a new file else: Display it."
    )
    parser.add_argument("--display", metavar="MAX",
        type=int, default=argparse.SUPPRESS,
        nargs="?",
        help="Display statistics how often a address is called.",
    )
    parser.add_argument("--filter", metavar="MAX",
        type=int,
        nargs="?",
        help="Filter the trace: skip addresses that called more than given count.",
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_cli_args()
    main(args)


