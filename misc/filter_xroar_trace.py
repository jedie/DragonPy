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

        for no, data in enumerate(sorted(list(self.addr_stat.items()), key=lambda x: x[1], reverse=True)):
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
        for addr, count in list(self.addr_stat.items()):
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

    def start_stop(self, start_addr, stop_addr):
        sys.stderr.write(
            "\nFilter starts with $%x and ends with $%x from %s in %s...\n\n" % (
                start_addr, stop_addr,
                self.infile.name, self.outfile.name
            )
        )

        all_addresses = set()
        passed_addresses = set()

        start_seperator = "\n ---- [ START $%x ] ---- \n" % start_addr
        end_seperator = "\n ---- [ END $%x ] ---- \n" % stop_addr

        last_line_no = 0
        next_update = time.time() + 1
        stat_out = False
        in_area = False
        for line_no, line in enumerate(self.infile):
            try:
                addr = int(line[:4], 16)
            except ValueError:
                continue

            passed_addresses.add(addr)

            if in_area:
                self.outfile.write(line)
                stat_out = False

                if addr == stop_addr:
                    sys.stderr.flush()
                    self.outfile.flush()

                    sys.stderr.write(end_seperator)
                    self.outfile.write(end_seperator)

                    sys.stderr.flush()
                    self.outfile.flush()
                    in_area = False
                continue
            else:
                if addr == start_addr:
                    sys.stderr.flush()
                    self.outfile.flush()

                    sys.stderr.write(start_seperator)
                    self.outfile.write(start_seperator)
                    in_area = True

                    self.outfile.write(line)

                    sys.stderr.flush()
                    self.outfile.flush()
                    stat_out = False
                    continue

                if time.time() > next_update:
                    self.outfile.flush()
                    if stat_out:
                        sys.stderr.write("\r")
                    else:
                        sys.stderr.write("\n")
                    sys.stderr.write(
                        "process %i lines (%i/sec.), wait for $%x..." % (
                            line_no, (line_no - last_line_no), start_addr,
                        )
                    )
                    passed_addresses -= all_addresses
                    if passed_addresses:
                        all_addresses.update(passed_addresses)
                        passed_addresses = ",".join(["$%x" % i for i in passed_addresses])
                        sys.stderr.write(
                            "\nPassed unique addresses: %s\n" % passed_addresses
                        )
                        passed_addresses = set()
                    else:
                        stat_out = True

                    sys.stderr.flush()
                    last_line_no = line_no
                    next_update = time.time() + 1

        self.outfile.close()


def main(args):
    xt = XroarTraceFilter(args.infile, args.outfile)

    if args.unique:
        xt.unique()
        return

    if args.start_stop:
        xt.start_stop(*args.start_stop)
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


def start_stop_value(arg):
    start_raw, stop_raw = arg.split("-")
    start = int(start_raw.strip("$ "), 16)
    stop = int(stop_raw.strip("$ "), 16)
    sys.stderr.write("Use: $%x-$%x" % (start, stop))
    return (start, stop)


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

    parser.add_argument("--start-stop", metavar="START-STOP",
        type=start_stop_value,
        nargs="?",
        help="Enable trace only from $START to $STOP e.g.: --area=$4000-$5000",
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
#    sys.argv += ["--area=broken"]
#    sys.argv += ["--area=1234-5678"]
    args = get_cli_args()
    main(args)


