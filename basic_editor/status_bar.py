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
import tkinter


log = logging.getLogger(__name__)


class MultiStatusBar(tkinter.Frame):
    """
    code from idlelib.MultiStatusBar.MultiStatusBar
    """

    def __init__(self, master, **kw):
        tkinter.Frame.__init__(self, master, **kw)
        self.labels = {}

    def set_label(self, name, text='', side=tkinter.LEFT):
        if name not in self.labels:
            label = tkinter.Label(self, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
            label.pack(side=side)
            self.labels[name] = label
        else:
            label = self.labels[name]
        label.config(text=text)
