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

from dragonpy.Dragon32.display_tkinter import DragonTextDisplayTkinter
from dragonpy.Dragon32.display_pygame import DragonTextDisplay
from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict


class Dragon32PeripheryBase(PeripheryBase):
    """
    GUI Independed stuff
    """
    def __init__(self, cfg):
        super(Dragon32PeripheryBase, self).__init__(cfg)

        self.kbd = 0xBF
        self.display = DragonTextDisplayTkinter()
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

        for addr in xrange(0x400, 0x600):
            self.read_byte_func_map[addr] = self.display.read_byte
            self.read_word_func_map[addr] = self.display.read_word
            self.write_byte_func_map[addr] = self.display.write_byte
            self.write_word_func_map[addr] = self.display.write_word

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

    def _handle_events(self):
        
#        log.critical("pygame handle events")
#         for event in pygame.event.get():
#             log.debug("Pygame event: %s", repr(event))
#             if event.type == pygame.QUIT:
#                 log.critical("pygame.QUIT: shutdown")
#                 self.exit()
#                 break
# 
#             if event.type == pygame.KEYDOWN:
#                 log.info("Pygame keydown event: %s", repr(event))
#                 char_or_code = event.unicode or event.scancode
#                 self.pia.key_down(char_or_code)

    def mainloop(self, cpu_process):
        log.critical("Pygame mainloop started.")
        while self.running and cpu_process.is_alive():
            self._handle_events()

        self.exit()
        log.critical("Pygame mainloop stopped.")



class Dragon32PeripheryTkInter(Dragon32PeripheryBase):
    """
    GUI Independed stuff
    """
    def __init__(self, cfg):
        super(Dragon32PeripheryBase, self).__init__(cfg)
        
        self.root = Tkinter.Tk(className="Dragon")
        self.root.title("Dragon - Text Display 32 rows x 16 columns")

        self.root.bind("<Key>", self.event_key_pressed)

    def exit(self):
        log.critical("Dragon32PeripheryBase.exit()")
        super(Dragon32PeripheryBase, self).exit()


def test_run():
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

if __name__ == "__main__":
    test_run()
