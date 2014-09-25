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

from dragonpy.core.gui import ScrolledTextGUI



class SBC09TkinterGUI(ScrolledTextGUI):
    pass



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
