#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Some code borrowed from Python IDLE

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging


log = logging.getLogger(__name__)


class TkTextTag:
    _id = 0

    def __init__(self, text_widget, **config):
        self.id = self._id
        self._id += 1
        text_widget.tag_configure(self.id, config)
