# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import logging
import string
from dragonlib.utils.auto_shift import invert_shift

log = logging.getLogger(__name__)

try:
    # Python 3
    import queue
    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import scrolledtext
    from tkinter import font as TkFont
except ImportError:
    # Python 2
    import Queue as queue
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    import tkFont as TkFont

from dragonpy.core.gui import BaseTkinterGUI



class MulticompTkinterGUI(BaseTkinterGUI):
    def __init__(self, *args, **kwargs):
        super(MulticompTkinterGUI, self).__init__(*args, **kwargs)

        self.root.title("DragonPy - %s" % self.cfg.MACHINE_NAME)

        self.text = scrolledtext.ScrolledText(
            master=self.root, height=30, width=80
        )
        self.text.config(
            background="#ffffff", foreground="#000000",
            highlightthickness=0,
            font=('courier', 11),
        )
        self.text.grid(row=0, column=0, sticky=tkinter.NSEW)

#         self._editor_window = None
#         self.menubar.insert_command(index=3, label="BASIC editor", command=self.open_basic_editor)

        self.root.unbind("<Key>")
        self.text.bind("<Key>", self.event_key_pressed)

        # TODO: self.root.bind("<<Paste>>", self.paste_clipboard) ???

        # display the menu
        self.root.config(menu=self.menubar)
        self.root.update()

    def event_key_pressed(self, event):
        """
        So a "invert shift" for user inputs:
        Convert all lowercase letters to uppercase and vice versa.
        """
        char = event.char
        if not char:
            return

        if char in string.ascii_letters:
            char = invert_shift(char)

        self.user_input_queue.put(char)

        # Don't insert the char in text widget, because it will be echoed
        # back from the machine!
        return "break"

    def display_callback(self, char):
        log.debug("Add to text: %s", repr(char))
        if char == "\x08":
            # Delete last input char
            self.text.delete(tkinter.INSERT + "-1c")
        else:
            # insert the new character:
            self.text.insert(tkinter.END, char)

            # scroll down if needed:
            self.text.see(tkinter.END)

            # Set cursor to the END position:
            self.text.mark_set(tkinter.INSERT, tkinter.END)


#------------------------------------------------------------------------------


def test_run():
    import os
    import sys
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#         "-h"
#         "--log_list",
#         "--log", "dragonpy.Multicomp6809,10", "dragonpy.core.gui,10",

#          "--verbosity", "10", # DEBUG
#         "--verbosity", "20", # INFO
#         "--verbosity", "30", # WARNING
#         "--verbosity", "40", # ERROR
#         "--verbosity", "50", # CRITICAL/FATAL
        "--verbosity", "99", # nearly all off

#         "--machine", "Dragon32", "run",
        "--machine", "Multicomp6809", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    test_run()
