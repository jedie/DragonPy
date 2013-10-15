#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys

log = logging.getLogger("DragonPy.Periphery")

class Simple6809Periphery(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.address2func_map = {
            0xbffe: self.reset_vector,
        }

    def read_byte(self, cpu_cycles, op_address, address):
        log.debug(
            "%04x| Periphery.read_byte from $%x (cpu_cycles: %i)" % (
            op_address, address, cpu_cycles
        ))
        if 0xa000 <= address <= 0xbfef:
            return self.read_rs232_interface(cpu_cycles, op_address, address)

        try:
            func = self.address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
            return func(address)

        raise NotImplementedError

    read_word = read_byte

    def write_byte(self, cpu_cycles, op_address, address, value):
        if 0xa000 <= address <= 0xbfef:
            return self.write_rs232_interface(cpu_cycles, op_address, address, value)

        msg = "%04x| TODO: write byte $%x to $%x" % (op_address, value, address)
        log.error(msg)
        raise NotImplementedError(msg)
    write_word = write_byte

    def cycle(self, cpu_cycles, op_address):
        log.debug("TODO: Simple6809Periphery.cycle")


    def read_rs232_interface(self, cpu_cycles, op_address, address):
        """
        $00   0  NUL (Null Prompt)
        $01   1  SOH (Start of heading)
        $02   2  STX (Start of Text)
        $03   3  ETX (End of Text)
        $04   4  EOT (End of transmission)
        $05   5  ENQ (Enqiry)
        $06   6  ACK (Acknowledge)
        $07   7  BEL (Bell)
        $08   8  BS  (Backspace)
        $09   9  HT  (Horizontal Tab)
        $0a  10  LF  (LineFeed)
        $0b  11  VT  (Vertical Tab)
        $0c  12  FF  (Form Feed)
        $0d  13  CR  (Carriage Return)
        $0e  14  SO  (Shift Out)
        $0f  15  SI  (Shift In)
        $10  16  DLE (Data link Escape)
        $11  17  DC1 (X-On)
        $12  18  DC2 (X-On)
        $13  19  DC3 (X-Off)
        $14  20  DC4 (X-Off)
        $15  21  NAK (No Acknowledge)
        $16  22  SYN (Synchronous idle)
        $17  23  ETB (End transmission blocks)
        $18  24  CAN (Cancel)
        $19  25  EM  (End of Medium)
        $1a  26  SUB (Substitute)
        $1b  27  ESC (Escape)
        $1c  28  FS  (File Separator)
        $1d  29  GS  (Group Separator)
        $1e  30  RS  (Record Seperator)
        $1f  31  US  (Unit Seperator)
        $20  32  BLA (Blank)
        """
        log.error("%04x| (%i) read from RS232 address: $%x",
            op_address, cpu_cycles, address,
        )
        return value

    def write_rs232_interface(self, cpu_cycles, op_address, address, value):

    def reset_vector(self, address):
        return 0xdb46



def test_run():
    import subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
#         "--verbosity=5",
#         "--verbosity=20",
        "--verbosity=30",
        "--cfg=Simple6809Cfg",
#         "--max=50000",
        "--max=20000",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
