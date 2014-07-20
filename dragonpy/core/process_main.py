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

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import multiprocessing
import os
import sys
import threading

from dragonpy.utils.simple_debugger import print_exc_plus
from dragonpy.core.process_sub import start_cpu

from dragonpy.utils.logging_utils import log


class BusReadThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, cfg, periphery, read_bus_request_queue, read_bus_response_queue):
        super(BusReadThread, self).__init__()
        log.critical(" *** BusReadThread init *** ")
        self.cfg = cfg
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.running = True

    def run(self):
        log.critical(" *** BusReadThread.run() started. *** ")
        while self.running:
#         for __ in xrange(100):
            try:
                cycles, op_address, structure, address = self.read_bus_request_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
#             log.critical("%04x| Bus read from $%04x", op_address, address)
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                value = self.periphery.read_word(cycles, op_address, address)
            else:
                value = self.periphery.read_byte(cycles, op_address, address)
#             log.critical("%04x| Bus read from $%04x: result is: $%x", op_address, address, value)
            self.read_bus_response_queue.put(value)
        log.critical(" *** BusReadThread.run() stopped. *** ")


class BusWriteThread(threading.Thread):
    """
    Wait for CPU/Memory bus write: Redirect write to periphery
    """
    def __init__ (self, cfg, periphery, write_bus_queue):
        super(BusWriteThread, self).__init__()
        log.critical(" *** BusWriteThread init *** ")
        self.cfg = cfg
        self.periphery = periphery
        self.write_bus_queue = write_bus_queue
        self.running = True

    def run(self):
        log.critical(" *** BusWriteThread.run() started. *** ")
        while self.running:
#         for __ in xrange(100):
            try:
                cycles, op_address, structure, address, value = self.write_bus_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
            log.debug("%04x| Bus write $%x to address $%04x", op_address, value, address)
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                self.periphery.write_word(cycles, op_address, address, value)
            else:
                self.periphery.write_byte(cycles, op_address, address, value)
        log.critical(" *** BusWriteThread.run() stopped. *** ")


def main_process_startup(cfg):
    log.critical("use cfg: %s", cfg.config_name)

    cfg_dict = cfg.cfg_dict
    cfg_dict["use_bus"] = True # Enable memory read/write via multiprocessing.Queue()
    periphery = cfg.periphery_class(cfg)

    # communication channel between processes:
    read_bus_request_queue = multiprocessing.Queue(maxsize=1)
    read_bus_response_queue = multiprocessing.Queue(maxsize=1)
    write_bus_queue = multiprocessing.Queue(maxsize=1)

    # API between processes and local periphery
    log.critical("start BusReadThread()")
    bus_read_thread = BusReadThread(cfg, periphery, read_bus_request_queue, read_bus_response_queue)
    bus_read_thread.start()
    log.critical("start BusWriteThread()")
    bus_write_thread = BusWriteThread(cfg, periphery, write_bus_queue)
    bus_write_thread.start()

    log.critical("Start CPU/Memory as separated process")
    cpu_process = multiprocessing.Process(target=start_cpu,
        args=(
            cfg_dict,
            read_bus_request_queue, read_bus_response_queue,
            write_bus_queue
        )
    )
    cpu_process.deamon = True
    cpu_process.start()

    periphery.mainloop(cpu_process)

    log.critical("Wait for CPU quit.")
    cpu_process.join()

    log.critical(" *** CPU process stopped. ***")

    # Quit all threads:
    bus_read_thread.running = False # Quit the while loop.
    bus_write_thread.running = False # Quit the while loop.
#     periphery.input_thread.running = True

    log.critical("Wait for bus_read_thread quit.")
    bus_read_thread.join()
    log.critical("bus_read_thread has stopped.")

    log.critical("Wait for bus_write_thread quit.")
    bus_write_thread.join()
    log.critical("write_read_thread has stopped.")

#     log.critical(" *** FIXME: Input one char to real END :(")
#     periphery.input_thread.join() # Will only end after one input char :(



def test_run():
    print "test run..."
    import subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL
#         "--cfg=sbc09",
        "--cfg=Simple6809",
#         "--cfg=Dragon32",
#         "--cfg=Multicomp6809",
#         "--max=100000",
        "--display_cycle",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args).wait()
    sys.exit(0)

if __name__ == '__main__':
    print "ERROR: Run DragonPy_CLI.py instead!"
    test_run()
    sys.exit(0)
