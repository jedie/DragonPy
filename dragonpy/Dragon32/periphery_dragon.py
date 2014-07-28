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
try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

from dragonpy.Dragon32.display import Display
from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict


class Dragon32Periphery(PeripheryBase):

    def __init__(self, cfg):
        super(Dragon32Periphery, self).__init__(cfg)

        self.charmap = get_charmap_dict()

        self.kbd = 0xBF
        self.display = Display()
        self.speaker = None # Speaker()
        self.cassette = None # Cassette()

        self.sam = SAM(cfg)
        self.pia = PIA(cfg)

        self.read_byte_func_map = {
            0xc000: self.no_dos_rom,
            0xfffe: self.reset_vector,
        }
        self.write_byte_func_map = {}

        # Collect all read/write functions from PIA:
        pia_read_func_map = self.pia.get_read_func_map()
        pia_write_func_map = self.pia.get_write_func_map()
        self.read_byte_func_map.update(pia_read_func_map)
        self.write_byte_func_map.update(pia_write_func_map)

        # Collect all read/write functions from SAM:
        sam_read_func_map = self.sam.get_read_func_map()
        sam_write_func_map = self.sam.get_write_func_map()
        self.read_byte_func_map.update(sam_read_func_map)
        self.write_byte_func_map.update(sam_write_func_map)

        self.debug_func_map(self.read_byte_func_map, "read_byte_func_map")
        self.debug_func_map(self.write_byte_func_map, "write_byte_func_map")

        self.display_ram = [None] * (0x400 + 0x200)
        for addr in xrange(0x400, 0x600):
            self.read_byte_func_map[addr] = self.display_read
            self.write_byte_func_map[addr] = self.display_write

        self.running = True
        self.output_count = 0

    def debug_func_map(self, d, txt):
        log.debug("*** Func map %s:", txt)
        for addr, func in sorted(d.items()):
            log.debug("\t$%04x: %s", addr, func.__name__)

    def display_read(self, cpu_cycles, op_address, address):
        value = self.display_ram[address]
        log.critical("%04x| TODO: read $%02x display RAM from: $%04x", op_address, value, address)
        return value

    def display_write(self, cpu_cycles, op_address, address, value):
        if self.output_count == 0:
            sys.stderr.write("|")

        char, color = self.charmap[value]
#         sys.stdout.write(char)
        sys.stderr.write(char)

        self.output_count += 1
        if self.output_count >= 32:
            sys.stderr.write("|\n")
            sys.stderr.flush()
            self.output_count = 0

        self.display_ram[address] = value

    def no_dos_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: DOS ROM requested. Send 0x00 back", op_address)
        return 0x00

    def reset_vector(self, cpu_cycles, op_address, address):
        ea = 0xb3b4
        log.info("%04x| %04x        [RESET]" % (address, ea))
        return ea # FIXME: RESET interrupt service routine ???

    def exit(self):
        log.critical("exit pygame")
        super(Dragon32Periphery, self).exit()
        pygame.display.quit()

    def update(self, cpu_cycles):
#        log.critical("update pygame")
        if not self.running:
            return
        self.display.flash()
        pygame.display.flip()
        if self.speaker:
            self.speaker.update(cpu_cycles)

    def _handle_events(self):
#        log.critical("pygame handle events")
        for event in pygame.event.get():
            log.critical("Pygame event: %s", repr(event))
            if event.type == pygame.QUIT:
                log.critical("pygame.QUIT: shutdown")
                self.exit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = ord(event.unicode) if event.unicode else 0
                self.pia.key_down(key)

    def mainloop(self, cpu_process):
        log.critical("Pygame mainloop started.")
        while self.running and cpu_process.is_alive():
            self._handle_events()

        self.exit()
        log.critical("Pygame mainloop stopped.")



def test_run():
    import sys, subprocess
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
        "--cfg=Dragon32",
#        "--cfg=Dragon64",
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
