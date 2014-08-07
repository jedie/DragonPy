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
from dragonpy.utils.simple_debugger import print_exc_plus


class Machine(object):
    """
    Non-Threaded Machine.
    """
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue):
        self.cfg = cfg
        self.periphery_class = periphery_class
        self.display_queue = display_queue
        self.key_input_queue = key_input_queue
        self.cpu_status_queue = cpu_status_queue

    def run(self):
        memory = Memory(self.cfg)

        periphery = self.periphery_class(
            self.cfg, memory, self.display_queue, self.key_input_queue
        )
        self.cfg.periphery = periphery  # Needed?!?

        self.cpu = CPU(memory, self.cfg, self.cpu_status_queue)
        cpu = self.cpu
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
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.machine = Machine(cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue)

    def run(self):
        log.critical(" *** MachineThread.run() start *** ")
        try:
            self.machine.run()
        except:
            thread.interrupt_main()
            raise
        log.critical(" *** MachineThread.run() stopped. *** ")

    def quit(self):
        self.machine.quit()


class ThreadedMachine(object):
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue):
        self.cpu_thread = MachineThread(
            cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue)
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

    # Use a LifoQueue to get the most recently added status first.
    cpu_status_queue = Queue.LifoQueue(maxsize=1)  # CPU cyltes/sec information

    key_input_queue = Queue.Queue(maxsize=1024)  # User keyboard input
    display_queue = Queue.Queue(maxsize=64)  # Display RAM write outputs

    log.critical("init GUI")
    # e.g. TkInter GUI
    gui = GUI_Class(
        cfg, display_queue, key_input_queue, cpu_status_queue,
    )

    log.critical("init machine")
    # start CPU+Memory+Periphery in a separate thread
    machine = ThreadedMachine(
        cfg, PeripheryClass, display_queue, key_input_queue, cpu_status_queue
    )

    try:
        gui.mainloop()
    except Exception, err:
        log.critical("GUI exception: %s", err)
        print_exc_plus()
    machine.quit()

    log.log(99, " --- END ---")


def test_run_direct():
    import subprocess
    import sys
    import os
    cmd_args = [
        sys.executable,
        #         "/usr/bin/pypy",
        os.path.join("..",
            "Dragon32_test.py"
#             "Dragon64_test.py"
        ),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    #     test_run_cli()
    test_run_direct()
