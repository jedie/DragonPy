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

import logging

log=logging.getLogger(__name__)
from dragonpy.components.periphery import PeripheryBase, TkPeripheryBase, \
    ConsolePeripheryBase, PeripheryUnittestBase


try:
    import queue # Python 3
except ImportError:
    import Queue as queue # Python 2

try:
    import tkinter # Python 3
except ImportError:
    try:
        import Tkinter as tkinter # Python 2
    except ImportError:
        log.critical("Error importing Tkinter!")
        tkinter = None



class SBC09Periphery(object):
    TITLE = "DragonPy - Buggy machine language monitor and rudimentary O.S. version 1.0"
    INITAL_INPUT = (
#        # Dump registers
#        'r\r\n'
#
#        # SSaddr,len - Dump memory region as Motorola S records.
#        'ss\r\n'
#
#        # Daddr,len - Dump memory region
#        'DE5E2\r\n'
#
#        # Iaddr - Display the contents of the given address.
#        'IE001\r\n' # e.g.: Show the ACIA status
#
#        # Uaddr,len - Diassemble memory region
#        'UE400\r\n'
#
#        # Calculate simple expression in hex with + and -
#        'H4444+A5\r\n'

        #
#         "UE400,20\r\n"
#         "ubasic\r\n"
    )

    def __init__(self, cfg, cpu, memory, display_callback, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory
        self.display_callback = display_callback
        self.user_input_queue = user_input_queue

        self.memory.add_read_byte_callback(self.read_acia_status, 0xe000) #  Control/status port of ACIA
        self.memory.add_read_byte_callback(self.read_acia_data, 0xe001) #  Data port of ACIA

        self.memory.add_write_byte_callback(self.write_acia_status, 0xe000) #  Control/status port of ACIA
        self.memory.add_write_byte_callback(self.write_acia_data, 0xe001) #  Data port of ACIA

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
        log.error("%04x| (%i) read from ACIA-data, send back %r $%x",
            op_address, cpu_cycles, char, value
        )
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        char = chr(value)
        log.debug("Write to screen: %s ($%x)" , repr(char), value)
#        log.error("*"*79)
#        log.error("Write to screen: %s ($%x)" , repr(char), value)
#        log.error("*"*79)

        self.display_callback(char)





class DummyStdout(object):
    def dummy_func(self, *args):
        pass
    write = dummy_func
    flush = dummy_func


class SBC09PeripheryConsole(SBC09Periphery, ConsolePeripheryBase):
    """
    A simple console to interact with the 6809 simulation.
    """
    def new_output_char(self, char):
        sys.stdout.write(char)
        sys.stdout.flush()


class SBC09PeripheryUnittest(SBC09Periphery):
    def __init__(self, *args, **kwargs):
        super(SBC09PeripheryUnittest, self).__init__(*args, **kwargs)
        self.memory.add_write_byte_callback(self.write_acia_data, 0xa001) #  Data port of ACIA

    def setUp(self):
        self.user_input_queue.queue.clear()
        self.output = "" # for unittest run_until_OK()
        self.output_len = 0

    def add_to_input_queue(self, txt):
        log.debug("Add %s to input queue.", repr(txt))
        for char in txt:
            self.user_input_queue.put(char)

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        char = chr(value)
#         log.info("%04x| Write to screen: %s ($%x)", op_address, repr(char), value)

        self.output_len += 1
        self.output += char



# SBC09Periphery = SBC09PeripherySerial
#SBC09Periphery = SBC09PeripheryTk
SBC09Periphery = SBC09PeripheryConsole


