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
"""


import pygame
import select
import socket
import struct
import subprocess
import sys

import logging


log = logging.getLogger(__name__)



class Dragon(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.periphery = cfg.periphery

        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(0)

        cmd_args = [
            sys.executable,
            "cpu6809.py",
            "--bus", str(listener.getsockname()[1]),
#             "--rom", cfg.rom,
            "--verbosity=%s" % cfg.verbosity,
            "--cfg=%s" % cfg.config_name,
        ]
#         if cfg.ram:
#             cmd_args.extend([
#                 "--ram", cfg.ram,
#             ])
#         if cfg.pc is not None:
#             cmd_args.extend([
#                 "--pc", str(cfg.pc),
#             ])
        self.core = subprocess.Popen(cmd_args)

        rs, _, _ = select.select([listener], [], [], 2)
        if not rs:
            print >> sys.stderr, "CPU module did not start"
            sys.exit(1)
        self.cpu, _ = listener.accept()

    def run(self):
        quit_cpu = False
        while not quit_cpu:
            op = self.cpu.recv(8)
            if len(op) == 0:
                break
            cpu_cycles, rw, address, value = struct.unpack("<IBHB", op)
            if rw == 0:
                value = self.periphery.read_byte(cpu_cycles, address)
                try:
                    char = chr(value)
                except ValueError, err:
                    raise ValueError("Error with $%x: %s" % (value, err))
                self.cpu.send(char)
            elif rw == 1:
                self.periphery.write_byte(cpu_cycles, address, value)
                # self.display.update(address, value)
            else:
                break

            quit_cpu = self.periphery.cycle(cpu_cycles)






if __name__ == "__main__":
    print "Run DragonPy_CLI.py instead"
    sys.exit(0)
