#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

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


class RuntimeCfg(object):
    """
    TODO: Load/save to ~/.DragonPy.ini
    """
    speedlimit = False
    cycles_per_sec = 888625 # cycles/sec
    sync_op_count = 100
    max_run_time = 0.1
    max_burst_count = 1000

    def __setattr__(self, attr, value):
        log.critical("Set RuntimeCfg %r to: %r" % (attr, value))
        return object.__setattr__(self, attr, value)

    def load(self):
        raise NotImplementedError("TODO!")

    def save(self):
        raise NotImplementedError("TODO!")


class BaseTkinterGUIConfig(object):
    """
    14.318180 Mhz crystal / 16 = 0.894886 MHz CPU frequency * 1000000 = 894886 cycles/sec
    14.218000 Mhz crystal / 16 = 0.888625 MHz CPU frequency * 1000000 = 888625 cycles/sec

    894886 cycles/sec - 888625 cycles/sec = 6261 cycles/sec slower
    14.218000 Mhz crystal = 0.00000113 Sec or 1.12533408356e-06 us cycle time
    """

    def __init__(self, gui, runtime_cfg):
        self.gui = gui
        self.runtime_cfg = runtime_cfg

        self.root = tkinter.Toplevel(self.gui.root)
        self.root.geometry("+%d+%d" % (
            self.gui.root.winfo_rootx() + self.gui.root.winfo_width(),
            self.gui.root.winfo_y() # FIXME: Different on linux.
        ))

        row = 0

        #
        # Speedlimit check button
        #
        # self.check_value_speedlimit = tkinter.BooleanVar( # FIXME: Doesn't work with PyPy ?!?!
        self.check_value_speedlimit = tkinter.IntVar(
            value=self.runtime_cfg.speedlimit
        )
        self.checkbutton_speedlimit = tkinter.Checkbutton(self.root,
            text="speedlimit", variable=self.check_value_speedlimit,
            command=self.command_checkbutton_speedlimit
        )
        self.checkbutton_speedlimit.grid(row=row, column=0)

        #
        # Cycles/sec entry
        #
        self.cycles_per_sec_var = tkinter.IntVar(
            value=self.runtime_cfg.cycles_per_sec
        )
        self.cycles_per_sec_entry = tkinter.Entry(self.root,
            textvariable=self.cycles_per_sec_var,
            width=8, # validate = 'key', validatecommand = vcmd
        )
        self.cycles_per_sec_entry.bind('<KeyRelease>', self.command_cycles_per_sec)
        self.cycles_per_sec_entry.grid(row=row, column=1)

        self.cycles_per_sec_label_var = tkinter.StringVar()
        self.cycles_per_sec_label = tkinter.Label(
            self.root, textvariable=self.cycles_per_sec_label_var
        )
        self.root.after_idle(self.command_cycles_per_sec) # Add Text
        self.cycles_per_sec_label.grid(row=row, column=2)

        row += 1

        #
        # CPU burst max running time - self.runtime_cfg.max_run_time
        #
        self.max_run_time_var = tkinter.DoubleVar(
            value=self.runtime_cfg.max_run_time
        )
        self.max_run_time_entry = tkinter.Entry(self.root,
            textvariable=self.max_run_time_var, width=8,
        )
        self.max_run_time_entry.bind('<KeyRelease>', self.command_max_run_time)
        self.max_run_time_entry.grid(row=row, column=1)
        self.max_run_time_label = tkinter.Label(self.root,
            text="How long should a CPU Op burst loop take (max_run_time)"
        )
        self.max_run_time_label.grid(row=row, column=2, sticky=tkinter.W)

        row += 1

        #
        # CPU sync OP count - self.runtime_cfg.sync_op_count
        #
        self.sync_op_count_var = tkinter.IntVar(
            value=self.runtime_cfg.sync_op_count
        )
        self.sync_op_count_entry = tkinter.Entry(self.root,
            textvariable=self.sync_op_count_var, width=8,
        )
        self.sync_op_count_entry.bind('<KeyRelease>', self.command_sync_op_count)
        self.sync_op_count_entry.grid(row=row, column=1)
        self.sync_op_count_label = tkinter.Label(self.root,
            text="How many Ops should the CPU process before check sync calls e.g. IRQ (sync_op_count)"
        )
        self.sync_op_count_label.grid(row=row, column=2, sticky=tkinter.W)

        row += 1

        #
        # max CPU burst op count - self.runtime_cfg.max_burst_count
        #
        self.max_burst_count_var = tkinter.IntVar(
            value=self.runtime_cfg.max_burst_count
        )
        self.max_burst_count_entry = tkinter.Entry(self.root,
            textvariable=self.max_burst_count_var, width=8,
        )
        self.max_burst_count_entry.bind('<KeyRelease>', self.command_max_burst_count)
        self.max_burst_count_entry.grid(row=row, column=1)
        self.max_burst_count_label = tkinter.Label(self.root,
            text="Max CPU op burst count (max_burst_count)"
        )
        self.max_burst_count_label.grid(row=row, column=2, sticky=tkinter.W)

        self.root.update()

    def command_checkbutton_speedlimit(self, event=None):
        self.runtime_cfg.speedlimit = self.check_value_speedlimit.get()

    def command_cycles_per_sec(self, event=None):
        try:
            cycles_per_sec = self.cycles_per_sec_var.get()
        except ValueError:
            self.cycles_per_sec_var.set(self.runtime_cfg.cycles_per_sec)
            return

        self.cycles_per_sec_label_var.set(
            "cycles/sec / 1000000 = %f MHz CPU frequency * 16 = %f Mhz crystal" % (
                cycles_per_sec / 1000000,
                cycles_per_sec / 1000000 * 16,
            )
        )

        self.runtime_cfg.cycles_per_sec = cycles_per_sec

    def command_sync_op_count(self, event=None):
        """ CPU burst max running time - self.runtime_cfg.sync_op_count """
        try:
            sync_op_count = self.sync_op_count_var.get()
        except ValueError:
            sync_op_count = self.runtime_cfg.sync_op_count

        if sync_op_count < 1:
            sync_op_count = self.runtime_cfg.sync_op_count

        self.runtime_cfg.sync_op_count = sync_op_count
        self.sync_op_count_var.set(self.runtime_cfg.sync_op_count)

    def command_max_burst_count(self, event=None):
        """ max CPU burst op count - self.runtime_cfg.max_burst_count """
        try:
            max_burst_count = self.max_burst_count_var.get()
        except ValueError:
            max_burst_count = self.runtime_cfg.max_burst_count

        if max_burst_count < 1:
            max_burst_count = self.runtime_cfg.max_burst_count

        self.runtime_cfg.max_burst_count = max_burst_count
        self.max_burst_count_var.set(self.runtime_cfg.max_burst_count)

    def command_max_run_time(self, event=None):
        """ CPU burst max running time - self.runtime_cfg.max_run_time """
        try:
            max_run_time = self.max_run_time_var.get()
        except ValueError:
            max_run_time = self.runtime_cfg.max_run_time

        self.runtime_cfg.max_run_time = max_run_time
        self.max_run_time_var.set(self.runtime_cfg.max_run_time)

    def focus(self):
        # see: http://www.python-forum.de/viewtopic.php?f=18&t=34643 (de)
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.focus_force()
        self.root.lift(aboveThis=self.gui.root)