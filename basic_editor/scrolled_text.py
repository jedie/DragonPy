#!/usr/bin/env python
# encoding:utf8

"""
    Tkinter ScrolledText widget with horizontal and vertical scroll bars.

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
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import scrolledtext
except ImportError:
    # Python 2
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext


class ScrolledText(tkinter.Text):
    def __init__(self, master=None, **kw):
        frame = tkinter.Frame(master)
        frame.rowconfigure(0, weight = 1)
        frame.columnconfigure(0, weight = 1)

        xscrollbar = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        yscrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)

        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        xscrollbar.grid(row=1, column=0, sticky=tkinter.EW)
        yscrollbar.grid(row=0, column=1, sticky=tkinter.NS)

        _defaults_options={"wrap": tkinter.NONE, "undo": tkinter.YES}
        options = _defaults_options.copy()
        options.update(kw)
        options.update({'yscrollcommand': yscrollbar.set})
        options.update({'xscrollcommand': xscrollbar.set})

        tkinter.Text.__init__(self, frame, **options)

        self.grid(row=0, column=0, sticky=tkinter.NSEW)

        xscrollbar.config(command=self.xview)
        yscrollbar.config(command=self.yview)

        self.bind('<Control-KeyPress-a>', self.event_select_all)
        self.bind('<Control-KeyPress-x>', self.event_cut)
        self.bind('<Control-KeyPress-c>', self.event_copy)
        self.bind('<Control-KeyPress-v>', self.event_paste)

    def event_select_all(self, event=None):
        log.critical("Select all.")
        self.tag_add(tkinter.SEL, "1.0", tkinter.END)
        self.mark_set(tkinter.INSERT, "1.0")
        self.see(tkinter.INSERT)
        return "break"

    def event_cut(self, event=None):
        if self.tag_ranges(tkinter.SEL):
            self.event_copy()
            self.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        return "break"

    def event_copy(self, event=None):
        if self.tag_ranges(tkinter.SEL): 
            text = self.get(tkinter.SEL_FIRST, tkinter.SEL_LAST)  
            self.clipboard_clear()              
            self.clipboard_append(text)
        return "break"

    def event_paste(self, event=None):
        text = self.selection_get(selection='CLIPBOARD')
        if text:
            self.insert(tkinter.INSERT, text)
            self.tag_remove(tkinter.SEL, '1.0', tkinter.END) 
            self.see(tkinter.INSERT)
        return "break"
    
    def __str__(self):
        return str(self.frame)

    def save_position(self):
        """
        save cursor and scroll position
        """
        # save text cursor position:
        self.old_text_pos = self.index(tkinter.INSERT)
        # save scroll position:
        self.old_first, self.old_last = self.yview()

    def restore_position(self):
        """
        restore cursor and scroll position
        """
        # restore text cursor position:
        self.mark_set(tkinter.INSERT, self.old_text_pos)
        # restore scroll position:
        self.yview_moveto(self.old_first)


def example():
    import __main__

    root = tkinter.Tk()

    text = ScrolledText(master=root, bg='white', height=20)
    text.insert(tkinter.END, "X"*150)
    text.insert(tkinter.END, __main__.__doc__)
    text.insert(tkinter.END, "X"*150)
    text.focus_set()
    text.grid(row=0, column=0, sticky=tkinter.NSEW)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()

if __name__ == "__main__":
    example()
