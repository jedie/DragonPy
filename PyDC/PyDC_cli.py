#!/usr/bin/env python
# coding: utf-8

"""
    Python dragon 32 converter - commandline interface
    ==================================================

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys

from PyDC import TITLE_LINE, VERSION_STRING, wav2bas, bas2wav, analyze, bas2cas, \
    cas2bas
from PyDC.base_cli import Base_CLI
from PyDC.configs import Dragon32Config


log = logging.getLogger("PyDC")


class PyDC_CLI(Base_CLI):
    LOG_NAME = "PyDC"
    DESCRIPTION = "Python dragon 32 converter"
    EPOLOG = TITLE_LINE
    VERSION = VERSION_STRING
    LOG_FORMATTER = logging.Formatter("%(message)s") # %(asctime)s %(message)s")

    def __init__(self):
        super(PyDC_CLI, self).__init__()

        self.parser.add_argument("src", help="Source filename (.wav/.bas)")
        self.parser.add_argument("--dst",
            help="Destination filename (.wav/.bas/.cas)"
        )

        self.parser.add_argument(
            "--analyze", action="store_true",
            help=(
                "Display zeror crossing information in the given wave file."
            )
        )

        # For Wave2Bitstream():
        self.parser.add_argument(
            "--hz_variation", type=int, default=450,
            help=(
                "How much Hz can signal scatter to match 1 or 0 bit ?"
                " (default: 450)"
            )
        )
        self.parser.add_argument(
            "--min_volume_ratio", type=int, default=5,
            help="percent volume to ignore sample (default: 5)"
        )
        self.parser.add_argument(
            "--avg_count", type=int, default=0,
            help=(
                "How many samples should be merged into a average value?"
                " (default: 0)"
            )
        )
        self.parser.add_argument(
            "--end_count", type=int, default=2,
            help=(
                "Sample count that must be pos/neg at once"
                " (default: 2)"
            )
        )
        self.parser.add_argument(
            "--mid_count", type=int, default=1,
            help=(
                "Sample count that can be around null"
                " (default: 1)"
            )
        )

    def parse_args(self):
        args = super(PyDC_CLI, self).parse_args()

        self.source_file = args.src
        print "source file.......: %s" % self.source_file

        if args.dst:
            self.destination_file = args.dst
            print "destination file..: %s" % self.destination_file

        return args

    def run(self):
        self.args = self.parse_args()

        source_filename, source_ext = os.path.splitext(self.source_file)
        source_ext = source_ext.lower()

        if self.args.dst:
            dest_filename, dest_ext = os.path.splitext(self.destination_file)
            dest_ext = dest_ext.lower()

            self.logfilename = dest_filename + ".log"
        else:
            self.logfilename = source_filename + ".log"
        log.info("Logfile: %s" % self.logfilename)

        self.setup_logging(self.args) # XXX: setup logging after the logfilename is set!

        self.cfg = Dragon32Config()

        self.cfg.HZ_VARIATION = self.args.hz_variation # How much Hz can signal scatter to match 1 or 0 bit ?
        self.cfg.MIN_VOLUME_RATIO = self.args.min_volume_ratio # percent volume to ignore sample
        self.cfg.AVG_COUNT = self.args.avg_count # How many samples should be merged into a average value?
        self.cfg.END_COUNT = self.args.end_count # Sample count that must be pos/neg at once
        self.cfg.MID_COUNT = self.args.mid_count # Sample count that can be around null

        if self.args.analyze:
            analyze(self.source_file, self.cfg)

        elif source_ext.startswith(".wav") and dest_ext.startswith(".bas"):
            wav2bas(self.source_file, self.destination_file, self.cfg)
        elif source_ext.startswith(".bas") and dest_ext.startswith(".wav"):
            bas2wav(self.source_file, self.destination_file, self.cfg)

        elif source_ext.startswith(".bas") and dest_ext.startswith(".cas"):
            bas2cas(self.source_file, self.destination_file, self.cfg)
        elif source_ext.startswith(".cas") and dest_ext.startswith(".bas"):
            cas2bas(self.source_file, self.destination_file, self.cfg)

        else:
            print "ERROR:"
            print "%s to %s ???" % (repr(self.source_file), repr(self.destination_file))
            sys.exit(-1)


if __name__ == "__main__":
    cli = PyDC_CLI()
    cli.run()

    print "\n --- END --- \n"
