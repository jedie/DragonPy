#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import thread
import threading

from dragonpy.Dragon32.periphery_dragon import DragonDisplayOutputHandler
from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonpy.utils.logging_utils import log


class Machine(object):
    """
    Non-Threaded Machine.
    """
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue):
        self.cfg = cfg
        self.periphery_class = periphery_class
        self.display_queue = display_queue
        self.key_input_queue = key_input_queue

    def run(self):
        memory = Memory(self.cfg)

        # redirect writes to display RAM area 0x0400-0x0600 into display_queue:
        DragonDisplayOutputHandler(self.display_queue, memory)

        periphery = self.periphery_class(
            self.cfg, memory, self.key_input_queue)
        self.cfg.periphery = periphery  # Needed?!?

        self.cpu = CPU(memory, self.cfg)
        cpu = self.cpu
        cpu.log_cpu_cycle_interval()  # turn on manually
        memory.cpu = cpu  # FIXME

        cpu.reset()
        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            log.critical("Running only %i ops!", max_ops)
            for __ in xrange(max_ops):
                cpu.get_and_call_next_op()
                if not cpu.running:
                    break
            log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
            return
        else:
            while cpu.running:
                cpu.get_and_call_next_op()

    def quit(self):
        self.cpu.running = False


class MachineThread(threading.Thread):
    """
    run machine in a seperated thread.
    """
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.machine = Machine(cfg, periphery_class, display_queue, key_input_queue)

    def run(self):
        log.critical(" *** MachineThread.run() start *** ")
        try:
            self.machine.run()
        except KeyboardInterrupt:
            thread.interrupt_main()
        log.critical(" *** MachineThread.run() stopped. *** ")

    def quit(self):
        self.machine.quit()


class ThreadedMachine(object):
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue):
        self.cpu_thread = MachineThread(
            cfg, periphery_class, display_queue, key_input_queue)
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


def run_machine(ConfigClass, cfg_dict, PeripheryClass, GUI_Class):
    cfg = ConfigClass(cfg_dict)
    log.log(99, "Startup '%s' machine...", cfg.MACHINE_NAME)

    key_input_queue = Queue.Queue()
    display_queue = Queue.Queue()

    # start CPU+Memory+Periphery in a seperate thread
    machine = ThreadedMachine(
        cfg, PeripheryClass, display_queue, key_input_queue
    )

    # e.g. TkInter GUI
    gui = GUI_Class(
        cfg, machine, display_queue, key_input_queue
    )
    gui.mainloop()
    machine.quit()

    log.log(99, " --- END ---")