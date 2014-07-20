#!/usr/bin/env python

"""
    DragonPy
    ========

    Just a multiprocessing concept

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from multiprocessing.managers import BaseManager
import Queue
import os
import threading
import time

from dragonpy.utils import pager


class InputPollThread(threading.Thread):
    def __init__ (self, in_queue):
        print " *** InputPollThread init, pid:", os.getpid()
        self.user_input_queue = in_queue
        super(InputPollThread, self).__init__()

    def run(self):
        print " *** InputPollThread running, pid:", os.getpid()
        while True:
            char = pager.getch()
            print "Char from InputPollThread:", repr(char)
            self.user_input_queue.put(char)


class Periphery(object):
    def __init__(self):
        print " *** Periphery init, pid:", os.getpid()

        self.user_input_queue = Queue.Queue() # Buffer for input to send back to the CPU
        self.output_queue = Queue.Queue() # Buffer with content from the CPU to display

        input_thread = InputPollThread(self.user_input_queue)
        input_thread.start()

    def read_byte(self, cpu_cycles, op_address, address):
        if address == 0xe001:
            return self.read_acia_data(cpu_cycles, op_address, address)
        else:
            # e.g. read to Display Buffer, serial port e.g.
            pass

    def write_byte(self, cpu_cycles, op_address, address, value):
        if address == 0xe001:
            self.write_acia_data(cpu_cycles, op_address, address, value)
        else:
            # e.g. write to Display Buffer, serial port e.g.
            pass

    def read_acia_data(self, cpu_cycles, op_address, address):
        if self.user_input_queue.empty():
            return 0x0
        char = self.user_input_queue.get()
        value = ord(char)
        print "read_acia_data() return:", repr(value)
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        print "write_acia_data():", chr(value)


#------------------------------------------------------------------------------


class PeripheryManager(BaseManager):
    pass

PeripheryManager.register("Periphery", Periphery)


class Memory(object):
    def __init__(self, cpu, size=0x1fff):
        self.cpu = cpu
        self._mem = [0x00] * size

        periphery_manager = PeripheryManager()
        periphery_manager.start()
        self.periphery = periphery_manager.Periphery()

        self._read_callbacks = {0xe001: self.periphery.read_byte}
        self._write_callbacks = {0xe001: self.periphery.write_byte}

    def read_byte(self, address):
        print "Memory.readbyte from $%04x" % address
        if address in self._read_callbacks:
            return self._read_callbacks[address](
                self.cpu.cycles, self.cpu.op_address, address
            )
        else:
            return self._mem[address]

    def write_byte(self, address, value):
        print "Memory.write_byte $%02x to $%04x" % (value, address)
        if address in self._write_callbacks:
            self._write_callbacks[address](
                self.cpu.cycles, self.cpu.op_address, address, value
            )
        else:
            self._mem[address] = value


class CPU(object):
    def __init__(self):
        print " *** CPU init, pid:", os.getpid()
        self.memory = Memory(self)
        self.op_address = 0
        self.cycles = 0
        self.quit = False

    def run(self):
        print " *** CPU running, pid:", os.getpid()
        while not self.quit:
            time.sleep(1)
            self.op_address += 1
            self.get_and_call_next_op()
        print "Quit CPU"

    def get_and_call_next_op(self):
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



if __name__ == '__main__':
    cpu = CPU()
    cpu.run()

    print " --- END --- "
