#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    simply run all existing Unittests

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest
import logging

from test_base import TextTestRunner2


if __name__ == '__main__':
    log = logging.getLogger("DragonPy")
    log.setLevel(
#         1
#         10 # DEBUG
#         20 # INFO
#         30 # WARNING
#         40 # ERROR
        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())


    loader = unittest.TestLoader()
    tests = loader.discover('.')

    test_runner = TextTestRunner2(
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )

    test_runner.run(tests)
