#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import queue
import _thread
import threading

from dragonlib.core.basic import log_program_dump
from dragonlib.utils.logging_utils import log
from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonpy.utils.simple_debugger import print_exc_plus


class BaseCommunicator(object):
    MEMORY_DUMP = "dump_program"
    MEMORY_LOAD = "load"
    MEMORY_WORD = "word"
    MEMORY_WORDS = "words"
    MEMORY_WRITE_WORDS = "write_words"


class CommunicatorRequest(BaseCommunicator):
    """
    Useable only with ThreadedMachine, because every request block until
    the response was created.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.machine_api = self.cfg.machine_api
        self.request_queue = queue.Queue(maxsize=1)
        self.response_queue = queue.Queue(maxsize=1)

    def get_queues(self):
        return self.request_queue, self.response_queue

    def _request(self, *args):
        log.critical("request: %s", repr(args))
        self.request_queue.put(args)
        log.critical("\twait for response")
        result = self.response_queue.get(block=True, timeout=10)
        log.critical("\tget response, result: %s", repr(result))
        return result

    def request_memory_dump(self, start_addr, end_addr):
        log.critical("request memory dump from $%04x-$%04x", start_addr, end_addr)
        return self._request(self.MEMORY_DUMP, start_addr, end_addr)

    def request_memory_load(self, address, data):
        log.critical("request memory load %iBytes to $%04s", len(data), address)
        return self._request(self.MEMORY_LOAD, address, data)

    def request_word(self, address):
        """ returns one word from the given address """
        return self._request(self.MEMORY_WORD, address)

    def request_words(self, addresses):
        """ returns a dict of words from all given addresses """
        return self._request(self.MEMORY_WORDS, addresses)

    def request_write_words(self, words_dict):
        """ writes words into memory """
        return self._request(self.MEMORY_WRITE_WORDS, words_dict)

    def get_basic_program(self):
        addresses = (
            self.machine_api.PROGRAM_START_ADDR,
            self.machine_api.VARIABLES_START_ADDR,
            self.machine_api.ARRAY_START_ADDR,
            self.machine_api.FREE_SPACE_START_ADDR,
        )
        result = self.request_words(addresses)
        log.critical(repr(result))
        program_start = result[self.machine_api.PROGRAM_START_ADDR]
        variables_start = result[self.machine_api.VARIABLES_START_ADDR]
        array_start = result[self.machine_api.ARRAY_START_ADDR]
        free_space_start = result[self.machine_api.FREE_SPACE_START_ADDR]
        program_end = variables_start - 1
        variables_end = array_start - 1
        array_end = free_space_start - 1

        log.critical("programm code: $%04x-$%04x", program_start, program_end)
        log.critical("variables....: $%04x-$%04x", variables_start, variables_end)
        log.critical("array........: $%04x-$%04x", array_start, array_end)

        dump, start_addr, end_addr = self.request_memory_dump(
            program_start, program_end
        )
        log_program_dump(dump)

        listing = self.machine_api.program_dump2ascii_lines(dump, program_start)
        log.critical("Listing in ASCII:\n%s", "\n".join(listing))
        return listing

    def inject_basic_program(self, ascii_listing):
        """
        save the given ASCII BASIC program listing into the emulator RAM.
        """
        program_start = self.request_word(
            self.machine_api.PROGRAM_START_ADDR
        )
        tokens = self.machine_api.ascii_listing2program_dump(ascii_listing)
        status = self.request_memory_load(program_start, tokens)
        log.critical("inject BASIC program: %s", status)

        # Update the BASIC addresses:
        program_end = program_start + len(tokens)
        status = self.request_write_words({
            self.machine_api.VARIABLES_START_ADDR:program_end,
            self.machine_api.ARRAY_START_ADDR:program_end,
            self.machine_api.FREE_SPACE_START_ADDR:program_end,
        })
        log.critical("Update BASIC addresses: %s", status)
        return "OK"


class CommunicatorResponse(BaseCommunicator):
    def __init__(self, request_queue, response_queue):
        self.request_queue = request_queue
        self.response_queue = response_queue

        self.cpu = None
        self._response_func_map = {
            self.MEMORY_DUMP:self._response_memory_dump,
            self.MEMORY_LOAD:self._response_memory_load,
            self.MEMORY_WORD:self._response_word,
            self.MEMORY_WORDS:self._response_words,
            self.MEMORY_WRITE_WORDS:self._response_write_words,
        }
    def add_cpu(self, cpu):
        self.cpu = cpu

    def do_response(self):
        try:
            queue_entry = self.request_queue.get(block=False)
        except queue.Empty:
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

    def _response_word(self, address):
        return self.cpu.memory.read_word(address)

    def _response_words(self, addresses):
        result = {}
        for address in addresses:
            result[address] = self.cpu.memory.read_word(address)
        return result

    def _response_write_words(self, words_dict):
        for address, word in sorted(words_dict.items()):
            log.critical("Write $%04x to $%04x", address, word)
            self.cpu.memory.write_word(address, word)
        return "OK"


class Machine(object):
    """
    Non-Threaded Machine.
    """
    def __init__(self, cfg, periphery_class, display_queue, user_input_queue, cpu_status_queue, response_comm):
        self.cfg = cfg
        self.periphery_class = periphery_class

        # Queue which contains "write into Display RAM" information
        # for render them in DragonTextDisplayCanvas():
        self.display_queue = display_queue

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        # LifoQueue filles in CPU Thread with CPU-Cycles information:
        self.cpu_status_queue = cpu_status_queue

        self.response_comm = response_comm

        self.burst_count = 1000

        memory = Memory(self.cfg)
        self.periphery = self.periphery_class(
            self.cfg, memory, self.display_queue, self.user_input_queue
        )

        self.cpu = CPU(memory, self.cfg, self.cpu_status_queue)
        memory.cpu = self.cpu  # FIXME

        self.response_comm.add_cpu(self.cpu)

        self.cpu.reset()
        self.max_ops = self.cfg.cfg_dict["max_ops"]

    def run(self):
        cpu = self.cpu
        op_count = 0
        while cpu.running:
            for __ in range(self.burst_count):
                cpu.get_and_call_next_op()

            self.response_comm.do_response()

            if self.max_ops:
                op_count += self.burst_count
                if op_count >= self.max_ops:
                    log.critical("Quit CPU after given 'max_ops' %i ops.", self.max_ops)
                    self.quit()
                    break

    def quit(self):
        self.cpu.running = False


class MachineThread(threading.Thread):
    """
    run machine in a seperated thread.
    """
    def __init__(self, cfg, periphery_class, display_queue, user_input_queue, cpu_status_queue, response_comm):
        super(MachineThread, self).__init__(name="CPU-Thread")
        log.critical(" *** MachineThread init *** ")
        self.machine = Machine(
            cfg, periphery_class, display_queue, user_input_queue, cpu_status_queue, response_comm
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
    def __init__(self, cfg, periphery_class, display_queue, user_input_queue, cpu_status_queue, response_comm):
        self.cpu_thread = MachineThread(
            cfg, periphery_class, display_queue, user_input_queue, cpu_status_queue, response_comm
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


class ThreadedMachineGUI(object):
    def __init__(self, cfg):
        self.cfg = cfg

        # LifoQueue filles in CPU Thread with CPU-Cycles information:
        # Use a LifoQueue to get the most recently added status first.
        self.cpu_status_queue = queue.LifoQueue(maxsize=1)  # CPU cyltes/sec information

        # Queue to send keyboard inputs from GUI to CPU Thread:
        self.user_input_queue = queue.Queue(maxsize=1024)

        # Queue which contains "write into Display RAM" information
        # for render them in DragonTextDisplayCanvas():
        self.display_queue = queue.Queue(maxsize=64)

        # Queue to send from GUI a request to the CPU/Memory
        # and send the response back to the GUI
        self.request_comm = CommunicatorRequest(cfg)
        request_queue, response_queue = self.request_comm.get_queues()
        self.response_comm = CommunicatorResponse(request_queue, response_queue)

    def run(self, PeripheryClass, GUI_Class):
        log.log(99, "Startup '%s' machine...", self.cfg.MACHINE_NAME)

        log.critical("init GUI")
        # e.g. TkInter GUI
        gui = GUI_Class(
            self.cfg,
            self.display_queue, self.user_input_queue, self.cpu_status_queue,
            self.request_comm
        )

        log.critical("init machine")
        # start CPU+Memory+Periphery in a separate thread
        machine = ThreadedMachine(
            self.cfg,
            PeripheryClass,
            self.display_queue, self.user_input_queue, self.cpu_status_queue,
            self.response_comm
        )

        try:
            gui.mainloop()
        except Exception as err:
            log.critical("GUI exception: %s", err)
            print_exc_plus()
        machine.quit()

        log.log(99, " --- END ---")


#------------------------------------------------------------------------------


def test_run():
    import sys
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#        "--verbosity", "5",
        "--machine", "Dragon32", "run",
#        "--machine", "Vectrex", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
