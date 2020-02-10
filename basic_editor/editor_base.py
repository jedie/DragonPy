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



import logging

log = logging.getLogger(__name__)

try:
    # Python 3
    import tkinter
except ImportError:
    # Python 2
    import tkinter as tkinter

from basic_editor.tkinter_utils import TkTextTag


class BaseExtension(object):
    def __init__(self, editor):
        self.editor = editor
        
        self.cfg=editor.cfg
        self.root = editor.root
        self.text = editor.text # ScrolledText() instance

