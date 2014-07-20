#!/usr/bin/env python

"""
    DragonPy
    ========

    Just a multiprocessing concept 2

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import threading
import time
import multiprocessing

from dragonpy.utils.logging_utils import log


#------------------------------------------------------------------------------


class Memory(object):
    def __init__(self, cpu, read_bus_request_queue, read_bus_response_queue, write_bus_queue, size=0x1fff):
        self.cpu = cpu
        self._mem = [0x00] * size

        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue

        self._read_callbacks = {0xe001: self.bus_read_byte}
        self._write_callbacks = {0xe001: self.bus_write_byte}

    def bus_read_byte(self, address):
        self.read_bus_request_queue.put(
            (self.cpu.cycles, self.cpu.op_address, address),
            block=True
        )
        return self.read_bus_response_queue.get(block=True)

    def bus_write_byte(self, address, value):
        self.write_bus_queue.put(
            (self.cpu.cycles, self.cpu.op_address, address, value),
            block=True
        )

    def read_byte(self, address):
        log.info("Memory.readbyte from $%04x" % address)
        if address in self._read_callbacks:
            return self._read_callbacks[address](address)
        else:
            return self._mem[address]

    def write_byte(self, address, value):
        log.info("Memory.write_byte $%02x to $%04x" % (value, address))
        if address in self._write_callbacks:
            self._write_callbacks[address](address, value)
        else:
            self._mem[address] = value


class CPU(object):
    def __init__(self):
        log.info(" *** CPU init *** ")
        self.op_address = 0
        self.cycles = 0
        self.quit = False

    def get_and_call_next_op(self):
        time.sleep(1)
        self.op_address += 1
        self.cycles += 1
        user_input = self.memory.read_byte(address=0xe001)
        if not user_input:
            return
        char = chr(user_input)
        print "User Input (type 'x' to exit!): %s -> %s" % (
            repr(user_input), char
        )
        if char == "x":
            self.quit = True

        value = ord(char.upper())
        self.memory.write_byte(address=0xe001, value=value)
        print


class CPUThread(threading.Thread):
    def __init__ (self, cpu):
        super(CPUThread, self).__init__()
        log.info(" *** CPUThread init *** ")
        self.cpu = cpu

    def run(self):
        log.info(" *** CPUThread.run() *** ")
        cpu = self.cpu
        while not cpu.quit:
            cpu.get_and_call_next_op()
        print "Quit CPU"


def start_cpu(cfg_dict, read_bus_request_queue, read_bus_response_queue, write_bus_queue):
    log.info(" +++ start_cpu() +++ ")
    log.info("cfg_dict: %s", repr(cfg_dict))
    
    log.setLevel(cfg_dict["log_level"])
    
    cpu = CPU()
    cpu.memory = Memory(cpu, read_bus_request_queue, read_bus_response_queue, write_bus_queue)

    cpu_thread = CPUThread(cpu)
    cpu_thread.start()
    cpu_thread.join()

    log.info(" +++ start_cpu(): CPU has quit +++ ")


