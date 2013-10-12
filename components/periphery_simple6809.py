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

    def read_byte(self, cpu_cycles, address):
        log.debug(
            "Periphery.read_byte from $%x (cpu_cycles: %i)" % (
            address, cpu_cycles
        ))
        if 0xa000 <= address <= 0xbfef:
            return self.read_rs232_interface(cpu_cycles, address)

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

    def write_byte(self, cpu_cycles, address, value):
        msg = "TODO: write byte $%x to $%x" % (value, address)
        log.error(msg)
        raise NotImplementedError(msg)
    write_word = write_byte

    def cycle(self, cpu_cycles):
        log.debug("TODO: Simple6809Periphery.cycle")


    def read_rs232_interface(self, cpu_cycles, address):
        log.error("read from RS232 address: $%x" % address)


    def reset_vector(self, address):
        return 0xdb46

def get_simple6809_periphery(cfg):
    return Simple6809Periphery(cfg)


def test_run():
    import subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
        "--verbosity=5",
        "--cfg=Simple6809Cfg",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
