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

INVERTED = "INVERTED"
NORMAL = "NORMAL"
GREEN = "GREEN"
YELLOW = "YELLOW"
BLUE = "BLUE"
RED = "RED"
WHITE = "WHITE"
CYAN = "CYAN"
MAGENTA = "MAGENTA"
ORANGE = "ORANGE"

DRAGON_CHAR_MAP={
    0x00: ("\x40", INVERTED), #   @
    0x01: ("\x41", INVERTED), #   A
    0x02: ("\x42", INVERTED), #   B
    0x03: ("\x43", INVERTED), #   C
    0x04: ("\x44", INVERTED), #   D
    0x05: ("\x45", INVERTED), #   E
    0x06: ("\x46", INVERTED), #   F
    0x07: ("\x47", INVERTED), #   G
    0x08: ("\x48", INVERTED), #   H
    0x09: ("\x49", INVERTED), #   I
    0x0a: ("\x4a", INVERTED), #   J
    0x0b: ("\x4b", INVERTED), #   K
    0x0c: ("\x4c", INVERTED), #   L
    0x0d: ("\x4d", INVERTED), #   M
    0x0e: ("\x4e", INVERTED), #   N
    0x0f: ("\x4f", INVERTED), #   O
    0x10: ("\x50", INVERTED), #   P
    0x11: ("\x51", INVERTED), #   Q
    0x12: ("\x52", INVERTED), #   R
    0x13: ("\x53", INVERTED), #   S
    0x14: ("\x54", INVERTED), #   T
    0x15: ("\x55", INVERTED), #   U
    0x16: ("\x56", INVERTED), #   V
    0x17: ("\x57", INVERTED), #   W
    0x18: ("\x58", INVERTED), #   X
    0x19: ("\x59", INVERTED), #   Y
    0x1a: ("\x5a", INVERTED), #   Z
    0x1b: ("\x5b", INVERTED), #   [
    0x1c: ("\x5c", INVERTED), #   REVERSE SOLIDUS
    0x1d: ("\x5d", INVERTED), #   ]
    0x1e: ("\x2191", INVERTED), # UPWARDS ARROW
    0x1f: ("\x2190", INVERTED), # LEFTWARDS ARROW
    0x20: ("\x20", INVERTED), #   SPACE
    0x21: ("\x21", INVERTED), #   !
    0x22: ("\x22", INVERTED), #   "
    0x23: ("\x23", INVERTED), #   #
    0x24: ("\x24", INVERTED), #   $
    0x25: ("\x25", INVERTED), #   %
    0x26: ("\x26", INVERTED), #   &
    0x27: ("\x27", INVERTED), #   '
    0x28: ("\x28", INVERTED), #   (
    0x29: ("\x29", INVERTED), #   )
    0x2a: ("\x2a", INVERTED), #   *
    0x2b: ("\x2b", INVERTED), #   +
    0x2c: ("\x2c", INVERTED), #   ,
    0x2d: ("\x2d", INVERTED), #   -
    0x2e: ("\x2e", INVERTED), #   .
    0x2f: ("\x2f", INVERTED), #   /
    0x30: ("\x30", INVERTED), #   0
    0x31: ("\x31", INVERTED), #   1
    0x32: ("\x32", INVERTED), #   2
    0x33: ("\x33", INVERTED), #   3
    0x34: ("\x34", INVERTED), #   4
    0x35: ("\x35", INVERTED), #   5
    0x36: ("\x36", INVERTED), #   6
    0x37: ("\x37", INVERTED), #   7
    0x38: ("\x38", INVERTED), #   8
    0x39: ("\x39", INVERTED), #   9
    0x3a: ("\x3a", INVERTED), #   :
    0x3b: ("\x3b", INVERTED), #   ;
    0x3c: ("\x3c", INVERTED), #   <
    0x3d: ("\x3d", INVERTED), #   =
    0x3e: ("\x3e", INVERTED), #   >
    0x3f: ("\x3f", INVERTED), #   ?
    0x40: ("\x40", NORMAL), #     @
    0x41: ("\x41", NORMAL), #     A
    0x42: ("\x42", NORMAL), #     B
    0x43: ("\x43", NORMAL), #     C
    0x44: ("\x44", NORMAL), #     D
    0x45: ("\x45", NORMAL), #     E
    0x46: ("\x46", NORMAL), #     F
    0x47: ("\x47", NORMAL), #     G
    0x48: ("\x48", NORMAL), #     H
    0x49: ("\x49", NORMAL), #     I
    0x4a: ("\x4a", NORMAL), #     J
    0x4b: ("\x4b", NORMAL), #     K
    0x4c: ("\x4c", NORMAL), #     L
    0x4d: ("\x4d", NORMAL), #     M
    0x4e: ("\x4e", NORMAL), #     N
    0x4f: ("\x4f", NORMAL), #     O
    0x50: ("\x50", NORMAL), #     P
    0x51: ("\x51", NORMAL), #     Q
    0x52: ("\x52", NORMAL), #     R
    0x53: ("\x53", NORMAL), #     S
    0x54: ("\x54", NORMAL), #     T
    0x55: ("\x55", NORMAL), #     U
    0x56: ("\x56", NORMAL), #     V
    0x57: ("\x57", NORMAL), #     W
    0x58: ("\x58", NORMAL), #     X
    0x59: ("\x59", NORMAL), #     Y
    0x5a: ("\x5a", NORMAL), #     Z
    0x5b: ("\x5b", NORMAL), #     [
    0x5c: ("\x5c", NORMAL), #     REVERSE SOLIDUS
    0x5d: ("\x5d", NORMAL), #     ]
    0x5e: ("\x2191", NORMAL), #   UPWARDS ARROW
    0x5f: ("\x2190", NORMAL), #   LEFTWARDS ARROW
    0x60: ("\x20", NORMAL), #     SPACE
    0x61: ("\x21", NORMAL), #     !
    0x62: ("\x22", NORMAL), #     "
    0x63: ("\x23", NORMAL), #     #
    0x64: ("\x24", NORMAL), #     $
    0x65: ("\x25", NORMAL), #     %
    0x66: ("\x26", NORMAL), #     &
    0x67: ("\x27", NORMAL), #     '
    0x68: ("\x28", NORMAL), #     (
    0x69: ("\x29", NORMAL), #     )
    0x6a: ("\x2a", NORMAL), #     *
    0x6b: ("\x2b", NORMAL), #     +
    0x6c: ("\x2c", NORMAL), #     ,
    0x6d: ("\x2d", NORMAL), #     -
    0x6e: ("\x2e", NORMAL), #     .
    0x6f: ("\x2f", NORMAL), #     /
    0x70: ("\x30", NORMAL), #     0
    0x71: ("\x31", NORMAL), #     1
    0x72: ("\x32", NORMAL), #     2
    0x73: ("\x33", NORMAL), #     3
    0x74: ("\x34", NORMAL), #     4
    0x75: ("\x35", NORMAL), #     5
    0x76: ("\x36", NORMAL), #     6
    0x77: ("\x37", NORMAL), #     7
    0x78: ("\x38", NORMAL), #     8
    0x79: ("\x39", NORMAL), #     9
    0x7a: ("\x3a", NORMAL), #     :
    0x7b: ("\x3b", NORMAL), #     ;
    0x7c: ("\x3c", NORMAL), #     <
    0x7d: ("\x3d", NORMAL), #     =
    0x7e: ("\x3e", NORMAL), #     >
    0x7f: ("\x3f", NORMAL), #     ?
    0x80: ("\x2588", GREEN), #    FULL BLOCK
    0x81: ("\x259b", GREEN), #    QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0x82: ("\x259c", GREEN), #    QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0x83: ("\x2580", GREEN), #    UPPER HALF BLOCK
    0x84: ("\x2599", GREEN), #    QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0x85: ("\x258c", GREEN), #    LEFT HALF BLOCK
    0x86: ("\x259a", GREEN), #    QUADRANT UPPER LEFT AND LOWER RIGHT
    0x87: ("\x2598", GREEN), #    QUADRANT UPPER LEFT
    0x88: ("\x259f", GREEN), #    QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0x89: ("\x259e", GREEN), #    QUADRANT UPPER RIGHT AND LOWER LEFT
    0x8a: ("\x2590", GREEN), #    RIGHT HALF BLOCK
    0x8b: ("\x259d", GREEN), #    QUADRANT UPPER RIGHT
    0x8c: ("\x2584", GREEN), #    LOWER HALF BLOCK
    0x8d: ("\x2596", GREEN), #    QUADRANT LOWER LEFT
    0x8e: ("\x2597", GREEN), #    QUADRANT LOWER RIGHT
    0x8f: ("\x20", GREEN), #      SPACE
    0x90: ("\x2588", YELLOW), #   FULL BLOCK
    0x91: ("\x259b", YELLOW), #   QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0x92: ("\x259c", YELLOW), #   QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0x93: ("\x2580", YELLOW), #   UPPER HALF BLOCK
    0x94: ("\x2599", YELLOW), #   QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0x95: ("\x258c", YELLOW), #   LEFT HALF BLOCK
    0x96: ("\x259a", YELLOW), #   QUADRANT UPPER LEFT AND LOWER RIGHT
    0x97: ("\x2598", YELLOW), #   QUADRANT UPPER LEFT
    0x98: ("\x259f", YELLOW), #   QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0x99: ("\x259e", YELLOW), #   QUADRANT UPPER RIGHT AND LOWER LEFT
    0x9a: ("\x2590", YELLOW), #   RIGHT HALF BLOCK
    0x9b: ("\x259d", YELLOW), #   QUADRANT UPPER RIGHT
    0x9c: ("\x2584", YELLOW), #   LOWER HALF BLOCK
    0x9d: ("\x2596", YELLOW), #   QUADRANT LOWER LEFT
    0x9e: ("\x2597", YELLOW), #   QUADRANT LOWER RIGHT
    0x9f: ("\x20", YELLOW), #     SPACE
    0xa0: ("\x2588", BLUE), #     FULL BLOCK
    0xa1: ("\x259b", BLUE), #     QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xa2: ("\x259c", BLUE), #     QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xa3: ("\x2580", BLUE), #     UPPER HALF BLOCK
    0xa4: ("\x2599", BLUE), #     QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xa5: ("\x258c", BLUE), #     LEFT HALF BLOCK
    0xa6: ("\x259a", BLUE), #     QUADRANT UPPER LEFT AND LOWER RIGHT
    0xa7: ("\x2598", BLUE), #     QUADRANT UPPER LEFT
    0xa8: ("\x259f", BLUE), #     QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xa9: ("\x259e", BLUE), #     QUADRANT UPPER RIGHT AND LOWER LEFT
    0xaa: ("\x2590", BLUE), #     RIGHT HALF BLOCK
    0xab: ("\x259d", BLUE), #     QUADRANT UPPER RIGHT
    0xac: ("\x2584", BLUE), #     LOWER HALF BLOCK
    0xad: ("\x2596", BLUE), #     QUADRANT LOWER LEFT
    0xae: ("\x2597", BLUE), #     QUADRANT LOWER RIGHT
    0xaf: ("\x20", BLUE), #       SPACE
    0xb0: ("\x2588", RED), #      FULL BLOCK
    0xb1: ("\x259b", RED), #      QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xb2: ("\x259c", RED), #      QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xb3: ("\x2580", RED), #      UPPER HALF BLOCK
    0xb4: ("\x2599", RED), #      QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xb5: ("\x258c", RED), #      LEFT HALF BLOCK
    0xb6: ("\x259a", RED), #      QUADRANT UPPER LEFT AND LOWER RIGHT
    0xb7: ("\x2598", RED), #      QUADRANT UPPER LEFT
    0xb8: ("\x259f", RED), #      QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xb9: ("\x259e", RED), #      QUADRANT UPPER RIGHT AND LOWER LEFT
    0xba: ("\x2590", RED), #      RIGHT HALF BLOCK
    0xbb: ("\x259d", RED), #      QUADRANT UPPER RIGHT
    0xbc: ("\x2584", RED), #      LOWER HALF BLOCK
    0xbd: ("\x2596", RED), #      QUADRANT LOWER LEFT
    0xbe: ("\x2597", RED), #      QUADRANT LOWER RIGHT
    0xbf: ("\x20", RED), #        SPACE
    0xc0: ("\x2588", WHITE), #    FULL BLOCK
    0xc1: ("\x259b", WHITE), #    QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xc2: ("\x259c", WHITE), #    QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xc3: ("\x2580", WHITE), #    UPPER HALF BLOCK
    0xc4: ("\x2599", WHITE), #    QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xc5: ("\x258c", WHITE), #    LEFT HALF BLOCK
    0xc6: ("\x259a", WHITE), #    QUADRANT UPPER LEFT AND LOWER RIGHT
    0xc7: ("\x2598", WHITE), #    QUADRANT UPPER LEFT
    0xc8: ("\x259f", WHITE), #    QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xc9: ("\x259e", WHITE), #    QUADRANT UPPER RIGHT AND LOWER LEFT
    0xca: ("\x2590", WHITE), #    RIGHT HALF BLOCK
    0xcb: ("\x259d", WHITE), #    QUADRANT UPPER RIGHT
    0xcc: ("\x2584", WHITE), #    LOWER HALF BLOCK
    0xcd: ("\x2596", WHITE), #    QUADRANT LOWER LEFT
    0xce: ("\x2597", WHITE), #    QUADRANT LOWER RIGHT
    0xcf: ("\x20", WHITE), #      SPACE
    0xd0: ("\x2588", CYAN), #     FULL BLOCK
    0xd1: ("\x259b", CYAN), #     QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xd2: ("\x259c", CYAN), #     QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xd3: ("\x2580", CYAN), #     UPPER HALF BLOCK
    0xd4: ("\x2599", CYAN), #     QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xd5: ("\x258c", CYAN), #     LEFT HALF BLOCK
    0xd6: ("\x259a", CYAN), #     QUADRANT UPPER LEFT AND LOWER RIGHT
    0xd7: ("\x2598", CYAN), #     QUADRANT UPPER LEFT
    0xd8: ("\x259f", CYAN), #     QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xd9: ("\x259e", CYAN), #     QUADRANT UPPER RIGHT AND LOWER LEFT
    0xda: ("\x2590", CYAN), #     RIGHT HALF BLOCK
    0xdb: ("\x259d", CYAN), #     QUADRANT UPPER RIGHT
    0xdc: ("\x2584", CYAN), #     LOWER HALF BLOCK
    0xdd: ("\x2596", CYAN), #     QUADRANT LOWER LEFT
    0xde: ("\x2597", CYAN), #     QUADRANT LOWER RIGHT
    0xdf: ("\x20", CYAN), #       SPACE
    0xe0: ("\x2588", MAGENTA), #  FULL BLOCK
    0xe1: ("\x259b", MAGENTA), #  QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xe2: ("\x259c", MAGENTA), #  QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xe3: ("\x2580", MAGENTA), #  UPPER HALF BLOCK
    0xe4: ("\x2599", MAGENTA), #  QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xe5: ("\x258c", MAGENTA), #  LEFT HALF BLOCK
    0xe6: ("\x259a", MAGENTA), #  QUADRANT UPPER LEFT AND LOWER RIGHT
    0xe7: ("\x2598", MAGENTA), #  QUADRANT UPPER LEFT
    0xe8: ("\x259f", MAGENTA), #  QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xe9: ("\x259e", MAGENTA), #  QUADRANT UPPER RIGHT AND LOWER LEFT
    0xea: ("\x2590", MAGENTA), #  RIGHT HALF BLOCK
    0xeb: ("\x259d", MAGENTA), #  QUADRANT UPPER RIGHT
    0xec: ("\x2584", MAGENTA), #  LOWER HALF BLOCK
    0xed: ("\x2596", MAGENTA), #  QUADRANT LOWER LEFT
    0xee: ("\x2597", MAGENTA), #  QUADRANT LOWER RIGHT
    0xef: ("\x20", MAGENTA), #    SPACE
    0xf0: ("\x2588", ORANGE), #   FULL BLOCK
    0xf1: ("\x259b", ORANGE), #   QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT
    0xf2: ("\x259c", ORANGE), #   QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT
    0xf3: ("\x2580", ORANGE), #   UPPER HALF BLOCK
    0xf4: ("\x2599", ORANGE), #   QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT
    0xf5: ("\x258c", ORANGE), #   LEFT HALF BLOCK
    0xf6: ("\x259a", ORANGE), #   QUADRANT UPPER LEFT AND LOWER RIGHT
    0xf7: ("\x2598", ORANGE), #   QUADRANT UPPER LEFT
    0xf8: ("\x259f", ORANGE), #   QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT
    0xf9: ("\x259e", ORANGE), #   QUADRANT UPPER RIGHT AND LOWER LEFT
    0xfa: ("\x2590", ORANGE), #   RIGHT HALF BLOCK
    0xfb: ("\x259d", ORANGE), #   QUADRANT UPPER RIGHT
    0xfc: ("\x2584", ORANGE), #   LOWER HALF BLOCK
    0xfd: ("\x2596", ORANGE), #   QUADRANT LOWER LEFT
    0xfe: ("\x2597", ORANGE), #   QUADRANT LOWER RIGHT
    0xff: ("\x20", ORANGE), #     SPACE
}



class Dragon32Periphery(PeripheryBase):

    def __init__(self, cfg):
        super(Dragon32Periphery, self).__init__(cfg)

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

    def debug_func_map(self, d, txt):
        log.debug("*** Func map %s:", txt)
        for addr, func in sorted(d.items()):
            log.debug("\t$%04x: %s", addr, func.__name__)

    def display_read(self, cpu_cycles, op_address, address):
        value = self.display_ram[address]
        log.critical("%04x| TODO: read $%02x display RAM from: $%04x", op_address, value, address)
        return value

    def display_write(self, cpu_cycles, op_address, address, value):
        # char = chr(value)
        char, color = DRAGON_CHAR_MAP[value]
#         sys.stdout.write(char)
        sys.stderr.write(char)
        # print repr(char)
        log.critical("%04x| TODO: write $%02x %s %s to display RAM at: $%04x", op_address, value, repr(char), color, address)
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
        log.critical("update pygame")
        if not self.running:
            return
        self.display.flash()
        pygame.display.flip()
        if self.speaker:
            self.speaker.update(cpu_cycles)

    def _handle_events(self):
        log.critical("pygame handle events")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log.critical("pygame.QUIT: shutdown")
                self.exit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = ord(event.unicode) if event.unicode else 0
                if event.key == pygame.K_LEFT:
                    key = 0x08
                if event.key == pygame.K_RIGHT:
                    key = 0x15
                if key:
                    if key == 0x7F:
                        key = 0x08
                    self.periphery.kbd = 0x80 + (key & 0x7F)

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
        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL
#
#         '--log_formatter=%(filename)s %(funcName)s %(lineno)d %(message)s',
#
        "--cfg=Dragon32",
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
