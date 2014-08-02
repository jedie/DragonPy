#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import time
try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

from dragonpy.utils.logging_utils import log

class DragonTextDisplay(object):
    """
    Text mode:
    32 rows x 16 columns
    """
    def __init__(self):
        self.rows = 32
        self.columns = 16

        self.row_pixels = 20
        self.column_pixels = 20

        total_size = (self.row_pixels * self.rows, self.column_pixels * self.columns)

        self.screen = pygame.display.set_mode(total_size)
        pygame.display.set_caption("Dragon - Text Display 32 rows x 16 columns")
        pygame.font.init()
        self.font = pygame.font.SysFont("monospace", 20)

        self.display_offset = 0x400

    def render_char(self, char, color, address):
        position = address - 0x400
        column, row = divmod(position, self.rows)
        position_px = (self.row_pixels * row, self.column_pixels * column)
        text = self.font.render(char, True, (255, 255, 0))
        self.screen.blit(text, position_px)
        pygame.display.update()
