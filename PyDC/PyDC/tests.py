#!/usr/bin/env python2
# coding: utf-8

"""
    PyDC - unittests
    ~~~~~~~~~~~~~~~~

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys
import unittest

# own modules
import configs
from __init__ import wav2bas


class TestDragon32Conversion(unittest.TestCase):

    def setUp(self):
        print
        print " <<<<<< unittest setUp() <<<<<< "
        self.base_path = os.path.normpath(
            os.path.join(os.path.split(configs.__file__)[0], "..")
        )
        self.cfg = configs.Dragon32Config()

    def tearDown(self):
        print "\n"*2
        print " >>>>>> unittest tearDown() >>>>>> ",

    def _src_file_path(self, filename):
        return os.path.relpath(
            os.path.join(self.base_path, "test_files", filename)
        )

    def _dst_file_path(self, filename):
        return os.path.relpath(
            os.path.join(self.base_path, filename)
        )

    def _get_and_delete_dst(self, destination_filepath):
        f = open(destination_filepath, "r")
        dest_content = f.read()
        f.close()
        os.remove(destination_filepath)
        return dest_content

    def test_wav2bas01(self):
        source_filepath = self._src_file_path("HelloWorld1 xroar.wav")
        destination_filepath = self._dst_file_path("unittest_wav2bas01.bas")
        wav2bas(source_filepath, destination_filepath, self.cfg)

        # no filename used in CSAVE:
        destination_filepath = self._dst_file_path("unittest_wav2bas01_.bas")

        dest_content = self._get_and_delete_dst(destination_filepath)

        self.assertEqual(dest_content, (
            '10 FOR I = 1 TO 10\n'
            '20 PRINT I;"HELLO WORLD!"\n'
            '30 NEXT I\n'
        ))

    def test_wav2bas02(self):
        source_filepath = self._src_file_path("HelloWorld1 origin.wav")
        destination_filepath = self._dst_file_path("unittest_wav2bas02.bas")
        wav2bas(source_filepath, destination_filepath, self.cfg)

        # no filename used in CSAVE:
        destination_filepath = self._dst_file_path("unittest_wav2bas02_.bas")

        dest_content = self._get_and_delete_dst(destination_filepath)

        self.assertEqual(dest_content, (
            '10 FOR I = 1 TO 10\n'
            '20 PRINT I;"HELLO WORLD!"\n'
            '30 NEXT I\n'
        ))

    def test_wav2bas03(self):
        source_filepath = self._src_file_path("LineNumber Test 01.wav")
        destination_filepath = self._dst_file_path("unittest_wav2bas03.bas")
        wav2bas(source_filepath, destination_filepath, self.cfg)

        # filename 'LINENO01' used in CSAVE:
        destination_filepath = self._dst_file_path("unittest_wav2bas03_LINENO01.bas")

        dest_content = self._get_and_delete_dst(destination_filepath)

        self.assertEqual(dest_content, (
            '1 PRINT "LINE NUMBER TEST"\n'
            '10 PRINT 10\n'
            '100 PRINT 100\n'
            '1000 PRINT 1000\n'
            '10000 PRINT 10000\n'
            '32768 PRINT 32768\n'
            '63999 PRINT "END";63999\n'
        ))

    def test_wav2bas04(self):
        source_filepath = self._src_file_path("LineNumber Test 02.wav")
        destination_filepath = self._dst_file_path("unittest_wav2bas03.bas")
        wav2bas(source_filepath, destination_filepath, self.cfg)

        # filename 'LINENO02' used in CSAVE:
        destination_filepath = self._dst_file_path("unittest_wav2bas03_LINENO02.bas")

        dest_content = self._get_and_delete_dst(destination_filepath)

        self.assertEqual(dest_content, (
            '1 PRINT "LINE NUMBER TEST"\n'
            '10 PRINT 10\n'
            '100 PRINT 100\n'
            '1000 PRINT 1000\n'
            '10000 PRINT 10000\n'
            '32768 PRINT 32768\n'
            '63999 PRINT "END";63999\n'
        ))


if __name__ == '__main__':
    log = logging.getLogger("PyDC")
    log.setLevel(
        #~ logging.ERROR
        logging.INFO
#         logging.WARNING
#         logging.DEBUG
    )
    log.addHandler(logging.StreamHandler())

    unittest.main(
        argv=(
            sys.argv[0],
#             "TestDragon32Conversion.test_wav2bas01",
#             "TestDragon32Conversion.test_wav2bas04",
        ),
#         verbosity=1,
        verbosity=2,
        failfast=True,
    )
