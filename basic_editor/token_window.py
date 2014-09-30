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
import sys

from basic_editor.scrolled_text import ScrolledText
from basic_editor.status_bar import MultiStatusBar
from dragonlib.utils.logging_utils import pformat_program_dump


log = logging.getLogger(__name__)

try:
    # Python 3
    import tkinter
except ImportError:
    # Python 2
    import Tkinter as tkinter


class TokenWindow(object):
    def __init__(self, cfg, master):
        self.cfg = cfg
        self.machine_api = self.cfg.machine_api

        self.root = tkinter.Toplevel(master)
        self.root.geometry("+%d+%d" % (
            master.winfo_rootx() + master.winfo_width(),
            master.winfo_y() # FIXME: Different on linux.
        ))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.base_title = "%s - Tokens" % self.cfg.MACHINE_NAME
        self.root.title(self.base_title)

        self.text = ScrolledText(
            master=self.root, height=30, width=80
        )
        self.text.config(
            background="#ffffff", foreground="#000000",
            highlightthickness=0,
            font=('courier', 11),
        )
        self.text.grid(row=0, column=0, sticky=tkinter.NSEW)

        self.set_status_bar() # Create widget, add bindings and after_idle() update

        self.text.after_idle(self.set_token_info)

    def display_listing(self, content):
        program_dump = self.machine_api.ascii_listing2program_dump(content)
        formated_dump = pformat_program_dump(program_dump)

        self.text.insert(tkinter.END, formated_dump)

        self.text.bind("<Any-Motion>", self.on_mouse_move)

    def on_mouse_move(self, event):
        index = self.text.index("@%s,%s" % (event.x, event.y))

        try:
            word = self.text.get("%s wordstart" % index, "%s wordend" % index)
        except tkinter.TclError as err:
            log.critical("TclError: %s", err)
            return

        try:
            token_value = int(word, 16)
        except ValueError:
            return

        log.critical("$%x", token_value)
        basic_word = self.machine_api.token_util.token2ascii(token_value)

        info = "%s $%02x == %r" % (index, token_value, basic_word)

        try:
            selection_index = "%s-%s" % (self.text.index("sel.first"), self.text.index("sel.last"))
            selection = self.text.selection_get()
        except tkinter.TclError:
            # no selection
            pass
        else:
            log.critical(" selection: %s: %r", selection_index, selection)

            selection = selection.replace("$", "")
            token_values = [int(part, 16) for part in selection.split() if part.strip()]
            log.critical("values: %r", token_values)
            basic_selection = self.machine_api.token_util.tokens2ascii(token_values)

            info += " - selection: %r" % basic_selection

        self.status_bar.set_label("cursor_info", info)

    # ##########################################################################
    # Status bar

    def set_status_bar(self):
        self.status_bar = MultiStatusBar(self.root)
        if sys.platform == "darwin":
            # Insert some padding to avoid obscuring some of the statusbar
            # by the resize widget.
            self.status_bar.set_label('_padding1', '    ', side=tkinter.RIGHT)
        self.status_bar.grid(row=1, column=0)

        self.text.bind("<<set-line-and-column>>", self.set_line_and_column)
        self.text.event_add("<<set-line-and-column>>",
            "<KeyRelease>", "<ButtonRelease>")
        self.text.after_idle(self.set_line_and_column)

    def set_line_and_column(self, event=None):
        line, column = self.text.index(tkinter.INSERT).split('.')
        self.status_bar.set_label('column', 'Column: %s' % column)
        self.status_bar.set_label('line', 'Line: %s' % line)

    ###########################################################################

    def set_token_info(self, event=None):
        line, column = self.text.index(tkinter.INSERT).split('.')

