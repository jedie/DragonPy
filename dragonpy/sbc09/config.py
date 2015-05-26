# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os

from dragonpy.components.rom import ROMFile
from dragonpy.core.configs import BaseConfig, SBC09
from dragonpy.sbc09.mem_info import get_sbc09_meminfo
from dragonpy.sbc09.periphery import SBC09Periphery
from dragonlib.api import CoCoAPI


class SBC09Cfg(BaseConfig):
    """
    DragonPy config for Lennart's 6809 single board computer

        Buggy machine language monitor and rudimentary O.S. version 1.0

    More info read ./sbc09/README.creole
    """
    CONFIG_NAME = SBC09
    MACHINE_NAME="Lennart's 6809 single board computer"

    RAM_START = 0x0000
    RAM_END = 0x7FFF
    # RAM size: 0x8000 == 32768 Bytes

    ROM_START = 0x8000
    ROM_END = 0xFFFF
    # ROM size: 0x4000 == 16384 Bytes

    BUS_ADDR_AREAS = (
        (0xe000, 0xe001, "RS232 interface"), # emulated serial port (ACIA)
        (0xFFF2, 0xFFFE, "Interrupt vectors"),
    )

    DEFAULT_ROMS = (
        ROMFile(address=0x8000, max_size=None,
            filepath=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                "v09.rom" # Source for this is monitor.asm
            )
        ),
    )

    # Used in unittest for init the machine:
    STARTUP_END_ADDR = 0xe45a # == O.S. routine to read a character into B register.

    def __init__(self, cmd_args):
        super(SBC09Cfg, self).__init__(cmd_args)

        self.machine_api = CoCoAPI() # FIXME!

#         if self.verbosity <= logging.INFO:
        self.mem_info = get_sbc09_meminfo()

        self.periphery_class = SBC09Periphery


config = SBC09Cfg


def test_run():
    import sys, subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL

        "--machine=sbc09",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
