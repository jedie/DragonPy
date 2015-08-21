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
import six

xrange = six.moves.xrange

import logging

from dragonpy.Dragon32 import dragon_charmap
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkImageFont

log = logging.getLogger(__name__)

try:
    # Python 3
    import tkinter
    from tkinter import font as TkFont
except ImportError:
    # Python 2
    import Tkinter as tkinter
    import tkFont as TkFont


class MC6847_TextModeCanvas(object):
    """
    MC6847 Video Display Generator (VDG) in Alphanumeric Mode.
    This display mode consumes 512 bytes of memory and is a 32 character wide screen with 16 lines.

    Here we only get the "write into Display RAM" information from the CPU-Thread
    from display_queue.

    The Display Tkinter.Canvas() which will be filled with Tkinter.PhotoImage() instances.
    Every displayed character is a Tkinter.PhotoImage()
    """

    def __init__(self, root):
        self.rows = 32
        self.columns = 16

        scale_factor = 2  # scale the complete Display/Characters
        self.tk_font = TkImageFont(CHARS_DICT, scale_factor)  # to generate PhotoImage()

        self.total_width = self.tk_font.width_scaled * self.rows
        self.total_height = self.tk_font.height_scaled * self.columns

        foreground, background = dragon_charmap.get_hex_color(dragon_charmap.NORMAL)
        self.canvas = tkinter.Canvas(root,
            width=self.total_width,
            height=self.total_height,
            bd=0, # no border
            highlightthickness=0, # no highlight border
            # bg="#ff0000",
            bg="#%s" % background,
        )

        # Contains the map from Display RAM value to char/color:
        self.charmap = get_charmap_dict()

        # Cache for the generated Tkinter.PhotoImage() in evry char/color combination:
        self.image_cache = {}

        # Tkinter.PhotoImage() IDs for image replace with canvas.itemconfigure():
        self.images_map = {}

        # Create all charachter images on the display and fill self.images_map:
        self.init_img = self.tk_font.get_char(char="?", color=dragon_charmap.INVERTED)
        for row in xrange(self.rows + 1):
            for column in xrange(self.columns + 1):
                x = self.tk_font.width_scaled * row
                y = self.tk_font.height_scaled * column
                image_id = self.canvas.create_image(x, y,
                    image=self.init_img,
                    state="normal",
                    anchor=tkinter.NW  # NW == NorthWest
                )
                # log.critical("Image ID: %s at %i x %i", image_id, x, y)
                self.images_map[(x, y)] = image_id

    def write_byte(self, cpu_cycles, op_address, address, value):
        # log.critical(
        #             "%04x| *** Display write $%02x ***%s*** %s at $%04x",
        #             op_address, value, repr(char), color, address
        #         )

        try:
            image = self.image_cache[value]
        except KeyError:
            # Generate a Tkinter.PhotoImage() for the requested char/color
            char, color = self.charmap[value]
            image = self.tk_font.get_char(char, color)
            self.image_cache[value] = image

        position = address - 0x400
        column, row = divmod(position, self.rows)
        x = self.tk_font.width_scaled * row
        y = self.tk_font.height_scaled * column

        #         log.critical("replace image %s at %i x %i", image, x, y)
        image_id = self.images_map[(x, y)]
        self.canvas.itemconfigure(image_id, image=image)
