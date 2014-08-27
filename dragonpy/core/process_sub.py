#!/usr/bin/env python

"""
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import importlib
import os
import sys
import thread
import threading
import time

from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonlib.utils.logging_utils import log


class CPUThread(threading.Thread):
    def __init__ (self, cfg, cpu):
        super(CPUThread, self).__init__(name="CPU-Thread")
        log.critical(" *** CPUThread init *** ")
        self.cfg = cfg
        self.cpu = cpu

        self.last_cycle_update = None
        self.last_cycles = None
        if cfg.display_cycle:
            self.display_cycle_interval()

    def display_cycle_interval(self):
        if self.last_cycle_update is not None: # Skip the first time call.
            cycles = self.cpu.cycles - self.last_cycles
            duration = time.time() - self.last_cycle_update
            log.critical(
                "%i cycles/sec (%i cycles in last %isec)",
                int(cycles / duration), cycles, duration
            )

        self.last_cycles = self.cpu.cycles
        self.last_cycle_update = time.time()
        t = threading.Timer(5.0, self.display_cycle_interval)
        t.deamon = True
        t.start()

    def loop(self):
        cpu = self.cpu
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
        log.critical(" *** CPUThread.run() start *** ")
        try:
            self.loop()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical(" *** CPUThread.run() stopped. *** ")


def start_cpu(cfg_dict, read_bus_request_queue, read_bus_response_queue, write_bus_queue):
    log.critical(" +++ start_cpu() +++ ")
    log.debug("cfg_dict: %s", repr(cfg_dict))

    log.setLevel(cfg_dict["verbosity"])
    cfg_module = importlib.import_module(cfg_dict["cfg_module"])
    cfg = cfg_module.config(cfg_dict)

    memory = Memory(cfg, read_bus_request_queue, read_bus_response_queue, write_bus_queue)
    cpu = CPU(memory, cfg)
    memory.cpu = cpu # FIXME

    cpu_thread = CPUThread(cfg, cpu)
    cpu_thread.deamon = True
    cpu_thread.start()
    log.critical("Wait for CPU thread stop.")
    try:
        cpu_thread.join()
    except KeyboardInterrupt:
        log.critical("CPU thread stops by keyboard interrupt.")
        thread.interrupt_main()
    else:
        log.critical("CPU thread stopped.")
    cpu.running = False


def test_run():
    print "test run..."
    import subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
        "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL
#         "--machine=sbc09",
        "--machine=Simple6809",
#         "--machine=Dragon32",
#         "--machine=Multicomp6809",
#         "--max=1",
        "--display_cycle",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args).wait()
    sys.exit(0)

if __name__ == '__main__':
    print "ERROR: Run DragonPy_CLI.py instead!"
    test_run()
    sys.exit(0)
