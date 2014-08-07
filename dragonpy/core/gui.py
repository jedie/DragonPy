#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import Tkinter
import os
import sys
import thread
import threading
import tkMessageBox

from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log


class Dragon32TextDisplayTkinter(object):

    """
    The GUI stuff
    """

    def __init__(self, root):
        self.rows = 32
        self.columns = 16

        #         scale_factor=1
        scale_factor = 2
#         scale_factor=3
#         scale_factor=4
#         scale_factor=8
        self.tk_font = TkFont(CHARS_DICT, scale_factor)

        self.total_width = self.tk_font.width_scaled * self.rows
        self.total_height = self.tk_font.height_scaled * self.columns

        self.canvas = Tkinter.Canvas(root,
            width=self.total_width,
            height=self.total_height,
            bd=0,  # Border
            bg="#ff0000",
        )

        self.charmap = get_charmap_dict()

    def write_byte(self, cpu_cycles, op_address, address, value):
        char, color = self.charmap[value]
#         log.critical(
#             "%04x| *** Display write $%02x ***%s*** %s at $%04x",
#             op_address, value, repr(char), color, address
#         )
        self.render_char(char, color, address)
        return value

    def render_char(self, char, color, address):
        img = self.tk_font.get_char(char, color)

        position = address - 0x400
        column, row = divmod(position, self.rows)
        x = self.tk_font.width_scaled * row
        y = self.tk_font.height_scaled * column

        self.canvas.create_image(x, y,
            image=img,
            state="normal",
            anchor=Tkinter.NW  # NW == NorthWest
        )


class DragonTkinterGUI(object):

    def __init__(self, cfg, machine, display_queue, key_input_queue, cpu_status_queue):
        self.cfg = cfg
        self.machine = machine  # needed here?
        self.display_queue = display_queue
        self.key_input_queue = key_input_queue
        self.cpu_status_queue = cpu_status_queue

        self.approximated_ops = 0
        self.cpu_burst_loops = 0

        self.root = Tkinter.Tk(className="DragonPy")
        machine_name = self.cfg.MACHINE_NAME
        self.root.title(
            "%s - Text Display 32 columns x 16 rows" % machine_name)

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        self.display = Dragon32TextDisplayTkinter(self.root)

        self.display.canvas.grid(row=0, column=0, columnspan=2)  # , rowspan=2)

        self.status = Tkinter.StringVar()
        self.status_widget = Tkinter.Label(
            self.root, textvariable=self.status, text="Info:", borderwidth=1)
        self.status_widget.grid(row=1, column=0, columnspan=2)

        menubar = Tkinter.Menu(self.root)

        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Tkinter.Menu(menubar, tearoff=0)
        editmenu.add_command(label="load", command=self.load)
        editmenu.add_command(label="dump", command=self.dump)
        menubar.add_cascade(label="edit", menu=editmenu)

        # help menu
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        menubar.add_cascade(label="help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)
        self.root.update()

    def dump(self):
        tkMessageBox.showinfo("TODO", "TODO: dump!")

    def load(self):
        tkMessageBox.showinfo("TODO", "TODO: load!")

    def menu_event_about(self):
        tkMessageBox.showinfo("DragonPy",
            "DragonPy the OpenSource emulator written in python.\n"
            "more info: https://github.com/jedie/DragonPy"
        )

    def menu_event_help(self):
        tkMessageBox.showinfo("Help",
            "Please read the README:"
            "https://github.com/jedie/DragonPy#readme"
        )

    def exit(self):
        log.critical("DragonTkinterGUI.exit()")
        try:
            self.root.destroy()
        except:
            pass
        super(DragonTkinterGUI, self).exit()

    def paste_clipboard(self, event):
        """
        Send the clipboard content as user input to the CPU.
        """
        log.critical("paste clipboard")
        clipboard = self.root.clipboard_get()
        for line in clipboard.splitlines():
            log.critical("paste line: %s", repr(line))
            for char in line:
                self.key_input_queue.put_nowait(char)
            self.key_input_queue.put_nowait("\r")

    def event_key_pressed(self, event):
        char_or_code = event.char or event.keycode
        self.key_input_queue.put_nowait(char_or_code)

    def display_cpu_status_interval(self, interval):
        """
        Update the 'cycles/sec' in the GUI
        """
        try:
            cycles_per_second = self.cpu_status_queue.get_nowait()
        except Queue.Empty:
            log.debug("no new cpu_status_queue entry")
            pass
        else:
            log.debug("new cpu_status_queue: %s", repr(cycles_per_second))
            msg = "%d cycles/sec (Dragon 32 == 895.000cycles/sec)" % cycles_per_second
            self.status.set(msg)
            self.root.update()
        self.root.after(interval, self.display_cpu_status_interval, interval)

    def display_queue_interval(self, interval):
        """
        consume all exiting "display RAM write" queue items and render them.
        """
        while True:
            try:
                cpu_cycles, op_address, address, value = self.display_queue.get_nowait()
            except Queue.Empty:
                break
            else:
                self.display.write_byte(cpu_cycles, op_address, address, value)
        self.root.after(interval, self.display_queue_interval, interval)

    def mainloop(self):
        log.critical("Start display_queue_interval()")
        self.display_queue_interval(interval=100)

        log.critical("Start display_cpu_status_interval()")
        self.display_cpu_status_interval(interval=500)

        log.critical("Start root.mainloop()")
        self.root.mainloop()
        log.critical("root.mainloop() has quit!")


def test_run_direct():
    import subprocess
    cmd_args = [
        sys.executable,
        #         "/usr/bin/pypy",
        os.path.join("..",
            "Dragon32_test.py"
#             "Dragon64_test.py"
        ),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    #     test_run_cli()
    test_run_direct()
