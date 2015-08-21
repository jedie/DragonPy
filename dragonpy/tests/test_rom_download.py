#!/usr/bin/env python

"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import os

import unittest
import sys

from dragonlib.utils.logging_utils import setup_logging

from dragonpy.CoCo.CoCo2b_rom import CoCo2b_Basic13_ROM, \
    CoCo2b_ExtendedBasic11_ROM
from dragonpy.Dragon32.Dragon32_rom import Dragon32Rom
from dragonpy.Dragon64.Dragon64_rom import Dragon64RomIC17, Dragon64RomIC18
from dragonpy.Multicomp6809.Multicomp6809_rom import Multicomp6809Rom
from dragonpy.Simple6809.Simple6809_rom import Simple6809Rom


class ROMTest(unittest.TestCase):
    def _test_rom(self, rom):
        print(" * test %r" % rom.FILENAME)
        if os.path.isfile(rom.rom_path):
            print(" * Remove %r for test" % rom.rom_path)
            os.remove(rom.rom_path)
        rom.get_data()
        print(" -"*30)
        print(" * test again (from cache):")
        rom.get_data()

    def test_dragon32Rom(self):
        self._test_rom(Dragon32Rom(address=None))

    def test_dragon64RomIC17(self):
        self._test_rom(Dragon64RomIC17(address=None))

    def test_dragon64RomIC18(self):
        self._test_rom(Dragon64RomIC18(address=None))

    def test_CoCo2b_Basic13_ROM(self):
        self._test_rom(CoCo2b_Basic13_ROM(address=None))

    def test_CoCo2b_ExtendedBasic11_ROM(self):
        self._test_rom(CoCo2b_ExtendedBasic11_ROM(address=None))

    def test_Multicomp6809Rom(self):
        self._test_rom(Multicomp6809Rom(address=None))

    def test_Simple6809Rom(self):
        self._test_rom(Simple6809Rom(address=None))


