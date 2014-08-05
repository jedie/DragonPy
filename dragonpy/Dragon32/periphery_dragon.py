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

from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.display_base import DragonTextDisplayBase
import time
import traceback


class Dragon32PeripheryBase(PeripheryBase):
    """
    GUI independent stuff
    """
    def __init__(self, cfg):
        super(Dragon32PeripheryBase, self).__init__(cfg)

        self.kbd = 0xBF
        self.display = None
        self.speaker = None # Speaker()
        self.cassette = None # Cassette()

        self.sam = SAM(cfg)
        self.pia = PIA(cfg)

        self.read_word_func_map = {
            0xc000: self.no_dos_rom,
            0xfffe: self.reset_vector,
        }

        # Collect all read/write functions from PIA:
        self.pia.add_read_write_callbacks(self)

        # Collect all read/write functions from SAM:
        self.sam.add_read_write_callbacks(self)

        self.debug_func_map(self.read_byte_func_map, "read_byte_func_map")
        self.debug_func_map(self.read_word_func_map, "read_word_func_map")
        self.debug_func_map(self.write_byte_func_map, "write_byte_func_map")
        self.debug_func_map(self.write_word_func_map, "write_word_func_map")

        self.running = True

    def debug_func_map(self, d, txt):
        log.debug("*** Func map %s:", txt)
        for addr, func in sorted(d.items()):
            log.debug("\t$%04x: %s", addr, func.__name__)

    def no_dos_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: DOS ROM requested. Send 0x00 back", op_address)
        return 0x00

    def reset_vector(self, cpu_cycles, op_address, address):
        ea = 0xb3b4
        log.info("%04x| %04x        [RESET]" % (address, ea))
        return ea # FIXME: RESET interrupt service routine ???

    def update(self, cpu_cycles):
#        log.critical("update pygame")
        if not self.running:
            return
        if self.speaker:
            self.speaker.update(cpu_cycles)



class Dragon32TextDisplayTkinter(DragonTextDisplayBase):
    """
    The GUI stuff
    """
    def __init__(self, root):
        super(Dragon32TextDisplayTkinter, self).__init__()

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



class Dragon32PeripheryTkinter(Dragon32PeripheryBase):
    def __init__(self, cfg):
        super(Dragon32PeripheryTkinter, self).__init__(cfg)

        self.cpu_burst_loops=0

        self.root = Tkinter.Tk(className="Dragon")
        self.root.title("Dragon - Text Display 32 columns x 16 rows")

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        self.display = Dragon32TextDisplayTkinter(self.root)

        # Collect all read/write functions from Display:
        self.display.add_read_write_callbacks(self)

        self.display.canvas.grid(row=0, column=0)# , columnspan=3, rowspan=2)

        self.status = Tkinter.StringVar()
        self.status_widget = Tkinter.Label(self.root, textvariable=self.status, text="Info:", borderwidth=1)
        self.status_widget.grid(row=1, column=0)

    def paste_clipboard(self, event):
        """
        POKE 1024,128

10 CLS
20 FOR I = 0 TO 255:
30 POKE 1024+(I*2),I
40 NEXT I
50 I$ = INKEY$:IF I$="" THEN 50
        """
        log.critical("paste clipboard")
        clipboard = self.root.clipboard_get()
        log.critical("Clipboard content: %s", repr(clipboard))
        clipboard = clipboard.replace("\n", "\r")
        for char in clipboard:
            self.pia.key_down(char, block=True)

    def event_key_pressed(self, event):
        char_or_code = event.char or event.keycode
        self.pia.key_down(char_or_code)

    def run_cpu_interval(self, cpu, last_cycles=0, last_cycle_update=sys.maxint, loops=0):
#         max_ops = self.cfg.cfg_dict["max_ops"]
#         if max_ops:
#             log.critical("Running only %i ops!", max_ops)
#             for __ in xrange(max_ops):
#                 cpu.get_and_call_next_op()
#                 if not (self.periphery.running and self.cpu.running):
#                     break
#             log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
#         else:
#             while self.periphery.running and self.cpu.running:

        for _ in xrange(20000):
            try:
                cpu.get_and_call_next_op()
            except:
                tb = traceback.format_exc()
                log.log(99, "Error running OP:\n%s" % tb)

        loops += 1
        duration = time.time() - last_cycle_update
        if duration > 1:
            cycles = cpu.cycles - last_cycles
            if cycles == 0:
                log.critical("Exit display_cycle_interval() thread, because cycles/sec == 0")
                return
            msg = "%i cycles/sec (%i cycles in last %isec, loops=%i)" % (
                int(cycles / duration), cycles, duration, loops
            )
#             msg = "%d cycles/sec (Dragon 32 == 895.000cycles/sec)" % int(cycles / duration)
            self.status.set(msg)
            loops = 0
            last_cycles = cpu.cycles
            last_cycle_update = time.time()

        self.root.after(1, self.run_cpu_interval, cpu,
            last_cycles, last_cycle_update, loops
        )

    def mainloop(self, cpu):
        self.run_cpu_interval(cpu, last_cycle_update=time.time())
        self.root.mainloop()


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
        os.path.join("..", "Dragon64_test.py"),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
#     test_run_cli()
    test_run_direct()
