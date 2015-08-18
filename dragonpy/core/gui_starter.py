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

if sys.version_info[0] == 2:
    # Python 2
    import Queue as queue
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    import tkFont as TkFont
else:
    # Python 3
    import queue
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import scrolledtext
    from tkinter import font as TkFont



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

class RunButtonsFrame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Run machines")
        self.grid(**kwargs)

        self.machine_dict = master.machine_dict

        self.var_machine = tk.StringVar()
        self.var_machine.set(configs.DRAGON64)
        for row, machine_name in enumerate(sorted(self.machine_dict)):
            print(row, machine_name)
            b = tk.Radiobutton(self, text=machine_name,
                        variable=self.var_machine, value=machine_name)
            b.grid(row=row, column=1, sticky=tk.W)

        button_run = tk.Button(self,
            width=25,
            text="run machine",
            command=master.run_machine
        )
        button_run.grid(row=row+1, column=1)


class GuiStarter(tk.Tk):
    def __init__(self, cli_file, machine_dict):
        tk.Tk.__init__(self)
        
        self.cli_file = os.path.abspath(cli_file)
        self.machine_dict = machine_dict

        self.geometry("+%d+%d" % (
            self.winfo_screenwidth() * 0.1, self.winfo_screenheight() * 0.1
        ))
        self.title("DragonPy v%s GUI starter" % dragonpy.__version__)

        _row = 0

        self.var_verbosity=tk.StringVar()
        self.var_verbosity.set(VERBOSITY_DEFAULT)
        w = tk.Label(self, text="Verbosity:")
        w.grid(row=_row, column=1, sticky=tk.E)
        w = tk.OptionMenu(
            self, self.var_verbosity,
            *VERBOSITY_STRINGS
        )
        w.config(width=20)
        w.grid(row=_row, column=2, sticky=tk.W)

        _row += 1

        w = tk.Label(
            self,
            text="CLI script:\n%r" % self.cli_file,
            justify=tk.LEFT
        )
        w.grid(row=_row, column=1, columnspan=2)

        self.add_widgets()

        self.update()

    def add_widgets(self):
        padding = 5
        defaults = {
            "ipadx": padding, # add internal padding in x direction
            "ipady": padding, # add internal padding in y direction
            "padx": padding, # add padding in x direction
            "pady": padding, # add padding in y direction
            "sticky": tk.NSEW, # stick to the cell boundary
        }

        self.run_buttons = RunButtonsFrame(self, column=0, row=0, **defaults)
        # self.inputs = Inputs(self, column=0, row=1, **defaults)
        # self.actions = Buttons(self, column=1, row=0, rowspan=2, **defaults)

    def run_machine(self):
        machine_name = self.run_buttons.var_machine.get()
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


def start_gui(cli_file, machine_dict):
    gui = GuiStarter(cli_file, machine_dict)
    gui.mainloop()


if __name__ == "__main__":
    from dragonpy.core.cli import main
    main(confirm_exit=False)