#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import sys

try:
    import queue # Python 3
except ImportError:
    import Queue as queue # Python 2

try:
    import pty # only available under Linux
    import serial # Maybe not installed
except ImportError:
    pass

from dragonlib.utils.logging_utils import log
from dragonpy.components.periphery import PeripheryBase, TkPeripheryBase, \
    PeripheryUnittestBase

try:
    import tkinter # Python 3
except ImportError:
    try:
        import Tkinter as tkinter # Python 2
    except ImportError:
        log.critical("Error importing Tkinter!")
        tkinter = None


class Simple6809PeripheryBase(PeripheryBase):
    def __init__(self, cfg, memory):
        super(Simple6809PeripheryBase, self).__init__(cfg, memory)

        self.memory.add_read_byte_callback(self.read_acia_status, 0xa000) #  Control/status port of ACIA
        self.memory.add_read_byte_callback(self.read_acia_data, 0xa001) #  Data port of ACIA

        self.memory.add_write_byte_callback(self.write_acia_status, 0xa000) #  Control/status port of ACIA
        self.memory.add_write_byte_callback(self.write_acia_data, 0xa001) #  Data port of ACIA

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        return 0xff
    def read_acia_status(self, cpu_cycles, op_address, address):
        return 0x03

    def read_acia_data(self, cpu_cycles, op_address, address):
        try:
            char = self.user_input_queue.get(block=False)
        except queue.Empty:
            return 0x0

        value = ord(char)
        log.info(
#         log.critical(
            "%04x| (%i) read from ACIA-data, send back %r $%x",
            op_address, cpu_cycles, char, value
        )
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        char = chr(value)
        log.info("*"*79)
        log.info("Write to screen: %s ($%x)" , repr(char), value)
        log.info("*"*79)

        if value >= 0x90: # FIXME: Why?
            value -= 0x60
            char = chr(value)
#            log.info("convert value -= 0x30 to %s ($%x)" , repr(char), value)

        if value <= 9: # FIXME: Why?
            value += 0x41
            char = chr(value)
#            log.info("convert value += 0x41 to %s ($%x)" , repr(char), value)

        self.display_queue.put(char)


class Simple6809PeripheryUnittest(PeripheryUnittestBase, Simple6809PeripheryBase):
    pass



class Simple6809PeripheryTk(TkPeripheryBase, Simple6809PeripheryBase):
    TITLE = "DragonPy - Simple 6809"
    GEOMETRY = "+500+300"
    KEYCODE_MAP = {
        19: 0x03, # Break Key under windows
        127: 0x03, # Break Key
    }
    INITAL_INPUT = "\r\n".join([
#         'PRINT "HELLO WORLD!"',
#         '? 123',

        '10 FOR I=1 TO 3',
        '20 PRINT STR$(I)+" DRAGONPY"',
        '30 NEXT I',
        'RUN',
        '',
        'LIST',

    ]) + "\r\n"

    def event_return(self, event):
        self.user_input_queue.put("\r")
#         self.user_input_queue.put("\n")



# Simple6809Periphery = Simple6809PeripherySerial
Simple6809Periphery = Simple6809PeripheryTk

Simple6809TestPeriphery = Simple6809PeripheryUnittest


def test_run():
    import subprocess
    cmd_args = [
        sys.executable,
#         "/usr/bin/pypy",
        os.path.join("..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL

        "--machine=Simple6809",
#         "--max=500000",
#         "--max=20000",
#         "--max=1",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
