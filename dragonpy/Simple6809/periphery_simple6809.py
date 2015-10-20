#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    http://searle.hostei.com/grant/6809/Simple6809.html


    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import sys
import os
import logging

log = logging.getLogger(__name__)

try:
    # Python 3
    import queue
    import tkinter
except ImportError:
    # Python 2
    import Queue as queue
    import Tkinter as tkinter


class Simple6809Periphery(object):
    def __init__(self, cfg, cpu, memory, display_callback, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory
        self.display_callback = display_callback
        self.user_input_queue = user_input_queue

#     BUS_ADDR_AREAS = (
#         (0xFFD8, 0xFFDF, "SD Card"),
#         (0xFFD2, 0xFFD3, "Interface 2"),
#         (0xFFD0, 0xFFD1, "Interface 1 (serial interface or TV/Keyboard)"),
#         (0xBFF0, 0xBFFF, "Interrupt vectors"),
#     )
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

        if isinstance(char, int):
            log.critical("Ignore %s from user_input_queue", repr(char))
            return 0x0

        value = ord(char)
        log.error("%04x| (%i) read from ACIA-data, send back %r $%x",
            op_address, cpu_cycles, char, value
        )
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        char = chr(value)
        log.debug("Write to screen: %s ($%x)" , repr(char), value)

#         if value >= 0x90: # FIXME: Why?
#             value -= 0x60
#             char = chr(value)
# #            log.error("convert value -= 0x30 to %s ($%x)" , repr(char), value)
#
#         if value <= 9: # FIXME: Why?
#             value += 0x41
#             char = chr(value)
# #            log.error("convert value += 0x41 to %s ($%x)" , repr(char), value)

        self.display_callback(char)


"""
    KEYCODE_MAP = {
        127: 0x03, # Break Key
    }
"""


class Simple6809PeripheryUnittest(Simple6809Periphery):
    def __init__(self, *args, **kwargs):
        super(Simple6809PeripheryUnittest, self).__init__(*args, **kwargs)
        self.display_callback = self._to_output

    def setUp(self):
        self.user_input_queue.queue.clear()
        self.output = "" # for unittest run_until_OK()
        self.output_len = 0

    def add_to_input_queue(self, txt):
        log.debug("Add %s to input queue.", repr(txt))
        for char in txt:
            self.user_input_queue.put(char)

    def _to_output(self, char):
        self.output_len += 1
        self.output += char


