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


import BaseHTTPServer
import inspect
import json
import logging
import os
import pprint
import re
import select
import socket
import struct
import sys

from Dragon32_mem_info import DragonMemInfo, print_out
from DragonPy_CLI import DragonPyCLI
from MC6809data import MC6809_data_raw as MC6809data
from MC6809data.MC6809_skeleton import CPU6809Skeleton
from cpu_utils.MC6809_registers import ValueStorage8Bit, ConcatenatedAccumulator, \
    ValueStorage16Bit, ConditionCodeRegister

log = logging.getLogger("DragonPy")

MC6809OP_DATA_DICT = dict(
    [(op["opcode"], op)for op in MC6809data.OP_DATA]
)


bus = None # socket for bus I/O
ILLEGAL_OPS = (
    0x1, 0x2, 0x5, 0xb,
    0x14, 0x15, 0x18, 0x1b,
    0x38,
    0x41, 0x42, 0x45, 0x4b, 0x4e,
    0x51, 0x52, 0x55, 0x5b, 0x5e,
    0x61, 0x62, 0x65, 0x6b,
    0x71, 0x72, 0x75, 0x7b,
    0x87, 0x8f,
    0xc7, 0xcd, 0xcf
)


def signed5(x):
    """ convert to signed 5-bit """
    if x > 0xf: # 0xf == 2**4-1 == 15
        x = x - 0x20 # 0x20 == 2**5 == 32
    return x

def signed8(x):
    """ convert to signed 8-bit """
    if x > 0x7f: # 0x7f ==  2**7-1 == 127
        x = x - 0x100 # 0x100 == 2**8 == 256
    return x

def signed16(x):
    """ convert to signed 16-bit """
    if x > 0x7fff: # 0x7fff ==  2**15-1 == 32767
        x = x - 0x10000 # 0x100 == 2**16 == 65536
    return x


def byte2bit_string(data):
    return '{0:08b}'.format(data)


def opcode(*opcodes):
    """A decorator for opcodes"""
    def decorator(func):
        setattr(func, "_is_opcode", True)
        setattr(func, "_opcodes", opcodes)
        return func
    return decorator


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
        log.debug("Read %sBytes from %s into ROM %s-%s" % (
            offset, filename, hex(address), hex(address + offset)
        ))

    def read_byte(self, address):
        assert self.start <= address <= self.end, "Read %s from %s is not in range %s-%s" % (hex(address), self.__class__.__name__, hex(self.start), hex(self.end))
        byte = self._mem[address - self.start]
#         log.debug("Read byte %s: %s" % (hex(address), hex(byte)))
#         self.cfg.mem_info(address, "read byte")
        return byte


class RAM(ROM):
    def write_byte(self, address, value):
        log.debug(" **** write $%x to $%x - mem info:" % (value, address))
        log.debug("      %s" % self.cfg.mem_info.get_shortest(value))
        log.debug("      %s" % self.cfg.mem_info.get_shortest(address))
        self._mem[address] = value


class Memory(object):
    def __init__(self, cpu, cfg, use_bus=True):
        self.cpu = cpu
        self.cfg = cfg
        self.use_bus = use_bus

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
        if address < self.cfg.RAM_END:
            return self.ram.read_byte(address)
        elif self.cfg.ROM_START <= address <= self.cfg.ROM_END:
            return self.rom.read_byte(address)
        else:
            return self.bus_read(address)

    def read_word(self, address):
        # 6809 is Big-Endian
        return self.read_byte(address + 1) + (self.read_byte(address) << 8)

    def write_byte(self, address, value):
        self.cpu.cycles += 1
        if 0x400 <= address < 0x600:
            # FIXME: to default text screen
            log.debug(" **** write $%x to text screen address $%x" % (value, address))
            return

        if address < self.cfg.RAM_END:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(address, value)

    def bus_read(self, address):
#         self.cpu.cycles += 1 # ???
        if not self.use_bus:
            return 0
        op = struct.pack("<IBHB", self.cpu.cycles, 0, address, 0)
        try:
            bus.send(op)
            b = bus.recv(1)
            if len(b) == 0:
                sys.exit(0)
            return ord(b)
        except socket.error:
            sys.exit(0)

    def bus_write(self, address, value):
#         self.cpu.cycles += 1 # ???
        if not self.use_bus:
            return
        op = struct.pack("<IBHB", self.cpu.cycles, 1, address, value)
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
            "flag_V",
            "break_flag",
            "decimal_mode_flag",
            "interrupt_disable_flag",
            "flag_Z",
            "flag_C",
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


class Instruction(object):
    def __init__(self, instr_func, cycles, addr_func, operand):
        self.instr_func = instr_func
        self.cycles = cycles
        self.addr_func = addr_func
        self.operand = operand


class CPU(CPU6809Skeleton):

    def __init__(self, cfg):
        self.cfg = cfg
        self.memory = Memory(self, cfg)

        if self.cfg.bus:
            self.control_server = BaseHTTPServer.HTTPServer(("127.0.0.1", 6809), ControlHandlerFactory(self))
        else:
            self.control_server = None

        self.index_x = ValueStorage16Bit("X", 0) # X - 16 bit index register
        self.index_y = ValueStorage16Bit("X", 0) # Y - 16 bit index register

        self.user_stack_pointer = ValueStorage16Bit("U", 0) # U - 16 bit user-stack pointer
        self.system_stack_pointer = ValueStorage16Bit("S", 0) # S - 16 bit system-stack pointer

        # PC - 16 bit program counter register
#         self.program_counter = ValueStorage16Bit("PC", -1)
        self._program_counter = ValueStorage16Bit("PC", 0x8000)
#         self.program_counter = ValueStorage16Bit("PC", 0xb3b4)
#         self.program_counter = ValueStorage16Bit("PC", 0xb3ba)

        self.accu_a = ValueStorage8Bit("A", 0) # A - 8 bit accumulator
        self.accu_b = ValueStorage8Bit("B", 0) # B - 8 bit accumulator

        # D - 16 bit concatenated reg. (A + B)
        self.accu_d = ConcatenatedAccumulator("D", self.accu_a, self.accu_b)

        # DP - 8 bit direct page register
        self.direct_page = ValueStorage8Bit("DP", 0)

        # 8 bit condition code register bits: E F H I N Z V C
        self.cc = ConditionCodeRegister()

        self.register_dict = {
            "X": self.index_x,
            "Y": self.index_y,

            "U": self.user_stack_pointer,
            "S": self.system_stack_pointer,

            "PC": self._program_counter,

            "A": self.accu_a,
            "B": self.accu_b,
            "D": self.accu_d,

            "DP": self.direct_page,
            "CC": self.cc,
        }

        self.cycles = 0

        log.debug("Add opcode functions:")
        self.opcode_dict = {}

        # Get the members not from class instance, so that's possible to
        # exclude properties without "activate" them.
        cls = type(self)
        for name, cls_method in inspect.getmembers(cls):
            if name.startswith("_") or isinstance(cls_method, property):
                continue

            try:
                opcodes = getattr(cls_method, "_opcodes")
            except AttributeError:
                continue

            instr_func = getattr(self, name)
            self._add_ops(opcodes, instr_func)

        log.debug("illegal ops: %s" % ",".join(["$%x" % c for c in ILLEGAL_OPS]))
        # add illegal ops
        for illegal_ops in ILLEGAL_OPS:
            self.opcode_dict[illegal_ops] = self.illegal_op

#         self.reset()
#         if cfg.pc is not None:
#             self.program_counter = cfg.pc

        self.running = True
        self.quit = False

    ####

    def _add_ops(self, opcodes, instr_func):
        log.debug("%20s: %s" % (
            instr_func.__name__, ",".join(["$%x" % c for c in opcodes])
        ))
        for opcode in opcodes:
            assert opcode not in self.opcode_dict, \
                "Opcode $%x (%s) defined more then one time!" % (
                    opcode, instr_func.__name__
            )

            try:
                opcode_data = MC6809OP_DATA_DICT[opcode]
            except IndexError:
                log.error("ERROR: no OP_DATA entry for $%x" % opcode)
                continue

            operand_txt = opcode_data["operand"]
            if operand_txt is None:
                operand = None
            else:
                operand = self.register_dict[operand_txt]

            addr_mode_id = opcode_data["addr_mode"]
            opcode_bytes = opcode_data["bytes"]

            if addr_mode_id == MC6809data.IMMEDIATE:
                if opcode_bytes == 2:
                    addr_func = self.immediate_byte
                else:
                    addr_func = self.immediate_word
            else:
                addr_func_name = MC6809data.ADDRES_MODE_DICT[addr_mode_id]
                if addr_func_name == MC6809data.INHERENT:
                    addr_func = None
                else:
                    addr_func = getattr(self, addr_func_name.lower())

#             log.debug("op code $%x data:" % opcode)
#             log.debug(pprint.pformat(opcode_data))
            self.opcode_dict[opcode] = Instruction(
                instr_func=instr_func,
                cycles=opcode_data["cycles"],
                addr_func=addr_func,
                operand=operand,
            )

    ####

    REGISTER_BIT2STR = {
        0x00: "D", # 0000 - 16 bit concatenated reg.(A B)
        0x01: "X", # 0001 - 16 bit index register
        0x02: "Y", # 0010 - 16 bit index register
        0x03: "U", # 0011 - 16 bit user-stack pointer
        0x04: "S", # 0100 - 16 bit system-stack pointer
        0x05: "PC", # 0101 - 16 bit program counter register
        0x08: "A", # 1000 - 8 bit accumulator
        0x09: "B", # 1001 - 8 bit accumulator
        0x0a: "CC", # 1010 - 8 bit condition code register as flags
        0x0b: "DP", # 1011 - 8 bit direct page register
    }

    def _get_register_obj(self, addr):
        addr_str = self.REGISTER_BIT2STR[addr]
        return self.register_dict[addr_str]

    def get_register(self, addr):
        log.debug("get register value from %s" % hex(addr))
        reg_obj = self._get_register_obj(addr)
        return reg_obj.get()

    def set_register(self, addr, value):
        log.debug("set register %s to %s" % (hex(addr), hex(value)))
        reg_obj = self._get_register_obj(addr)
        return reg_obj.set(value)

    ####

    def reset(self):
        pc = self.read_word(self.cfg.RESET_VECTOR)
        log.debug("$%x CPU reset: read word from $%x set pc to %s" % (
            self.program_counter, self.cfg.RESET_VECTOR,
            self.cfg.mem_info.get_shortest(pc)
        ))
        self.program_counter = pc - 1

    same_op_count = 0
    last_op_code = None
    def call_instruction(self):
        opcode = self.read_pc_byte()
        try:
            instruction = self.opcode_dict[opcode]
        except KeyError:
            msg = "$%x *** UNKNOWN OP $%x" % (self.program_counter - 1, self.opcode)
            log.error(msg)
            sys.exit(msg)

        func_kwargs = {"opcode": opcode}

        unbound_addr_method = instruction.addr_func
        if unbound_addr_method is not None:
#             log.debug("unbound_addr_method: %s" % repr(unbound_addr_method))
            func_kwargs["ea"] = unbound_addr_method()
#             log.debug("ea: %s" % repr(ea))

        if instruction.operand is not None:
            func_kwargs["operand"] = instruction.operand

        if opcode == self.last_op_code:
            self.same_op_count += 1
        elif self.same_op_count == 0:
            log.debug("$%x *** new op code: $%x '%s' kwargs: %s" % (
                self.program_counter - 1, opcode, instruction.instr_func.__name__,
                repr(func_kwargs),
            ))
            log.debug(pprint.pformat(instruction))
        else:
            opcode_data = MC6809OP_DATA_DICT[opcode]
            log.debug("$%x *** last op code %s count: %s - new op code: $%x (%s -> %s)" % (
                self.program_counter - 1, self.last_op_code, self.same_op_count,
                opcode, opcode_data["mnemonic"], instruction.instr_func.__name__
            ))
            self.same_op_count = 0

        self.last_op_code = opcode

        log.debug("kwargs: %s" % repr(func_kwargs))

        instruction.instr_func(**func_kwargs)
        self.cycles += instruction.cycles

    def run(self, bus_port):
        global bus
        bus = socket.socket()
        bus.connect(("127.0.0.1", bus_port))

        assert self.cfg.bus != None

        last_op_code = None
        same_op_count = 0

#         while not self.quit:
#         for x in xrange(10):
        for x in xrange(100):
#         for x in xrange(1000):
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

#             for count in xrange(10):
#             for count in xrange(100):
            for count in xrange(1000):
                if not self.running:
                    break

                self.call_instruction()

    def test_run(self, start, end):
        self.program_counter = start
        while True:
            if self.program_counter == end:
                break
            self.call_instruction()

    def illegal_op(self):
        self.program_counter -= 1
        op = self.read_pc_byte()
        log.error("$%x +++ Illegal op code: $%x" % (
            self.program_counter - 1, op
        ))

    ####

    def get_CC(self):
        """ 8 bit condition code register bits: E F H I N Z V C """
        self.cc.status_as_byte()

    def get_X(self):
        """ return X - 16 bit index register """
        return self.index_x

    def get_Y(self):
        """ return Y - 16 bit index register """
        return self.index_y

    def get_U(self):
        """ return U - 16 bit user-stack pointer """
        return self.user_stack_pointer

    def get_S(self):
        """ return S - 16 bit system-stack pointer """
        return self.stack_pointer

    def get_V(self):
        """ return V - 16 bit variable inter-register """
        return self.value_register

    def read_pc_byte(self):
        pc = self.get_pc()
        value = self.memory.read_byte(pc)
        log.debug("$%x read pc byte: $%x" % (pc, value))
        return value

    def read_pc_word(self):
        return self.memory.read_word(self.get_pc(2))

    ####

    def _get_program_counter(self):
        return self._program_counter.get()
    def _set_program_counter(self, value):
        self._program_counter.set(value)
    program_counter = property(_get_program_counter, _set_program_counter)

    def get_pc(self, inc=1):
        pc = self.program_counter
        self.program_counter += inc
#         log.debug(" ++++ inc pc: $%x + %i = $%x" % (pc, inc, self.program_counter))
        return pc

    def push_byte(self, byte):
        self.memory.write_byte(self.cfg.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100

    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.read_byte(self.cfg.STACK_PAGE + self.stack_pointer)

    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)

    def pull_word(self):
        s = self.cfg.STACK_PAGE + self.stack_pointer + 1
        self.stack_pointer += 2
        return self.read_word(s)

    ####

    def immediate_byte(self):
        value = self.read_pc_byte()
        log.debug("$%x addressing 'immediate byte' value: $%x \t| %s" % (
            self.program_counter, value, self.cfg.mem_info.get_shortest(self.program_counter)
        ))
        return value

    def immediate_word(self):
        value = self.read_pc_word()
        log.debug("$%x addressing 'immediate word' value: $%x \t| %s" % (
            self.program_counter, value, self.cfg.mem_info.get_shortest(self.program_counter)
        ))
        return value

    def direct(self):
        value = self.read_pc_byte()
        ea = self.direct_page << 8 | value
        log.debug("$%x addressing 'direct' value: $%x << 8 | $%x = $%x \t| %s" % (
            self.program_counter,
            self.direct_page, value, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        return ea

    INDEX_POSTBYTE2STR = {
        0x00: "X", # 16 bit index register
        0x01: "Y", # 16 bit index register
        0x02: "U", # 16 bit user-stack pointer
        0x03: "S", # 16 bit system-stack pointer
    }
    def indexed(self):
        """
        Calculate the address for all indexed addressing modes
        """
        postbyte = self.read_pc_byte()
        log.debug("$%x addressing 'indexed' with postbyte: $%x == %s" % (
            self.program_counter, postbyte, byte2bit_string(postbyte)
        ))

        rr = (postbyte >> 5) & 3
        try:
            register_str = self.INDEX_POSTBYTE2STR[rr]
        except KeyError:
            raise RuntimeError("Register $%x doesn't exists! (postbyte: $%x)" % (rr, postbyte))

        register_obj = self.register_dict[register_str]
        register_value = register_obj.get()

        if (postbyte & 0x80) == 0: # bit 7 == 0
            # EA = n, R - use 5-bit offset from post-byte
            return register_value + signed5(postbyte) # FIXME: cutout only the 5bits from post byte?

        indirect = postbyte & 0x10 == 1 # bit 4 is 1 -> Indirect

        addr_mode = postbyte & 0x0f
        self.cycles += 1
        if addr_mode == 0x0: # 0000 0x0 | ,R+ | increment by 1
            ea = register_value + 1
        elif addr_mode == 0x1: # 0001 0x1 | ,R++ | increment by 2
            ea = register_value + 2
            self.cycles += 1
        elif addr_mode == 0x2: # 0010 0x2 | ,R- | decrement by 1
            ea = register_value - 1
        elif addr_mode == 0x3: # 0011 0x3 | ,R-- | decrement by 2
            ea = register_value - 2
            self.cycles += 1
        elif addr_mode == 0x4: # 0100 0x4 | ,R | No offset
            ea = register_value
        elif addr_mode == 0x5: # 0101 0x5 | B, R | B register offset
            ea = register_value + signed8(self.accu.B)
        elif addr_mode == 0x6: # 0110 0x6 | A, R | A register offset
            ea = register_value + signed8(self.accu.A)
        elif addr_mode == 0x8: # 1000 0x8 | n, R | 8 bit offset
            ea = register_value + signed8(self.read_pc_byte())
        elif addr_mode == 0x9: # 1001 0x9 | n, R | 16 bit offset
            ea = register_value + signed16(self.read_pc_word()) # FIXME: signed16() ok?
            self.cycles += 1

#         elif addr_mode == 0xa: # 1010 0xa | FIXME: illegal???
#             ea = self.program_counter | 0xff

        elif addr_mode == 0xb: # 1011 0xb | D, R | D register offset
            # D - 16 bit concatenated reg. (A + B)
            ea = register_value + signed16(self.accu.D) # FIXME: signed16() ok?
            self.cycles += 1
        elif addr_mode == 0xc: # 1100 0xc | n, PCR | 8 bit offset from program counter
            ea = signed8(self.read_pc_byte()) + self.program_counter
        elif addr_mode == 0xd: # 1101 0xd | n, PCR | 16 bit offset from program counter
            ea = self.read_pc_word() + self.program_counter # FIXME: use signed16() here?
            self.cycles += 1
        elif addr_mode == 0xf and indirect: # 1111 0xf | [n] | 16 bit address - extended indirect
            ea = self.read_pc_word()
        else:
            raise RuntimeError("Illegal indexed addressing mode: $%x" % addr_mode)

        if indirect: # bit 4 is 1 -> Indirect
            tmp_ea = self.read_pc_byte()
            tmp_ea = tmp_ea << 8
            ea = tmp_ea | self.read_byte(ea + 1)

        log.debug("$%x indexed addressing mode ea=$%x \t| %s" % (
            self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
        ))
        return ea

    def extended(self):
        """
        extended indirect addressing mode takes a 2-byte value from post-bytes
        """
        value = self.read_pc_word()
        log.debug("$%x addressing 'extended indirect' value: $%x \t| %s" % (
            self.program_counter, value, self.cfg.mem_info.get_shortest(value)
        ))
        return value

    def relative(self):
        raise NotImplementedError

    def variant(self):
        raise NotImplementedError

    #### Op methods:

    @opcode(# Complement accumulator or memory location
        0x3, 0x63, 0x73, # COM (direct, indexed, extended)
    )
    def instruction_COM(self, opcode, ea):
        """
        Replaces the contents of memory location M with
        its logical complement. When operating on unsigned values, only BEQ and
        BNE branches can be expected to behave properly following a COM
        instruction. When operating on twos complement values, all signed
        branches are available.

        source code forms: COM Q; COMA; COMB

        CC bits "HNZVC": -aa01
        """
        value = ea ^ -1
        log.debug("$%x COM $%x to $%x \t| %s" % (
            self.program_counter,
            ea, value,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.update_NZ01_8(value)
        self.memory.write_byte(ea, value)

    @opcode(# Complement accumulator or memory location
        0x43, # COMA (inherent)
        0x53, # COMB (inherent)
    )
    def instruction_COM_register(self, opcode, operand):
        """
        Replaces the contents of accumulator A or B with
        its logical complement. When operating on unsigned values, only BEQ and
        BNE branches can be expected to behave properly following a COM
        instruction. When operating on twos complement values, all signed
        branches are available.

        source code forms: COM Q; COMA; COMB

        CC bits "HNZVC": -aa01
        """
        old_value = operand.get()
        value = old_value ^ -1
        operand.set(value)
        log.debug("$%x COM %s from $%x to $%x \t| %s" % (
            self.program_counter,
            operand.name, old_value, value,
            self.cfg.mem_info.get_shortest(value)
        ))
        self.cc.update_NZ01_8(value)

    @opcode(# Jump
        0xe, 0x6e, 0x7e, # JMP (direct, indexed, extended)
    )
    def instruction_JMP(self, opcode, ea=None):
        """
        Program control is transferred to the effective address.

        source code forms: JMP EA

        CC bits "HNZVC": -----
        """
        log.debug("$%x JMP to $%x \t| %s" % (
            self.program_counter,
            ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.program_counter = ea

    @opcode(# Load stack pointer from memory
        0xcc, 0xdc, 0xec, 0xfc, # LDD (immediate, direct, indexed, extended)
        0x10ce, 0x10de, 0x10ee, 0x10fe, # LDS (immediate, direct, indexed, extended)
        0xce, 0xde, 0xee, 0xfe, # LDU (immediate, direct, indexed, extended)
        0x8e, 0x9e, 0xae, 0xbe, # LDX (immediate, direct, indexed, extended)
        0x108e, 0x109e, 0x10ae, 0x10be, # LDY (immediate, direct, indexed, extended)
    )
    def instruction_LD16(self, opcode, ea=None, operand=None):
        """
        Load the contents of the memory location M:M+1 into the designated
        16-bit register.

        source code forms: LDD P; LDX P; LDY P; LDS P; LDU P

        CC bits "HNZVC": -aa0-
        """
        log.debug("$%x LD16 set %s to $%x \t| %s" % (
            self.program_counter,
            operand.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        operand.set(ea)
        self.cc.update_NZ0_16(ea)

    @opcode(# Store accumulator to memroy
        0x97, 0xa7, 0xb7, # STA (direct, indexed, extended)
        0xd7, 0xe7, 0xf7, # STB (direct, indexed, extended)
    )
    def instruction_ST8(self, opcode, ea=None, operand=None):
        """
        Writes the contents of an 8-bit register into a memory location.

        source code forms: STA P; STB P

        CC bits "HNZVC": -aa0-
        """
        value = operand.get()

#         ea = self.get_ea16(op)
        log.debug("$%x ST8 store value $%x from %s at $%x \t| %s" % (
            self.program_counter,
            value, operand.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.update_NZ0_8(ea)
        self.memory.write_byte(ea, value)

class OLD:
    @opcode(0x26)
    def BNE(self):
        new_pc = self.program_counter + 2

        if self.cc.Z == 0:
            new_pc += self.read_pc_byte()

        log.debug("$%x BNE: set pc to $%x \t| %s" % (
                self.program_counter,
                new_pc,
                self.cfg.mem_info.get_shortest(new_pc)
        ))
        self.program_counter = new_pc

    @opcode(0x6f)
    def CLR_indexed(self):
        """
        CLeaR
        Number of Program Bytes: 2+
        """
        self.cycles += 6
        addr = self.indexed()
        self.memory.write_byte(addr, 0x0)
        self.cc.N = 0
        self.cc.Z = 1
        self.cc.V = 0
        self.cc.C = 0

    @opcode(0xbc)
    def CMPX_extended(self):
        """
        CoMPare with X index
        """
        self.cycles += 7
        value = self.extended
        log.debug("$%x CMPX extended - set index X to $%x ($%x - $%s) |" % (
            self.program_counter,
        ))

        result = self.index_x - value

        self.cfg.mem_info(self.program_counter,
            "$%x CMPX extended - $%x (index X) - $%x (post word) = $%x | update NZVC with $%x |" % (
                self.program_counter, self.index_x, value, result, result
        ))

#         self.cc.C = 1 if (result >= 0) else 0
        self.cc.update_nzvc(result)
#         log.debug("%s - 0xbc CMPX extended: %s - %s = %s (Set C to %s)" % (
#             self.program_counter, hex(self.index_x), hex(value), hex(result), self.cc.C
#         ))

    @opcode([
        0x43, # COMA
        0x53, # COMB
        0x03, 0x63, 0x73 # COM
    ])
    def COM(self):
        """
        COMplement
        COM Q; COMA; COMB
        """
        self.cycles += 6
        op = self.opcode
        reg_type = (op >> 4) & 0xf
        func = {
            0x0: self.direct,
            0x4: self.accu.get_A,
            0x5: self.accu.get_B,
            0x6: self.indexed,
            0x7: self.extended,
        }[reg_type]
        ea = func()

        value = ea ^ -1
        log.debug("$%x COM %s $%x to $%x \t| %s" % (
            self.program_counter,
            func.__name__, ea, value,
            self.cfg.mem_info.get_shortest(value)
        ))
        self.memory.write_byte(ea, value)
        self.cc.set_NZ8(value)
        self.cc.V = 0
        self.cc.C = 1


    @opcode(0xbd)
    def JSR_extended(self):
        """
        Jump to SubRoutine
        Addressing Mode: extended
        """
        self.cycles += 8
        addr = self.extended
        self.push_word(self.program_counter - 1)
        self.program_counter = addr
        log.debug("$%x JSR extended: push %s to stack and jump to %s" % (
            self.program_counter, hex(self.program_counter - 1), hex(addr)
        ))

    @opcode(0x30)
    def LEAX_indexed(self):
        """
        Load Effective Address from index X
        Number of Program Bytes: 4+
        """
        self.cycles += 2 # Number of MPU Cycles
        ea = self.indexed()
        self.index_x = ea
        self.cfg.mem_info(self.program_counter,
            "$%x LEAX indexed: set $%x to index X |" % (
                self.program_counter, ea
        ))

    @opcode(0x74)
    def LSR_extended(self):
        """
        Logical Shift Right
        """
        self.cycles += 7
        m = self.extended
        result = m >> 1
        self.cc.N = 0
        self.cc.Z = 0
        self.cc.C = m & 1
        address = self.program_counter - 2
        log.debug("$%x LSR extended source $%x %s shifted to $%x %s (carry %i) write to $%x \t| %s" % (
            self.program_counter,
            m, byte2bit_string(m), result, byte2bit_string(result), self.cc.C, address,
            self.cfg.mem_info.get_shortest(address)
        ))
        self.memory.write_byte(address, result)

    @opcode([
        0x40, # NEGA
        0x50, # NEGB
        0x00, 0x60, 0x70 # NEG
    ])
    def NEG(self):
        """
        Negate (Twos Complement) a Byte in Memory
        Number of Program Bytes: 2
        Addressing Mode: direct
        """
        self.cycles += 6
        reg_type = divmod(self.opcode, 16)[0]
        reg_dict = {
            0x0: self.direct,
            0x4: "accu.A",
            0x5: "accu.B",
            0x6: self.indexed,
            0x7: self.extended,
        }
        ea, txt = reg_dict[reg_type]

        log.debug("$%x NEG %s $%x \t| %s" % (
            self.program_counter,
            txt, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        value = -ea
        self.cc.set_NZVC8(0, ea, value)

        if reg_type == 0x4:
            self.accu.A = value
        elif reg_type == 0x5:
            self.accu.B = value
        else:
            self.memory.write_byte(ea, value)

    @opcode(0x1f)
    def TFR(self):
        """
        TransFeR Register to Register
        Number of Program Bytes: 2
        Copies data in register r1 to another register r2 of the same size.
        Addressing Mode: immediate register numbers
        """
        self.cycles += 7
        post_byte = self.immediate_byte
        high, low = divmod(post_byte, 16)
        log.debug("$%x TFR: post byte: %s high: %s low: %s" % (
            self.program_counter, hex(post_byte), hex(high), hex(low)
        ))
        # TODO: check if source and dest has the same size
        source = self.get_register(high)
        self.set_register(low, source)

    #### 8-bit arithmetic operations

    def ADD8(self, a, b):
        value = a + b
        self.cc.set_NZVC8(a, b, value)
        return value

    def SUB8(self, a, b):
        value = a - b
        self.cc.set_NZVC8(a, b, value)
        return value

    def AND8(self, a, b):
        value = a & b
        self.cc.set_NZVC8(a, b, value)
        return value

    def OR8(self, a, b):
        value = a | b
        self.cc.set_NZVC8(a, b, value)
        return value

    @opcode(0xbb)
    def ADDA_extended(self):
        """
        A = A + M
        """
        self.cycles += 5
        m = self.extended()
        value = self.ADD8(self.accu.A, m)
        log.debug("$%x ADDA extended: set A to $%x ($%x + $%x) \t| %s" % (
            self.program_counter, value, self.accu.A, m,
            self.cfg.mem_info.get_shortest(m)
        ))
        self.accu.A = value

    @opcode(0x84)
    def ANDA_immediate(self):
        """
        A = A & M
        """
        self.cycles += 2 # Number of MPU Cycles
        m = self.immediate_byte()
        value = self.ADD8(self.accu.A, m)
        log.debug("$%x ADDA extended: set A to $%x ($%x & $%x) \t| %s" % (
            self.program_counter, value, self.accu.A, m,
            self.cfg.mem_info.get_shortest(m)
        ))
        self.accu.A = value

    @opcode(0xba)
    def ORA_extended(self):
        """
        A = A || M
        Number of Program Bytes: 2
        """
        self.cycles += 2
        m = self.extended()
        value = self.OR8(self.accu.A, m)
        log.debug("$%x ORA extended: set A to $%x ($%x | $%x) \t| %s" % (
            self.program_counter, value, self.accu.A, m,
            self.cfg.mem_info.get_shortest(m)
        ))
        self.accu.A = value

    @opcode(0x80)
    def SUBA_immediate(self):
        """
        A = A - M
        Number of Program Bytes: 2
        """
        self.cycles += 2 # Number of MPU Cycles
        m = self.immediate_word()
        value = self.SUB8(self.accu.A, m)
        log.debug("$%x ORA extended: set A to $%x ($%x - $%x) \t| %s" % (
            self.program_counter, value, self.accu.A, m,
            self.cfg.mem_info.get_shortest(m)
        ))
        self.accu.A = value

    ####

    def get_ea16(self, op):
        access_type = (op >> 4) & 3
        func = {
            0x00: self.immediate_word,
            0x01: self.direct,
            0x02: self.indexed,
            0x03: self.extended,
        }[access_type]
        ea = func()
        log.debug("$%x get_ea16(): ea: $%x accessed by %s (op:$%x) \t| %s" % (
            self.program_counter,
            ea, func.__name__, op,
            self.cfg.mem_info.get_shortest(ea)
        ))
        return ea

    ####

    @opcode([
        0x9f, 0xaf, 0xbf, # STX
        0xdd, 0xed, 0xfd, # STD
        0xdf, 0xef, 0xff, # STU
    ])
    def ST16(self):
        """ ST 16-bit store register into memory """
        self.cycles += 5
        op = self.opcode
        ea = self.get_ea16(op)

        reg_type = op & 0x42
        func = {
            0x02: self.get_X, # X - 16 bit index register
            0x40: self.accu.get_D, # D - 16 bit concatenated reg. (A + B)
            0x42: self.get_U # U - 16 bit user-stack pointer
        }[reg_type]
        r = func()

        log.debug("$%x ST16 store $%x (reg. %s) to $%x \t| %s" % (
            self.program_counter,
            r, r.__name__, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.memory.write_byte(ea, r)
        self.cc.set_NZV16(r)

    @opcode([
        0x86, 0x96, 0xa6, 0xb6, # LDA
        0xc6, 0xd6, 0xe6, 0xf6, # LDB
    ])
    def LD8(self):
        """ LD 8-bit load register from memory
        case 0x6: tmp1 = op_ld(cpu, 0, tmp2); break; // LDA, LDB
        """
        self.cycles += 5
        op = self.opcode
        ea = self.get_ea16(op)

        self.cc.set_NZC8(ea)

        if not op & 0x40:
            self.accu.A = ea
        else:
            self.accu.B = ea






if __name__ == "__main__":
    cli = DragonPyCLI()
    cfg = cli.get_cfg()

    if cfg.bus is None:
        import subprocess
        subprocess.Popen([sys.executable,
            "DragonPy_CLI.py",
            "--verbosity=5",
#             "--verbosity=50",
        ]).wait()
        sys.exit(0)
        print "DragonPy cpu core"
        print "Run DragonPy_CLI.py instead"
        sys.exit(0)

    log.debug("Use bus port: %s" % repr(cfg.bus))

    cpu = CPU(cfg)
    cpu.run(cfg.bus)
