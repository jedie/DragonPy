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
from utils.simple_debugger import print_exc_plus


log = logging.getLogger(__name__)



class Dragon(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.periphery = cfg.periphery_class(cfg)

        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(0)

        bus_socket_host, bus_socket_port = listener.getsockname()
        cmd_args = [
            sys.executable,
            "cpu6809.py",
             "--bus_socket_host=%s" % bus_socket_host,
             "--bus_socket_port=%i" % bus_socket_port,
        ]
        cmd_args += sys.argv[1:]
        print "Startup CPU with: %s" % " ".join(cmd_args)

        try:
            self.core = subprocess.Popen(cmd_args)
        except:
            print_exc_plus()

        rs, _, _ = select.select([listener], [], [], 2)
        if not rs:
            print >> sys.stderr, "CPU module did not start"
            sys.exit(1)
        else:
            print "CPU started"
        self.cpu, _ = listener.accept()

        self.bus_type_func_map = {
            (self.cfg.BUS_ACTION_READ, self.cfg.BUS_STRUCTURE_BYTE): self.periphery.read_byte,
            (self.cfg.BUS_ACTION_READ, self.cfg.BUS_STRUCTURE_WORD): self.periphery.read_word,
            (self.cfg.BUS_ACTION_WRITE, self.cfg.BUS_STRUCTURE_BYTE): self.periphery.write_byte,
            (self.cfg.BUS_ACTION_WRITE, self.cfg.BUS_STRUCTURE_WORD): self.periphery.write_word,
        }

    def run(self):
        quit_cpu = False
        while not quit_cpu:
            cpu_data = self.cpu.recv(self.cfg.STRUCT_TO_PERIPHERY_LEN)
            log.debug("receive %s Bytes from CPU via bus" % self.cfg.STRUCT_TO_PERIPHERY_LEN)
            if len(cpu_data) == 0:
                break

            try:
                cpu_cycles, op_address, action, structure, address, value = struct.unpack(self.cfg.STRUCT_TO_PERIPHERY_FORMAT, cpu_data)
            except Exception, err:
                msg = "Error unpack %s with %s: %s" % (
                    repr(cpu_data), self.cfg.STRUCT_TO_PERIPHERY_FORMAT, err
                )
                print >> sys.stderr, msg
                raise

            periphery_func = self.bus_type_func_map[(action, structure)]

            if action == self.cfg.BUS_ACTION_READ: # == 1
                value = periphery_func(cpu_cycles, op_address, address)
                assert isinstance(value, int), "Periphery Func. %r must return a integer! It has returned: %s" % (periphery_func.__name__, repr(value))
                try:
                    data = struct.pack(self.cfg.STRUCT_TO_MEMORY_FORMAT, value)
                except struct.error, err:
                    msg = "Error pack response %s with %s: %s" % (
                        repr(value), self.cfg.STRUCT_TO_MEMORY_FORMAT, err
                    )
                    print >> sys.stderr, msg
                    raise
                self.cpu.send(data)
            elif action == self.cfg.BUS_ACTION_WRITE: # == 0
                periphery_func(cpu_cycles, op_address, address, value)
            else:
                raise RuntimeError

            quit_cpu = self.periphery.cycle(cpu_cycles, op_address)






if __name__ == "__main__":
    print "Run DragonPy_CLI.py instead"
    sys.exit(0)
