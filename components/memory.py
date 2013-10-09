#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    6809 is Big-Endian

    Links:
        http://dragondata.worldofdragon.org/Publications/inside-dragon.htm
        http://www.burgins.com/m6809.html
        http://koti.mbnet.fi/~atjs/mc6809/

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on:
        * ApplyPy by James Tauber (MIT license)
        * XRoar emulator by Ciaran Anscomb (GPL license)
    more info, see README
"""

import logging
import os
import sys
import socket
import struct

log = logging.getLogger("DragonPy.memory")


class ROM(object):

    def __init__(self, cfg, start, size):
        self.cfg = cfg
        self.start = start
        self.end = start + size
        self._mem = [0x00] * size
        log.info("init %s Bytes %s (%s - %s)" % (
            size, self.__class__.__name__, hex(start), hex(self.end)
        ))

    def load(self, address, data):
        for offset, datum in enumerate(data):
            self._mem[address - self.start + offset] = datum

    def load_file(self, address, filename):
        with open(filename, "rb") as f:
            for offset, datum in enumerate(f.read()):
                index = address - self.start + offset
                try:
                    self._mem[index] = ord(datum)
                except IndexError:
                    size = os.stat(filename).st_size
                    log.error("Error: File %s (%sBytes in hex: %s) is bigger than: %s" % (
                        filename, size, hex(size), hex(index)
                    ))
        log.debug("\tread %sBytes from %s into ROM %s-%s" % (
            offset, filename, hex(address), hex(address + offset)
        ))

    def read_byte(self, address):
        assert self.start <= address <= self.end, "Read %s from %s is not in range %s-%s" % (hex(address), self.__class__.__name__, hex(self.start), hex(self.end))
        byte = self._mem[address - self.start]
#         log.debug("\tread byte %s: %s" % (hex(address), hex(byte)))
#         self.cfg.mem_info(address, "read byte")
        return byte


class RAM(ROM):
    def write_byte(self, address, value):
        log.debug(" **** write $%x to $%x - mem info:" % (value, address))
        log.debug("      %s" % self.cfg.mem_info.get_shortest(value))
        log.debug("      %s" % self.cfg.mem_info.get_shortest(address))
        self._mem[address] = value


class Memory(object):
    def __init__(self, cpu, cfg):
        self.cpu = cpu
        self.cfg = cfg
        self.use_bus = cfg.use_bus
        if self.use_bus:
            self.bus = cfg.bus # socket for internal bus I/O
            log.debug("Bus socket: %s" % repr(self.bus))
            assert self.bus is not None
        else:
            self.bus = None

        self.rom = ROM(cfg, start=cfg.ROM_START, size=cfg.ROM_SIZE)

        if cfg:
            self.rom.load_file(cfg.ROM_START, cfg.rom)

        self.ram = RAM(cfg, start=cfg.RAM_START, size=cfg.RAM_SIZE)

        if cfg and cfg.ram:
            self.ram.load_file(cfg.RAM_START, cfg.ram)

    def load(self, address, data):
        if address < self.cfg.RAM_END:
            self.ram.load(address, data)

    def read_byte(self, address):
        self.cpu.cycles += 1
        log.debug("\tread byte at $%x" % address)

        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
            log.debug("\tread byte at $%x from bus: %s" % (address, info))
            return self.bus_read_byte(address)

        if address < self.cfg.RAM_END:
            return self.ram.read_byte(address)
        elif self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            return self.rom.read_byte(address)
        else:
            raise

    def read_word(self, address):
        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
            log.debug("\twrite word at $%x to bus: %s" % (address, info))
            return self.bus_read_word(address)

        # 6809 is Big-Endian
        return self.read_byte(address + 1) + (self.read_byte(address) << 8)

    def write_byte(self, address, value):
        self.cpu.cycles += 1
        
        assert 0x0 <= value <= 0xff, "Write out of range value $%x to $%x" % (value, address)

        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
            log.debug("\twrite byte at $%x to bus: %s" % (address, info))
            return self.bus_write_byte(address, value)

        if address < self.cfg.RAM_END:
            self.ram.write_byte(address, value)
        else:
            raise

    def write_word(self, address, value):
        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
            log.debug("\twrite word at $%x to bus: %s" % (address, info))
            return self.bus_write_word(address, value)

        # 6809 is Big-Endian
        self.write_byte(address, value >> 8)
        self.write_byte(address + 1, value & 0xff)

    def _bus_communication(self, structure, address, value=None):
        if value is None:
            log.debug(" **** bus read $%x" % (address))
            action = self.cfg.BUS_ACTION_READ # = 0
            value = 0
        else:
            log.debug(" **** bus write $%x to $%x" % (value, address))
            action = self.cfg.BUS_ACTION_WRITE # = 1

        if not self.use_bus:
            log.debug(" **** don't use bus")
            return

        args = (
            self.cpu.cycles,
            action, # 0 = read, 1 = write
            structure, # 0 = byte, 1 = word
            address,
            value, # value to write
        )
        data = struct.pack(self.cfg.STRUCT_TO_PERIPHERY_FORMAT, *args)
        log.debug("struct.pack %s with %s: %s" % (
            repr(args), self.cfg.STRUCT_TO_PERIPHERY_FORMAT, repr(data)
        ))
        try:
            self.bus.send(data)
        except IOError:
            sys.exit(0)

    def _bus_read(self, structure, address):
#         self.cpu.cycles += 1 # ???
        self._bus_communication(structure, address)
        if not self.cfg.use_bus:
            raise NotImplementedError
        try:
            data = self.bus.recv(self.cfg.STRUCT_MEMORY_LEN)
        except socket.error, err:
            log.error("Socket error: %s" % err)
            sys.exit(0)
            
        if len(data) != self.cfg.STRUCT_MEMORY_LEN:
            log.error("Error: Get wrong data length back: %s" % repr(data))
            sys.exit(0)

        value = struct.unpack(self.cfg.STRUCT_TO_MEMORY_FORMAT, data)[0]
        log.debug("Receive from bus: %s -> $%x" % (repr(data), value))
            
        return value

    def _bus_write(self, structure, address, value):
#         self.cpu.cycles += 1 # ???
        self._bus_communication(structure, address, value)

    def bus_read_byte(self, address):
        log.debug(" **** bus read byte from $%x" % (address))
        return self._bus_read(self.cfg.BUS_STRUCTURE_BYTE, address)

    def bus_read_word(self, address):
        log.debug(" **** bus read word from $%x" % (address))
        return self._bus_read(self.cfg.BUS_STRUCTURE_WORD, address)

    def bus_write_byte(self, address, value):
        log.debug(" **** bus write byte $%x to $%x" % (value, address))
        return self._bus_write(self.cfg.BUS_STRUCTURE_BYTE, address, value)

    def bus_write_word(self, address, value):
        log.debug(" **** bus write word $%x to $%x" % (value, address))
        return self._bus_write(self.cfg.BUS_STRUCTURE_WORD, address, value)


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
