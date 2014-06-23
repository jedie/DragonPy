# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from core.configs import BaseConfig
# from Simple6809.mem_info import get_simple6809_meminfo
from Multicomp6809.periphery_Multicomp6809 import Multicomp6809Periphery


class Multicomp6809Cfg(BaseConfig):
    """
    DragonPy config for Grant Searle's Multicomp FPGA project
    Mhttp://searle.hostei.com/grant/Multicomp/
    """
    RAM_START = 0x0000
    RAM_END = 0x7FFF
    RAM_SIZE = 0x8000 # 32768 Bytes

    ROM_START = 0xE000
    ROM_END = 0xFFFF
    ROM_SIZE = 0x2000 # 8192 Bytes

    RESET_VECTOR = 0xBFFE

    BUS_ADDR_AREAS = (
        (0xFFD8, 0xFFDF, "SD Card"),
        (0xFFD2, 0xFFD3, "Interface 2"),
        (0xFFD0, 0xFFD1, "Interface 1 (serial interface or TV/Keyboard)"),
        (0xBFF0, 0xBFFF, "Interrupt vectors"),
    )

    DEFAULT_ROM = os.path.join("Multicomp6809", "EXT_BASIC_NO_USING.bin")

    def __init__(self, cmd_args):
        self.ROM_SIZE = (self.ROM_END - self.ROM_START) + 1
        super(Multicomp6809Cfg, self).__init__(cmd_args)

#         if self.verbosity <= logging.INFO:
#         self.mem_info = get_simple6809_meminfo()

        self.periphery_class = Multicomp6809Periphery

