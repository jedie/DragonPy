#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import Tkinter
import tkMessageBox
import threading
import thread
import Queue

from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase
from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.components.memory import Memory
from dragonpy.components.cpu6809 import CPU
from dragonpy.Dragon32.periphery_dragon import DragonDisplayOutputHandler


class MachineThread(threading.Thread):

    def __init__(self, cfg, periphery_class, display_queue, key_input_queue):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.cfg = cfg
        self.periphery_class = periphery_class
        self.display_queue = display_queue
        self.key_input_queue = key_input_queue

    def _run(self):
        memory = Memory(self.cfg)

        # redirect writes to display RAM area 0x0400-0x0600 into display_queue:
        DragonDisplayOutputHandler(self.display_queue, memory)

        periphery = self.periphery_class(
            self.cfg, memory, self.key_input_queue)
        self.cfg.periphery = periphery  # Needed?!?

        self.cpu = CPU(memory, self.cfg)
        cpu = self.cpu
        cpu.log_cpu_cycle_interval()  # turn on manually
        memory.cpu = cpu  # FIXME

        cpu.reset()
        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            log.critical("Running only %i ops!", max_ops)
            for __ in xrange(max_ops):
                cpu.get_and_call_next_op()
                if not cpu.running:
                    break
            log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
            return
        else:
            while cpu.running:
                cpu.get_and_call_next_op()

    def run(self):
        log.critical(" *** MachineThread.run() start *** ")
        try:
            self._run()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical(" *** MachineThread.run() stopped. *** ")


class Machine(object):

    def __init__(self, cfg, periphery_class, display_queue, key_input_queue):
        self.cpu_thread = MachineThread(
            cfg, periphery_class, display_queue, key_input_queue)
        self.cpu_thread.deamon = True
        self.cpu_thread.start()
#         log.critical("Wait for CPU thread stop.")
#         try:
#             cpu_thread.join()
#         except KeyboardInterrupt:
#             log.critical("CPU thread stops by keyboard interrupt.")
#             thread.interrupt_main()
#         else:
#             log.critical("CPU thread stopped.")
#         cpu.running = False

    def quit(self):
        self.cpu_thread.cpu.running = False
