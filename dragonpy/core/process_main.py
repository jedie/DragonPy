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
import thread

from dragonpy.core.process_sub import start_cpu
from dragonpy.utils.logging_utils import log


class BusCommunicationThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, cfg, periphery, read_bus_request_queue, read_bus_response_queue, write_bus_queue):
        super(BusCommunicationThread, self).__init__(name="BusThread")
        log.critical(" *** BusCommunicationThread init *** ")
        self.cfg = cfg
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue
        self.running = True

    def bus_read_poll(self):
        cycles, op_address, structure, address = self.read_bus_request_queue.get(block=True)

#        log.critical("%04x| Bus read from $%04x", op_address, address)
        if structure == self.cfg.BUS_STRUCTURE_WORD:
            value = self.periphery.read_word(cycles, op_address, address)
        else:
            value = self.periphery.read_byte(cycles, op_address, address)
#        log.critical("%04x| Bus read from $%04x: result is: $%x", op_address, address, value)
        self.read_bus_response_queue.put(value, block=True)

    def bus_write_poll(self):
        cycles, op_address, structure, address, value = self.write_bus_queue.get(block=True)

        log.debug("%04x| Bus write $%x to address $%04x", op_address, value, address)
        if structure == self.cfg.BUS_STRUCTURE_WORD:
            self.periphery.write_word(cycles, op_address, address, value)
        else:
            self.periphery.write_byte(cycles, op_address, address, value)

    def loop(self):
        while self.running:
            if not self.read_bus_request_queue.empty():
                self.bus_read_poll()

            if not self.write_bus_queue.empty():
                self.bus_write_poll()

    def run(self):
        log.critical(" *** BusCommunicationThread.run() started. *** ")
        try:
            self.loop()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical(" *** BusCommunicationThread.run() stopped. *** ")


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
    log.critical("start BusCommunicationThread()")
    bus_thread = BusCommunicationThread(cfg, periphery,
        read_bus_request_queue, read_bus_response_queue, write_bus_queue
    )
    bus_thread.deamon = True
    bus_thread.start()

    log.critical("Start CPU/Memory as separated process")
    cpu_process = multiprocessing.Process(
        name="CPU",
        target=start_cpu,
        args=(
            cfg_dict,
            read_bus_request_queue, read_bus_response_queue,
            write_bus_queue
        )
    )
    cpu_process.deamon = True
    cpu_process.start()

    try:
        periphery.mainloop(cpu_process)
    except KeyboardInterrupt:
        periphery.exit("Exit from main process.")

    log.critical("Wait for CPU quit.")
    try:
        cpu_process.join()
    except KeyboardInterrupt:
        log.critical("CPU process stops by keyboard interrupt.")
    else:
        log.critical(" *** CPU process stopped. ***")

    # Quit all threads:
    bus_thread.running = False # Quit the while loop.
#     periphery.input_thread.running = True

    log.critical("Wait for bus_thread quit.")
    bus_thread.join()
    log.critical("bus_thread has stopped.")

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
