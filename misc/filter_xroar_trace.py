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
        addr_stat = {} # TODO: Use collections.Counter
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

    def unique(self):
        sys.stderr.write(
            "\nunique %s in %s...\n\n" % (self.infile.name, self.outfile.name)
        )
        unique_addr = set()
        total_skiped_lines = 0
        skip_count = 0
        last_line_no = 0
        next_update = time.time() + 1
        stat_out = False
        for line_no, line in enumerate(self.infile):
            if time.time() > next_update:
                self.outfile.flush()
                if stat_out:
                    sys.stderr.write("\r")
                else:
                    sys.stderr.write("\n")
                sys.stderr.write(
                    "In %i lines (%i/sec.) are %i unique address calls..." % (
                        line_no, (line_no - last_line_no), len(unique_addr)
                    )
                )
                stat_out = True
                sys.stderr.flush()
                last_line_no = line_no
                next_update = time.time() + 1

            addr = line[:4]
            if addr in unique_addr:
                total_skiped_lines += 1
                skip_count += 1
                continue

            unique_addr.add(addr)

            if skip_count != 0:
                if stat_out:
                    # Skip info should not in the same line after stat info
                    sys.stderr.write("\n")
                self.outfile.write(
                    "... [Skip %i lines] ...\n" % skip_count
                )
                skip_count = 0
            self.outfile.write(line)
            stat_out = False

        self.outfile.close()
        sys.stderr.write(
            "%i lines was filtered.\n" % total_skiped_lines
        )

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
        last_line_no = 0
        next_update = time.time() + 1
        for line_no, line in enumerate(self.infile):
            if time.time() > next_update:
                sys.stderr.write(
                    "\rFilter %i lines (%i/sec.)..." % (
                        line_no, (line_no - last_line_no)
                    )
                )
                sys.stderr.flush()
                last_line_no = line_no
                next_update = time.time() + 1

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

    if args.unique:
        xt.unique()
        return

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
    parser.add_argument("--unique",
        action="store_true",
        help="Read infile and store in outfile only unique addresses.",
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


