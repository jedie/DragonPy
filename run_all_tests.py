#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    simply run all existing Unittests

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import unittest

from dragonpy.tests.test_base import TextTestRunner2


if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('.')

#    test_runner = TextTestRunner2(
    test_runner = unittest.TextTestRunner(
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )

    test_runner.run(tests)
