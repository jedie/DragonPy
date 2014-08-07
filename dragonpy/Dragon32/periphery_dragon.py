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
import Tkinter
import tkMessageBox
import threading
import thread

from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
import Queue


class Dragon32Periphery(PeripheryBase):

    """
    GUI independent stuff
    """

    def __init__(self, cfg, memory, key_input_queue):
        super(Dragon32Periphery, self).__init__(cfg, memory)

        self.kbd = 0xBF
        self.display = None
        self.speaker = None  # Speaker()
        self.cassette = None  # Cassette()

        self.sam = SAM(cfg, memory)
        self.pia = PIA(cfg, memory, key_input_queue)

        self.memory.add_read_byte_callback(self.no_dos_rom, 0xC000)
        self.memory.add_read_word_callback(self.no_dos_rom, 0xC000)

        self.running = True

    def no_dos_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: DOS ROM requested. Send 0x00 back", op_address)
        return 0x00

    def update(self, cpu_cycles):
        #        log.critical("update pygame")
        if not self.running:
            return
        if self.speaker:
            self.speaker.update(cpu_cycles)


class DragonDisplayOutputHandler(object):

    """
    redirect writes to display RAM area 0x0400-0x0600 into display_queue.
    """

    def __init__(self, display_queue, memory):
        self.display_queue = display_queue
        self.memory = memory
        self.memory.add_write_byte_middleware(
            self.to_display_queue, 0x0400, 0x0600)

    def to_display_queue(self, cpu_cycles, op_address, address, value):
        self.display_queue.put(
            (cpu_cycles, op_address, address, value)
        )
        return value


#------------------------------------------------------------------------------


def test_run_cli():
    import subprocess
    cmd_args = [
        sys.executable,
        #         "/usr/bin/pypy",
        os.path.join("..", "DragonPy_CLI.py"),
        #         "--verbosity=5",
        # "--verbosity=10", # DEBUG
        # "--verbosity=20", # INFO
        # "--verbosity=30", # WARNING
        # "--verbosity=40", # ERROR
        "--verbosity=50",  # CRITICAL/FATAL
        #
        #         '--log_formatter=%(filename)s %(funcName)s %(lineno)d %(message)s',
        #
        #         "--cfg=Dragon32",
        "--cfg=Dragon64",
        #
        "--dont_open_webbrowser",
        "--display_cycle",  # print CPU cycle/sec while running.
        #
        #         "--max=15000",
        #         "--max=46041",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


def test_run_direct():
    import sys
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        #         "/usr/bin/pypy",
        os.path.join("..",
                     "Dragon32_test.py"
                     #             "Dragon64_test.py"
                     ),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    #     test_run_cli()
    test_run_direct()
