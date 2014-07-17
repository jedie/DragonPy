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

import Queue
import dragonpy
import logging
import multiprocessing
import multiprocessing
import os
import os
import select
import socket
import struct
import subprocess
import sys
import sys
import threading
import time
import inspect

from dragonpy.utils import pager
from dragonpy.utils.simple_debugger import print_exc_plus
from dragonpy.core.cpu_startup import start_cpu

log = multiprocessing.log_to_stderr()


class BusReadThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, cfg, periphery, read_bus_request_queue, read_bus_response_queue):
        super(BusReadThread, self).__init__()
        log.info(" *** BusReadThread init *** ")
        self.cfg = cfg
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.quit = False

    def run(self):
        log.info(" *** BusReadThread.run() *** ")
        while not self.quit:
#         for __ in xrange(100):
            try:
                cycles, op_address, structure, address = self.read_bus_request_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
#             log.info("%04x| Bus read from $%04x", op_address, address)
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                value = self.periphery.read_word(cycles, op_address, address)
            else:
                value = self.periphery.read_byte(cycles, op_address, address)
#             log.info("%04x| Bus read from $%04x: result is: $%x", op_address, address, value)
            self.read_bus_response_queue.put(value)


class BusWriteThread(threading.Thread):
    """
    Wait for CPU/Memory bus write: Redirect write to periphery
    """
    def __init__ (self, cfg, periphery, write_bus_queue):
        super(BusWriteThread, self).__init__()
        log.info(" *** BusWriteThread init *** ")
        self.cfg = cfg
        self.periphery = periphery
        self.write_bus_queue = write_bus_queue
        self.quit = False

    def run(self):
        log.info(" *** BusWriteThread.run() *** ")
        while not self.quit:
#         for __ in xrange(100):
            try:
                cycles, op_address, structure, address, value = self.write_bus_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
            log.info("%04x| Bus write $%x to address $%04x", op_address, value, address)
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                self.periphery.write_word(cycles, op_address, address, value)
            else:
                self.periphery.write_byte(cycles, op_address, address, value)


def main_process_startup(cfg):
    log.info("use cfg: %s", cfg.config_name)

    cfg_dict = cfg.cfg_dict
    cfg_dict["use_bus"] = True # Enable memory read/write via multiprocessing.Queue()
    periphery = cfg.periphery_class(cfg)

    # communication channel between processes:
    read_bus_request_queue = multiprocessing.Queue(maxsize=1)
    read_bus_response_queue = multiprocessing.Queue(maxsize=1)
    write_bus_queue = multiprocessing.Queue(maxsize=1)

    # API between processes and local periphery
    log.info("start BusReadThread()")
    bus_read_thread = BusReadThread(cfg, periphery, read_bus_request_queue, read_bus_response_queue)
    bus_read_thread.start()
    log.info("start BusWriteThread()")
    bus_write_thread = BusWriteThread(cfg, periphery, write_bus_queue)
    bus_write_thread.start()

    log.info("Start CPU/Memory as separated process")
    p = multiprocessing.Process(target=start_cpu,
        args=(
            cfg_dict,
            read_bus_request_queue, read_bus_response_queue,
            write_bus_queue
        )
    )
    p.start()

    periphery.mainloop()

    p.join() # Wait if CPU quits
    log.info(" *** CPU has quit ***")

    periphery.exit()

    # Quit all threads:
    bus_read_thread.quit = True
    bus_write_thread.quit = True
#     periphery.input_thread.quit = True

    log.info("Wait for quit bus threads")
    bus_read_thread.join()
    bus_write_thread.join()

#     log.info(" *** FIXME: Input one char to real END :(")
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



# OLD:

log = logging.getLogger("DragonPy")

def activate_full_debug_logging():
    log2 = logging.getLogger("DragonPy")
    handler = logging.StreamHandler()
    handler.level = 5
    log2.handlers = (handler,)
    log.critical("Activate full debug logging in %s!", __file__)


class Dragon(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.periphery = cfg.periphery_class(cfg)
        # self.cfg.periphery = self.periphery

        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(0)

        bus_socket_host, bus_socket_port = listener.getsockname()

        process_args = (self.cfg, True, bus_socket_host, bus_socket_port)
        #
        # TODO: Using multiprocessing doesn't work under windows, yet.
        #
        # Problem are not pickleable objects from self.cfg
        # http://www.python-forum.de/viewtopic.php?p=261671#p261671 (de)
        #
        # Test with:
        # import pickle
        # pickle.dumps(process_args)
        #
        if sys.platform != "win32":
            periphery_process = multiprocessing.Process(
                target=cpu6809.start_CPU, args=process_args
            )
            periphery_process.daemon = True
            periphery_process.start()
        else:
            cfg_dict = [sys.executable, "-m", "dragonpy.cpu6809",
                 "--bus_socket_host=%s" % bus_socket_host,
                 "--bus_socket_port=%i" % bus_socket_port,
            ]
            cfg_dict += sys.argv[1:]
            root_path = os.path.abspath(
                os.path.join(os.path.dirname(dragonpy.__file__), "..")
            )
            print "Startup CPU with: %s in %s" % (" ".join(cfg_dict), root_path)
            try:
                self.core = subprocess.Popen(cfg_dict, cwd=root_path)
            except:
                print_exc_plus()

        rs, _, _ = select.select([listener], [], [], 2)
        if not rs:
            print >> sys.stderr, "CPU module did not start"
            sys.exit(1)
        else:
            print "CPU started"
        self.cpu, _ = listener.accept()

        self.bus_type_func_map = {
            (self.cfg.BUS_ACTION_READ, self.cfg.BUS_STRUCTURE_BYTE): self.periphery.read_byte,
            (self.cfg.BUS_ACTION_READ, self.cfg.BUS_STRUCTURE_WORD): self.periphery.read_word,
            (self.cfg.BUS_ACTION_WRITE, self.cfg.BUS_STRUCTURE_BYTE): self.periphery.write_byte,
            (self.cfg.BUS_ACTION_WRITE, self.cfg.BUS_STRUCTURE_WORD): self.periphery.write_word,
        }

    def run(self):
        while True:
            cpu_data = self.cpu.recv(self.cfg.STRUCT_TO_PERIPHERY_LEN)
#            log.debug("receive %s Bytes from CPU via bus" % self.cfg.STRUCT_TO_PERIPHERY_LEN)
            if len(cpu_data) == 0:
                break

            try:
                cpu_cycles, op_address, action, structure, address, value = struct.unpack(self.cfg.STRUCT_TO_PERIPHERY_FORMAT, cpu_data)
            except Exception, err:
                msg = "Error unpack %s with %s: %s" % (
                    repr(cpu_data), self.cfg.STRUCT_TO_PERIPHERY_FORMAT, err
                )
                print >> sys.stderr, msg
                raise

            periphery_func = self.bus_type_func_map[(action, structure)]

            if action == self.cfg.BUS_ACTION_READ: # == 1
                value = periphery_func(cpu_cycles, op_address, address)
                assert isinstance(value, int), "Periphery Func. %r must return a integer! It has returned: %s" % (periphery_func.__name__, repr(value))
                try:
                    data = struct.pack(self.cfg.STRUCT_TO_MEMORY_FORMAT, value)
                except struct.error, err:
                    msg = "Error pack response %s with %s: %s" % (
                        repr(value), self.cfg.STRUCT_TO_MEMORY_FORMAT, err
                    )
                    print >> sys.stderr, msg
                    raise
                self.cpu.send(data)
            elif action == self.cfg.BUS_ACTION_WRITE: # == 0
                periphery_func(cpu_cycles, op_address, address, value)
            else:
                raise RuntimeError

            should_quit = self.periphery.cycle(cpu_cycles, op_address)
            if should_quit is False:
                log.critical("Exit DragonPy run loop.")
                return


if __name__ == "__main__":
    print "Run DragonPy_CLI.py instead"
    sys.exit(0)
