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
import time
import traceback

from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.display_base import DragonTextDisplayBase


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

        self.display.canvas.grid(row=0, column=0)# , columnspan=3, rowspan=2)

        self.status = Tkinter.StringVar()
        self.status_widget = Tkinter.Label(self.root, textvariable=self.status, text="Info:", borderwidth=1)
        self.status_widget.grid(row=1, column=0)

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

    def run_cpu_interval(self, cpu, burst_count):
#         
#         if max_ops:
#             log.critical("Running only %i ops!", max_ops)
#             for __ in xrange(max_ops):
#                 cpu.get_and_call_next_op()
#                 if not (self.periphery.running and self.cpu.running):
#                     break
#             log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
#         else:
#             while self.periphery.running and self.cpu.running:

        for _ in xrange(burst_count):
            try:
                cpu.get_and_call_next_op()
            except:
                raise
                tb = traceback.format_exc()
                log.log(99, "Error running OP:\n%s" % tb)

        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            self.approximated_ops += burst_count
            if self.approximated_ops>max_ops:
                log.critical("'max_ops' Quit after %i ops", self.approximated_ops)
                self.exit()
                return

        self.cpu_burst_loops += 1
        self.root.after(1, self.run_cpu_interval, cpu, burst_count)
    
    def update_status_interval(self, cpu, last_update=None, last_cycles=0):
        if last_update is not None:
            duration = time.time() - last_update
            cycles = cpu.cycles - last_cycles
            if cycles == 0:
                log.critical("Exit display_cycle_interval() thread, because cycles/sec == 0")
                return
            msg = "%i cycles/sec (%i cycles in last %isec, cpu_burst_loops=%i)" % (
                int(cycles / duration), cycles, duration, self.cpu_burst_loops
            )
    #             msg = "%d cycles/sec (Dragon 32 == 895.000cycles/sec)" % int(cycles / duration)
            self.status.set(msg)
            self.cpu_burst_loops=0

        last_cycles = cpu.cycles
        last_update = time.time()

        self.root.update()        
        self.root.after(1000, self.update_status_interval, cpu,
            last_update, last_cycles
        )

    def mainloop(self, cpu):
        self.update_status_interval(cpu)
        self.run_cpu_interval(cpu,burst_count=5000)
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
