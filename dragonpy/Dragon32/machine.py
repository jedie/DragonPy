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

from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonpy.utils.logging_utils import log
from dragonpy.utils.simple_debugger import print_exc_plus


class BaseCommunicator(object):
    MEMORY_DUMP="dump_program"
    MEMORY_LOAD="load"
    MEMORY_WORDS="words"


class CommunicatorRequest(BaseCommunicator):
    def __init__(self):
        self.request_queue = Queue.Queue(maxsize=1)
        self.response_queue = Queue.Queue(maxsize=1)

    def get_queues(self):
        return self.request_queue, self.response_queue
    
    def _request(self, *args):
        log.critical("request: %s",repr(args))
        self.request_queue.put(args)
        log.critical("\twait for response")
        result = self.response_queue.get(block=True, timeout=10)
        log.critical("\tget response, result: %s", repr(result))
        return result
    
    def request_memory_dump(self, start_addr,end_addr):
        log.critical("request memory dump from $%04x-$%04x", start_addr, end_addr)
        return self._request(self.MEMORY_DUMP, start_addr, end_addr)
    
    def request_memory_load(self, address, data):
        log.critical("request memory load %iBytes to $%04s", len(data), address)
        return self._request(self.MEMORY_LOAD, address, data)

    def request_words(self, addresses):
        return self._request(self.MEMORY_WORDS, addresses)
        

class CommunicatorResponse(BaseCommunicator):
    def __init__(self, request_queue, response_queue):
        self.request_queue = request_queue
        self.response_queue = response_queue

        self.cpu = None
        self._response_func_map = {
            self.MEMORY_DUMP:self._response_memory_dump,
            self.MEMORY_LOAD:self._response_memory_load,
            self.MEMORY_WORDS:self._response_words,
        }
    def add_cpu(self, cpu):
        self.cpu = cpu

    def do_response(self):
        try:
            queue_entry = self.request_queue.get(block=False)
        except Queue.Empty:
            return

        func_key = queue_entry[0]
        args = queue_entry[1:]
        func = self._response_func_map[func_key]
        log.critical("Call %s with: %s", func.__name__, repr(args))
        response = func(*args)
        self.response_queue.put(response)
        log.critical("\tput response: %s", repr(response))

    def _response_memory_dump(self, start_addr, end_addr):
        log.critical("Dump memory from $%04x-$%04x", start_addr, end_addr)
        dump = [
            value
            for addr, value in self.cpu.memory.iter_bytes(start_addr, end_addr)
        ]
        return (dump, start_addr, end_addr)

    def _response_memory_load(self, address, data):
        log.critical("Load into memory %iBytes to $%04s", len(data), address)
        self.cpu.memory.load(address, data)
        return "OK"

    def _response_words(self, addresses):
        result = {}
        for address in addresses:
            result[address] = self.cpu.memory.read_word(address)
        return result


class Machine(object):
    """
    Non-Threaded Machine.
    """
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue, response_comm):
        self.cfg = cfg
        self.periphery_class = periphery_class

        # Queue which contains "write into Display RAM" information
        # for render them in DragonTextDisplayCanvas():
        self.display_queue = display_queue

        # Queue to send keyboard inputs to CPU Thread:
        self.key_input_queue = key_input_queue

        # LifoQueue filles in CPU Thread with CPU-Cycles information:
        self.cpu_status_queue = cpu_status_queue

        self.response_comm = response_comm

        self.burst_count=1000

        memory = Memory(self.cfg)
        periphery = self.periphery_class(
            self.cfg, memory, self.display_queue, self.key_input_queue
        )
        self.cfg.periphery = periphery  # Needed?!?

        self.cpu = CPU(memory, self.cfg, self.cpu_status_queue)
        memory.cpu = self.cpu  # FIXME

        self.response_comm.add_cpu(self.cpu)

        self.cpu.reset()
        self.max_ops = self.cfg.cfg_dict["max_ops"]

    def run(self):
        cpu = self.cpu
        op_count=0
        while cpu.running:
            for __ in xrange(self.burst_count):
                cpu.get_and_call_next_op()
            
            self.response_comm.do_response()
                
            if self.max_ops:
                op_count += self.burst_count
                if op_count >= self.max_ops:
                    log.critical("Quit CPU after given 'max_ops' %i ops.", self.max_ops)
                    break
                

                


    def quit(self):
        self.cpu.running = False


class MachineThread(threading.Thread):
    """
    run machine in a seperated thread.
    """
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue, response_comm):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.machine = Machine(
            cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue, response_comm
        )

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
    def __init__(self, cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue, response_comm):
        self.cpu_thread = MachineThread(
            cfg, periphery_class, display_queue, key_input_queue, cpu_status_queue, response_comm
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


def run_machine(ConfigClass, cfg_dict, PeripheryClass, GUI_Class):
    cfg = ConfigClass(cfg_dict)
    log.log(99, "Startup '%s' machine...", cfg.MACHINE_NAME)

    # LifoQueue filles in CPU Thread with CPU-Cycles information:
    # Use a LifoQueue to get the most recently added status first.
    cpu_status_queue = Queue.LifoQueue(maxsize=1)  # CPU cyltes/sec information

    # Queue to send keyboard inputs from GUI to CPU Thread:
    key_input_queue = Queue.Queue(maxsize=1024)

    # Queue which contains "write into Display RAM" information
    # for render them in DragonTextDisplayCanvas():
    display_queue = Queue.Queue(maxsize=64)

    
    # Queue to send from GUI a request to the CPU/Memory
    # and send the response back to the GUI
    req_communicator = CommunicatorRequest()
    request_queue, response_queue = req_communicator.get_queues()
    response_comm = CommunicatorResponse(request_queue, response_queue)

    log.critical("init GUI")
    # e.g. TkInter GUI
    gui = GUI_Class(
        cfg, display_queue, key_input_queue, cpu_status_queue, req_communicator
    )

    log.critical("init machine")
    # start CPU+Memory+Periphery in a separate thread
    machine = ThreadedMachine(
        cfg, PeripheryClass, display_queue, key_input_queue, cpu_status_queue, response_comm
    )

    try:
        gui.mainloop()
    except Exception as err:
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
