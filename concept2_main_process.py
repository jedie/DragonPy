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
from dragonpy.utils.thread_utils import info
from concept2_sub_process import start_cpu
from dragonpy.utils import pager
import sys


from dragonpy.utils.logging_utils import log

#------------------------------------------------------------------------------


class InputPollThread(threading.Thread):
    """
    Seperate thread for user input from console.
    """
    def __init__ (self, in_queue):
        super(InputPollThread, self).__init__()
        log.info(" *** InputPollThread init *** ")
        self.user_input_queue = in_queue
        self.quit = False

    def run(self):
        log.info(" *** InputPollThread running *** ")
        while not self.quit:
            char = pager.getch() # XXX: Blocks, becuase it waits for one input char
            print "Char from InputPollThread: %s" % repr(char)
            if char == '\x04':
                sys.exit()
            self.user_input_queue.put(char)


class Periphery(object):
    def __init__(self):
        log.info(" *** Periphery init *** ")

        self.user_input_queue = Queue.Queue() # Buffer for input to send back to the CPU
        self.output_queue = Queue.Queue() # Buffer with content from the CPU to display

        self.input_thread = InputPollThread(self.user_input_queue)
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
        log.info("write_acia_data(): %r" % chr(value))



class BusReadThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, periphery, read_bus_request_queue, read_bus_response_queue):
        super(BusReadThread, self).__init__()
        log.info(" *** BusReadThread init *** ")
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.quit = False

    def run(self):
        log.info(" *** BusReadThread.run() *** ")
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
        log.info(" *** BusWriteThread init *** ")
        self.periphery = periphery
        self.write_bus_queue = write_bus_queue
        self.quit = False

    def run(self):
        log.info(" *** BusWriteThread.run() *** ")
        while not self.quit:
            try:
                cycles, op_address, address, value = self.write_bus_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                continue
            self.periphery.write_byte(cycles, op_address, address, value)

cfg_dict = {
    "log_level": multiprocessing.SUBDEBUG
}

def startup():
    periphery = Periphery()

    # communication channel between processes:
    read_bus_request_queue = multiprocessing.Queue(maxsize=1)
    read_bus_response_queue = multiprocessing.Queue(maxsize=1)
    write_bus_queue = multiprocessing.Queue(maxsize=1)

    # API between processes and local periphery
    log.info("start BusReadThread()")
    bus_read_thread = BusReadThread(periphery, read_bus_request_queue, read_bus_response_queue)
    bus_read_thread.start()
    log.info("start BusWriteThread()")
    bus_write_thread = BusWriteThread(periphery, write_bus_queue)
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
    p.join() # Wait if CPU quits
    log.info(" *** CPU has quit ***")

    # Quit all threads:
    bus_read_thread.quit = True
    bus_write_thread.quit = True
    periphery.input_thread.quit = True

    log.info("Wait for quit bus threads")
    bus_read_thread.join()
    bus_write_thread.join()

    log.info(" *** FIXME: Input one char to real END :(")
    periphery.input_thread.join() # Will only end after one input char :(


if __name__ == '__main__':
    log.setLevel(multiprocessing.SUBDEBUG)
    startup()
    print " --- END --- "
