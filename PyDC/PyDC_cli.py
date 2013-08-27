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

from PyDC import TITLE_LINE, VERSION_STRING
from PyDC.CassetteObjects import Cassette
from PyDC.PyDC import BitstreamHandler
from PyDC.configs import Dragon32Config
from PyDC.wave2bitstream import Wave2Bitstream
from PyDC.base_cli import Base_CLI


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
        self.parser.add_argument("dst", help="Destination filename (.wav/.bas)")

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

        self.destination_file = args.dst
        print "destination file..: %s" % self.destination_file

        return args

    def run(self):
        self.args = self.parse_args()

        source_filename, source_ext = os.path.splitext(self.source_file)
        dest_filename, dest_ext = os.path.splitext(self.destination_file)

        source_ext = source_ext.lower()
        dest_ext = dest_ext.lower()

        self.logfilename = dest_filename + ".log"
        self.setup_logging(self.args)

        self.d32cfg = Dragon32Config()

        if source_ext.startswith(".wav") and dest_ext.startswith(".bas"):
            self.wav2bas()
        elif source_ext.startswith(".bas") and dest_ext.startswith(".wav"):
            self.bas2wav()
        else:
            print "ERROR:"
            print "%s to %s ???" % (repr(self.source_file), repr(self.destination_file))
            sys.exit(-1)

    def bas2wav(self):
        raise NotImplementedError("TBD")
        # Create a bitstream from a existing .bas file:
    #     c.add_from_bas("test_files/HelloWorld1.bas")
    #     c.add_from_bas("test_files/Dragon Data Ltd - Examples from the Manual - 39~58 [run].bas")
    #     c.add_from_bas("test_files/LineNumberTest.bas")
    #     c.print_debug_info()
    #     bitstream = c.get_as_bitstream()

    def wav2bas(self):
        # get bitstream from WAVE file:
        st = Wave2Bitstream(self.source_file,
            bit_nul_hz=1200, # "0" is a single cycle at 1200 Hz
            bit_one_hz=2400, # "1" is a single cycle at 2400 Hz
            hz_variation=self.args.hz_variation, # How much Hz can signal scatter to match 1 or 0 bit ?

            min_volume_ratio=self.args.min_volume_ratio, # percent volume to ignore sample
            avg_count=self.args.avg_count, # How many samples should be merged into a average value?
            end_count=self.args.end_count, # Sample count that must be pos/neg at once
            mid_count=self.args.mid_count # Sample count that can be around null
        )
        bitstream = iter(st)

        bh = BitstreamHandler(self.d32cfg)
        bh.feed(bitstream)
        bh.cassette.save_bas(self.destination_file)


if __name__ == "__main__":
#     import doctest
#     print doctest.testmod(
#         verbose=False
#         # verbose=True
#     )

    sys.argv.append("--help")

#     sys.argv.append("test_files/HelloWorld1 origin.wav")
#     sys.argv.append("HelloWorld1 origin.bas")

    cli = PyDC_CLI()
    cli.run()

    print "\n --- END --- \n"
