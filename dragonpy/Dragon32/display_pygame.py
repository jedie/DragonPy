#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

from dragonpy.Dragon32.display_base import DragonTextDisplayBase
from dragonpy.Dragon32.dragon_charmap import get_rgb_color, NORMAL, \
    get_charmap_dict
import logging

log=logging.getLogger(__name__)


class DragonTextDisplay(DragonTextDisplayBase):
    """
    Text mode:
    32 rows x 16 columns
    """
    def __init__(self):
        super(DragonTextDisplay, self).__init__()

        pygame.font.init()
        self.font = pygame.font.SysFont("monospace", 26, bold=True)

        width, height = self.font.size("X")
        self.char_width = width
        self.char_height = height

        screen_width = self.char_width * self.rows
        screen_height = self.char_height * self.columns
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        pygame.display.set_caption("Dragon - Text Display 32 rows x 16 columns")

        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        foreground, background = get_rgb_color(NORMAL)
        self.background.fill(background)

        self.display_offset = 0x400
        self.display_ram = [None] * self.display_offset # empty Offset
        self.display_ram += [0x00] * 0x200

    def render_char(self, char, color, address):
        foreground, background = get_rgb_color(color)

        position = address - 0x400
        column, row = divmod(position, self.rows)
        position_px = (self.char_width * row, self.char_height * column)

        text = self.font.render(char,
            True, # antialias
            foreground, background
        )

        self.screen.blit(text, position_px)
        pygame.display.update()
#         pygame.display.flip()



def test_run():
    import sys, os, subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "Dragon64_test.py"),
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
