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
import sys
import logging
import click
import os
from dragonpy.utils.starter import run_dragonpy, run_mc6809

if sys.version_info[0] == 2:
    # Python 2
    import Tkinter as tk
    # import tkFileDialog as filedialog
    # import tkMessageBox as messagebox
    # import ScrolledText as scrolledtext
    # import tkFont as TkFont
else:
    # Python 3
    import tkinter as tk
    # from tkinter import filedialog
    # from tkinter import messagebox
    # from tkinter import scrolledtext
    # from tkinter import font as TkFont

import dragonpy
from dragonpy.utils.humanize import get_python_info
from dragonpy.core import configs


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

VERBOSITY_DICT2 = {}
VERBOSITY_STRINGS = []
VERBOSITY_DEFAULT = None

for no, text in sorted(VERBOSITY_DICT.items()):
    text = "%3i: %s" % (no, text)
    if no == VERBOSITY_DEFAULT_VALUE:
        VERBOSITY_DEFAULT = text
    VERBOSITY_STRINGS.append(text)
    VERBOSITY_DICT2[text] = no

# print(VERBOSITY_STRINGS)
# print(VERBOSITY_DICT2)
# print(VERBOSITY_DEFAULT_VALUE, VERBOSITY_DEFAULT)

assert VERBOSITY_DEFAULT is not None
assert VERBOSITY_DICT2[VERBOSITY_DEFAULT] == VERBOSITY_DEFAULT_VALUE


class SettingsFrame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Settings")
        self.grid(**kwargs)

        self.var_verbosity = tk.StringVar()
        self.var_verbosity.set(VERBOSITY_DEFAULT)
        w = tk.Label(self, text="Verbosity:")
        w.grid(row=0, column=1, sticky=tk.E)
        w = tk.OptionMenu(
            self, self.var_verbosity,
            *VERBOSITY_STRINGS
        )
        w.config(width=20)
        w.grid(row=0, column=2, sticky=tk.W)


class RunButtonsFrame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master, text="Run machines")
        self.grid(**kwargs)

        self.machine_dict = master.machine_dict

        self.var_machine = tk.StringVar()
        self.var_machine.set(configs.DRAGON64)
        for row, machine_name in enumerate(sorted(self.machine_dict)):
            # print(row, machine_name)
            b = tk.Radiobutton(self, text=machine_name,
                variable=self.var_machine, value=machine_name)
            b.grid(row=row, column=1, sticky=tk.W)

        button_run = tk.Button(self,
            width=25,
            text="run machine",
            command=master.run_machine
        )
        button_run.grid(row=len(self.machine_dict), column=1)



class ActionButtonsFrame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        tk.LabelFrame.__init__(self, master, text="other actions")
        self.grid(**kwargs)

        _column=0

        button_run = tk.Button(self,
            width=25,
            text="BASIC editor",
            command=master.run_basic_editor
        )
        button_run.grid(row=0, column=_column)

        _column+=1

        button_run = tk.Button(self,
            width=25,
            text="MC6809 benchmark",
            command=master.run_6809_benchmark
        )
        button_run.grid(row=0, column=1)


class MultiStatusBar(tk.Frame):
    """
    base on code from idlelib.MultiStatusBar.MultiStatusBar
    """

    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master)
        self.grid(**kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.labels = {}

    def set_label(self, name, text='', **kwargs):
        defaults = {
            "ipadx": 2, # add internal padding in x direction
            "ipady": 2, # add internal padding in y direction
            "padx": 1, # add padding in x direction
            "pady": 0, # add padding in y direction
            "sticky": tk.NSEW, # stick to the cell boundary
        }
        defaults.update(kwargs)
        if name not in self.labels:
            label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
            label.grid(column=len(self.labels), row=0, **defaults)
            self.labels[name] = label
        else:
            label = self.labels[name]
        label.config(text=text)


class StarterGUI(tk.Tk):
    def __init__(self, machine_dict):
        tk.Tk.__init__(self)

        print("\n".join(sys.path))

        self.machine_dict = machine_dict

        self.geometry("+%d+%d" % (
            self.winfo_screenwidth() * 0.1, self.winfo_screenheight() * 0.1
        ))
        self.title("DragonPy starter GUI")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.add_widgets()
        self.set_status_bar()

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

        self.frame_settings = SettingsFrame(self, column=0, row=0, **defaults)
        self.frame_run_buttons = RunButtonsFrame(self, column=1, row=0, **defaults)
        self.frame_action_buttons = ActionButtonsFrame(self, column=0, row=1, columnspan=2, **defaults)
        self.status_bar = MultiStatusBar(self, column=0, row=2, columnspan=2,
            sticky=tk.NSEW,
        )

    def set_status_bar(self):
        defaults = {
            "padx": 5, # add padding in x direction
            "pady": 0, # add padding in y direction
        }
        self.status_bar.set_label("python_version", get_python_info(), **defaults)
        self.status_bar.set_label("dragonpy_version", "DragonPy v%s" % dragonpy.__version__, **defaults)

    def _print_run_info(self, txt):
        click.echo("\n")
        click.secho(txt, bg='blue', fg='white', bold=True, underline=True)

    def _run_dragonpy_cli(self, *args):
        """
        Run DragonPy cli with given args.
        Add "--verbosity" from GUI.
        """
        verbosity = self.frame_settings.var_verbosity.get()
        verbosity_no = VERBOSITY_DICT2[verbosity]
        log.debug("Verbosity: %i (%s)" % (verbosity_no, verbosity))

        args = (
            "--verbosity", "%s" % verbosity_no
            # "--log_list",
            # "--log",
            # "dragonpy.components.cpu6809,40",
            # "dragonpy.Dragon32.MC6821_PIA,50",
        ) + args
        click.echo("\n")
        run_dragonpy(*args, verbose=True)

    def _run_command(self, command):
        """
        Run DragonPy cli with given command like "run" or "editor"
        Add "--machine" from GUI.
        "--verbosity" will also be set, later.
        """
        machine_name = self.frame_run_buttons.var_machine.get()
        self._run_dragonpy_cli("--machine", machine_name, command)

    def run_machine(self):
        self._print_run_info("Run machine emulation")
        self._run_command("run")

    def run_basic_editor(self):
        self._print_run_info("Run only the BASIC editor")
        self._run_command("editor")

    def run_6809_benchmark(self):
        self._print_run_info("Run MC6809 benchmark")
        click.echo("\n")
        run_mc6809("benchmark", verbose=True)



if __name__ == "__main__":
    from dragonpy.core.cli import main

    main(confirm_exit=False)
