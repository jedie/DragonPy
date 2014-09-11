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

import array
import os
import sys

from dragonlib.utils import lib2and3
from dragonlib.utils.logging_utils import log, log_hexlist


class ROM(object):

    def __init__(self, cfg, memory, start, size):
        self.cfg = cfg
        self.start = start
        self.end = start + size - 1

        # About different types of memory see:
        # http://www.python-forum.de/viewtopic.php?p=263775#p263775 (de)

        # The old variant: Use a simple List:
#        self._mem = [None] * start + memory

        # Bytearray will be consume less RAM, but it's slower:
#        self._mem = bytearray(start) + bytearray(memory)

        # array consumes also less RAM than lists and it's a little bit faster:
        self._mem = array.array("B", [0x00] * start + memory) # unsigned char

        # assert len(self._mem) == size, "%i != %i" len(self._mem) == size
        log.critical("init $%04x (dez.:%s) Bytes (real: %s) %s ($%04x - $%04x)",
            size, size, len(self._mem), self.__class__.__name__, start, self.end
        )

    def load(self, address, data):
        if isinstance(data, lib2and3.string_types):
            data = [ord(c) for c in data]

        log.debug("ROM load at $%04x: %s", address,
            ", ".join(["$%02x" % i for i in data])
        )
        for offset, datum in enumerate(data):
            self._mem[address - self.start + offset] = datum

    def load_file(self, address, filename, max_size=None):
        log.critical("Load ROM file %r to $%04x", filename, address)
        with open(filename, "rb") as f:
            filesize = os.stat(filename).st_size
            for offset, datum in enumerate(f.read()):
                if max_size and offset > max_size:
                    log.critical("Load only $%04x (dez.: %i) Bytes - file size is $%04x (dez.: %i) Bytes",
                        max_size, max_size, filesize, filesize
                    )
                    break

                index = address + offset
                if lib2and3.PY2:
                    datum = ord(datum)

#                 log.critical("$%04x - $%02x", index, datum)
                try:
                    self._mem[index] = datum
                except IndexError:
                    log.error("Error: File %s $%04x (dez.: %i) Bytes is bigger than: $%04x" % (
                        filename, filesize, filesize, index
                    ))
                    break
        log.info("read $%04x (dez.: %i) Bytes from %r into ROM $%04x-$%04x",
            offset, offset, filename, address, (address + offset)
        )

    def read_byte(self, address):
        try:
#            byte = self._mem[address]
            return self._mem[address]
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
#        return byte


class RAM(ROM):
    def write_byte(self, address, value):
#        log.debug(" **** write $%x to $%x", value, address)
#        log.log(5, "\t\t%s", self.cfg.mem_info.get_shortest(value))
#        log.log(5, "\t\t%s", self.cfg.mem_info.get_shortest(address))
        try:
            self._mem[address] = value
        except TypeError as err:
            msg = "%s - value: %s address: $%04x" % (err, repr(value), address)
            lib2and3.reraise(TypeError, TypeError(msg), sys.exc_info()[2])


class Memory(object):
    def __init__(self, cfg, read_bus_request_queue=None, read_bus_response_queue=None, write_bus_queue=None):
        self.cfg = cfg
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue

        self.rom = ROM(
            cfg, memory=cfg.get_initial_ROM(),
            start=cfg.ROM_START, size=cfg.ROM_SIZE
        )
        if cfg and cfg.rom_cfg:
            for romfile in cfg.rom_cfg:
                self.rom.load_file(
                    address=romfile.address,
                    filename=romfile.filepath,
                    max_size=romfile.max_size
                )

        self.ram = RAM(
            cfg, memory=cfg.get_initial_RAM(),
            start=cfg.RAM_START, size=cfg.RAM_SIZE
        )

        if cfg and cfg.ram:
            self.ram.load_file(cfg.RAM_START, cfg.ram)

        self._read_byte_callbacks = {}
        self._read_word_callbacks = {}
        self._write_byte_callbacks = {}
        self._write_word_callbacks = {}

        # Memory middlewares are function that called on memory read or write
        # the function can change the value that is read/write
        #
        # init read/write byte middlewares:
        self._read_byte_middleware = {}
        self._write_byte_middleware = {}
        for addr_range, functions in list(cfg.memory_byte_middlewares.items()):
            start_addr, end_addr = addr_range
            read_func, write_func = functions

            if read_func:
                self.add_read_byte_middleware(read_func, start_addr, end_addr)

            if write_func:
                self.add_write_byte_middleware(write_func, start_addr, end_addr)

        # init read/write word middlewares:
        self._read_word_middleware = {}
        self._write_word_middleware = {}
        for addr_range, functions in list(cfg.memory_word_middlewares.items()):
            start_addr, end_addr = addr_range
            read_func, write_func = functions

            if read_func:
                self.add_read_word_middleware(read_func, start_addr, end_addr)

            if write_func:
                self.add_write_word_middleware(write_func, start_addr, end_addr)

#         log.critical(
# #         log.debug(
#             "memory read middlewares: %s", self._read_byte_middleware
#         )
#         log.critical(
# #         log.debug(
#             "memory write middlewares: %s", self._write_byte_middleware
#         )

    #---------------------------------------------------------------------------

    def _map_address_range(self, callbacks_dict, callback_func, start_addr, end_addr=None):
        if end_addr is None:
            callbacks_dict[start_addr] = callback_func
        else:
            for addr in range(start_addr, end_addr + 1):
                callbacks_dict[addr] = callback_func

    #---------------------------------------------------------------------------

    def add_read_byte_callback(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._read_byte_callbacks, callback_func, start_addr, end_addr)

    def add_read_word_callback(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._read_word_callbacks, callback_func, start_addr, end_addr)

    def add_write_byte_callback(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._write_byte_callbacks, callback_func, start_addr, end_addr)

    def add_write_word_callback(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._write_word_callbacks, callback_func, start_addr, end_addr)

    #---------------------------------------------------------------------------

    def add_read_byte_middleware(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._read_byte_middleware, callback_func, start_addr, end_addr)

    def add_write_byte_middleware(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._write_byte_middleware, callback_func, start_addr, end_addr)

    def add_read_word_middleware(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._read_word_middleware, callback_func, start_addr, end_addr)

    def add_write_word_middleware(self, callback_func, start_addr, end_addr=None):
        self._map_address_range(self._write_word_middleware, callback_func, start_addr, end_addr)

    #---------------------------------------------------------------------------

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

        if address in self._read_byte_callbacks:
            byte = self._read_byte_callbacks[address](
                self.cpu.cycles, self.cpu.last_op_address, address
            )
            assert byte is not None, "Error: read byte callback for $%04x func %r has return None!" % (
                address, self._read_byte_callbacks[address].__name__
            )
            return byte

        if address < self.cfg.RAM_END:
            byte = self.ram.read_byte(address)
        elif self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            byte = self.rom.read_byte(address)
        else:
            msg = "reading outside memory area (PC:$%x)" % self.cpu.program_counter.get()
            self.cfg.mem_info(address, msg)
            msg2 = "%s: $%x" % (msg, address)
            log.warning(msg2)
            # raise RuntimeError(msg2)
            byte = 0x0

        if address in self._read_byte_middleware:
            byte = self._read_byte_middleware[address](
                self.cpu.cycles, self.cpu.last_op_address, address, byte
            )
            assert byte is not None, "Error: read byte middleware for $%04x func %r has return None!" % (
                address, self._read_byte_middleware[address].__name__
            )

#        log.log(5, "%04x| (%i) read byte $%x from $%x",
#            self.cpu.last_op_address, self.cpu.cycles,
#            byte, address
#        )
        return byte

    def read_word(self, address):
        if address in self._read_word_callbacks:
            word = self._read_word_callbacks[address](
                self.cpu.cycles, self.cpu.last_op_address, address
            )
            assert word is not None, "Error: read word callback for $%04x func %r has return None!" % (
                address, self._read_word_callbacks[address].__name__
            )
            return word

        # 6809 is Big-Endian
        return (self.read_byte(address) << 8) + self.read_byte(address + 1)

    def write_byte(self, address, value):
        self.cpu.cycles += 1

        assert value >= 0, "Write negative byte hex:%00x dez:%i to $%04x" % (value, value, address)
        assert value <= 0xff, "Write out of range byte hex:%02x dez:%i to $%04x" % (value, value, address)
#         if not (0x0 <= value <= 0xff):
#             log.error("Write out of range value $%02x to $%04x", value, address)
#             value = value & 0xff
#             log.error(" ^^^^ wrap around to $%x", value)

        if address in self._write_byte_middleware:
            value = self._write_byte_middleware[address](
                self.cpu.cycles, self.cpu.last_op_address, address, value
            )
            assert value is not None, "Error: write byte middleware for $%04x func %r has return None!" % (
                address, self._write_byte_middleware[address].__name__
            )

        if address in self._write_byte_callbacks:
            return self._write_byte_callbacks[address](
                self.cpu.cycles, self.cpu.last_op_address, address, value
            )

        if address < self.cfg.RAM_END:
            self.ram.write_byte(address, value)
        else:
            msg = "writing to %x is outside RAM end %x (PC:$%x)" % (
                address, self.cfg.RAM_END, self.cpu.program_counter.get()
            )
            self.cfg.mem_info(address, msg)
            msg2 = "%s: $%x" % (msg, address)
            log.warning(msg2)
#             raise RuntimeError(msg2)

    def write_word(self, address, word):
        assert word >= 0, "Write negative word hex:%04x dez:%i to $%04x" % (word, word, address)
        assert word <= 0xffff, "Write out of range word hex:%04x dez:%i to $%04x" % (word, word, address)

        if address in self._write_word_middleware:
            word = self._write_word_middleware[address](
                self.cpu.cycles, self.cpu.last_op_address, address, word
            )
            assert word is not None, "Error: write word middleware for $%04x func %r has return None!" % (
                address, self._write_word_middleware[address].__name__
            )

        if address in self._write_word_callbacks:
            return self._write_word_callbacks[address](
                self.cpu.cycles, self.cpu.last_op_address, address, word
            )

        # 6809 is Big-Endian
        self.write_byte(address, word >> 8)
        self.write_byte(address + 1, word & 0xff)

    def iter_bytes(self, start, end):
        for addr in range(start, end + 1):
            yield addr, self.read_byte(addr)

    def get_dump(self, start, end):
        dump_lines = []
        for addr, value in self.iter_bytes(start, end):
            msg = "$%04x: $%02x (dez: %i)" % (addr, value, value)
            msg = "%-25s| %s" % (
                msg, self.cfg.mem_info.get_shortest(addr)
            )
            dump_lines.append(msg)
        return dump_lines

    def print_dump(self, start, end):
        print("Memory dump from $%04x to $%04x:" % (start, end))
        dump_lines = self.get_dump(start, end)
        print("\n".join(["\t%s" % line for line in dump_lines]))


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
        "--machine=Simple6809",
#         "--max=100000",
#         "--max=30000",
#         "--max=20000",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
