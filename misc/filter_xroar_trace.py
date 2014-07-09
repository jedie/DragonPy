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

    def load_tracefile(self, f):
        sys.stderr.write(
            "\nRead %s...\n\n" % f.name
        )
        addr_stat = {}
        next_update = time.time() + 0.5
        line_no = 0 # e.g. empty file
        for line_no, line in enumerate(f):
            if time.time() > next_update:
                sys.stderr.write(
                    "\rAnalyzed %i op calls..." % line_no
                )
                sys.stderr.flush()
                next_update = time.time() + 0.5

            addr = line[:4]
            addr_stat.setdefault(addr, 0)
            addr_stat[addr] += 1

        f.seek(0) # if also used in self.filter()

        sys.stderr.write(
            "\rAnalyzed %i op calls, complete.\n" % line_no
        )
        sys.stderr.write(
            "\nThe tracefile contains %i unique addresses.\n" % len(addr_stat)
        )
        return addr_stat

    def display_addr_stat(self, addr_stat, display_max=None):
        if display_max is None:
            sys.stdout.write(
                "\nList of all called addresses:\n"
            )
        else:
            sys.stdout.write(
                "List of the %i most called addresses:\n" % display_max
            )

        for no, data in enumerate(sorted(self.addr_stat.items(), key=lambda x: x[1], reverse=True)):
            if display_max is not None and no >= display_max:
                break
            sys.stdout.write(
                "\tAddress %s called %s times.\n" % data
            )

    def get_max_count_filter(self, addr_stat, max_count=10):
        sys.stderr.write(
            "Filter addresses with more than %i calls:\n" % max_count
        )
        addr_filter = {}
        for addr, count in self.addr_stat.items():
            if count >= max_count:
                addr_filter[addr] = count
        return addr_filter

    def filter(self, addr_filter):
        sys.stderr.write(
            "Filter %i addresses.\n" % len(addr_filter)
        )
        total_skiped_lines = 0
        skip_count = 0
        for line in self.infile:
            addr = line[:4]
            if addr in addr_filter:
                total_skiped_lines += 1
                skip_count += 1
                continue

            if skip_count != 0:
                self.outfile.write(
                    "... [Skip %i lines] ...\n" % skip_count
                )
                skip_count = 0
            self.outfile.write(line)

        self.outfile.close()
        sys.stderr.write(
            "%i lines was filtered.\n" % total_skiped_lines
        )


def main(args):
    xt = XroarTraceFilter(args.infile, args.outfile)
    if args.loop_filter:
        addr_stat = xt.load_tracefile(args.loop_filter)
        xt.filter(addr_filter=addr_stat)

    if "display" in args:
        addr_stat = xt.load_tracefile(args.infile)
        xt.display_addr_stat(addr_stat,
            display_max=args.display
        )

    if args.filter:
        addr_stat = xt.load_tracefile(args.infile)
        addr_filter = xt.get_max_count_filter(addr_stat,
            max_count=args.filter
        )
        xt.filter(addr_filter)


def get_cli_args():
    parser = argparse.ArgumentParser(description="Filter Xroar traces")
    parser.add_argument("infile", nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Xroar trace file or stdin"
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
    parser.add_argument("--loop-filter", metavar="FILENAME",
        type=argparse.FileType("r"),
        nargs="?",
        help="Live Filter with given address file.",
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_cli_args()
    main(args)


