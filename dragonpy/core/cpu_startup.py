#!/usr/bin/env python

"""
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import threading
import time
import multiprocessing
import importlib

from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
import sys


log = multiprocessing.log_to_stderr()


class CPUThread(threading.Thread):
    def __init__ (self, cfg, cpu):
        super(CPUThread, self).__init__()
        log.info(" *** CPUThread init *** ")
        self.cfg = cfg
        self.cpu = cpu

    def run(self):
        log.info(" *** CPUThread.run() *** ")
        cpu = self.cpu
        cpu.reset()
        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            log.critical("Runing only %i ops!", max_ops)
            for __ in xrange(max_ops):
                cpu.get_and_call_next_op()
            log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
        else:
            while not cpu.quit:
#             for __ in xrange(20000):
                cpu.get_and_call_next_op()
        print "Quit CPU"


def start_cpu(cfg_dict, read_bus_request_queue, read_bus_response_queue, write_bus_queue):
    log.info(" +++ start_cpu() +++ ")
    log.info("cfg_dict: %s", repr(cfg_dict))

    log.setLevel(cfg_dict["verbosity"])
    cfg_module = importlib.import_module(cfg_dict["cfg_module"])
    cfg = cfg_module.config(cfg_dict)

    memory = Memory(cfg, read_bus_request_queue, read_bus_response_queue, write_bus_queue)
    cpu = CPU(memory, cfg)
    memory.cpu = cpu

    cpu_thread = CPUThread(cfg, cpu)
    cpu_thread.start()
    cpu_thread.join()

    log.info(" +++ start_cpu(): CPU has quit +++ ")


def test_run():
    print "test run..."
    import subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "..", "DragonPy_CLI.py"),
        "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL
#         "--cfg=sbc09",
        "--cfg=Simple6809",
#         "--cfg=Dragon32",
#         "--cfg=Multicomp6809",
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
