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
import os
import string
import sys

import dragonlib
from basic_editor.scrolled_text import ScrolledText
from basic_editor.status_bar import MultiStatusBar
from basic_editor.token_window import TokenWindow
from basic_editor.highlighting import TkTextHighlighting, TkTextHighlightCurrentLine
from dragonlib.utils.auto_shift import invert_shift


log = logging.getLogger(__name__)

try:
    # Python 3
    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox
except ImportError:
    # Python 2
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox



class EditorWindow(object):
    FILETYPES = [# For filedialog
        ("BASIC Listings", "*.bas", "TEXT"),
        ("Text files", "*.txt", "TEXT"),
        ("All files", "*"),
    ]
    DEFAULTEXTENSION = "*.bas"

    def __init__(self, cfg, gui=None):
        self.cfg = cfg
        if gui is None:
            self.standalone_run = True
        else:
            self.gui = gui
            self.standalone_run = False

        self.machine_api = self.cfg.machine_api

        if self.standalone_run:
            self.root = tkinter.Tk(className="EDITOR")
            self.root.geometry("+%d+%d" % (
                self.root.winfo_screenwidth() * 0.1, self.root.winfo_screenheight() * 0.1
            ))
        else:
            # As sub window in DragonPy Emulator
            self.root = tkinter.Toplevel(self.gui.root)
            self.root.geometry("+%d+%d" % (
                self.gui.root.winfo_rootx() + self.gui.root.winfo_width(),
                self.gui.root.winfo_y() # FIXME: Different on linux.
            ))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.base_title = "%s - BASIC Editor" % self.cfg.MACHINE_NAME
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

        self.highlighting = TkTextHighlighting(self)
        self.highlight_currentline = TkTextHighlightCurrentLine(self)

        #self.auto_shift = True # use invert shift for letters?

        self.menubar = tkinter.Menu(self.root)

        filemenu = tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.command_load_file)
        filemenu.add_command(label="Save", command=self.command_save_file)
        if self.standalone_run:
            filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tkinter.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="renum", command=self.renumber_listing)
        editmenu.add_command(label="reformat", command=self.reformat_listing)
        editmenu.add_command(label="display tokens", command=self.debug_display_tokens)
        self.menubar.add_cascade(label="tools", menu=editmenu)

        # help menu
        helpmenu = tkinter.Menu(self.menubar, tearoff=0)
#        helpmenu.add_command(label="help", command=self.menu_event_help)
#        helpmenu.add_command(label="about", command=self.menu_event_about)
        self.menubar.add_cascade(label="help", menu=helpmenu)

        # startup directory for file open/save
        self.current_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(dragonlib.__file__), "..", "BASIC examples",
            )
        )

        self.set_status_bar() # Create widget, add bindings and after_idle() update

        self.text.bind("<Key>", self.event_text_key)
#         self.text.bind("<space>", self.event_syntax_check)

        # display the menu
        self.root.config(menu=self.menubar)
        self.root.update()

    ###########################################################################
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

    def event_text_key(self, event):
        """
        So a "invert shift" for user inputs:
        Convert all lowercase letters to uppercase and vice versa.
        """
        char = event.char
        if not char or char not in string.ascii_letters:
            # ignore all non letter inputs
            return

        converted_char = invert_shift(char)
        log.debug("convert keycode %s - char %s to %s", event.keycode, repr(char), converted_char)
#         self.text.delete(Tkinter.INSERT + "-1c") # Delete last input char
        self.text.insert(tkinter.INSERT, converted_char) # Insert converted char
        return "break"

    #     def event_syntax_check(self, event):
    #         index = self.text.search(r'\s', "insert", backwards=True, regexp=True)
    #         if index == "":
    #             index ="1.0"
    #         else:
    #             index = self.text.index("%s+1c" % index)
    #         word = self.text.get(index, "insert")
    #         log.critical("inserted word: %r", word)
    #         print self.machine_api.parse_ascii_listing(word)

    def setup_filepath(self, filepath):
        log.critical(filepath)
        self.filepath = os.path.normpath(os.path.abspath(filepath))
        self.current_dir, self.filename = os.path.split(self.filepath)

        self.root.title("%s - %s" % (self.base_title, repr(self.filename)))

    def command_load_file(self):
        infile = filedialog.askopenfile(
            parent=self.root,
            mode="r",
            title="Select a BASIC file to load",
            filetypes=self.FILETYPES,
            initialdir=self.current_dir,
        )
        if infile is not None:
            content = infile.read()
            infile.close()
            content = content.strip()
            listing_ascii = content.splitlines()
            self.set_content(listing_ascii)

            self.setup_filepath(infile.name)


    def command_save_file(self):
        outfile = filedialog.asksaveasfile(
            parent=self.root,
            mode="w",
            filetypes=self.FILETYPES,
            defaultextension=self.DEFAULTEXTENSION,
            initialdir=self.current_dir,
        )
        if outfile is not None:
            content = self.get_content()
            outfile.write(content)
            outfile.close()
            self.setup_filepath(outfile.name)

    def debug_display_tokens(self):
        content = self.get_content()
        self.token_window = TokenWindow(self.cfg, self.root)
        self.token_window.display_listing(content)

    def renumber_listing(self):
        # save text cursor and scroll position
        self.text.save_position()

        # renumer the content
        content = self.get_content()
        content = self.machine_api.renum_ascii_listing(content)
        self.set_content(content)

        # restore text cursor and scroll position
        self.text.restore_position()

    def reformat_listing(self):
        # save text cursor and scroll position
        self.text.save_position()

        # renumer the content
        content = self.get_content()
        content = self.machine_api.reformat_ascii_listing(content)
        self.set_content(content)

        # restore text cursor and scroll position
        self.text.restore_position()

    def get_content(self):
        content = self.text.get("1.0", tkinter.END)
        content = content.strip()
        return content

    def set_content(self, listing_ascii):
#        self.text.config(state=Tkinter.NORMAL)
        self.text.delete("1.0", tkinter.END)
        log.critical("insert listing:")
        if not isinstance(listing_ascii, (list, tuple)):
            listing_ascii = listing_ascii.splitlines()

        for line in listing_ascii:
            line = "%s\n" % line # use os.sep ?!?
            log.debug("\t%s", repr(line))
            self.text.insert(tkinter.END, line)
#        self.text.config(state=Tkinter.DISABLED)
        self.text.mark_set(tkinter.INSERT, '1.0') # Set cursor at start
        self.focus_text()
        self.highlight_currentline.update(force=True)
        self.highlighting.update(force=True)

    def focus_text(self):
        if not self.standalone_run:
            # see:
            # http://www.python-forum.de/viewtopic.php?f=18&t=34643 (de)
            # http://bugs.python.org/issue11571
            # http://bugs.python.org/issue9384

            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

            self.root.focus_force()

            self.root.lift(aboveThis=self.gui.root)

        self.text.focus()

    def mainloop(self):
        """ for standalone usage """
        self.root.mainloop()


def run_basic_editor(cfg, default_content=None):
    editor = EditorWindow(cfg)
    if default_content is not None:
        editor.set_content(default_content)
    editor.mainloop()


def test():
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
#        level=1 # hardcore debug ;)
#         level=10  # DEBUG
#         level=20  # INFO
#         level=30  # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )

    CFG_DICT = {
        "verbosity": None,
        "display_cycle": False,
        "trace": None,
        "max_ops": None,
        "bus_socket_host": None,
        "bus_socket_port": None,
        "ram": None,
        "rom": None,
        "use_bus": False,
    }
    from dragonpy.Dragon32.config import Dragon32Cfg

    cfg = Dragon32Cfg(CFG_DICT)

    filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
        # "..", "BASIC examples", "hex_view01.bas"
        "..", "BASIC games", "INVADER.bas"
    )

    with open(filepath, "r") as f:
        listing_ascii = f.read()

    run_basic_editor(cfg, default_content=listing_ascii)


if __name__ == "__main__":
    test()
