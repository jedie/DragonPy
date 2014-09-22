#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import sys

import logging

log=logging.getLogger(__name__)
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.components.periphery import PeripheryBase


class Dragon32PeripheryBase(object):
    """
    GUI independent stuff
    """
    def __init__(self, cfg, cpu, memory, display_queue, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory
        self.display_queue = display_queue # Buffer for output from CPU
        self.user_input_queue = user_input_queue

        self.kbd = 0xBF
        self.display = None
        self.speaker = None  # Speaker()
        self.cassette = None  # Cassette()

        self.sam = SAM(cfg, cpu, memory)
        self.pia = PIA(cfg, cpu, memory, self.user_input_queue)

        self.memory.add_read_byte_callback(self.no_dos_rom, 0xC000)
        self.memory.add_read_word_callback(self.no_dos_rom, 0xC000)

        self.running = True

    def reset(self):
        self.sam.reset()
        self.pia.reset()
        self.pia.internal_reset()

    def no_dos_rom(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: DOS ROM requested. Send 0x00 back", op_address)
        return 0x00

#     def update(self, cpu_cycles):
#         #        log.critical("update pygame")
#         if not self.running:
#             return
#         if self.speaker:
#             self.speaker.update(cpu_cycles)


class Dragon32Periphery(Dragon32PeripheryBase):
    def __init__(self, cfg, cpu, memory, display_queue, user_input_queue):
        super(Dragon32Periphery, self).__init__(cfg, cpu, memory, display_queue, user_input_queue)

        # redirect writes to display RAM area 0x0400-0x0600 into display_queue:
        DragonDisplayOutputHandler(display_queue, memory)


class DragonDisplayOutputHandler(object):
    """
    redirect writes to display RAM area 0x0400-0x0600 into display_queue.
    """
    def __init__(self, display_queue, memory):
        self.display_queue = display_queue
        self.memory = memory

        # Add a hook in the display RAM:
        self.memory.add_write_byte_middleware(
            self.to_display_queue, 0x0400, 0x0600
        )

    def to_display_queue(self, cpu_cycles, op_address, address, value):
        """
        Send a "write to Display RAM" information to GUI main thread.
        So the GUI can display it.

        Block until a free slot is available in display_queue buffer.
        """
        self.display_queue.put(
            (cpu_cycles, op_address, address, value),
            block=True, timeout=3
        )
        return value


#------------------------------------------------------------------------------

class Dragon32PeripheryUnittest(Dragon32PeripheryBase):
    def __init__(self, cfg, cpu, memory, display_queue, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.display_queue = display_queue
        self.user_input_queue = user_input_queue
        super(Dragon32PeripheryUnittest, self).__init__(cfg, cpu, memory, self.display_queue, self.user_input_queue)

        self.rows = 32
        self.columns = 16
        # Contains the map from Display RAM value to char/color:
        self.charmap = get_charmap_dict()

        # redirect writes to display RAM area 0x0400-0x0600 into display_queue:
        self.memory.add_write_byte_middleware(
            self.to_line_buffer, 0x0400, 0x0600
        )

    def setUp(self):
        self.pia.internal_reset()
        self.user_input_queue.queue.clear()
        self.display_queue.queue.clear()
        self.old_columns = None
        self.output_lines = [""] # for unittest run_until_OK()
        self.display_buffer = {} # for striped_output()

    def add_to_input_queue(self, txt):
        log.debug("Add %s to input queue.", repr(txt))
        for char in txt:
            self.user_input_queue.put(char)

    def to_line_buffer(self, cpu_cycles, op_address, address, value):
        char, color = self.charmap[value]
#        log.critical(
#            "%04x| *** Display write $%02x ***%s*** %s at $%04x",
#            op_address, value, repr(char), color, address
#        )
        position = address - 0x400
        column, row = divmod(position, self.rows)

        if column != self.old_columns:
            if self.old_columns is not None:
                self.output_lines.append("")
            self.old_columns = column

        self.output_lines[-1] += char
        self.display_buffer[address] = char

        return value

    def striped_output(self):
        """
        It's a little bit tricky to get the "written output"...
        Because user input would be first cleared and then
        the new char would be written.

        "FOO" output looks like this:

        bcd9| *** Display write $62 ***u'"'*** NORMAL at $04a2
        b544| *** Display write $60 ***u' '*** NORMAL at $04a3
        bcd9| *** Display write $46 ***u'F'*** NORMAL at $04a3
        b544| *** Display write $60 ***u' '*** NORMAL at $04a4
        bcd9| *** Display write $4f ***u'O'*** NORMAL at $04a4
        b544| *** Display write $60 ***u' '*** NORMAL at $04a5
        bcd9| *** Display write $4f ***u'O'*** NORMAL at $04a5
        b544| *** Display write $60 ***u' '*** NORMAL at $04a6
        bcd9| *** Display write $62 ***u'"'*** NORMAL at $04a6
        """
        output_lines = [""]
        old_columns = None
        for address, char in sorted(self.display_buffer.items()):
            position = address - 0x400
            column, row = divmod(position, self.rows)
            if column != old_columns:
                if old_columns is not None:
                    output_lines.append("")
                old_columns = column

            output_lines[-1] += char

        return [
            line.strip()
            for line in output_lines
        ]



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
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
