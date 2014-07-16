#!/usr/bin/env python
# encoding:utf-8

"""
    6809 BASIC console
    ~~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import logging
import sys
import threading
import time

from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809PeripheryBase
from dragonpy.cpu6809 import CPU
from dragonpy.utils.logging_utils import setup_logging
from dragonpy.utils import pager


log = logging.getLogger("DragonPy.6809Console")


class CmdArgs(object):
    bus_socket_host = None
    bus_socket_port = None
    ram = None
    rom = None
    verbosity = None
    max = None
    trace = False

    # print CPU cycle/sec while running
    display_cycle = False


class InputPoll(threading.Thread):
    def __init__ (self, in_queue):
        self.input_queue = in_queue
        threading.Thread.__init__ (self)

    def run(self):
        while True:
            char = pager.getch()
            if char == "\n":
                self.input_queue.put("\r")

            char = char.upper()
            self.input_queue.put(char)


class Console6809Periphery(Simple6809PeripheryBase):
    def __init__(self, input_queue, *args, **kwargs):
        super(Console6809Periphery, self).__init__(*args, **kwargs)

        self.user_input_queue = input_queue # Buffer for input to send back to the CPU

        self.last_cycles = 0
        self.update_duration = 10
        self.last_cycles_update = time.time()
        self.next_cycles_update = self.last_cycles_update + self.update_duration

    def new_output_char(self, char):
        sys.stdout.write(char)
        sys.stdout.flush()

    def update(self, cpu_cycles):
        if time.time() >= self.next_cycles_update:
            current_time = time.time()
            duration = current_time - self.last_cycles_update

            count = cpu_cycles - self.last_cycles
            log.critical("%.2f cycles/sec. (current cycle: %i)", float(count / duration), cpu_cycles)

            self.last_cycles = cpu_cycles
            self.last_cycles_update = current_time
            self.next_cycles_update = current_time + self.update_duration


def calc_new_burst_count(burst_count, loop_count, target_loop_count):
    a = float(burst_count) / float(loop_count) * target_loop_count
    b = (burst_count - a)
    new_burst_count = burst_count + b
    new_burst_count = int(round(new_burst_count))
    if new_burst_count < 1:
        new_burst_count = 1
    return new_burst_count


class Console6809(object):
    def __init__(self):
        cmd_args = CmdArgs
        cfg = Simple6809Cfg(cmd_args)

        self.input_queue = Queue.Queue()
        self.periphery = Console6809Periphery(self.input_queue, cfg)
        cfg.periphery = self.periphery

        self.cpu = CPU(cfg)

    def run(self):
        self.cpu.reset()

        self.periphery.add_to_input_queue("\r\n".join([
            '10 FOR I=1 TO 3',
            '20 PRINT STR$(I)+" DRAGONPY"',
            '30 NEXT I',
            'RUN',
        ]) + "\r\n")

        print "Startup 6809 machine..."

        input_thread = InputPoll(self.input_queue)
        input_thread.start()

        update_duration = 0.5
        next_update = time.time() + update_duration
        burst_count = 1000
        op_count = 0
        loop_count = 0
        target_loop_count = 5
        try:
            while True:
                loop_count += 1
                if time.time() > next_update:
                    self.periphery.update(self.cpu.cycles)
                    next_update = time.time() + update_duration

                    if loop_count != target_loop_count:
                        # Recalculate the burst_count
                        # to match the arget_loop_count
#                        old_burst = burst_count # Only for display updates
                        burst_count = calc_new_burst_count(burst_count, loop_count, target_loop_count)
#                        if old_burst != burst_count: # Display a update
#                            print "*** Set burst count to: %s op calls." % burst_count

                for __ in xrange(burst_count):
                    self.cpu.get_and_call_next_op()

                op_count += burst_count
        except SystemExit:
            print "EXIT. Running %i op calls." % op_count


if __name__ == '__main__':
    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )
    c = Console6809()
    c.run()

    print " --- END --- "
