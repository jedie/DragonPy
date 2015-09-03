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

from __future__ import absolute_import, division, print_function
import six
xrange = six.moves.xrange

import array
import os
import sys
import logging

import six
from dragonlib.utils.logging_utils import log_hexlist


log = logging.getLogger(__name__)


class Memory(object):
    def __init__(self, cfg, read_bus_request_queue=None, read_bus_response_queue=None, write_bus_queue=None):
        self.cfg = cfg
        self.read_bus_request_queue = read_bus_request_queue
        self.read_bus_response_queue = read_bus_response_queue
        self.write_bus_queue = write_bus_queue

        self.INTERNAL_SIZE = (0xFFFF + 1)

        self.RAM_SIZE = (self.cfg.RAM_END - self.cfg.RAM_START) + 1
        self.ROM_SIZE = (self.cfg.ROM_END - self.cfg.ROM_START) + 1
        assert not hasattr(cfg, "RAM_SIZE"), "cfg.RAM_SIZE is deprecated! Remove it from: %s" % self.cfg.__class__.__name__
        assert not hasattr(cfg, "ROM_SIZE"), "cfg.ROM_SIZE is deprecated! Remove it from: %s" % self.cfg.__class__.__name__

        assert not hasattr(cfg, "ram"), "cfg.ram is deprecated! Remove it from: %s" % self.cfg.__class__.__name__

        assert not hasattr(cfg, "DEFAULT_ROM"), "cfg.DEFAULT_ROM must be converted to DEFAULT_ROMS tuple in %s" % self.cfg.__class__.__name__

        assert self.RAM_SIZE + self.RAM_SIZE <= self.INTERNAL_SIZE, "%s Bytes < %s Bytes" % (
            self.RAM_SIZE + self.RAM_SIZE, self.INTERNAL_SIZE
        )

        # About different types of memory see:
        # http://www.python-forum.de/viewtopic.php?p=263775#p263775 (de)

        # The old variant: Use a simple List:
#        self._mem = [None] * self.cfg.MEMORY_SIZE

        # Bytearray will be consume less RAM, but it's slower:
#        self._mem = bytearray(self.cfg.MEMORY_SIZE)

        # array consumes also less RAM than lists and it's a little bit faster:
        self._mem = array.array("B", [0x00] * self.INTERNAL_SIZE) # unsigned char

        if cfg and cfg.rom_cfg:
            for romfile in cfg.rom_cfg:
                self.load_file(romfile)

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


        log.critical("init RAM $%04x (dez.:%s) Bytes RAM $%04x (dez.:%s) Bytes (total %s real: %s)",
            self.RAM_SIZE, self.RAM_SIZE,
            self.ROM_SIZE, self.ROM_SIZE,
            self.RAM_SIZE + self.ROM_SIZE,
            len(self._mem)
        )


    #---------------------------------------------------------------------------

    def _map_address_range(self, callbacks_dict, callback_func, start_addr, end_addr=None):
        if end_addr is None:
            callbacks_dict[start_addr] = callback_func
        else:
            for addr in xrange(start_addr, end_addr + 1):
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
        if isinstance(data, six.string_types):
            data = [ord(c) for c in data]

        log.debug("ROM load at $%04x: %s", address,
            ", ".join(["$%02x" % i for i in data])
        )
        for ea, datum in enumerate(data, address):
            try:
                self._mem[ea] = datum
            except OverflowError as err:
                msg="%s - datum=$%x ea=$%04x (load address was: $%04x - data length: %iBytes)" % (
                    err, datum, ea, address, len(data)
                )
                raise OverflowError(msg)

    def load_file(self, romfile):
        data = romfile.get_data()
        self.load(romfile.address, data)
        log.critical("Load ROM file %r to $%04x", romfile.rom_path, romfile.address)

    #---------------------------------------------------------------------------

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

        try:
            byte = self._mem[address]
        except KeyError:
            msg = "reading outside memory area (PC:$%x)" % self.cpu.program_counter.value
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

    #---------------------------------------------------------------------------

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

        if self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            msg = "%04x| writing into ROM at $%04x ignored." % (
                self.cpu.program_counter.value, address
            )
            self.cfg.mem_info(address, msg)
            msg2 = "%s: $%x" % (msg, address)
            log.critical(msg2)
            return

        try:
            self._mem[address] = value
        except (IndexError, KeyError):
            msg = "%04x| writing to %x is outside RAM/ROM !" % (
                self.cpu.program_counter.value, address
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

    #---------------------------------------------------------------------------

    def get(self, start, end):
        """
        used in unittests
        """
        return [self.read_byte(addr) for addr in xrange(start, end)]

    def iter_bytes(self, start, end):
        for addr in xrange(start, end):
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


