#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    6809 is Big-Endian

    Links:
        http://dragondata.worldofdragon.org/Publications/inside-dragon.htm
        http://www.burgins.com/m6809.html
        http://koti.mbnet.fi/~atjs/mc6809/

        MAME
        http://mamedev.org/source/src/mess/drivers/dragon.c.html
        http://mamedev.org/source/src/mess/machine/dragon.c.html
        http://mamedev.org/source/src/emu/cpu/m6809/m6809.c.html

    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License
"""


import BaseHTTPServer
import json
import re
import select
import socket
import struct
import sys
import logging
from DragonPy_CLI import DragonPyCLI
import inspect


log = logging.getLogger("DragonPy")

bus = None # socket for bus I/O


def signed(x):
    if x > 0x7F:
        x = x - 0x100
    return x


def opcode(code):
    """A decorator for opcodes"""
    def decorator(func):
        setattr(func, "_is_opcode", True)
        setattr(func, "_opcode", code)
        return func
    return decorator


class ROM:

    def __init__(self, start, size):
        self.start = start
        self.end = start + size - 1
        self._mem = [0x00] * size
        print "init %s Bytes %s (start: %s end: %s size: %s)" % (
            size, self.__class__.__name__, hex(start), hex(self.end), hex(size)
        )

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
                    raise IndexError("ROM file %s bigger than: %s" % (filename, hex(index)))

    def read_byte(self, address):
        assert self.start <= address <= self.end, "Read %s from %s is not in range %s-%s" % (hex(address), self.__class__.__name__, hex(self.start), hex(self.end))
        byte = self._mem[address - self.start]
        log.debug("Read byte %s: %s" % (hex(address), hex(byte)))
        return byte


class RAM(ROM):

    def write_byte(self, address, value):
        self._mem[address] = value





class Memory:

    def __init__(self, cfg=None, use_bus=True):
        self.cfg = cfg
        self.use_bus = use_bus

        self.rom = ROM(start=self.cfg.ROM_START, size=self.cfg.ROM_SIZE)

        if cfg:
            self.rom.load_file(self.cfg.ROM_START, cfg.rom)

        self.ram = RAM(start=self.cfg.RAM_START, size=self.cfg.RAM_SIZE)

        if cfg and cfg.ram:
            self.ram.load_file(0x0000, cfg.ram)

    def load(self, address, data):
        if address < self.cfg.RAM_END:
            self.ram.load(address, data)

    def read_byte(self, cycle, address):
        if address < self.cfg.RAM_END:
            return self.ram.read_byte(address)
        elif self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            return self.rom.read_byte(address)
        else:
            return self.bus_read(cycle, address)

    def read_word(self, cycle, address):
        return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)

    def write_byte(self, cycle, address, value):
        if address < self.cfg.RAM_END:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)

    def bus_read(self, cycle, address):
        if not self.use_bus:
            return 0
        op = struct.pack("<IBHB", cycle, 0, address, 0)
        try:
            bus.send(op)
            b = bus.recv(1)
            if len(b) == 0:
                sys.exit(0)
            return ord(b)
        except socket.error:
            sys.exit(0)

    def bus_write(self, cycle, address, value):
        if not self.use_bus:
            return
        op = struct.pack("<IBHB", cycle, 1, address, value)
        try:
            bus.send(op)
        except IOError:
            sys.exit(0)


class ControlHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server, cpu):
        self.cpu = cpu

        self.get_urls = {
            r"/disassemble/(\d+)$": self.get_disassemble,
            r"/memory/(\d+)(-(\d+))?$": self.get_memory,
            r"/memory/(\d+)(-(\d+))?/raw$": self.get_memory_raw,
            r"/status$": self.get_status,
        }

        self.post_urls = {
            r"/memory/(\d+)(-(\d+))?$": self.post_memory,
            r"/memory/(\d+)(-(\d+))?/raw$": self.post_memory_raw,
            r"/quit$": self.post_quit,
            r"/reset$": self.post_reset,
        }

        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def log_request(self, code, size=0):
        pass

    def dispatch(self, urls):
        for r, f in urls.items():
            m = re.match(r, self.path)
            if m is not None:
                f(m)
                break
        else:
            self.send_response(404)
            self.end_headers()

    def response(self, s):
        self.send_response(200)
        self.send_header("Content-Length", str(len(s)))
        self.end_headers()
        self.wfile.write(s)

    def do_GET(self):
        self.dispatch(self.get_urls)

    def do_POST(self):
        self.dispatch(self.post_urls)

    def get_disassemble(self, m):
        addr = int(m.group(1))
        r = []
        n = 20
        while n > 0:
            dis, length = self.disassemble.disasm(addr)
            r.append(dis)
            addr += length
            n -= 1
        self.response(json.dumps(r))

    def get_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        self.response("".join([chr(self.cpu.read_byte(x)) for x in range(addr, end + 1)]))

    def get_memory(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        self.response(json.dumps(list(map(self.cpu.read_byte, range(addr, end + 1)))))

    def get_status(self, m):
        self.response(json.dumps(dict((x, getattr(self.cpu, x)) for x in (
            "accumulator",
            "x_index",
            "y_index",
            "stack_pointer",
            "program_counter",
            "sign_flag",
            "overflow_flag",
            "break_flag",
            "decimal_mode_flag",
            "interrupt_disable_flag",
            "zero_flag",
            "carry_flag",
        ))))

    def post_memory(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = self.rfile.read(int(self.headers["Content-Length"]))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_quit(self, m):
        self.cpu.quit = True
        self.response("")

    def post_reset(self, m):
        self.cpu.reset()
        self.cpu.running = True
        self.response("")


class ControlHandlerFactory:

    def __init__(self, cpu):
        self.cpu = cpu

    def __call__(self, request, client_address, server):
        return ControlHandler(request, client_address, server, self.cpu)


class CPU(object):

    STACK_PAGE = 0x100
#     RESET_VECTOR = 0xb44f
    RESET_VECTOR = 0xB3B4
#     RESET_VECTOR = 0xfffe

    def __init__(self, cfg, memory):
        self.cfg = cfg
        self.memory = memory

        if self.cfg.bus:
            self.control_server = BaseHTTPServer.HTTPServer(("127.0.0.1", 6809), ControlHandlerFactory(self))
        else:
            self.control_server = None

        self.index_x = 0 # X - 16 bit index register
        self.index_y = 0 # Y - 16 bit index register

        self.user_stack_pointer = 0 # U - 16 bit user-stack pointer
        self.stack_pointer = 0 # S - 16 bit system-stack pointer

        self.value_register = 0 # V - 16 bit variable inter-register

        self.program_counter = None # PC - 16 bit program counter register

        self.accumulator_a = 0 # A - 8 bit accumulator
        self.accumulator_b = 0 # B - 8 bit accumulator
        self.accumulator_e = 0 # E - 8 bit accumulator
        self.accumulator_f = 0 # F - 8 bit accumulator

        # D - 16 bit concatenated reg. (A + B)
        # W - 16 bit concatenated reg. (E + F)
        # Q - 32 bit concatenated reg. (D + W)

        # CC - 8 bit condition code register as flags:
        self.entire_flag = 0 # E - bit 7
        self.firq_mask_flag = 0 # F - bit 6
        self.half_carry_flag = 0 # H - bit 5
        self.irq_mask_flag = 0 # I - bit 4
        self.negative_flag = 0 # N - bit 3
        self.zero_flag = 0 # Z - bit 2
        self.overflow_flag = 0 # V - bit 1
        self.carry_flag = 0 # C - bit 0

        self.mode_error = 0 # MD - 8 bit mode/error register
        self.condition_code = 0
        self.direct_page = 0 # DP - 8 bit direct page register

        self.cycles = 0

        self.opcodes = {}
        for name, value in inspect.getmembers(self):
            if inspect.ismethod(value) and getattr(value, "_is_opcode", False):
                self.opcodes[getattr(value, "_opcode")] = value

        self.reset()
        if cfg.pc is not None:
            self.program_counter = cfg.pc
        self.running = True
        self.quit = False

    ####

    def status_from_byte(self, status):
        self.carry_flag = [0, 1][0 != status & 1]
        self.overflow_flag = [0, 1][0 != status & 2]
        self.zero_flag = [0, 1][0 != status & 4]
        self.negative_flag = [0, 1][0 != status & 8]
        self.irq_mask_flag = [0, 1][0 != status & 16]
        self.half_carry_flag = [0, 1][0 != status & 32]
        self.firq_mask_flag = [0, 1][0 != status & 64]
        self.entire_flag = [0, 1][0 != status & 128]

    def status_as_byte(self):
        return self.carry_flag | \
            self.overflow_flag << 1 | \
            self.zero_flag << 2 | \
            self.negative_flag << 3 | \
            self.irq_mask_flag << 4 | \
            self.half_carry_flag << 5 | \
            self.firq_mask_flag << 6 | \
            self.entire_flag << 7

    def get_register(self, addr):
        log.debug("get register value from %s" % hex(addr))
        if addr == 0x00: # 0000 - D - 16 bit concatenated reg.(A B)
            return self.accumulator_a + self.accumulator_b
        elif addr == 0x01: # 0001 - X - 16 bit index register
            return self.index_x
        elif addr == 0x02: # 0010 - Y - 16 bit index register
            return self.index_y
        elif addr == 0x03: # 0011 - U - 16 bit user-stack pointer
            return self.user_stack_pointer
        elif addr == 0x04: # 0100 - S - 16 bit system-stack pointer
            return self.stack_pointer
        elif addr == 0x05: # 0101 - PC - 16 bit program counter register
            return self.program_counter
        elif addr == 0x08: # 1000 - A - 8 bit accumulator
            return self.accumulator_a
        elif addr == 0x09: # 1001 - B - 8 bit accumulator
            return self.accumulator_b
        elif addr == 0x0a: # 1010 - CC - 8 bit condition code register as flags
            return self.status_as_byte()
        elif addr == 0x0b: # 1011 - DP - 8 bit direct page register
            return self.direct_page
        else:
            raise RuntimeError("Register %s doesn't exists!" % hex(addr))

    def set_register(self, addr, value):
        log.debug("set register %s to %s" % (hex(addr), hex(value)))
        if addr == 0x00: # 0000 - D - 16 bit concatenated reg.(A B)
            self.accumulator_a, self.accumulator_b = divmod(value, 256)
        elif addr == 0x01: # 0001 - X - 16 bit index register
            self.index_x = value
        elif addr == 0x02: # 0010 - Y - 16 bit index register
            self.index_y = value
        elif addr == 0x03: # 0011 - U - 16 bit user-stack pointer
            self.user_stack_pointer = value
        elif addr == 0x04: # 0100 - S - 16 bit system-stack pointer
            self.stack_pointer = value
        elif addr == 0x05: # 0101 - PC - 16 bit program counter register
            self.program_counter = value
        elif addr == 0x08: # 1000 - A - 8 bit accumulator
            self.accumulator_a = value
        elif addr == 0x09: # 1001 - B - 8 bit accumulator
            self.accumulator_b = value
        elif addr == 0x0a: # 1010 - CC - 8 bit condition code register as flags
            self.status_from_byte(value)
        elif addr == 0x0b: # 1011 - DP - 8 bit direct page register
            self.direct_page = value
        else:
            raise RuntimeError("Register %s doesn't exists!" % hex(addr))

    ####

    def reset(self):
        self.program_counter = self.read_word(self.RESET_VECTOR)

    def run(self, bus_port):
        global bus
        bus = socket.socket()
        bus.connect(("127.0.0.1", bus_port))

        assert self.cfg.bus != None

        while not self.quit:

            timeout = 0
            if not self.running:
                timeout = 1
            # Currently this handler blocks from the moment
            # a connection is accepted until the response
            # is sent. TODO: use an async HTTP server that
            # handles input data asynchronously.
            sockets = [self.control_server]
            rs, _, _ = select.select(sockets, [], [], timeout)
            for s in rs:
                if s is self.control_server:
                    self.control_server._handle_request_noblock()
                else:
                    pass

            count = 10
            while count > 0 and self.running:
                self.cycles += 2 # all instructions take this as a minimum
                op = self.read_pc_byte()
                try:
                    func = self.opcodes[op]
                except KeyError:
                    print "UNKNOWN OP %s (program counter: %s)" % (
                        hex(op), hex(self.program_counter - 1)
                    )
                    sys.exit()
                    break
                else:
                    func()
                count -= 1

    def test_run(self, start, end):
        self.program_counter = start
        while True:
            self.cycles += 2 # all instructions take this as a minimum
            if self.program_counter == end:
                break
            op = self.read_pc_byte()
            try:
                func = self.opcodes[op]
            except KeyError:
                print "UNKNOWN OP %s (program counter: %s)" % (
                    hex(op), hex(self.program_counter - 1)
                )
                break
            else:
                func()

    ####

    def get_pc(self, inc=1):
        pc = self.program_counter
        self.program_counter += inc
        return pc

    def read_byte(self, address):
        return self.memory.read_byte(self.cycles, address)

    def read_word(self, address):
        return self.memory.read_word(self.cycles, address)

    def read_pc_byte(self):
        return self.read_byte(self.get_pc())

    def read_pc_word(self):
        return self.read_word(self.get_pc(2))

    def write_byte(self, address, value):
        self.memory.write_byte(self.cycles, address, value)

    ####

    def push_byte(self, byte):
        self.write_byte(self.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100

    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.read_byte(self.STACK_PAGE + self.stack_pointer)

    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)

    def pull_word(self):
        s = self.STACK_PAGE + self.stack_pointer + 1
        self.stack_pointer += 2
        return self.read_word(s)

    ####

    @opcode(0x1f)
    def TFR(self):
        """
        Transfer Register to Register
        Addressing Mode: Immediate
        """
        post_byte = self.read_pc_byte()
        high, low = divmod(post_byte, 16)
        log.debug("TFR: post byte: %s high: %s low: %s" % (hex(post_byte), hex(high), hex(low)))
        # TODO: check if source and dest has the same size
        source = self.get_register(high)
        self.set_register(low, source)







if __name__ == "__main__":
    cli = DragonPyCLI()
    cfg = cli.get_cfg()

    if cfg.bus is None:
        import subprocess
        subprocess.Popen([sys.executable, "DragonPy_CLI.py"]).wait()
        sys.exit(0)
        print "DragonPy cpu core"
        print "Run DragonPy_CLI.py instead"
        sys.exit(0)

    print "Use bus port:", repr(cfg.bus)

    mem = Memory(cfg)
    cpu = CPU(cfg, mem)
    cpu.run(cfg.bus)
