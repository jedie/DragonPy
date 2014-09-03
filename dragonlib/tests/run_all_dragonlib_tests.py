#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import unittest

from dragonpy.tests.test_base import TextTestRunner2


if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('dragonlib')

    test_runner = TextTestRunner2(verbosity=2,
#         failfast=True,
    )

    test_runner.run(tests)
    print(" --- END --- ")