#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Some code borrowed from Python IDLE

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging


log = logging.getLogger(__name__)

try:
    # Python 3
    import tkinter
except ImportError:
    # Python 2
    import Tkinter as tkinter


class TkTextTag(object):
    _id=0
    def __init__(self, text_widget, **config):
        self.id = self._id
        self._id+=1
        text_widget.tag_configure(self.id, config)