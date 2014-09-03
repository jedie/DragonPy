#!/usr/bin/env python2
# encoding:utf-8

"""
    6809 BASIC console
    ~~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import queue
import sys
import threading
import time

from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809PeripheryBase
from dragonlib.utils.logging_utils import setup_logging
from dragonpy.utils import pager
from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonlib.utils.logging_utils import log


CFG_DICT = {
    "verbosity":None,
    "display_cycle":True,
    "trace":None,
    "bus_socket_host":None,
    "bus_socket_port":None,
    "ram":None,
    "rom":None,

    "use_bus":False,
}


class InputPollThread(threading.Thread):
    def __init__ (self, in_queue):
        self.user_input_queue = in_queue
        super(InputPollThread, self).__init__()

    def run(self):
        while True:
            char = pager.getch()
            if char == "\n":
                self.user_input_queue.put("\r")

            char = char.upper()
            self.user_input_queue.put(char)


class Console6809Periphery(Simple6809PeripheryBase):
    def __init__(self, input_queue, *args, **kwargs):
        super(Console6809Periphery, self).__init__(*args, **kwargs)

        self.user_input_queue = input_queue # Buffer for input to send back to the CPU

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        super(Console6809Periphery, self).write_acia_data(cpu_cycles, op_address, address, value)
        while True:
            try:
                char = self.display_queue.get(block=False)
            except queue.Empty:
                break
            else:
                sys.stdout.write(char)
        sys.stdout.flush()


class Console6809(object):
    def __init__(self):
        cfg = Simple6809Cfg(CFG_DICT)

        self.user_input_queue = queue.Queue()
        self.periphery = Console6809Periphery(self.user_input_queue, cfg)
        cfg.periphery = self.periphery

        memory = Memory(cfg)
        self.cpu = CPU(memory, cfg)
        memory.cpu = self.cpu # FIXME

    def update_display(self):
        self.periphery.update(self.cpu.cpu_cycles)
        if self.cpu.running:
            t = threading.Timer(0.25, self.update_display)
            t.deamon = True
            t.start()

    def run(self):
        self.cpu.reset()

        self.periphery.add_to_input_queue("\r\n".join([
            '10 FOR I=1 TO 3',
            '20 PRINT STR$(I)+" DRAGONPY"',
            '30 NEXT I',
            'RUN',
        ]) + "\r\n")

        input_thread = InputPollThread(self.user_input_queue)
        input_thread.deamon = True
        input_thread.start()

        while self.cpu.running == True:
            self.cpu.get_and_call_next_op()


if __name__ == '__main__':
    print("Startup 6809 machine...")

    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
        level=40 # ERROR
#         level=50 # CRITICAL/FATAL
    )
    c = Console6809()
    c.run()

    print(" --- END --- ")
