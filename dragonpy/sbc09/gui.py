# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""




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
    import queue as queue
    import tkinter as tkinter
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext
    import tkinter.font as TkFont

from dragonpy.core.gui import ScrolledTextGUI



class SBC09TkinterGUI(ScrolledTextGUI):
    pass



