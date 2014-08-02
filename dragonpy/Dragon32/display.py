#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

from dragonpy.Dragon32.dragon_charmap import get_rgb_color, NORMAL, \
    get_charmap_dict
from dragonpy.utils.logging_utils import log


class DragonTextDisplay(object):
    """
    Text mode:
    32 rows x 16 columns
    """
    def __init__(self):
        self.charmap = get_charmap_dict()

        self.rows = 32
        self.columns = 16

        pygame.font.init()
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

        width, height = self.font.size("X")
        self.row_pixels = width
        self.column_pixels = height

        screen_width = self.row_pixels * self.rows
        screen_height = self.column_pixels * self.columns
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        pygame.display.set_caption("Dragon - Text Display 32 rows x 16 columns")

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        foreground, background = get_rgb_color(NORMAL)
        self.background.fill(background)

        self.display_offset = 0x400
        self.display_ram = [None] * (0x400 + 0x200)

    def read_byte(self, cpu_cycles, op_address, address):
        value = self.display_ram[address]
        # log.critical("%04x| TODO: read $%02x display RAM from: $%04x", op_address, value, address)
        return value

    def write_byte(self, cpu_cycles, op_address, address, value):
        char, color = self.charmap[value]
        log.debug(
            "%04x| *** Display write $%02x ***%s*** %s at $%04x",
            op_address, value, repr(char), color, address
        )
        self.render_char(char, color, address)
        self.display_ram[address] = value

    def render_char(self, char, color, address):
        foreground, background = get_rgb_color(color)

        position = address - 0x400
        column, row = divmod(position, self.rows)
        position_px = (self.row_pixels * row, self.column_pixels * column)

        text = self.font.render(char,
            True, # antialias
            foreground, background
        )

        self.screen.blit(text, position_px)
        # pygame.display.update()
        pygame.display.flip()



def test_run():
    import sys, os, subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "Dragon64_test.py"),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
