"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015-2022 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import unittest

from dragonpy.CoCo.CoCo2b_rom import CoCo2b_Basic13_ROM, CoCo2b_ExtendedBasic11_ROM
from dragonpy.components.rom import ROMFile
from dragonpy.Dragon32.Dragon32_rom import Dragon32Rom
from dragonpy.Dragon64.Dragon64_rom import Dragon64RomIC17, Dragon64RomIC18
from dragonpy.Multicomp6809.Multicomp6809_rom import Multicomp6809Rom
from dragonpy.Simple6809.Simple6809_rom import Simple6809Rom
from dragonpy.tests.utils import no_http_requests


class ROMTest(unittest.TestCase):
    no_http_requests()  # FIXME: Find a better place for this!

    def _test_rom(self, rom: ROMFile):
        data = rom.get_data()
        self.assertIsNotNone(data)

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
