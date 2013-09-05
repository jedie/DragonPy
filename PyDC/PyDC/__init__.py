#!/usr/bin/env python2
# coding: utf-8

"""
    Python dragon 32 converter
    ==========================

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from CassetteObjects import Cassette
from bitstream_handler import BitstreamHandler, CasStream, BytestreamHandler
from utils import print_bitlist
from wave2bitstream import Wave2Bitstream, Bitstream2Wave
import sys


__version__ = (0, 1, 0, 'dev')
VERSION_STRING = '.'.join(str(part) for part in __version__)

TITLE_LINE = "PyDC v%s copyleft 2013 by htfx.de - Jens Diemer, GNU GPL v3 or above" % VERSION_STRING


def analyze(wave_file, cfg):
    wb = Wave2Bitstream(wave_file, cfg)
    wb.analyze()

def bas2cas(source_filepath, destination_filepath, cfg):
    """
    Create a .cas file from a existing .bas file
    """
    c = Cassette(cfg)
    c.add_from_bas(source_filepath)
    c.print_debug_info()
    c.write_cas(destination_filepath)


def cas2bas(source_filepath, destination_filepath, cfg):
    """
    Read .cas file and create a .bas file
    """
    cas_stream = CasStream(source_filepath)
    bh = BytestreamHandler(cfg)
    bh.feed(cas_stream)

    # save .bas file
    bh.cassette.save_bas(destination_filepath)

#     c = Cassette(cfg)
#     c.add_from_cas(source_filepath)
#     c.print_debug_info()
#     c.save_bas(destination_filepath)


def bas2wav(source_filepath, destination_filepath, cfg):
    """
    Create a wave file from a existing .bas file
    """
    c = Cassette(cfg)

    c.add_from_bas(source_filepath)
    c.print_debug_info()

    wav = Bitstream2Wave(destination_filepath, cfg)

    c.write_wave(wav)

    wav.close()




def wav2bas(source_filepath, destination_filepath, cfg):
    """
    get bitstream generator from WAVE file
    """
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
#     sys.exit()

    import subprocess

    # bas -> wav
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
        "--verbosity=10",
#         "--verbosity=5",
#         "--logfile=5",
#         "--log_format=%(module)s %(lineno)d: %(message)s",
#         "../test_files/HelloWorld1.bas", "--dst=../test.wav"
        "../test_files/HelloWorld1.bas", "--dst=../test.cas"
    ]).wait()

    print "\n"*3
    print "="*79
    print "\n"*3

#     # wav -> bas
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
#         "--verbosity=10",
        "--verbosity=7",
#         "../test.wav", "--dst=../test.bas",
        "../test.cas", "--dst=../test.bas",
#         "../test_files/HelloWorld1 origin.wav", "--dst=../test_files/HelloWorld1.bas",
    ]).wait()

    print "-- END --"
