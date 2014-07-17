#!/usr/bin/env python

"""
    DragonPy
    ========

    Just a multiprocessing concept 2

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import multiprocessing
import os
import threading
import time

from dragonpy.utils import pager


def info(title):
    print "%s (module: '%s', pid:'%s'" % (title, __name__, os.getpid())


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
        info("Memory.readbyte from $%04x" % address)
        if address in self._read_callbacks:
            return self._read_callbacks[address](address)
        else:
            return self._mem[address]

    def write_byte(self, address, value):
        info("Memory.write_byte $%02x to $%04x" % (value, address))
        if address in self._write_callbacks:
            self._write_callbacks[address](address, value)
        else:
            self._mem[address] = value


class CPU(object):
    def __init__(self):
        info(" *** CPU init *** ")
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
        info(" *** CPUThread init *** ")
        self.cpu = cpu

    def run(self):
        info(" *** CPUThread.run() *** ")
        cpu = self.cpu
        while not cpu.quit:
            cpu.get_and_call_next_op()
        print "Quit CPU"


def start_cpu(read_bus_request_queue, read_bus_response_queue, write_bus_queue):
    info(" +++ start_cpu() +++ ")
    cpu = CPU()
    cpu.memory = Memory(cpu, read_bus_request_queue, read_bus_response_queue, write_bus_queue)

    cpu_thread = CPUThread(cpu)
    cpu_thread.start()
    cpu_thread.join()

    info(" +++ start_cpu(): CPU has quit +++ ")


#------------------------------------------------------------------------------


class InputPoll(threading.Thread):
    """
    Seperate thread for user input from console.
    """
    def __init__ (self, in_queue):
        super(InputPoll, self).__init__()
        info(" *** InputPoll init *** ")
        self.input_queue = in_queue
        self.quit = False

    def run(self):
        info(" *** InputPoll running *** ")
        while not self.quit:
            char = pager.getch() # XXX: Blocks, becuase it waits for one input char
            print "Char from InputPoll:", repr(char)
            self.input_queue.put(char)


class Periphery(object):
    def __init__(self):
        info(" *** Periphery init *** ")

        self.user_input_queue = Queue.Queue() # Buffer for input to send back to the CPU
        self.output_queue = Queue.Queue() # Buffer with content from the CPU to display

        self.input_thread = InputPoll(self.user_input_queue)
        self.input_thread.start()

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
        char = self.user_input_queue.get(timeout=0.5)
        value = ord(char)
        print "read_acia_data() return:", repr(value)
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        info("write_acia_data(): %r" % chr(value))



class BusReadThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, periphery, read_bus_request_queue, read_bus_response_queue):
        super(BusReadThread, self).__init__()
        info(" *** BusReadThread init *** ")
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.quit = False

    def run(self):
        info(" *** BusReadThread.run() *** ")
        while not self.quit:
            try:
                cycles, op_address, address = self.read_bus_request_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
            value = self.periphery.read_byte(cycles, op_address, address)
            self.read_bus_response_queue.put(value)


class BusWriteThread(threading.Thread):
    """
    Wait for CPU/Memory bus write: Redirect write to periphery
    """
    def __init__ (self, periphery, write_bus_queue):
        super(BusWriteThread, self).__init__()
        info(" *** BusWriteThread init *** ")
        self.periphery = periphery
        self.write_bus_queue = write_bus_queue
        self.quit = False

    def run(self):
        info(" *** BusWriteThread.run() *** ")
        while not self.quit:
            try:
                cycles, op_address, address, value = self.write_bus_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
            self.periphery.write_byte(cycles, op_address, address, value)



def startup():
    periphery = Periphery()

    # communication channel between processes:
    read_bus_request_queue = multiprocessing.Queue(maxsize=1)
    read_bus_response_queue = multiprocessing.Queue(maxsize=1)
    write_bus_queue = multiprocessing.Queue(maxsize=1)

    # API between processes and local periphery
    bus_read_thread = BusReadThread(periphery, read_bus_request_queue, read_bus_response_queue)
    bus_read_thread.start()
    bus_write_thread = BusWriteThread(periphery, write_bus_queue)
    bus_write_thread.start()

    # Start CPU/Memory as seperated process:
    p = multiprocessing.Process(target=start_cpu,
        args=(read_bus_request_queue, read_bus_response_queue, write_bus_queue)
    )
    p.start()
    p.join() # Wait if CPU quits

    # Quit all threads:
    bus_read_thread.quit = True
    bus_write_thread.quit = True
    periphery.input_thread.quit = True

    # Wait for quit:
    bus_read_thread.join()
    bus_write_thread.join()

    info(" *** FIXME: Input one char to real END :(")
    periphery.input_thread.join() # Will only end after one input char :(


if __name__ == '__main__':
    startup()
    print " --- END --- "
