#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import subprocess
import os
import distutils
from dragonlib.utils import six

import sys
import time
import logging
import string
import dragonpy
from dragonpy.core import configs

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

log = logging.getLogger(__name__)


VERBOSITY_DICT = {
    1: "hardcode DEBUG ;)",
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL/FATAL",
    99: "nearly all off",
    100: "all off",
}
VERBOSITY_DEFAULT_VALUE = 100

VERBOSITY_DICT2={}
VERBOSITY_STRINGS = []
VERBOSITY_DEFAULT=None

for no,text in sorted(VERBOSITY_DICT.items()):
    text = "%3i: %s" % (no,text)
    if no==VERBOSITY_DEFAULT_VALUE:
        VERBOSITY_DEFAULT=text
    VERBOSITY_STRINGS.append(text)
    VERBOSITY_DICT2[text] = no

# print(VERBOSITY_STRINGS)
# print(VERBOSITY_DICT2)
# print(VERBOSITY_DEFAULT_VALUE, VERBOSITY_DEFAULT)

assert VERBOSITY_DEFAULT is not None
assert VERBOSITY_DICT2[VERBOSITY_DEFAULT] == VERBOSITY_DEFAULT_VALUE

# sys.exit()



class GuiStarter(object):
    def __init__(self, cli_file, machine_dict):
        self.cli_file = os.path.abspath(cli_file)
        self.machine_dict = machine_dict

        self.root = tkinter.Tk(className="STARTER")
        self.root.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() * 0.1, self.root.winfo_screenheight() * 0.1
        ))
        self.root.title("DragonPy v%s GUI starter" % dragonpy.__version__)

        _row = -1

        self.var_machine = tkinter.StringVar()
        self.var_machine.set(configs.DRAGON64)
        for machine_name, data in self.machine_dict.items():
            b = tkinter.Radiobutton(self.root, text=machine_name,
                        variable=self.var_machine, value=machine_name)
            _row += 1
            b.grid(row=_row, column=1, columnspan=2, sticky=tkinter.W)

        _row += 1

        self.var_verbosity=tkinter.StringVar()
        self.var_verbosity.set(VERBOSITY_DEFAULT)
        w = tkinter.Label(self.root, text="Verbosity:")
        w.grid(row=_row, column=1, sticky=tkinter.E)
        w = tkinter.OptionMenu(
            self.root, self.var_verbosity,
            *VERBOSITY_STRINGS
        )
        w.config(width=20)
        w.grid(row=_row, column=2, sticky=tkinter.W)

        _row += 1

        button_run = tkinter.Button(self.root,
            width=25,
            text="run",
            command=self.run_machine
        )
        button_run.grid(row=_row, column=1, columnspan=2)

        _row += 1

        w = tkinter.Label(
            self.root,
            text="CLI script:\n%r" % self.cli_file,
            justify=tkinter.LEFT
        )
        w.grid(row=_row, column=1, columnspan=2)

        self.root.update()

    def run_machine(self):
        machine_name = self.var_machine.get()
        print("run: %r" % machine_name)

        verbosity = self.var_verbosity.get()
        verbosity_no = VERBOSITY_DICT2[verbosity]
        print("Verbosity: %i (%s)" % (verbosity_no, verbosity))

        cmd_args = [
            sys.executable,
            self.cli_file,
        #     # "--log_list",
            "--verbosity", "%s" % verbosity_no,

        #     # "--verbosity", "10", # DEBUG
        #     # "--verbosity", "20", # INFO
        #     #         "--verbosity", "30", # WARNING
        #     #         "--verbosity", "40", # ERROR
        #     #         "--verbosity", "50", # CRITICAL/FATAL
        #     #         "--verbosity", "99", # nearly all off
        #     "--verbosity", "100", # all off
        #
        #     # "--log",
        #     # "dragonpy.components.cpu6809,40",
        #     # "dragonpy.Dragon32.MC6821_PIA,50",
        #
            "--machine", machine_name, "run",
        #     #        "--machine", "Vectrex", "run",
        #     #        "--max_ops", "1",
        #     #        "--trace",
        ]
        print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
        subprocess.Popen(cmd_args)

    def mainloop(self):
        """ for standalone usage """
        self.root.mainloop()

def start_gui(cli_file, machine_dict):
    gui = GuiStarter(cli_file, machine_dict)
    gui.mainloop()


if __name__ == "__main__":
    from dragonpy.core.cli import main
    main()