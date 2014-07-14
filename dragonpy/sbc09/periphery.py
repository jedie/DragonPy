#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import threading
import logging
import sys
import os

try:
    import Tkinter
except Exception, err:
    print "Error importing Tkinter: %s" % err
    Tkinter = None

from dragonpy.components.periphery import PeripheryBase, TkPeripheryBase

log = logging.getLogger("DragonPy.sbc09Periphery")





class SBC09PeripheryBase(PeripheryBase):
    TITLE = "DragonPy - Buggy machine language monitor and rudimentary O.S. version 1.0"
    INITAL_INPUT = (
        # Dump registers
        'r\r\n'

        # SSaddr,len - Dump memory region as Motorola S records.
        'ss\r\n'

        # Daddr,len - Dump memory region
        'DE5E2\r\n'

        # Iaddr - Display the contents of the given address.
        'IE001\r\n' # e.g.: Show the ACIA status

        # Uaddr,len - Diassemble memory region
        'UE400\r\n'

        # Calculate simple expression in hex with + and -
        'H4444+A5\r\n'

        #
#         "UE400,20\r\n"
#         "ubasic\r\n"
    )

    def __init__(self, cfg):
        super(SBC09PeripheryBase, self).__init__(cfg)
        self.read_address2func_map = {
            0xe000: self.read_acia_status, # Control/status port of ACIA
            0xe001: self.read_acia_data, # Data port of ACIA
            0xfffe: self.reset_vector,
        }
        self.write_address2func_map = {
            0xe000: self.write_acia_status, # Control/status port of ACIA
            0xe001: self.write_acia_data, # Data port of ACIA
        }

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        return 0xff
    def read_acia_status(self, cpu_cycles, op_address, address):
        return 0x03

    def read_acia_data(self, cpu_cycles, op_address, address):
        if self.user_input_queue.empty():
            return 0x0

        char = self.user_input_queue.get()
        value = ord(char)
        log.error("%04x| (%i) read from ACIA-data, send back %r $%x",
            op_address, cpu_cycles, char, value
        )
        return value

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        char = chr(value)
#        log.error("*"*79)
#        log.error("Write to screen: %s ($%x)" , repr(char), value)
#        log.error("*"*79)

        if value >= 0x90: # FIXME: Why?
            value -= 0x60
            char = chr(value)
#            log.error("convert value -= 0x30 to %s ($%x)" , repr(char), value)

        if value <= 9: # FIXME: Why?
            value += 0x41
            char = chr(value)
#            log.error("convert value += 0x41 to %s ($%x)" , repr(char), value)

        self.output_queue.put(char)


class SBC09PeripheryTk(SBC09PeripheryBase, TkPeripheryBase):
    GEOMETRY = "+500+300"


class DummyStdout(object):
    def dummy_func(self, *args):
        pass
    write = dummy_func
    flush = dummy_func


class SBC09PeripheryConsole(SBC09PeripheryBase):
    """
    A simple console to interact with the 6809 simulation.
    """
    def __init__(self, cfg):
        super(SBC09PeripheryConsole, self).__init__(cfg)

        input_thread = threading.Thread(target=self.input_thread, args=(self.user_input_queue,))
        input_thread.daemon = True
        input_thread.start()

        # "redirect" use input into nirvana, because the ROM code will echo
        # the user input back.
        self.origin_stdout = sys.stdout
        sys.stdout = DummyStdout()

    def input_thread(self, input_queue):
        while True:
            input_queue.put(sys.stdin.read(1))

    def update(self, cpu_cycles):
        super(SBC09PeripheryConsole, self).update(cpu_cycles)
        if not self.output_queue.empty():
            text_buffer = []
            while not self.output_queue.empty():
                text_buffer.append(self.output_queue.get())

            text = "".join(text_buffer)
            self.origin_stdout.write(text)
            self.origin_stdout.flush()


# SBC09Periphery = SBC09PeripherySerial
# SBC09Periphery = SBC09PeripheryTk
SBC09Periphery = SBC09PeripheryConsole


def test_run():
    import subprocess
    cmd_args = [
        sys.executable,
#        "/usr/bin/pypy",
        os.path.join("..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL

        "--cfg=sbc09",
#         "--max=500000",
#         "--max=30000",
#         "--max=20000",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
