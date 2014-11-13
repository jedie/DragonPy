#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    simply run all existing Unittests

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import unittest


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
#         level=1 # hardcore debug ;)
#         level=10 # DEBUG
#         level=20 # INFO
#         level=30 # WARNING
#         level=40 # ERROR
#         level=50 # CRITICAL/FATAL
        level=99
    )

    loader = unittest.TestLoader()
    tests = loader.discover('.')

#    test_runner = TextTestRunner2(
    test_runner = unittest.TextTestRunner(
#         verbosity=1,
        verbosity=2,
        failfast=True,
    )

    test_runner.run(tests)
