#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import Tkinter
import tkMessageBox
import threading
import thread

from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict


class Dragon32PeripheryBase(PeripheryBase):
    """
    GUI independent stuff
    """
    def __init__(self, cfg, memory):
        super(Dragon32PeripheryBase, self).__init__(cfg, memory)

        self.kbd = 0xBF
        self.display = None
        self.speaker = None # Speaker()
        self.cassette = None # Cassette()

        self.sam = SAM(cfg, memory)
        self.pia = PIA(cfg, memory)

        self.memory.add_read_byte_callback(self.no_dos_rom, 0xC000)
        self.memory.add_read_word_callback(self.no_dos_rom, 0xC000)

        self.running = True

    def no_dos_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: DOS ROM requested. Send 0x00 back", op_address)
        return 0x00

    def update(self, cpu_cycles):
#        log.critical("update pygame")
        if not self.running:
            return
        if self.speaker:
            self.speaker.update(cpu_cycles)


class DragonTextDisplayBase(object):
    """
    Every stuff with is GUI independent.

    Text mode:
    32 rows x 16 columns
    """
    def __init__(self, memory):
        self.memory = memory
        
        self.charmap = get_charmap_dict()
        self.rows = 32
        self.columns = 16
        
        self.memory.add_write_byte_middleware(self.write_byte, 0x0400, 0x0600)

    def write_byte(self, cpu_cycles, op_address, address, value):
        char, color = self.charmap[value]
#         log.critical(
#             "%04x| *** Display write $%02x ***%s*** %s at $%04x",
#             op_address, value, repr(char), color, address
#         )
        self.render_char(char, color, address)
        return value


class Dragon32TextDisplayTkinter(DragonTextDisplayBase):
    """
    The GUI stuff
    """
    def __init__(self, root, memory):
        super(Dragon32TextDisplayTkinter, self).__init__(memory)

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
            bd=0, # Border
            bg="#ff0000",
        )

    def render_char(self, char, color, address):
        img = self.tk_font.get_char(char, color)

        position = address - 0x400
        column, row = divmod(position, self.rows)
        x = self.tk_font.width_scaled * row
        y = self.tk_font.height_scaled * column

        self.canvas.create_image(x, y,
            image=img,
            state="normal",
            anchor=Tkinter.NW # NW == NorthWest
        )

    def exit(self):
        log.critical("Dragon32PeripheryBase.exit()")
        super(Dragon32PeripheryBase, self).exit()


class CPUThread(threading.Thread):
    def __init__ (self, cfg, cpu):
        super(CPUThread, self).__init__(name="CPU-Thread")
        log.critical(" *** CPUThread init *** ")
        self.cfg = cfg
        self.cpu = cpu
        
        self.cpu.log_cpu_cycle_interval() # turn on manually
        
    def loop(self):
        cpu = self.cpu
        cpu.reset()
        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            log.critical("Running only %i ops!", max_ops)
            for __ in xrange(max_ops):
                cpu.get_and_call_next_op()
                if not cpu.running:
                    break
            log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
            return
        else:
            while cpu.running:
                cpu.get_and_call_next_op()

    def run(self):
        log.critical(" *** CPUThread.run() start *** ")
        try:
            self.loop()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical(" *** CPUThread.run() stopped. *** ")




class Dragon32PeripheryTkinter(Dragon32PeripheryBase):
    def __init__(self, cfg, memory):
        super(Dragon32PeripheryTkinter, self).__init__(cfg, memory)

        self.approximated_ops=0
        self.cpu_burst_loops=0

        self.root = Tkinter.Tk(className="DragonPy")
        machine_name = self.cfg.MACHINE_NAME
        self.root.title("%s - Text Display 32 columns x 16 rows" % machine_name)

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        self.display = Dragon32TextDisplayTkinter(self.root, self.memory)

        self.display.canvas.grid(row=0, column=0, columnspan=2)# , rowspan=2)

        self.status = Tkinter.StringVar()
        self.status_widget = Tkinter.Label(self.root, textvariable=self.status, text="Info:", borderwidth=1)
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
        log.critical("Dragon32PeripheryTkinter.exit()")
        try:
            self.root.destroy()
        except:
            pass
        super(Dragon32PeripheryTkinter, self).exit()

    def paste_clipboard(self, event):
        """
        Send the clipboard content as user input to the CPU.
        """
        log.critical("paste clipboard")
        clipboard = self.root.clipboard_get()
        for line in clipboard.splitlines():
            log.critical("paste line: %s", repr(line))
            for char in line:
                self.pia.key_down(char, block=True)
            self.pia.key_down("\r", block=True)

    def event_key_pressed(self, event):
        char_or_code = event.char or event.keycode
        self.pia.key_down(char_or_code)

    def mainloop(self, cpu):      
        cpu_thread = CPUThread(self.cfg, cpu)
        cpu_thread.deamon = True
        cpu_thread.start()
#         log.critical("Wait for CPU thread stop.")
#         try:
#             cpu_thread.join()
#         except KeyboardInterrupt:
#             log.critical("CPU thread stops by keyboard interrupt.")
#             thread.interrupt_main()
#         else:
#             log.critical("CPU thread stopped.")
#         cpu.running = False

        self.root.mainloop()



#------------------------------------------------------------------------------



def test_run_cli():
    import subprocess
    cmd_args = [
        sys.executable,
#         "/usr/bin/pypy",
        os.path.join("..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL
#
#         '--log_formatter=%(filename)s %(funcName)s %(lineno)d %(message)s',
#
#         "--cfg=Dragon32",
        "--cfg=Dragon64",
#
        "--dont_open_webbrowser",
        "--display_cycle", # print CPU cycle/sec while running.
#
#         "--max=15000",
#         "--max=46041",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


def test_run_direct():
    import sys, os, subprocess
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
