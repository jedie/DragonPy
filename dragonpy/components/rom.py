# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals



class ROMFile(object):
    def __init__(self, filepath, address, max_size=None):
        self.filepath = filepath
        self.address = address
        self.max_size = max_size
