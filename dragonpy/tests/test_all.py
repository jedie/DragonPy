#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    simply run all existing Unittests

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from dragonpy.utils.logging_utils import setup_logging, log
from dragonpy.tests.test_base import TextTestRunner2


if __name__ == '__main__':   
    setup_logging(log,
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
