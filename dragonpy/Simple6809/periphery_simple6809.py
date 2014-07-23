#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import os
import Queue
import multiprocessing

try:
    import Tkinter
except Exception, err:
    print "Error importing Tkinter: %s" % err
    Tkinter = None

try:
    import pty # only available under Linux
    import serial # Maybe not installed
except ImportError:
    pass

from dragonpy.components.periphery import PeripheryBase, TkPeripheryBase


from dragonpy.utils.logging_utils import log


class Simple6809PeripheryBase(PeripheryBase):
    def __init__(self, cfg):
        super(Simple6809PeripheryBase, self).__init__(cfg)
        self.read_address2func_map = {
            0xa000: self.read_acia_status, # Control/status port of ACIA
            0xa001: self.read_acia_data, # Data port of ACIA
            0xbffe: self.reset_vector,
        }
        self.write_address2func_map = {
            0xa000: self.write_acia_status, # Control/status port of ACIA
            0xa001: self.write_acia_data, # Data port of ACIA
        }

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        return 0xff
    def read_acia_status(self, cpu_cycles, op_address, address):
        return 0x03

    def read_acia_data(self, cpu_cycles, op_address, address):
        if self.user_input_queue.empty():
            return 0x0

        char = self.user_input_queue.get()
        value = ord(char)
#         log.info(
        log.critical(
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

        self.output_queue.put(char)


class Simple6809PeripheryUnittest(Simple6809PeripheryBase):
    def __init__(self, *args, **kwargs):
        super(Simple6809PeripheryUnittest, self).__init__(*args, **kwargs)
        self._out_buffer = ""
        self.out_lines = []

    def new_output_char(self, char):
#        sys.stdout.write(char)
#        sys.stdout.flush()
        self._out_buffer += char
        if char == "\n":
            self.out_lines.append(self._out_buffer)
            self._out_buffer = ""


class Simple6809PeripheryTk(TkPeripheryBase, Simple6809PeripheryBase):
    TITLE = "DragonPy - Simple 6809"
    GEOMETRY = "+500+300"
    KEYCODE_MAP = {
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

#     _STOP_AFTER_OK_COUNT = None
# #     _STOP_AFTER_OK_COUNT = 2
#     def update(self):
#         is_empty = self.output_queue.empty()
#         super(Simple6809PeripheryTk, self).update()
#         if self._STOP_AFTER_OK_COUNT is not None and not is_empty:
#             txt = self.text.get(1.0, Tkinter.END)
#             if txt.count("OK\r\n") >= self._STOP_AFTER_OK_COUNT:
#                 log.critical("-> exit!")
#                 self.destroy()


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

        "--cfg=Simple6809",
#         "--max=500000",
#         "--max=20000",
#         "--max=1",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
