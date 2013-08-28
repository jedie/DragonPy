#!/usr/bin/env python2
# coding: utf-8

"""
    Python dragon 32 converter
    ==========================

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from wave2bitstream import Wave2Bitstream
from PyDC import BitstreamHandler


__version__ = (0, 1, 0, 'dev')
VERSION_STRING = '.'.join(str(part) for part in __version__)

TITLE_LINE = "PyDC v%s copyleft 2013 by htfx.de - Jens Diemer, GNU GPL v3 or above" % VERSION_STRING


def bas2wav(self):
    raise NotImplementedError("TBD")
    # Create a bitstream from a existing .bas file:
#     c.add_from_bas("test_files/HelloWorld1.bas")
#     c.add_from_bas("test_files/Dragon Data Ltd - Examples from the Manual - 39~58 [run].bas")
#     c.add_from_bas("test_files/LineNumberTest.bas")
#     c.print_debug_info()
#     bitstream = c.get_as_bitstream()


def wav2bas(source_filepath, destination_filepath, cfg):
    # get bitstream generator from WAVE file:
    bitstream = iter(Wave2Bitstream(source_filepath, cfg))

    # store bitstream into python objects
    bh = BitstreamHandler(cfg)
    bh.feed(bitstream)

    # save .bas file
    bh.cassette.save_bas(destination_filepath)



if __name__ == "__main__":
#     import doctest
#     print doctest.testmod(
#         verbose=False
#         # verbose=True
#     )
    print TITLE_LINE

    from configs import Dragon32Config
    cfg = Dragon32Config()
    wav2bas(
        "../test_files/HelloWorld1 origin.wav",
        "../HelloWorld1 origin.bas",
        cfg
    )

    print "\n --- END ---"
