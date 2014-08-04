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
    import Tkinter
except ImportError:
    # Maybe Dragon would not be emulated ;)
    Tkinter = None

from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.display_base import DragonTextDisplayBase
from dragonpy.Dragon32.dragon_charmap import get_rgb_color, NORMAL, \
    get_charmap_dict
from dragonpy.utils.logging_utils import log


class DragonTextDisplayTkinter(DragonTextDisplayBase):
    """
    The GUI specific stuff.
    """
    def __init__(self):
        super(DragonTextDisplayTkinter, self).__init__()
        
        self.tk_font = TkFont(CHARS_DICT,
    #         scale_factor=1
    #         scale_factor=2
    #         scale_factor=3
            scale_factor=4
    #         scale_factor=8
        )

        self.total_width = self.tk_font.width_scaled * self.rows
        self.total_height = self.tk_font.height_scaled * self.columns

        print "Window/Canvas geometry: %spx x %spx" % (self.total_width, self.total_height)
        self.root.geometry("+%i+%i" % (self.total_width, self.total_height))

        self.canvas = Tkinter.Canvas(self.root,
            width=self.total_width,
            height=self.total_height,
            bd=0, # Border
            bg="#ff0000",
        )
        self.canvas.pack()

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
