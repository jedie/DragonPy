#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    TODO:
        Maybe "merge" ROM, RAM,
        so the offset calulation in ROM is not needed.

    6809 is Big-Endian

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
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

    def __init__(self, cfg, memory, start, size):
        self.cfg = cfg
        self.start = start
        self.end = start + size

        self._mem = [None] * start
        self._mem += memory
#         self._mem = memory # [0x00] * size
        # assert len(self._mem) == size, "%i != %i" len(self._mem) == size
        log.critical("init %s Bytes (real: %s) %s ($%04x - $%04x)" % (
            size, len(self._mem), self.__class__.__name__, start, self.end
        ))

    def load(self, address, data):
        if isinstance(data, basestring):
            data = [ord(c) for c in data]
        log.debug("ROM load at $%04x: %s", address,
            ", ".join(["$%02x" % i for i in data])
        )
        for offset, datum in enumerate(data):
            self._mem[address - self.start + offset] = datum

    def load_file(self, address, filename):
        with open(filename, "rb") as f:
            for offset, datum in enumerate(f.read()):
                index = address + offset
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
        try:
            byte = self._mem[address]
        except IndexError:
            raise IndexError(
                "Read $%04x from %s is not in range $%04x-$%04x (%s size: %i Bytes)" % (
                    address - self.start,
                    self.__class__.__name__,
                    self.start, self.end,
                    self.__class__.__name__, len(self._mem),
                )
            )
#         log.debug("\tread byte %s: %s" % (hex(address), hex(byte)))
#         self.cfg.mem_info(address, "read byte")
        return byte


class RAM(ROM):
    def write_byte(self, address, value):
#        log.debug(" **** write $%x to $%x", value, address)
#        log.log(5, "\t\t%s", self.cfg.mem_info.get_shortest(value))
#        log.log(5, "\t\t%s", self.cfg.mem_info.get_shortest(address))
        self._mem[address] = value


class Memory(object):
    def __init__(self, cfg, read_bus_request_queue=None, read_bus_response_queue=None, write_bus_queue=None):
        self.cfg = cfg
        self.use_bus = cfg.cfg_dict["use_bus"]
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue

        self.rom = ROM(
            cfg, memory=cfg.get_initial_ROM(),
            start=cfg.ROM_START, size=cfg.ROM_SIZE
        )
        if cfg and cfg.rom:
            self.rom.load_file(cfg.ROM_START, cfg.rom)

        self.ram = RAM(
            cfg, memory=cfg.get_initial_RAM(),
            start=cfg.RAM_START, size=cfg.RAM_SIZE
        )

        if cfg and cfg.ram:
            self.ram.load_file(cfg.RAM_START, cfg.ram)

        self._read_callbacks = {}
        self._write_callbacks = {}
        for addr_range, functions in cfg.memory_callbacks.items():
            start_addr, end_addr = addr_range
            for addr in xrange(start_addr, end_addr):
                read_func, write_func = functions
                if read_func:
                    self._read_callbacks[addr] = read_func
                if write_func:
                    self._write_callbacks[addr] = write_func
        log.debug("memory read callbacks: %s", self._read_callbacks)
        log.debug("memory write callbacks: %s", self._write_callbacks)

    def load(self, address, data):
        if address < self.cfg.RAM_END:
            self.ram.load(address, data)
        else:
            raise RuntimeError(
                "Load data into ROM?!? Load into $%x, RAM end is $%x" % (
                    address, self.cfg.RAM_END
                )
            )

    def read_byte(self, address):
        self.cpu.cycles += 1

        if address in self._read_callbacks:
            self._read_callbacks[address](self.cpu, address)

        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
            byte = self.bus_read_byte(address)
#            log.log(5, "%04x| (%i) read byte $%x from address $%x from bus: %s",
#                self.cpu.last_op_address, self.cpu.cycles,
#                byte, address, info
#            )
            return byte

        if address < self.cfg.RAM_END:
            byte = self.ram.read_byte(address)
        elif self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            byte = self.rom.read_byte(address)
        else:
            msg = "reading outside memory area (PC:$%x)" % self.cpu.program_counter.get()
            self.cfg.mem_info(address, msg)
            msg2 = "%s: $%x" % (msg, address)
            log.warn(msg2)
            # raise RuntimeError(msg2)
            byte = 0x0

#        log.log(5, "%04x| (%i) read byte $%x from $%x",
#            self.cpu.last_op_address, self.cpu.cycles,
#            byte, address
#        )
#         if 32 <= byte <= 126:
#         if 65 <= byte <= 90:
#            log.info("%04x| (%i) read char %r ($%x) from $%x",
#                self.cpu.last_op_address, self.cpu.cycles, chr(byte), byte, address
#            )
        return byte

    def read_word(self, address):
        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
#            log.log(5, "\tread word at $%x from bus: %s", address, info)
            return self.bus_read_word(address)

        # 6809 is Big-Endian
        return self.read_byte(address + 1) + (self.read_byte(address) << 8)

    def write_byte(self, address, value):
        self.cpu.cycles += 1

        assert value >= 0, "Write negative byte hex:%00x dez:%i to $%04x" % (value, value, address)
        assert value <= 0xff, "Write out of range byte hex:%02x dez:%i to $%04x" % (value, value, address)
#         if not (0x0 <= value <= 0xff):
#             log.error("Write out of range value $%02x to $%04x", value, address)
#             value = value & 0xff
#             log.error(" ^^^^ wrap around to $%x", value)

        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
#            log.log(5, "\twrite byte at $%x to bus: %s" % (address, info))
            return self.bus_write_byte(address, value)

        if address < self.cfg.RAM_END:
            self.ram.write_byte(address, value)
        else:
            msg = "writing to %x is outside RAM end %x (PC:$%x)" % (
                address, self.cfg.RAM_END, self.cpu.program_counter.get()
            )
            self.cfg.mem_info(address, msg)
            msg2 = "%s: $%x" % (msg, address)
            log.warn(msg2)
#             raise RuntimeError(msg2)

        if address in self._write_callbacks:
            self._write_callbacks[address](self.cpu, address, value)

    def write_word(self, address, value):
        if address in self.cfg.bus_addr_areas:
            info = self.cfg.bus_addr_areas[address]
#            log.log(5, "\twrite word at $%x to bus: %s" % (address, info))
            return self.bus_write_word(address, value)

        assert value >= 0, "Write negative word hex:%04x dez:%i to $%04x" % (value, value, address)
        assert value <= 0xffff, "Write out of range word hex:%04x dez:%i to $%04x" % (value, value, address)

        # 6809 is Big-Endian
        self.write_byte(address, value >> 8)
        self.write_byte(address + 1, value & 0xff)

    def _bus_read(self, structure, address):
#         self.cpu.cycles += 1 # ???
        if self.use_bus:
            self.read_bus_request_queue.put(
                (self.cpu.cycles, self.cpu.last_op_address, structure, address),
                block=True
            )
            self.read_bus_request_queue.join() # Wait for result
            value = self.read_bus_response_queue.get(block=True)
            self.read_bus_response_queue.task_done()
            return value
        else:
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                return self.cfg.periphery.read_word(
                    self.cpu.cycles, self.cpu.last_op_address, address
                )
            else:
                return self.cfg.periphery.read_byte(
                    self.cpu.cycles, self.cpu.last_op_address, address
                )

    def _bus_write(self, structure, address, value):
#         self.cpu.cycles += 1 # ???
        if self.use_bus:
            self.write_bus_queue.put(
                (self.cpu.cycles, self.cpu.last_op_address, structure, address, value),
                block=True
            )
            self.write_bus_queue.join() # Wait to finish
        else:
            if structure == self.cfg.BUS_STRUCTURE_WORD:
                self.cfg.periphery.write_word(
                    self.cpu.cycles, self.cpu.last_op_address, address, value
                )
            else:
                self.cfg.periphery.write_byte(
                    self.cpu.cycles, self.cpu.last_op_address, address, value
                )

    def bus_read_byte(self, address):
#        log.debug(" **** bus read byte from $%x" % (address))
        value = self._bus_read(self.cfg.BUS_STRUCTURE_BYTE, address)
        return value

    def bus_read_word(self, address):
#        log.debug(" **** bus read word from $%x" % (address))
        return self._bus_read(self.cfg.BUS_STRUCTURE_WORD, address)

    def bus_write_byte(self, address, value):
#        log.debug(" **** bus write byte $%x to $%x" % (value, address))
        return self._bus_write(self.cfg.BUS_STRUCTURE_BYTE, address, value)

    def bus_write_word(self, address, value):
#        log.debug(" **** bus write word $%x to $%x" % (value, address))
        return self._bus_write(self.cfg.BUS_STRUCTURE_WORD, address, value)

    def iter_bytes(self, start, end):
        for addr in xrange(start, end):
            yield addr, self.read_byte(addr)

    def get_dump(self, start, end):
        dump_lines = []
        for addr, value in self.iter_bytes(start, end + 1):
            msg = "$%04x: $%02x (dez: %i)" % (addr, value, value)
            msg = "%-25s| %s" % (
                msg, self.cfg.mem_info.get_shortest(addr)
            )
            dump_lines.append(msg)
        return dump_lines

    def print_dump(self, start, end):
        print "Memory dump from $%04x to $%04x:" % (start, end)
        dump_lines = self.get_dump(start, end)
        print "\n".join(["\t%s" % line for line in dump_lines])


def test_run():
    import subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
#         "--verbosity=5",
#         "--verbosity=10",
#         "--verbosity=20",
#         "--verbosity=30",
#         "--verbosity=40",
        "--verbosity=50",
        "--cfg=Simple6809",
#         "--max=100000",
#         "--max=30000",
#         "--max=20000",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
