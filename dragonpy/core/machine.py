#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import threading

from dragonlib.core.basic import log_program_dump
import logging

log=logging.getLogger(__name__)
from MC6809.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonpy.utils.simple_debugger import print_exc_plus


try:
    # Python 3
    import queue
    import _thread
except ImportError:
    # Python 2
    import Queue as queue
    import thread as _thread




class Machine(object):
    def __init__(self, cfg, periphery_class, display_callback, user_input_queue):
        self.cfg = cfg
        self.machine_api = cfg.machine_api
        self.periphery_class = periphery_class

        # "write into Display RAM" for render them in DragonTextDisplayCanvas():
        self.display_callback = display_callback

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        memory = Memory(self.cfg)
        self.cpu = CPU(memory, self.cfg)
        memory.cpu = self.cpu  # FIXME

        try:
            self.periphery = self.periphery_class(
                self.cfg, self.cpu, memory, self.display_callback, self.user_input_queue
            )
        except TypeError as err:
            raise TypeError("%s - class: %s" % (err, self.periphery_class.__name__))

        self.cpu_init_state = self.cpu.get_state() # Used for hard reset
#        from dragonpy.tests.test_base import print_cpu_state_data
#        print_cpu_state_data(self.cpu_init_state)

        self.cpu.reset()

        self.max_ops = self.cfg.cfg_dict["max_ops"]
        self.op_count = 0

    def get_basic_program(self):
        program_start = self.cpu.memory.read_word(self.machine_api.PROGRAM_START_ADDR)
        variables_start = self.cpu.memory.read_word(self.machine_api.VARIABLES_START_ADDR)
        array_start = self.cpu.memory.read_word(self.machine_api.ARRAY_START_ADDR)
        free_space_start = self.cpu.memory.read_word(self.machine_api.FREE_SPACE_START_ADDR)

        program_end = variables_start - 1
        variables_end = array_start - 1
        array_end = free_space_start - 1

        log.critical("programm code: $%04x-$%04x", program_start, program_end)
        log.critical("variables....: $%04x-$%04x", variables_start, variables_end)
        log.critical("array........: $%04x-$%04x", array_start, array_end)

        dump = [
            value
            for addr, value in self.cpu.memory.iter_bytes(program_start, program_end)
        ]
        log.critical("Dump: %s", repr(dump))
        log_program_dump(dump)

        listing = self.machine_api.program_dump2ascii_lines(dump, program_start)
        log.critical("Listing in ASCII:\n%s", "\n".join(listing))
        return listing

    def inject_basic_program(self, ascii_listing):
        """
        save the given ASCII BASIC program listing into the emulator RAM.
        """
        program_start = self.cpu.memory.read_word(
            self.machine_api.PROGRAM_START_ADDR
        )
        tokens = self.machine_api.ascii_listing2program_dump(ascii_listing)
        self.cpu.memory.load(program_start, tokens)
        log.critical("BASIC program injected into Memory.")

        # Update the BASIC addresses:
        program_end = program_start + len(tokens)
        self.cpu.memory.write_word(self.machine_api.VARIABLES_START_ADDR, program_end)
        self.cpu.memory.write_word(self.machine_api.ARRAY_START_ADDR, program_end)
        self.cpu.memory.write_word(self.machine_api.FREE_SPACE_START_ADDR, program_end)
        log.critical("BASIC addresses updated.")

    def hard_reset(self):
        self.periphery.reset()
#        from dragonpy.tests.test_base import print_cpu_state_data
#        print_cpu_state_data(self.cpu_init_state)
        self.cpu.set_state(self.cpu_init_state)
#        print_cpu_state_data(self.cpu.get_state())
        self.cpu.reset()

    def quit(self):
        self.cpu.running = False


class MachineThread(threading.Thread):
    """
    run machine in a seperated thread.
    """
    def __init__(self, cfg, periphery_class,  user_input_queue):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.machine = Machine(
            cfg, periphery_class,  user_input_queue
        )

    def run(self):
        log.critical(" *** MachineThread.run() start *** ")
        try:
            self.machine.run()
        except Exception as err:
            log.critical("MachineThread exception: %s", err)
            print_exc_plus()
            _thread.interrupt_main()
            raise
        log.critical(" *** MachineThread.run() stopped. *** ")

    def quit(self):
        self.machine.quit()


class ThreadedMachine(object):
    def __init__(self, cfg, periphery_class,  user_input_queue):
        self.cpu_thread = MachineThread(
            cfg, periphery_class,  user_input_queue
        )
        self.cpu_thread.deamon = True
        self.cpu_thread.start()
#         log.critical("Wait for CPU thread stop.")
#         try:
#             cpu_thread.join()
#         except KeyboardInterrupt:
#             log.critical("CPU thread stops by keyboard interrupt.")
#             thread.interrupt_main()
#         else:
#             log.critical("CPU thread stopped.")
#         cpu.running = False

    def quit(self):
        self.cpu_thread.quit()


class MachineGUI(object):
    def __init__(self, cfg):
        self.cfg = cfg

        # Queue to send keyboard inputs from GUI to CPU Thread:
        self.user_input_queue = queue.Queue()


    def run(self, PeripheryClass, GUI_Class):
        log.log(99, "Startup '%s' machine...", self.cfg.MACHINE_NAME)

        log.critical("init GUI")
        # e.g. TkInter GUI
        gui = GUI_Class(
            self.cfg,
            self.user_input_queue
        )

        log.critical("init machine")
        # start CPU+Memory+Periphery in a separate thread
        machine = Machine(
            self.cfg,
            PeripheryClass,
            gui.display_callback,
            self.user_input_queue
        )

        try:
            gui.mainloop(machine)
        except Exception as err:
            log.critical("GUI exception: %s", err)
            print_exc_plus()
        machine.quit()

        log.log(99, " --- END ---")


#------------------------------------------------------------------------------


