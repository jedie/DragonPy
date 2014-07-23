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
import thread
import threading

from dragonpy.utils import pager
from dragonpy.utils.logging_utils import log

from concept2_sub_process import start_cpu

#------------------------------------------------------------------------------

def info(title):
    print title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

#------------------------------------------------------------------------------


class InputPollThread(threading.Thread):
    def __init__ (self, cpu_process, user_input_queue):
        self.cpu_process = cpu_process
        self.user_input_queue = user_input_queue
        self.check_cpu_interval(cpu_process)
        super(InputPollThread, self).__init__()

    def check_cpu_interval(self, cpu_process):
        """
        work-a-round for blocking input
        """
        try:
            log.critical("check_cpu_interval()")
            if not cpu_process.is_alive():
                log.critical("raise SystemExit, because CPU is not alive.")
                thread.interrupt_main()
                raise SystemExit("Kill pager.getch()")
        except KeyboardInterrupt:
            thread.interrupt_main()
        else:
            t = threading.Timer(1.0, self.check_cpu_interval, args=[cpu_process])
            t.start()

    def loop(self):
        while self.cpu_process.is_alive():
            char = pager.getch() # Important: It blocks while waiting for a input
            if char == "\n":
                self.user_input_queue.put("\r")

            char = char.upper()
            self.user_input_queue.put(char)

    def run(self):
        log.critical("InputPollThread.run() start")
        try:
            self.loop()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical("InputPollThread.run() ends, because CPU not alive anymore.")


class Periphery(object):
    def __init__(self):
        log.info(" *** Periphery init *** ")

        self.user_input_queue = Queue.Queue() # Buffer for input to send back to the CPU
        self.output_queue = Queue.Queue() # Buffer with content from the CPU to display

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

    def exit(self, msg):
        log.info("Periphery.exit(): %s" % msg)

    def mainloop(self, cpu_process):
        self.input_thread = InputPollThread(cpu_process, self.user_input_queue)
        self.input_thread.start()
        self.input_thread.join()


class BusCommunicationThread(threading.Thread):
    """
    Wait for CPU/Memory bus read: Read from periphery and send result back.
    """
    def __init__ (self, periphery, read_bus_request_queue, read_bus_response_queue, write_bus_queue):
        super(BusCommunicationThread, self).__init__()
        log.info(" *** BusCommunicationThread init *** ")
        self.periphery = periphery
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue
        self.running = False

    def run(self):
        log.info(" *** BusCommunicationThread.run() *** ")
        while not self.running:
            try:
                cycles, op_address, address = self.read_bus_request_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                pass
            else:
                value = self.periphery.read_byte(cycles, op_address, address)
                self.read_bus_response_queue.put(value)

            try:
                cycles, op_address, address, value = self.write_bus_queue.get(timeout=0.5)
            except multiprocessing.queues.Empty:
                pass
            else:
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
    log.info("start BusCommunicationThread()")
    bus_thread = BusCommunicationThread(periphery,
        read_bus_request_queue, read_bus_response_queue,
        write_bus_queue
    )
    bus_thread.deamon = True
    bus_thread.start()

    log.info("Start CPU/Memory as separated process")
    cpu_process = multiprocessing.Process(target=start_cpu,
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

    cpu_process.join() # Wait if CPU quits
    log.info(" *** CPU has running ***")

    # Quit all threads:
    bus_thread.running = True
    periphery.input_thread.running = True

    log.info("Wait for running bus threads")
    bus_thread.join()

    log.info(" *** FIXME: Input one char to real END :(")
    periphery.input_thread.join() # Will only end after one input char :(


if __name__ == '__main__':
    log.setLevel(multiprocessing.SUBDEBUG)
    startup()
    print " --- END --- "
