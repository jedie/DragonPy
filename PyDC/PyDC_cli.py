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

from PyDC import TITLE_LINE, VERSION_STRING, analyze, convert
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
        self.cfg = Dragon32Config()

        self.parser.add_argument("src", help="Source filename (.wav/.cas/.bas)")
        self.parser.add_argument("--dst",
            help="Destination filename (.wav/.cas/.bas)"
        )

        self.parser.add_argument(
            "--analyze", action="store_true",
            help=(
                "Display zeror crossing information in the given wave file."
            )
        )

        # For Wave2Bitstream():
        self.parser.add_argument(
            "--bit_one_hz", type=int, default=self.cfg.BIT_ONE_HZ,
            help=(
                "Frequency of bit '1' in Hz"
                " (default: %s)"
            ) % self.cfg.BIT_ONE_HZ
        )
        self.parser.add_argument(
            "--bit_nul_hz", type=int, default=self.cfg.BIT_NUL_HZ,
            help=(
                "Frequency of bit '0' in Hz"
                " (default: %s)"
            ) % self.cfg.BIT_NUL_HZ
        )

        self.parser.add_argument(
            "--hz_variation", type=int, default=self.cfg.HZ_VARIATION,
            help=(
                "How much Hz can signal scatter to match 1 or 0 bit ?"
                " (default: %s)"
            ) % self.cfg.HZ_VARIATION
        )

        self.parser.add_argument(
            "--min_volume_ratio", type=int, default=self.cfg.MIN_VOLUME_RATIO,
            help="percent volume to ignore sample (default: %s)" % self.cfg.MIN_VOLUME_RATIO
        )
        self.parser.add_argument(
            "--avg_count", type=int, default=self.cfg.AVG_COUNT,
            help=(
                "How many samples should be merged into a average value?"
                " (default: %s)"
            ) % self.cfg.AVG_COUNT
        )
        self.parser.add_argument(
            "--end_count", type=int, default=self.cfg.END_COUNT,
            help=(
                "Sample count that must be pos/neg at once"
                " (default: %s)"
            ) % self.cfg.END_COUNT
        )
        self.parser.add_argument(
            "--mid_count", type=int, default=self.cfg.MID_COUNT,
            help=(
                "Sample count that can be around null"
                " (default: %s)"
            ) % self.cfg.MID_COUNT
        )

        self.parser.add_argument(
            "--case_convert", action="store_true",
            help=(
                "Convert to uppercase if source is .bas"
                " and to lowercase if destination is .bas"
            )
        )

    def parse_args(self):
        args = super(PyDC_CLI, self).parse_args()

        self.source_file = args.src
        print("source file.......: %s" % self.source_file)

        if args.dst:
            self.destination_file = args.dst
            print("destination file..: %s" % self.destination_file)

        return args

    def run(self):
        self.args = self.parse_args()

        source_filename = os.path.splitext(self.source_file)[0]
        if self.args.dst:
            dest_filename = os.path.splitext(self.destination_file)[0]
            self.logfilename = dest_filename + ".log"
        else:
            self.logfilename = source_filename + ".log"
        log.info("Logfile: %s" % self.logfilename)

        self.setup_logging(self.args) # XXX: setup logging after the logfilename is set!

        self.cfg.BIT_ONE_HZ = self.args.bit_one_hz # Frequency of bit '1' in Hz
        self.cfg.BIT_NUL_HZ = self.args.bit_nul_hz # Frequency of bit '0' in Hz
        self.cfg.HZ_VARIATION = self.args.hz_variation # How much Hz can signal scatter to match 1 or 0 bit ?

        self.cfg.MIN_VOLUME_RATIO = self.args.min_volume_ratio # percent volume to ignore sample
        self.cfg.AVG_COUNT = self.args.avg_count # How many samples should be merged into a average value?
        self.cfg.END_COUNT = self.args.end_count # Sample count that must be pos/neg at once
        self.cfg.MID_COUNT = self.args.mid_count # Sample count that can be around null

        self.cfg.case_convert = self.args.case_convert

        if self.args.analyze:
            analyze(self.source_file, self.cfg)
        else:
            convert(self.source_file, self.destination_file, self.cfg)


if __name__ == "__main__":
    cli = PyDC_CLI()
    cli.run()

    print("\n --- END --- \n")
