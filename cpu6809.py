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
import re
import select
import socket
import sys
import time

from DragonPy_CLI import DragonPyCLI
from MC6809data import MC6809_data_raw as MC6809data
from MC6809data.MC6809_data_raw import ILLEGAL_OPS, MEM_ACCESS_BYTE, \
    MEM_ACCESS_WORD, REG_A, REG_PC, REG_S, REG_B, REG_U, REG_D, REG_Y, \
    REG_X, REG_CC, REG_DP
from components.memory import Memory
from cpu_utils.MC6809_registers import ValueStorage8Bit, ConcatenatedAccumulator, \
    ValueStorage16Bit, ConditionCodeRegister, unsigned8, cc_value2txt
from utils.simple_debugger import print_exc_plus


log = logging.getLogger("DragonPy")

MC6809OP_DATA_DICT = dict(
    [(op["opcode"], op)for op in MC6809data.OP_DATA]
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


def hex_repr(d):
    txt = []
    for k, v in sorted(d.items()):
        if isinstance(v, int):
            txt.append("%s=$%x" % (k, v))
        else:
            txt.append("%s=%s" % (k, v))
    return " ".join(txt)


def opcode(*opcodes):
    """A decorator for opcodes"""
    def decorator(func):
        setattr(func, "_is_opcode", True)
        setattr(func, "_opcodes", opcodes)
        return func
    return decorator





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

import os
try:
    # FIXME: Hacked bugtracking...
    trace_file = open(os.path.expanduser(r"~/xroar_trace.txt"), "r")
except IOError, err:
    log.error("No trace file: %s" % err)
    sys.exc_clear() # clears all information relating this exception
    trace_file = None
else:
    trace_file.readline() # Skip reset line

class Instruction(object):
    def __init__(self, cpu, opcode, opcode_data, instr_func):
        self.cpu = cpu
        self.opcode = opcode
        self.data = opcode_data # dict entry from: MC6809OP_DATA_DICT
        self.instr_func = instr_func # unbound function for this op from cpu class

        self.static_kwargs = {
            "opcode": opcode
        }

        try:
            register_txt = opcode_data["register"]
        except KeyError:
            # instruction need no register access
            pass
        else:
            self.static_kwargs["register"] = cpu.register_str2object[register_txt]

        self.get_m_func = None
        self.get_ea_func = None

        addr_mode = opcode_data["addr_mode"]
        if addr_mode not in (MC6809data.INHERENT, MC6809data.VARIANT):
            func_name = "get_%s" % opcode_data["addr_mode"].lower()
            mem_read = opcode_data["mem_read"]
            if mem_read:
                # instruction used the memory content
                mem_access = opcode_data["mem_access"]
                if mem_access == MEM_ACCESS_BYTE:
                    func_name += "_byte"
                elif mem_access == MEM_ACCESS_WORD:
                    func_name += "_word"
                else:
                    raise ValueError(repr(mem_access))
                self.get_m_func = getattr(cpu, func_name)
            else:
                # instruction don't used the memory content
                func_name += "_ea"
                self.get_ea_func = getattr(cpu, func_name)

#         log.debug("op code $%x data: %s" % (opcode, repr(instr_kwargs)))
#         log.debug(pprint.pformat(opcode_data))
#         log.debug(repr(opcode_data))
#         log.debug(pprint.pformat(instr_kwargs))
#         log.debug("-"*79)

    def call_instr_func(self):
        op_kwargs = self.static_kwargs.copy()
        if self.get_ea_func is not None:
            op_kwargs["ea"] = self.get_ea_func()
        elif self.get_m_func is not None:
            op_kwargs["ea"], op_kwargs["m"] = self.get_m_func()

        if log.level <= logging.INFO:
            kwargs_info = []
            if "register" in op_kwargs:
                kwargs_info.append(str(op_kwargs["register"]))

            if "ea" in op_kwargs:
                kwargs_info.append("ea:%04x" % op_kwargs["ea"])

            if "m" in op_kwargs:
                kwargs_info.append("m:%x" % op_kwargs["m"])

#         log.info("CPU cycles: %i", self.cpu.cycles)

        try:
            self.instr_func(**op_kwargs)
        except Exception, err:
            # Display the op information log messages
            handler = logging.StreamHandler()
            handler.level = logging.DEBUG
            log.handlers = (handler,)
            log.info("Activate debug at $%x", self.cpu.last_op_address)

            # raise the error later, after op information log messages
            etype, evalue, etb = sys.exc_info()
            evalue = etype("%s\n   kwargs: %s" % (evalue, hex_repr(op_kwargs)))
        else:
            etype = None

        self.cpu.cycles += self.data["cycles"]

        if log.level <= logging.INFO:
            op_address = self.cpu.last_op_address

            msg = "%(op_address)04x| %(opcode)-4s %(mnemonic)-6s %(kwargs)-27s %(cpu)s | %(cc)s" % {
                "op_address": op_address,
                "opcode": "%02x" % self.opcode,
                "mnemonic": self.data["mnemonic"],
                "kwargs": " ".join(kwargs_info),
                "cpu": self.cpu.get_info,
                "cc": self.cpu.cc.get_info,
            }
            log.info(msg)

            if trace_file: # Hacked bugtracking...

                if self.opcode in (0x10, 0x11): # PAGE 1/2 instructions
                    return

                ref_line = trace_file.readline()
                if ref_line == "":
                    log.error("no XRoar log line (CPU cycles: %i)", self.cpu.cycles)
                    return

                ref_line = ref_line.strip()

                # Add CC register info, e.g.: .F.IN..C
                xroar_cc = int(ref_line[49:51], 16)
                xroar_cc = cc_value2txt(xroar_cc)
                ref_line = "%s | %s" % (ref_line, xroar_cc)
#                 log.info("%s | %s", ref_line, xroar_cc)
                log.info(ref_line)

                addr1 = msg.split("|", 1)[0]
                addr2 = ref_line.split("|", 1)[0]
                if addr1 != addr2:
                    log.info("trace: %s", ref_line)
                    log.info("own..: %s", msg)
                    log.error("Error in CPU cycles: %i", self.cpu.cycles)
                    log.error("address (%r != %r) not the same as trace reference!\n" % (
                        addr1, addr2
                    ))

                mnemonic1 = msg[11:18].strip()
                mnemonic2 = ref_line[18:24].strip()
                if mnemonic1 != mnemonic2:
                    log.info("trace: %s", ref_line)
                    log.info("own..: %s" , msg)
                    log.error("Error in CPU cycles: %i", self.cpu.cycles)
                    log.error("mnemonic (%r != %r) not the same as trace reference!\n" % (
                        mnemonic1, mnemonic2
                    ))

                registers1 = msg[52:95]
                registers2 = ref_line[52:95]
                if registers1 != registers2:
                    log.info("trace: %s" , ref_line)
                    log.info("own..: %s" , msg)
                    log.error("Error in CPU cycles: %i", self.cpu.cycles)
                    log.error("registers (%r != %r) not the same as trace reference!\n" % (
                        registers1, registers2
                    ))
                else:
                    cc1 = msg[98:106]
                    if cc1 != xroar_cc:
                        log.info("trace: %s" , ref_line)
                        log.info("own..: %s" , msg)
                        log.error("Error in CPU cycles: %i", self.cpu.cycles)
                        log.error("CC (%r != %r) not the same as trace reference!\n" % (
                            cc1, xroar_cc
                        ))

                log.debug("\t%s", repr(self.data))
            log.debug("-"*79)

        if etype is not None:
            # raise the error while calling instruction, above.
            raise etype, evalue, etb


class IllegalInstruction(object):
    def __init__(self, cpu, opcode):
        self.cpu = cpu
        self.opcode = opcode

    def call_instr_func(self):
        op_address = self.cpu.last_op_address
        log.error("$%x +++ Illegal op code: $%x", op_address, self.opcode)


class CPU(object):

    def __init__(self, cfg):
        self.cfg = cfg
        log.info("Use config: %s", cfg)

        if self.cfg.__class__.__name__ == "Simple6809Cfg":
            # FIXME: Hacked bugtracking only with Dragon 32
            global trace_file
            trace_file = None

        if self.cfg.area_debug is not None:
            self.area_debug_active = False
            log.warn(
                "Activate area debug: Set debug level to %i from $%x to $%x" % self.cfg.area_debug
            )

        if self.cfg.max_cpu_cycles is not None:
            log.warn(
                "--max set: Stop CPU after %i cycles" % self.cfg.max_cpu_cycles
            )

        self.memory = Memory(self, cfg)

        if not self.cfg.use_bus:
            self.control_server = None
        else:
            control_handler = ControlHandlerFactory(self)
            self.control_server = BaseHTTPServer.HTTPServer(
                ("127.0.0.1", 6809), control_handler
            )


        self.index_x = ValueStorage16Bit(REG_X, 0) # X - 16 bit index register
        self.index_y = ValueStorage16Bit(REG_Y, 0) # Y - 16 bit index register

        self.user_stack_pointer = ValueStorage16Bit(REG_U, 0) # U - 16 bit user-stack pointer
        self.user_stack_pointer.counter = 0

        # S - 16 bit system-stack pointer:
        # Position will be set by ROM code after detection of total installed RAM
        self._system_stack_pointer = ValueStorage16Bit(REG_S, 0)
        self._system_stack_pointer.counter = 0

        # PC - 16 bit program counter register
        self._program_counter = ValueStorage16Bit(REG_PC, self.cfg.RESET_VECTOR)

        self.accu_a = ValueStorage8Bit(REG_A, 0) # A - 8 bit accumulator
        self.accu_b = ValueStorage8Bit(REG_B, 0) # B - 8 bit accumulator

        # D - 16 bit concatenated reg. (A + B)
        self.accu_d = ConcatenatedAccumulator(REG_D, self.accu_a, self.accu_b)

        # DP - 8 bit direct page register
        self.direct_page = ValueStorage8Bit(REG_DP, 0)

        # 8 bit condition code register bits: E F H I N Z V C
        self.cc = ConditionCodeRegister()

        self.register_str2object = {
            REG_X: self.index_x,
            REG_Y: self.index_y,

            REG_U: self.user_stack_pointer,
            REG_S: self._system_stack_pointer,

            REG_PC: self._program_counter,

            REG_A: self.accu_a,
            REG_B: self.accu_b,
            REG_D: self.accu_d,

            REG_DP: self.direct_page,
            REG_CC: self.cc,
        }

        self.cycles = 0
        self.last_op_address = 0 # Store the current run opcode memory address

#         log.debug("Add opcode functions:")
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

#         log.debug("illegal ops: %s" % ",".join(["$%x" % c for c in ILLEGAL_OPS]))
        # add illegal instruction
        for opcode in ILLEGAL_OPS:
            self.opcode_dict[opcode] = IllegalInstruction(self, opcode)

        self.running = True
        self.quit = False

    ####

    def _add_ops(self, opcodes, instr_func):
#         log.debug("%20s: %s" % (
#             instr_func.__name__, ",".join(["$%x" % c for c in opcodes])
#         ))
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

            try:
                instruction = Instruction(self, opcode, opcode_data, instr_func)
            except Exception, err:
                print >> sys.stderr, "Error init instruction for $%x" % opcode
                print >> sys.stderr, "opcode data: %s" % repr(opcode_data)
                print >> sys.stderr, "instr_func: %s" % instr_func.__name__
                raise

            self.opcode_dict[opcode] = instruction

    ####

    REGISTER_BIT2STR = {
        0x00: REG_D, # 0000 - 16 bit concatenated reg.(A B)
        0x01: REG_X, # 0001 - 16 bit index register
        0x02: REG_Y, # 0010 - 16 bit index register
        0x03: REG_U, # 0011 - 16 bit user-stack pointer
        0x04: REG_S, # 0100 - 16 bit system-stack pointer
        0x05: REG_PC, # 0101 - 16 bit program counter register
        0x08: REG_A, # 1000 - 8 bit accumulator
        0x09: REG_B, # 1001 - 8 bit accumulator
        0x0a: REG_CC, # 1010 - 8 bit condition code register as flags
        0x0b: REG_DP, # 1011 - 8 bit direct page register
    }

    def _get_register_obj(self, addr):
        addr_str = self.REGISTER_BIT2STR[addr]
        reg_obj = self.register_str2object[addr_str]
#         log.debug("get register obj: addr: $%x addr_str: %s -> register: %s" % (
#             addr, addr_str, reg_obj.name
#         ))
#         log.debug(repr(self.register_str2object))
        return reg_obj

    def get_register(self, addr):
        reg_obj = self._get_register_obj(addr)
        value = reg_obj.get()
        log.debug("\tget register value $%x from %s ($%x)" % (value, reg_obj.name, addr))
        return value

    def set_register(self, addr, value):
        reg_obj = self._get_register_obj(addr)
        log.debug("\tset register %s ($%x) to $%x" % (reg_obj.name, addr, value))
        return reg_obj.set(value)

    ####

    def reset(self):
        log.debug("$%x CPU reset:" % self.program_counter)

        self.last_op_address = 0

        log.debug("\tset cc.F=1: FIRQ interrupt masked")
        self.cc.F = 1

        log.debug("\tset cc.I=1: IRQ interrupt masked")
        self.cc.I = 1

#         log.debug("\tset PC to $%x" % self.cfg.RESET_VECTOR)
#         self.program_counter = self.cfg.RESET_VECTOR

        log.debug("\tread word from $%x" % self.cfg.RESET_VECTOR)
        pc = self.memory.read_word(self.cfg.RESET_VECTOR)
        log.debug("\tset PC to $%x" % (pc))
        self.program_counter = pc


    def get_and_call_next_op(self):
        op_address, opcode = self.read_pc_byte()
        self.call_instruction_func(op_address, opcode)

    same_op_count = 0
    last_op_code = None
    def call_instruction_func(self, op_address, opcode):
        self.last_op_address = op_address
        try:
            instruction = self.opcode_dict[opcode]
        except KeyError:
            msg = "$%x *** UNKNOWN OP $%x" % (op_address, opcode)
            log.error(msg)
            sys.exit(msg)

        instruction.call_instr_func()

    @opcode(
        0x10, # PAGE1+ instructions
        0x11, # PAGE2+ instructions
    )
    def instruction_PAGE(self, opcode):
        """ call op from page 1 or 2 """
        op_address, opcode2 = self.read_pc_byte()
        paged_opcode = opcode * 256 + opcode2
        log.debug("$%x *** call paged opcode $%x" % (
            self.program_counter, paged_opcode
        ))
        self.call_instruction_func(op_address - 1, paged_opcode)

    def run(self):
        log.debug("-"*79)

        last_update = time.time()
        last_cycles = 0
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

#             for count in xrange(10):
            for count in xrange(100):
#             for count in xrange(1000):
                if not self.running:
                    break
                self.get_and_call_next_op()

            duration = time.time() - last_update
            if duration >= 1:
                count = self.cycles - last_cycles
                log.error("%.2f cycles/sec.", float(count / duration))
                last_cycles = self.cycles
                last_update = time.time()

            if self.cfg.max_cpu_cycles is not None \
                and self.cycles >= self.cfg.max_cpu_cycles:
                log.warn(
                    "Stop CPU after %i cycles" % self.cycles
                )
                self.quit = True

    def test_run(self, start, end):
        self.program_counter = start
        log.debug("-"*79)
        while True:
            if self.program_counter == end:
                break
            self.get_and_call_next_op()

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
        return self._system_stack_pointer

    def get_V(self):
        """ return V - 16 bit variable inter-register """
        return self.value_register

    @property
    def get_info(self):
        return "cc=%02x a=%02x b=%02x dp=%02x x=%04x y=%04x u=%04x s=%04x" % (
            self.cc.get(),
            self.accu_a.get(), self.accu_b.get(),
            self.direct_page.get(),
            self.index_x.get(), self.index_y.get(),
            self.user_stack_pointer.get(), self.system_stack_pointer
        )

    ####

    def _get_system_stack_pointer(self):
        return self._system_stack_pointer.get()
    system_stack_pointer = property(_get_system_stack_pointer)

    def push_byte(self, stack_pointer, byte):
        """ pushed a byte onto stack """
        stack_pointer.counter += 1 # for internal check

        # FIXME: self._system_stack_pointer -= 1
        stack_pointer.decrement(1)
        addr = stack_pointer.get()

        log.info("\tpush $%x to %s stack at $%x",
            byte, stack_pointer.name, addr
        )
        self.memory.write_byte(addr, byte)

    def pull_byte(self, stack_pointer):
        """ pulled a byte from stack """
        stack_pointer.counter -= 1 # for internal check
        assert stack_pointer.counter >= 0, "pulled more than pushed from stack %s" % stack_pointer.name

        addr = stack_pointer.get()
        byte = self.memory.read_byte(addr)
        log.info("\tpull $%x from %s stack at $%x",
            byte, stack_pointer.name, addr
        )

        # FIXME: self._system_stack_pointer += 1
        stack_pointer.increment(1)

        return byte

    def push_word(self, stack_pointer, word):
        # FIXME: hi/lo in the correct order?

        # FIXME: self._system_stack_pointer -= 2
        stack_pointer.decrement(2)

        addr = stack_pointer.get()
        log.info("\tpush word $%x to %s stack at $%x",
            word, stack_pointer.name, addr
        )

        self.memory.write_word(addr, word)

#         hi, lo = divmod(word, 0x100)
#         self.push_byte(hi)
#         self.push_byte(lo)

    def pull_word(self, stack_pointer):
        # FIXME: hi/lo in the correct order?
        addr = stack_pointer.get()
        word = self.memory.read_word(addr)
        log.info("\tpull word $%x from %s stack at $%x",
            word, stack_pointer.name, addr
        )
        # FIXME: self._system_stack_pointer += 2
        stack_pointer.increment(2)
        return word

    ####

    def _get_program_counter(self):
        return self._program_counter.get()

    def _set_program_counter(self, value):
        if self.cfg.area_debug is not None:
            # cfg.area_debug = (level, start, end)
            # TODO: make it workable with the other loggers
            if not self.area_debug_active:
                if value >= self.cfg.area_debug[1]: # start
                    self.area_debug_active = True
                    handler = logging.StreamHandler()
                    handler.level = self.cfg.area_debug[0] # FIXME: Doesn't work?!?!
                    log.handlers = (handler,)
#                     log.addHandler(handler)
                    log.info("Activate area debug at $%x", value)
            else:
                if value >= self.cfg.area_debug[2]: # end
                    log.info("Deactivate area debug at $%x", value)
                    self.area_debug_active = False
                    self.cfg.area_debug = None
#                     handler = log.handlers[-1]
#                     log.removeHandler(handler)
                    log.handlers = (logging.NullHandler(),)

        self._program_counter.set(value)
    program_counter = property(_get_program_counter, _set_program_counter)

    def read_pc_byte(self):
        op_addr = self.program_counter
        m = self.memory.read_byte(op_addr)
        self.program_counter += 1
        log.debug("\tread pc byte: $%02x from $%04x", m, op_addr)
        return op_addr, m

    def read_pc_word(self):
        op_addr = self.program_counter
        m = self.memory.read_word(op_addr)
        self.program_counter += 2
        log.debug("\tread pc word: $%04x from $%04x", m, op_addr)
        return op_addr, m

    ####

    def get_immediate_byte(self):
        ea, m = self.read_pc_byte()
        log.debug("\tget_immediate_byte(): ea=$%x m=$%x", ea, m)
        return ea, m

    def get_immediate_word(self):
        ea, m = self.read_pc_word()
        log.debug("\tget_immediate_word(): ea=$%x m=$%x", ea, m)
        return ea, m

    def get_direct_ea(self):
        op_addr, m = self.read_pc_byte()
        dp = self.direct_page.get()
        ea = dp << 8 | m
        log.debug("\tget_direct_ea(): ea = dp << 8 | m  =>  $%x=$%x<<8|$%x", ea, dp, m)
        return ea

    def get_direct_byte(self):
        ea = self.get_direct_ea()
        m = self.memory.read_byte(ea)
        log.debug("\tget_direct_byte(): ea=$%x m=$%x", ea, m)
        return ea, m

    def get_direct_word(self):
        ea = self.get_direct_ea()
        m = self.memory.read_word(ea)
        log.debug("\tget_direct_word(): ea=$%x m=$%x", ea, m)
        return ea, m

    INDEX_POSTBYTE2STR = {
        0x00: REG_X, # 16 bit index register
        0x01: REG_Y, # 16 bit index register
        0x02: REG_U, # 16 bit user-stack pointer
        0x03: REG_S, # 16 bit system-stack pointer
    }
    def get_indexed_ea(self):
        """
        Calculate the address for all indexed addressing modes
        """
        addr, postbyte = self.read_pc_byte()
        log.debug("\tget_indexed_ea(): postbyte: $%x (%s) from $%x",
            postbyte, byte2bit_string(postbyte), addr
        )

        rr = (postbyte >> 5) & 3
        try:
            register_str = self.INDEX_POSTBYTE2STR[rr]
        except KeyError:
            raise RuntimeError("Register $%x doesn't exists! (postbyte: $%x)" % (rr, postbyte))

        register_obj = self.register_str2object[register_str]
        register_value = register_obj.get()

        if (postbyte & 0x80) == 0: # bit 7 == 0
            # EA = n, R - use 5-bit offset from post-byte
            return register_value + signed5(postbyte) # FIXME: cutout only the 5bits from post byte?

        indirect = postbyte & 0x10 == 1 # bit 4 is 1 -> Indirect

        addr_mode = postbyte & 0x0f
        self.cycles += 1
        if addr_mode == 0x0: # 0000 0x0 | ,R+ | increment by 1
            ea = register_value
            register_obj.increment(1)
        elif addr_mode == 0x1: # 0001 0x1 | ,R++ | increment by 2
            ea = register_value
            register_obj.increment(2)
            self.cycles += 1
        elif addr_mode == 0x2: # 0010 0x2 | ,R- | decrement by 1
            ea = register_obj.decrement(1)
        elif addr_mode == 0x3: # 0011 0x3 | ,R-- | decrement by 2
            ea = register_obj.decrement(2)
            self.cycles += 1
        elif addr_mode == 0x4: # 0100 0x4 | ,R | No offset
            ea = register_value
        elif addr_mode == 0x5: # 0101 0x5 | B, R | B register offset
            ea = register_value + signed8(self.accu.B)
        elif addr_mode == 0x6: # 0110 0x6 | A, R | A register offset
            ea = register_value + signed8(self.accu.A)
        elif addr_mode == 0x8: # 1000 0x8 | n, R | 8 bit offset
            ea = register_value + signed8(self.read_pc_byte()[1])
        elif addr_mode == 0x9: # 1001 0x9 | n, R | 16 bit offset
            ea = register_value + signed16(self.read_pc_word()[1]) # FIXME: signed16() ok?
            self.cycles += 1

#         elif addr_mode == 0xa: # 1010 0xa | FIXME: illegal???
#             ea = self.program_counter | 0xff

        elif addr_mode == 0xb: # 1011 0xb | D, R | D register offset
            # D - 16 bit concatenated reg. (A + B)
            ea = register_value + signed16(self.accu.D) # FIXME: signed16() ok?
            self.cycles += 1
        elif addr_mode == 0xc: # 1100 0xc | n, PCR | 8 bit offset from program counter
            ea = signed8(self.read_pc_byte()[1]) + self.program_counter
        elif addr_mode == 0xd: # 1101 0xd | n, PCR | 16 bit offset from program counter
            ea = self.read_pc_word()[1] + self.program_counter # FIXME: use signed16() here?
            self.cycles += 1
        elif addr_mode == 0xf and indirect: # 1111 0xf | [n] | 16 bit address - extended indirect
            ea = self.read_pc_word()[1]
        else:
            raise RuntimeError("Illegal indexed addressing mode: $%x" % addr_mode)

        if indirect: # bit 4 is 1 -> Indirect
            tmp_ea = self.read_pc_byte()[1]
            tmp_ea = tmp_ea << 8
            ea = tmp_ea | self.read_byte(ea + 1)

        log.debug("\tget_indexed_ea(): ea=$%x", ea)
        return ea

    def get_indexed_byte(self):
        ea = self.get_indexed_ea()
        m = self.memory.read_byte(ea)
        log.debug("\tget_indexed_byte(): ea=$%x m=$%x", ea, m)
        return ea, m

    def get_indexed_word(self):
        ea = self.get_indexed_ea()
        m = self.memory.read_word(ea)
        log.debug("\tget_indexed_word(): ea=$%x m=$%x", ea, m)
        return ea, m

    def get_extended_ea(self):
        """
        extended indirect addressing mode takes a 2-byte value from post-bytes
        """
        attr, ea = self.read_pc_word()
        log.debug("\tget_extended_ea() ea=$%x from $%x", ea, attr)
        return ea

    def get_extended_byte(self):
        ea = self.get_extended_ea()
        m = self.memory.read_byte(ea)
        log.debug("$%x get 'extended' byte: ea = $%x m = $%x" % (
            self.program_counter, ea, m,
        ))
        return ea, m

    def get_extended_word(self):
        ea = self.get_extended_ea()
        m = self.memory.read_word(ea)
        log.debug("$%x get 'extended' word: ea = $%x m = $%x" % (
            self.program_counter, ea, m,
        ))
        return ea, m

    def get_relative_ea(self):
        addr, x = self.read_pc_byte()
        x = signed8(x)
        ea = self.program_counter + x
        log.debug("$%x addressing 'relative' ea = $%x + %i = $%x \t| %s" % (
            self.program_counter, self.program_counter, x, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        return ea

    def get_relative_byte(self):
        ea = self.get_relative_ea()
        m = self.memory.read_byte(ea)
        log.debug("$%x get 'relative' byte: ea = $%x m = $%x" % (
            self.program_counter, ea, m,
        ))
        return ea, m

    def get_relative_word(self):
        ea = self.get_relative_ea()
        m = self.memory.read_word(ea)
        log.debug("$%x get 'relative' word: ea = $%x m = $%x" % (
            self.program_counter, ea, m,
        ))
        return ea, m

    #### Op methods:

    @opcode(# Add B accumulator to X (unsigned)
        0x3a, # ABX (inherent)
    )
    def instruction_ABX(self, opcode):
        """
        Add the 8-bit unsigned value in accumulator B into index register X.

        source code forms: ABX

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x ABX" % opcode)

    @opcode(# Add memory to accumulator with carry
        0x89, 0x99, 0xa9, 0xb9, # ADCA (immediate, direct, indexed, extended)
        0xc9, 0xd9, 0xe9, 0xf9, # ADCB (immediate, direct, indexed, extended)
    )
    def instruction_ADC(self, opcode, ea, m, register):
        """
        Adds the contents of the C (carry) bit and the memory byte into an 8-bit
        accumulator.

        source code forms: ADCA P; ADCB P

        CC bits "HNZVC": aaaaa
        """
        a = register.get()
        r = a + m + self.cc.C
        log.debug("$%x %02x ADC %s: %i + %i + %i = %i (=$%x)" % (
            self.program_counter, opcode, register.name,
            a, m, self.cc.C, r, r
        ))
        self.cc.clear_HNZVC()
        self.cc.update_HNZVC_8(a, m, r)

    @opcode(# Add memory to D accumulator
        0xc3, 0xd3, 0xe3, 0xf3, # ADDD (immediate, direct, indexed, extended)
    )
    def instruction_ADD16(self, opcode, ea, m, register):
        """
        Adds the 16-bit memory value into the 16-bit accumulator

        source code forms: ADDD P

        CC bits "HNZVC": -aaaa
        """
        assert register.WIDTH == 16
        x1 = register.get()
#         x2 = signed8(x1)
        r1 = x1 + m
        r2 = unsigned8(r1)
        register.set(r2)
        log.debug("$%x %02x %02x ADD16 %s: %i + %i = %i (signed: %i)" % (
            self.program_counter, opcode, m,
            register.name,
            x1, m, r2, r1,
        ))
        self.cc.clear_NZVC()
        self.cc.update_NZVC_16(x1, m, r1)

    @opcode(# Add memory to accumulator
        0x8b, 0x9b, 0xab, 0xbb, # ADDA (immediate, direct, indexed, extended)
        0xcb, 0xdb, 0xeb, 0xfb, # ADDB (immediate, direct, indexed, extended)
    )
    def instruction_ADD8(self, opcode, ea, m, register):
        """
        Adds the memory byte into an 8-bit accumulator.

        source code forms: ADDA P; ADDB P

        CC bits "HNZVC": aaaaa
        """
        x1 = register.get()
#         x2 = signed8(x1)
        r1 = x1 + m
        r2 = unsigned8(r1)
        register.set(r2)
        log.debug("$%x %02x %02x ADD8 %s: %i + %i = %i (signed: %i)" % (
            self.program_counter, opcode, m,
            register.name,
            x1, m, r2, r1,
        ))
        self.cc.clear_HNZVC()
        self.cc.update_HNZVC_8(x1, m, r1)

    @opcode(# AND memory with accumulator
        0x84, 0x94, 0xa4, 0xb4, # ANDA (immediate, direct, indexed, extended)
        0xc4, 0xd4, 0xe4, 0xf4, # ANDB (immediate, direct, indexed, extended)
    )
    def instruction_AND(self, opcode, ea, m, register):
        """
        Performs the logical AND operation between the contents of an
        accumulator and the contents of memory location M and the result is
        stored in the accumulator.

        source code forms: ANDA P; ANDB P

        CC bits "HNZVC": -aa0-
        """
        a = register.get()
        r = a & m
        register.set(r)
        self.cc.update_NZ0_8(r)
        log.debug("$%x %02x AND %s: %i & %i = %i" % (
            self.program_counter, opcode,
            register.name,
            a, m, r
        ))

    @opcode(# AND condition code register
        0x1c, # ANDCC (immediate)
    )
    def instruction_ANDCC(self, opcode, ea, register):
        """
        Performs a logical AND between the condition code register and the
        immediate byte specified in the instruction and places the result in the
        condition code register.

        source code forms: ANDCC #xx

        CC bits "HNZVC": ddddd
        """
        raise NotImplementedError("$%x ANDCC" % opcode)
        # Update CC bits: ddddd

    @opcode(# Arithmetic shift of accumulator or memory right
        0x7, 0x67, 0x77, # ASR (direct, indexed, extended)
        0x47, # ASRA (inherent)
        0x57, # ASRB (inherent)
    )
    def instruction_ASR(self, opcode, ea, register):
        """
        Shifts all bits of the register one place to the right. Bit seven is held
        constant. Bit zero is shifted into the C (carry) bit.

        source code forms: ASR Q; ASRA; ASRB

        CC bits "HNZVC": uaa-s
        """
        raise NotImplementedError("$%x ASR" % opcode)
        # self.cc.update_NZC()

    @opcode(# Branch if equal
        0x27, # BEQ (relative)
        0x1027, # LBEQ (relative)
    )
    def instruction_BEQ(self, opcode, ea):
        """
        Tests the state of the Z (zero) bit and causes a branch if it is set.
        When used after a subtract or compare operation, this instruction will
        branch if the compared values, signed or unsigned, were exactly the
        same.

        source code forms: BEQ dd; LBEQ DDDD

        CC bits "HNZVC": -----
        """
        if self.cc.Z == 1:
            log.debug("$%x BEQ branch to $%x, because Z==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BEQ: don't branch to $%x, because Z==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch if greater than or equal (signed)
        0x2c, # BGE (relative)
        0x102c, # LBGE (relative)
    )
    def instruction_BGE(self, opcode, ea, m):
        """
        Causes a branch if the N (negative) bit and the V (overflow) bit are
        either both set or both clear. That is, branch if the sign of a valid
        twos complement result is, or would be, positive. When used after a
        subtract or compare operation on twos complement values, this
        instruction will branch if the register was greater than or equal to the
        memory register.

        source code forms: BGE dd; LBGE DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BGE" % opcode)

    @opcode(# Branch if greater (signed)
        0x2e, # BGT (relative)
        0x102e, # LBGT (relative)
    )
    def instruction_BGT(self, opcode, ea, m):
        """
        Causes a branch if the N (negative) bit and V (overflow) bit are either
        both set or both clear and the Z (zero) bit is clear. In other words,
        branch if the sign of a valid twos complement result is, or would be,
        positive and not zero. When used after a subtract or compare operation
        on twos complement values, this instruction will branch if the register
        was greater than the memory register.

        source code forms: BGT dd; LBGT DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BGT" % opcode)

    @opcode(# Branch if higher (unsigned)
        0x22, # BHI (relative)
        0x1022, # LBHI (relative)
    )
    def instruction_BHI(self, opcode, ea):
        """
        Causes a branch if the previous operation caused neither a carry nor a
        zero result. When used after a subtract or compare operation on unsigned
        binary values, this instruction will branch if the register was higher
        than the memory register.

        Generally not useful after INC/DEC, LD/TST, and TST/CLR/COM
        instructions.

        source code forms: BHI dd; LBHI DDDD

        CC bits "HNZVC": -----
        """
        if self.cc.C == 0 and self.cc.Z == 0:
            log.debug("$%x BHI branch to $%x, because C==0 and Z==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BHI: don't branch to $%x, because C and Z not 0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Bit test memory with accumulator
        0x85, 0x95, 0xa5, 0xb5, # BITA (immediate, direct, indexed, extended)
        0xc5, 0xd5, 0xe5, 0xf5, # BITB (immediate, direct, indexed, extended)
    )
    def instruction_BIT(self, opcode, ea, m, register):
        """
        Performs the logical AND of the contents of accumulator A or B and the
        contents of memory location M and modifies the condition codes
        accordingly. The contents of accumulator A or B and memory location M
        are not affected.

        source code forms: BITA P; BITB P

        CC bits "HNZVC": -aa0-
        """
        x = register.get()
        r = m & x
        log.debug("$%x BIT update CC with $%x (m:%i & %s:%i)" % (
            self.program_counter,
            r, m, register.name, x
        ))
        self.cc.update_NZ0_8(r)

    @opcode(# Branch if less than or equal (signed)
        0x2f, # BLE (relative)
        0x102f, # LBLE (relative)
    )
    def instruction_BLE(self, opcode, ea, m):
        """
        Causes a branch if the exclusive OR of the N (negative) and V (overflow)
        bits is 1 or if the Z (zero) bit is set. That is, branch if the sign of
        a valid twos complement result is, or would be, negative. When used
        after a subtract or compare operation on twos complement values, this
        instruction will branch if the register was less than or equal to the
        memory register.

        source code forms: BLE dd; LBLE DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BLE" % opcode)

    @opcode(# Branch if lower or same (unsigned)
        0x23, # BLS (relative)
        0x1023, # LBLS (relative)
    )
    def instruction_BLS(self, opcode, ea):
        """
        Causes a branch if the previous operation caused either a carry or a
        zero result. When used after a subtract or compare operation on unsigned
        binary values, this instruction will branch if the register was lower
        than or the same as the memory register.

        Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.

        source code forms: BLS dd; LBLS DDDD

        CC bits "HNZVC": -----
        """
#         if (self.cc.C|self.cc.Z) == 0:
        if self.cc.C == 1 or self.cc.Z == 1:
            log.debug("$%x BLS branch to $%x, because C|Z==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BLS: don't branch to $%x, because C|Z!=1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch if less than (signed)
        0x2d, # BLT (relative)
        0x102d, # LBLT (relative)
    )
    def instruction_BLT(self, opcode, ea, m):
        """
        Causes a branch if either, but not both, of the N (negative) or V
        (overflow) bits is set. That is, branch if the sign of a valid twos
        complement result is, or would be, negative. When used after a subtract
        or compare operation on twos complement binary values, this instruction
        will branch if the register was less than the memory register.

        source code forms: BLT dd; LBLT DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BLT" % opcode)

    @opcode(# Branch if minus
        0x2b, # BMI (relative)
        0x102b, # LBMI (relative)
    )
    def instruction_BMI(self, opcode, ea):
        """
        Tests the state of the N (negative) bit and causes a branch if set. That
        is, branch if the sign of the twos complement result is negative.

        When used after an operation on signed binary values, this instruction
        will branch if the result is minus. It is generally preferred to use the
        LBLT instruction after signed operations.

        source code forms: BMI dd; LBMI DDDD

        CC bits "HNZVC": -----
        """
        if self.cc.N == 1:
            log.debug("$%x BMI branch to $%x, because N==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BMI: don't branch to $%x, because N==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch if not equal
        0x26, # BNE (relative)
        0x1026, # LBNE (relative)
    )
    def instruction_BNE(self, opcode, ea):
        """
        Tests the state of the Z (zero) bit and causes a branch if it is clear.
        When used after a subtract or compare operation on any binary values,
        this instruction will branch if the register is, or would be, not equal
        to the memory register.

        source code forms: BNE dd; LBNE DDDD

        CC bits "HNZVC": -----
        """
        if self.cc.Z == 0:
            log.debug("$%x BNE branch to $%x, because Z==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BNE: don't branch to $%x, because Z==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch if plus
        0x2a, # BPL (relative)
        0x102a, # LBPL (relative)
    )
    def instruction_BPL(self, opcode, ea):
        """
        Tests the state of the N (negative) bit and causes a branch if it is
        clear. That is, branch if the sign of the twos complement result is
        positive.

        When used after an operation on signed binary values, this instruction
        will branch if the result (possibly invalid) is positive. It is
        generally preferred to use the BGE instruction after signed operations.

        source code forms: BPL dd; LBPL DDDD

        CC bits "HNZVC": -----
        """
        if self.cc.N == 0:
            log.debug("$%x BPL branch to $%x, because N==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BPL: don't branch to $%x, because N==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch always
        0x20, # BRA (relative)
        0x16, # LBRA (relative)
    )
    def instruction_BRA(self, opcode, ea):
        """
        Causes an unconditional branch.

        source code forms: BRA dd; LBRA DDDD

        CC bits "HNZVC": -----
        """
        # FIXME:
        if self.cfg.__class__.__name__ == "Simple6809Cfg":
            if self.program_counter == 0xdb79 and ea == 0xdb6a: # RAM size test loop
#                 msg = repr(["%x" % x for x in [self.program_counter, ea, m, self.index_x.get()]])
#                 raise RuntimeError(msg)
                new_x = 0x7ffd
                new_ea = 0xdb79
                log.warn(
                    "Speedup Simple6809 RAM test: Set X to $%x and goto $%x" % (
                        new_x, new_ea
                ))
                self.index_x.set(new_x)
                self.program_counter = new_ea
                return

        log.debug("$%x BRA branch to $%x \t| %s" % (
            self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
        ))
        self.program_counter = ea

    @opcode(# Branch never
        0x21, # BRN (relative)
        0x1021, # LBRN (relative)
    )
    def instruction_BRN(self, opcode, ea, m):
        """
        Does not cause a branch. This instruction is essentially a no operation,
        but has a bit pattern logically related to branch always.

        source code forms: BRN dd; LBRN DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BRN" % opcode)

    @opcode(# Branch if valid twos complement result
        0x28, # BVC (relative)
        0x1028, # LBVC (relative)
    )
    def instruction_BVC(self, opcode, ea, m):
        """
        Tests the state of the V (overflow) bit and causes a branch if it is
        clear. That is, branch if the twos complement result was valid. When
        used after an operation on twos complement binary values, this
        instruction will branch if there was no overflow.

        source code forms: BVC dd; LBVC DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BVC" % opcode)

    @opcode(# Branch if invalid twos complement result
        0x29, # BVS (relative)
        0x1029, # LBVS (relative)
    )
    def instruction_BVS(self, opcode, ea, m):
        """
        Tests the state of the V (overflow) bit and causes a branch if it is
        set. That is, branch if the twos complement result was invalid. When
        used after an operation on twos complement binary values, this
        instruction will branch if there was an overflow.

        source code forms: BVS dd; LBVS DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x BVS" % opcode)

    @opcode(0xf, 0x6f, 0x7f) # CLR (direct, indexed, extended)
    def instruction_CLR(self, opcode, ea):
        """
        Clear memory location
        source code forms: CLR
        CC bits "HNZVC": -0100
        """
        self.memory.write_byte(ea, 0x00)
        self.cc.update_0100()

    @opcode(
        0x4f, # CLRA (inherent)
        0x5f, # CLRB (inherent)
    )
    def instruction_CLR_register(self, opcode, register):
        """
        Clear accumulator A or B

        source code forms: CLRA; CLRB
        CC bits "HNZVC": -0100
        """
        register.set(0x00)
        self.cc.update_0100()

    @opcode(# Compare memory from stack pointer
        0x1083, 0x1093, 0x10a3, 0x10b3, # CMPD (immediate, direct, indexed, extended)
        0x118c, 0x119c, 0x11ac, 0x11bc, # CMPS (immediate, direct, indexed, extended)
        0x1183, 0x1193, 0x11a3, 0x11b3, # CMPU (immediate, direct, indexed, extended)
        0x8c, 0x9c, 0xac, 0xbc, # CMPX (immediate, direct, indexed, extended)
        0x108c, 0x109c, 0x10ac, 0x10bc, # CMPY (immediate, direct, indexed, extended)
    )
    def instruction_CMP16(self, opcode, ea, m, register):
        """
        Compares the 16-bit contents of the concatenated memory locations M:M+1
        to the contents of the specified register and sets the appropriate
        condition codes. Neither the memory locations nor the specified register
        is modified unless autoincrement or autodecrement are used. The carry
        flag represents a borrow and is set to the inverse of the resulting
        binary carry.

        source code forms: CMPD P; CMPX P; CMPY P; CMPU P; CMPS P

        CC bits "HNZVC": -aaaa
        """
        a = register.get()
        b = m
        r = a - b
        log.debug("$%x CMP16 %s $%x - $%x = $%x" % (
            self.program_counter,
            register.name,
            a, b, r
        ))
        self.cc.update_NZVC_16(a, b, r)

    @opcode(# Compare memory from accumulator
        0x81, 0x91, 0xa1, 0xb1, # CMPA (immediate, direct, indexed, extended)
        0xc1, 0xd1, 0xe1, 0xf1, # CMPB (immediate, direct, indexed, extended)
    )
    def instruction_CMP8(self, opcode, ea, m, register):
        """
        Compares the contents of memory location to the contents of the
        specified register and sets the appropriate condition codes. Neither
        memory location M nor the specified register is modified. The carry flag
        represents a borrow and is set to the inverse of the resulting binary
        carry.

        source code forms: CMPA P; CMPB P

        CC bits "HNZVC": uaaaa

        static uint8_t op_sub(struct MC6809 *cpu, uint8_t a, uint8_t b) {
            unsigned out = a - b;
            CLR_NZVC;
            SET_NZVC8(a, b, out);
            return out;
        }

        """
        a = register.get()
        b = m
        r = a - b
        log.debug("$%x CMP8 %s $%x - $%x = $%x" % (
            self.program_counter,
            register.name,
            a, b, r
        ))
        self.cc.update_NZVC_8(a, b, r)

    def COM(self, value):
        value = unsigned8(~value) # the bits of m inverted
        self.cc.update_NZ01_8(value)
        return value

    @opcode(# Complement memory location
        0x3, 0x63, 0x73, # COM (direct, indexed, extended)
    )
    def instruction_COM_memory(self, opcode, ea, m):
        """
        Replaces the contents of memory location M with its logical complement.
        source code forms: COM Q
        CC bits "HNZVC": -aa01
        """
        self.memory.write_byte(ea, self.COM(value=m))
        log.debug("$%x COM memory $%x" % (
            self.program_counter, m,
        ))

    @opcode(# Complement accumulator
        0x43, # COMA (inherent)
        0x53, # COMB (inherent)
    )
    def instruction_COM_register(self, opcode, register):
        """
        Replaces the contents of accumulator A or B with its logical complement.
        source code forms: COMA; COMB
        CC bits "HNZVC": -aa01
        """
        register.set(self.COM(value=register.get()))
        log.debug("$%x COM %s" % (
            self.program_counter, register.name,
        ))

    @opcode(# AND condition code register, then wait for interrupt
        0x3c, # CWAI (immediate)
    )
    def instruction_CWAI(self, opcode, ea, m):
        """
        This instruction ANDs an immediate byte with the condition code register
        which may clear the interrupt mask bits I and F, stacks the entire
        machine state on the hardware stack and then looks for an interrupt.
        When a non-masked interrupt occurs, no further machine state information
        need be saved before vectoring to the interrupt handling routine. This
        instruction replaced the MC6800 CLI WAI sequence, but does not place the
        buses in a high-impedance state. A FIRQ (fast interrupt request) may
        enter its interrupt handler with its entire machine state saved. The RTI
        (return from interrupt) instruction will automatically return the entire
        machine state after testing the E (entire) bit of the recovered
        condition code register.

        The following immediate values will have the following results: FF =
        enable neither EF = enable IRQ BF = enable FIRQ AF = enable both

        source code forms: CWAI #$XX E F H I N Z V C

        CC bits "HNZVC": ddddd
        """
        raise NotImplementedError("$%x CWAI" % opcode)
        # Update CC bits: ddddd

    @opcode(# Decimal adjust A accumulator
        0x19, # DAA (inherent)
    )
    def instruction_DAA(self, opcode):
        """
        The sequence of a single-byte add instruction on accumulator A (either
        ADDA or ADCA) and a following decimal addition adjust instruction
        results in a BCD addition with an appropriate carry bit. Both values to
        be added must be in proper BCD form (each nibble such that: 0 <= nibble
        <= 9). Multiple-precision addition must add the carry generated by this
        decimal addition adjust into the next higher digit during the add
        operation (ADCA) immediately prior to the next decimal addition adjust.

        source code forms: DAA

        CC bits "HNZVC": -aa0a
        """
        raise NotImplementedError("$%x DAA" % opcode)
        # Update CC bits: -aa0a

    def DEC(self, a):
        """
        Subtract one from the register. The carry bit is not affected, thus
        allowing this instruction to be used as a loop counter in multiple-
        precision computations. When operating on unsigned values, only BEQ and
        BNE branches can be expected to behave consistently. When operating on
        twos complement values, all signed branches are available.

        source code forms: DEC Q; DECA; DECB

        CC bits "HNZVC": -aaa-

        #define SET_Z(r)          ( REG_CC |= ((r) ? 0 : CC_Z) )
        #define SET_N8(r)         ( REG_CC |= (r&0x80)>>4 )
        #define SET_NZ8(r)        ( SET_N8(r), SET_Z(r&0xff) )

        #define CLR_NZV   ( REG_CC &= ~(CC_N|CC_Z|CC_V) )

        static uint8_t op_dec(struct MC6809 *cpu, uint8_t in) {
            unsigned out = in - 1;
            CLR_NZV;
            SET_NZ8(out);
            if (out == 0x7f) REG_CC |= CC_V;
            return out;
        }

        tmp1 = op_dec(cpu, tmp1); break; // DEC, DECA, DECB
        """
        r = a - 1
        self.cc.update_NZ_8(r)
        if r == 0x7f:
            self.cc.V = 1
        return r

    @opcode(0xa, 0x6a, 0x7a) # DEC (direct, indexed, extended)
    def instruction_DEC_memory(self, opcode, ea, m):
        """ Decrement memory location """
        r = self.DEC(m)
        log.debug("$%x DEC memory value $%x -1 = $%x and write it to $%x \t| %s" % (
            self.program_counter,
            m, r, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.memory.write_byte(ea, r)

    @opcode(0x4a, 0x5a) # DECA / DECB (inherent)
    def instruction_DEC_register(self, opcode, register):
        """ Decrement accumulator """
        a = register.get()
        r = self.DEC(a)
        log.debug("$%x DEC %s value $%x -1 = $%x" % (
            self.program_counter,
            register.name, a, r
        ))
        register.set(r)

    @opcode(# Exclusive OR memory with accumulator
        0x88, 0x98, 0xa8, 0xb8, # EORA (immediate, direct, indexed, extended)
        0xc8, 0xd8, 0xe8, 0xf8, # EORB (immediate, direct, indexed, extended)
    )
    def instruction_EOR(self, opcode, ea, register):
        """
        The contents of memory location M is exclusive ORed into an 8-bit
        register.

        source code forms: EORA P; EORB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("$%x EOR" % opcode)
        # self.cc.update_NZ0()

    @opcode(# Exchange Rl with R2
        0x1e, # EXG (immediate)
    )
    def instruction_EXG(self, opcode, ea, m):
        """
        0000 = A:B 1000 = A 0001 = X 1001 = B 0010 = Y 1010 = CCR 0011 = US 1011
        = DPR 0100 = SP 1100 = Undefined 0101 = PC 1101 = Undefined 0110 =
        Undefined 1110 = Undefined 0111 = Undefined 1111 = Undefined

        source code forms: EXG R1,R2

        CC bits "HNZVC": ccccc
        """
        raise NotImplementedError("$%x EXG" % opcode)
        # Update CC bits: ccccc

    @opcode(# Increment accumulator
        0x4c, # INCA (inherent)
        0x5c, # INCB (inherent)
    )
    def instruction_INC_register(self, opcode, register):
        """
        Adds to the register. The carry bit is not affected, thus allowing this
        instruction to be used as a loop counter in multiple-precision
        computations. When operating on unsigned values, only the BEQ and BNE
        branches can be expected to behave consistently. When operating on twos
        complement values, all signed branches are correctly available.

        source code forms: INC Q; INCA; INCB

        CC bits "HNZVC": -aaa-
        """
        a = register.get()
        r = register.set(a + 1)
        self.cc.update_NZV_8(a=a, b=1, r=r)


    @opcode(# Increment memory location
        0xc, 0x6c, 0x7c, # INC (direct, indexed, extended)
    )
    def instruction_INC_memory(self, opcode, ea, m):
        """
        Adds to the register. The carry bit is not affected, thus allowing this
        instruction to be used as a loop counter in multiple-precision
        computations. When operating on unsigned values, only the BEQ and BNE
        branches can be expected to behave consistently. When operating on twos
        complement values, all signed branches are correctly available.

        source code forms: INC Q; INCA; INCB

        CC bits "HNZVC": -aaa-
        """
        r = m + 1
        log.debug("$%x INC memory value $%x +1 = $%x and write it to $%x \t| %s" % (
            self.program_counter,
            m, r, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.update_NZV_8(a=m, b=1, r=r)
        self.memory.write_byte(ea, r)

    @opcode(# Jump
        0xe, 0x6e, 0x7e, # JMP (direct, indexed, extended)
    )
    def instruction_JMP(self, opcode, ea):
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

    @opcode(
        # Branch to subroutine:
        0x8d, # BSR (relative)
        0x17, # LBSR (relative)
        # Jump to subroutine:
        0x9d, 0xad, 0xbd, # JSR (direct, indexed, extended)
    )
    def instruction_BSR_JSR(self, opcode, ea):
        """
        Program control is transferred to the effective address after storing
        the return address on the hardware stack.

        A return from subroutine (RTS) instruction is used to reverse this
        process and must be the last instruction executed in a subroutine.

        source code forms: BSR dd; LBSR DDDD; JSR EA

        CC bits "HNZVC": -----
        """
        log.info("$%x JSR to $%x \t| %s" % (
            self.program_counter,
            ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.push_word(self._system_stack_pointer, self.program_counter)
        self.program_counter = ea

    @opcode(# Load register from memory
        0xcc, 0xdc, 0xec, 0xfc, # LDD (immediate, direct, indexed, extended)
        0x10ce, 0x10de, 0x10ee, 0x10fe, # LDS (immediate, direct, indexed, extended)
        0xce, 0xde, 0xee, 0xfe, # LDU (immediate, direct, indexed, extended)
        0x8e, 0x9e, 0xae, 0xbe, # LDX (immediate, direct, indexed, extended)
        0x108e, 0x109e, 0x10ae, 0x10be, # LDY (immediate, direct, indexed, extended)
    )
    def instruction_LD16(self, opcode, ea, m, register):
        """
        Load the contents of the memory location M:M+1 into the designated
        16-bit register.

        source code forms: LDD P; LDX P; LDY P; LDS P; LDU P

        CC bits "HNZVC": -aa0-
        """
        log.debug("$%x LD16 set %s to $%x \t| %s" % (
            self.program_counter,
            register.name, m,
            self.cfg.mem_info.get_shortest(m)
        ))
        register.set(m)
        self.cc.update_NZ0_16(m)

    @opcode(# Load accumulator from memory
        0x86, 0x96, 0xa6, 0xb6, # LDA (immediate, direct, indexed, extended)
        0xc6, 0xd6, 0xe6, 0xf6, # LDB (immediate, direct, indexed, extended)
    )
    def instruction_LD8(self, opcode, ea, m, register):
        """
        Loads the contents of memory location M into the designated register.

        source code forms: LDA P; LDB P

        CC bits "HNZVC": -aa0-
        """
        log.debug("$%x LD8 %s = $%x \t| %s" % (
            self.program_counter,
            register.name, m,
            self.cfg.mem_info.get_shortest(ea)
        ))
        register.set(m)
        self.cc.update_NZ0_8(m)

    @opcode(# Load effective address into an indexable register
        0x32, # LEAS (indexed)
        0x33, # LEAU (indexed)
    )
    def instruction_LEA_pointer(self, opcode, ea, register):
        """
        Calculates the effective address from the indexed addressing mode and
        places the address in an indexable register.

        LEAX and LEAY affect the Z (zero) bit to allow use of these registers
        as counters and for MC6800 INX/DEX compatibility.

        LEAU and LEAS do not affect the Z bit to allow cleaning up the stack
        while returning the Z bit as a parameter to a calling routine, and also
        for MC6800 INS/DES compatibility.

        Instruction Operation Comment Instruction  Operation  Comment LEAX 10,X
        X+10 -> X Adds 5-bit constant 10 to X LEAX 500,X X+500 -> X Adds 16-bit
        constant 500 to X LEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y LEAY D,Y
        Y+D -> Y Adds 16-bit D accumulator to Y LEAU -10,U U-10 -> U Subtracts
        10 from U LEAS -10,S S-10 -> S Used to reserve area on stack LEAS 10,S
        S+10 -> S Used to 'clean up' stack LEAX 5,S S+5 -> X Transfers as well
        as adds

        source code forms: LEAX, LEAY, LEAS, LEAU

        CC bits "HNZVC": -----
        """
        log.debug("$%x LEA %s: Set %s and Z to $%x \t| %s" % (
            self.program_counter,
            register.name, register.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        register.set(ea)

    @opcode(# Load effective address into an indexable register
        0x30, # LEAX (indexed)
        0x31, # LEAY (indexed)
    )
    def instruction_LEA_register(self, opcode, ea, register):
        """ see instruction_LEA_pointer

        CC bits "HNZVC": --a--
        """
        log.debug("$%x LEA %s: Set %s to $%x \t| %s" % (
            self.program_counter,
            register.name, register.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        register.set(ea)
        self.cc.set_Z16(ea)

    def LSL(self, a):
        """
        Shifts all bits of accumulator A or B or memory location M one place to
        the left. Bit zero is loaded with a zero. Bit seven of accumulator A or
        B or memory location M is shifted into the C (carry) bit.

        This is a duplicate assembly-language mnemonic for the single machine
        instruction ASL.

        source code forms: LSL Q; LSLA; LSLB

        CC bits "HNZVC": naaas
        """
        r = a << 1
        self.cc.clear_NZVC()
        self.cc.update_NZVC_8(a, a, r)
        return r

    @opcode(0x8, 0x68, 0x78) # LSL/ASL (direct, indexed, extended)
    def instruction_LSL_memory(self, opcode, ea, m):
        """
        Logical shift left memory location / Arithmetic shift of memory left
        """
        r = self.LSL(m)
        log.debug("$%x LSL memory value $%x << 1 = $%x and write it to $%x \t| %s" % (
            self.program_counter,
            m, r, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.memory.write_byte(ea, r)

    @opcode(0x48, 0x58) # LSLA/ASLA / LSLB/ASLB (inherent)
    def instruction_LSL_register(self, opcode, register):
        """
        Logical shift left accumulator / Arithmetic shift of accumulator
        """
        a = register.get()
        r = self.LSL(a)
        log.debug("$%x LSL %s value $%x << 1 = $%x" % (
            self.program_counter,
            register.name, a, r
        ))
        register.set(r)

    @opcode(# Logical shift right accumulator or memory location
        0x4, 0x64, 0x74, # LSR (direct, indexed, extended)
        0x44, # LSRA (inherent)
        0x54, # LSRB (inherent)
    )
    def instruction_LSR(self, opcode, ea, register):
        """
        Performs a logical shift right on the register. Shifts a zero into bit
        seven and bit zero into the C (carry) bit.

        source code forms: LSR Q; LSRA; LSRB

        CC bits "HNZVC": -0a-s
        """
        raise NotImplementedError("$%x LSR" % opcode)
        # self.cc.update_0ZC()

    @opcode(# Unsigned multiply (A * B ? D)
        0x3d, # MUL (inherent)
    )
    def instruction_MUL(self, opcode):
        """
        Multiply the unsigned binary numbers in the accumulators and place the
        result in both accumulators (ACCA contains the most-significant byte of
        the result). Unsigned multiply allows multiple-precision operations.

        The C (carry) bit allows rounding the most-significant byte through the
        sequence: MUL, ADCA #0.

        source code forms: MUL

        CC bits "HNZVC": --a-a
        """
        raise NotImplementedError("$%x MUL" % opcode)
        # Update CC bits: --a-a

    @opcode(# Negate accumulator
        0x40, # NEGA (inherent)
        0x50, # NEGB (inherent)
    )
    def instruction_NEG_register(self, opcode, register):
        """
        Replaces the register with its twos complement. The C (carry) bit
        represents a borrow and is set to the inverse of the resulting binary
        carry. Note that 80 16 is replaced by itself and only in this case is
        the V (overflow) bit set. The value 00 16 is also replaced by itself,
        and only in this case is the C (carry) bit cleared.

        source code forms: NEG Q; NEGA; NEG B

        CC bits "HNZVC": uaaaa
        """
        x1 = register.get()
        x2 = signed8(x1)
        r1 = x2 * -1
        r2 = unsigned8(r1)
        register.set(r2)
        log.debug("$%x NEG %s unsigned:$%x (signed:$%x) to unsigned:$%x (signed:$%x) \t| %s" % (
            self.program_counter,
            register.name, x1, x2, r1, r2,
            self.cfg.mem_info.get_shortest(r2)
        ))
        self.cc.clear_NZVC()
        self.cc.update_NZVC_8(0, x1, r2)

    _wrong_NEG = 0
    @opcode(0x0, 0x60, 0x70) # NEG (direct, indexed, extended)
    def instruction_NEG_memory(self, opcode, ea, m):
        """ Negate memory """
        if opcode == 0x0 and ea == 0x0 and m == 0x0:
            self._wrong_NEG += 1
            if self._wrong_NEG > 10:
                raise RuntimeError
        else:
            self._wrong_NEG = 0
        m2 = signed8(m)
        r1 = m2 * -1
        r2 = unsigned8(r1)

        self.memory.write_byte(ea, r2)

        log.debug("$%x NEG memory addr: $%x with unsigned:$%x (signed:$%x) to unsigned:$%x (signed:$%x) \t| %s" % (
            self.program_counter,
            ea,
            m, m2, r1, r2,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.clear_NZVC()
        self.cc.update_NZVC_8(0, m, r2)

#     @opcode([
#         0x40, # NEGA
#         0x50, # NEGB
#         0x00, 0x60, 0x70 # NEG
#     ])
#     def NEG(self):
#         """
#         Negate (Twos Complement) a Byte in Memory
#         Number of Program Bytes: 2
#         Addressing Mode: direct
#         """
#         self.cycles += 6
#         reg_type = divmod(self.opcode, 16)[0]
#         reg_dict = {
#             0x0: self.direct,
#             0x4: "accu.A",
#             0x5: "accu.B",
#             0x6: self.indexed,
#             0x7: self.extended,
#         }
#         ea, txt = reg_dict[reg_type]
#

#         value = -ea
#         self.cc.set_NZVC8(0, ea, value)
#
#         if reg_type == 0x4:
#             self.accu.A = value
#         elif reg_type == 0x5:
#             self.accu.B = value
#         else:
#             self.memory.write_byte(ea, value)

    @opcode(# No operation
        0x12, # NOP (inherent)
    )
    def instruction_NOP(self, opcode):
        """
        source code forms: NOP

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x NOP" % opcode)

    @opcode(# OR memory with accumulator
        0x8a, 0x9a, 0xaa, 0xba, # ORA (immediate, direct, indexed, extended)
        0xca, 0xda, 0xea, 0xfa, # ORB (immediate, direct, indexed, extended)
    )
    def instruction_OR(self, opcode, ea, register):
        """
        Performs an inclusive OR operation between the contents of accumulator A
        or B and the contents of memory location M and the result is stored in
        accumulator A or B.

        source code forms: ORA P; ORB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("$%x OR" % opcode)
        # self.cc.update_NZ0()

    @opcode(# OR condition code register
        0x1a, # ORCC (immediate)
    )
    def instruction_ORCC(self, opcode, ea, m, register):
        """
        Performs an inclusive OR operation between the contents of the condition
        code registers and the immediate value, and the result is placed in the
        condition code register. This instruction may be used to set interrupt
        masks (disable interrupts) or any other bit(s).

        source code forms: ORCC #XX

        CC bits "HNZVC": ddddd

            // 0x1a ORCC immediate
            case 0x1a: {
                unsigned data;
                data = byte_immediate(cpu);
                REG_CC |= data;
                peek_byte(cpu, REG_PC);
            } break;

        """
        old_cc_info = self.cc.get_info
        cc = old_cc = register.get()
        cc |= m
        register.set(cc)
        log.error("$%x ORCC: $%x |= $%x ; set CC to $%x (from %r to %r)" % (
            self.program_counter,
            old_cc, m, cc, old_cc_info, self.cc.get_info
        ))

    @opcode(# Branch if lower (unsigned)
        0x25, # BLO/BCS (relative)
        0x1025, # LBLO/LBCS (relative)
    )
    def instruction_BLO(self, opcode, ea):
        """
        CC bits "HNZVC": -----
        case 0x5: cond = REG_CC & CC_C; break; // BCS, BLO, LBCS, LBLO
        """
        if self.cc.C == 1:
            log.debug("$%x BLO/BCS/LBLO/LBCS branch to $%x, because C==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BLO/BCS/LBLO/LBCS: don't branch to $%x, because C==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Branch if lower (unsigned)
        0x24, # BHS/BCC (relative)
        0x1024, # LBHS/LBCC (relative)
    )
    def instruction_BHS(self, opcode, ea):
        """
        CC bits "HNZVC": -----
        case 0x4: cond = !(REG_CC & CC_C); break; // BCC, BHS, LBCC, LBHS
        """
        if self.cc.C == 0:
            log.debug("$%x BHS/BCC/LBHS/LBCC branch to $%x, because C==0 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))
            self.program_counter = ea
        else:
            log.debug("$%x BHS/BCC/LBHS/LBCC: don't branch to $%x, because C==1 \t| %s" % (
                self.program_counter, ea, self.cfg.mem_info.get_shortest(ea)
            ))

    @opcode(# Push A, B, CC, DP, D, X, Y, U, or PC onto stack
        0x36, # PSHU (immediate)
        0x34, # PSHS (immediate)
    )
    def instruction_PSH(self, opcode, ea, m, register):
        """
        All, some, or none of the processor registers are pushed onto stack
        (with the exception of stack pointer itself).

        A single register may be placed on the stack with the condition codes
        set by doing an autodecrement store onto the stack (example: STX ,--S).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC U Y X DP B A CC push order
        ->

        CC bits "HNZVC": -----
        """
        assert register in (self._system_stack_pointer, self.user_stack_pointer)

        def push(register_str, stack_pointer):
            register_obj = self.register_str2object[register_str]
            data = register_obj.get()

            if register_obj.WIDTH == 8:
                self.push_byte(register, data)
            else:
                assert register_obj.WIDTH == 16
                self.push_word(register, data)

        log.debug("$%x PSH%s:", self.program_counter, register.name)

        # m = postbyte
        if m & 0x80: push(REG_PC, register) # 16 bit program counter register
        if m & 0x40: push(REG_U, register) # 16 bit user-stack pointer
        if m & 0x20: push(REG_Y, register) # 16 bit index register
        if m & 0x10: push(REG_X, register) # 16 bit index register
        if m & 0x08: push(REG_DP, register) # 8 bit direct page register
        if m & 0x04: push(REG_B, register) # 8 bit accumulator
        if m & 0x02: push(REG_A, register) # 8 bit accumulator
        if m & 0x01: push(REG_CC, register) # 8 bit condition code register


    @opcode(# Pull A, B, CC, DP, D, X, Y, U, or PC from stack
        0x37, # PULU (immediate)
        0x35, # PULS (immediate)
    )
    def instruction_PUL(self, opcode, ea, m, register):
        """
        All, some, or none of the processor registers are pulled from stack
        (with the exception of stack pointer itself).

        A single register may be pulled from the stack with condition codes set
        by doing an autoincrement load from the stack (example: LDX ,S++).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC U Y X DP B A CC = pull
        order

        CC bits "HNZVC": ccccc
        """
        assert register in (self._system_stack_pointer, self.user_stack_pointer)

        def pull(register_str, stack_pointer):
            reg_obj = self.register_str2object[register_str]

            reg_width = reg_obj.WIDTH # 8 / 16
            if reg_width == 8:
                data = self.pull_byte(stack_pointer)
            else:
                assert reg_width == 16
                data = self.pull_word(stack_pointer)

            reg_obj.set(data)

        log.debug("$%x PUL%s:", self.program_counter, register.name)

        # m = postbyte
        if m & 0x01: pull(REG_CC, register) # 8 bit condition code register
        if m & 0x02: pull(REG_A, register) # 8 bit accumulator
        if m & 0x04: pull(REG_B, register) # 8 bit accumulator
        if m & 0x08: pull(REG_DP, register) # 8 bit direct page register
        if m & 0x10: pull(REG_X, register) # 16 bit index register
        if m & 0x20: pull(REG_Y, register) # 16 bit index register
        if m & 0x40: pull(REG_U, register) # 16 bit user-stack pointer
        if m & 0x80: pull(REG_PC, register) # 16 bit program counter register


    @opcode(#
        0x3e, # RESET* (inherent)
    )
    def instruction_RESET(self, opcode):
        """
         Build the ASSIST09 vector table and setup monitor defaults, then invoke
        the monitor startup routine.

        source code forms:

        CC bits "HNZVC": *****
        """
        raise NotImplementedError("$%x RESET" % opcode)
        # Update CC bits: *****

    def ROL(self, a):
        """
        Rotates all bits of the register one place left through the C (carry)
        bit. This is a 9-bit rotation.

        source code forms: ROL Q; ROLA; ROLB

        CC bits "HNZVC": -aaas

        static uint8_t op_rol(struct MC6809 *cpu, uint8_t in) {
            unsigned out = (in << 1) | (REG_CC & 1);
            CLR_NZVC;
            SET_NZVC8(in, in, out);
            return out;
        }

        case 0x9: tmp1 = op_rol(cpu, tmp1); break; // ROL, ROLA, ROLB
        """
        r = (a << 1) | self.cc.C
        self.cc.clear_NZVC()
        self.cc.update_NZVC_8(a, a, r)
        return r

    @opcode(0x9, 0x69, 0x79) # ROL (direct, indexed, extended)
    def instruction_ROL_memory(self, opcode, ea, m):
        """ Rotate memory left """
        r = self.ROL(m)
        log.debug("$%x ROL memory value $%x << 1 | Carry = $%x and write it to $%x \t| %s" % (
            self.program_counter,
            m, r, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.memory.write_byte(ea, r)

    @opcode(0x49, 0x59) # ROLA / ROLB (inherent)
    def instruction_ROL_register(self, opcode, ea, register):
        """ Rotate accumulator left """
        a = register.get()
        r = self.ROL(a)
        log.debug("$%x ROL %s value $%x << 1 | Carry = $%x" % (
            self.program_counter,
            register.name, a, r
        ))
        register.set(r)

    @opcode(# Rotate accumulator or memory right
        0x6, 0x66, 0x76, # ROR (direct, indexed, extended)
        0x46, # RORA (inherent)
        0x56, # RORB (inherent)
    )
    def instruction_ROR(self, opcode, ea, register):
        """
        Rotates all bits of the register one place right through the C (carry)
        bit. This is a 9-bit rotation.

        source code forms: ROR Q; RORA; RORB

        CC bits "HNZVC": -aa-s
        """
        raise NotImplementedError("$%x ROR" % opcode)
        # self.cc.update_NZC()

    @opcode(# Return from interrupt
        0x3b, # RTI (inherent)
    )
    def instruction_RTI(self, opcode):
        """
        The saved machine state is recovered from the hardware stack and control
        is returned to the interrupted program. If the recovered E (entire) bit
        is clear, it indicates that only a subset of the machine state was saved
        (return address and condition codes) and only that subset is recovered.

        source code forms: RTI

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x RTI" % opcode)

    @opcode(# Return from subroutine
        0x39, # RTS (inherent)
    )
    def instruction_RTS(self, opcode):
        """
        Program control is returned from the subroutine to the calling program.
        The return address is pulled from the stack.

        source code forms: RTS

        CC bits "HNZVC": -----
        """
        ea = self.pull_word(self._system_stack_pointer)
        log.debug("$%x RTS to $%x \t| %s" % (
            self.program_counter,
            ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.program_counter = ea

    @opcode(# Subtract memory from accumulator with borrow
        0x82, 0x92, 0xa2, 0xb2, # SBCA (immediate, direct, indexed, extended)
        0xc2, 0xd2, 0xe2, 0xf2, # SBCB (immediate, direct, indexed, extended)
    )
    def instruction_SBC(self, opcode, ea, register):
        """
        Subtracts the contents of memory location M and the borrow (in the C
        (carry) bit) from the contents of the designated 8-bit register, and
        places the result in that register. The C bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SBCA P; SBCB P

        CC bits "HNZVC": uaaaa
        """
        raise NotImplementedError("$%x SBC" % opcode)
        # self.cc.update_NZVC(a, b, r)

    @opcode(# Sign Extend B accumulator into A accumulator
        0x1d, # SEX (inherent)
    )
    def instruction_SEX(self, opcode):
        """
        This instruction transforms a twos complement 8-bit value in accumulator
        B into a twos complement 16-bit value in the D accumulator.

        source code forms: SEX

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("$%x SEX" % opcode)
        # self.cc.update_NZ0()

    @opcode(# Store stack pointer to memory
        0xdd, 0xed, 0xfd, # STD (direct, indexed, extended)
        0x10df, 0x10ef, 0x10ff, # STS (direct, indexed, extended)
        0xdf, 0xef, 0xff, # STU (direct, indexed, extended)
        0x9f, 0xaf, 0xbf, # STX (direct, indexed, extended)
        0x109f, 0x10af, 0x10bf, # STY (direct, indexed, extended)
    )
    def instruction_ST16(self, opcode, ea, register):
        """
        Writes the contents of a 16-bit register into two consecutive memory
        locations.

        source code forms: STD P; STX P; STY P; STS P; STU P

        CC bits "HNZVC": -aa0-
        """
        value = register.get()
        log.debug("$%x ST16 store value $%x from %s at $%x \t| %s" % (
            self.program_counter,
            value, register.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.update_NZ0_16(value)
        self.memory.write_word(ea, value)

    @opcode(# Store accumulator to memroy
        0x97, 0xa7, 0xb7, # STA (direct, indexed, extended)
        0xd7, 0xe7, 0xf7, # STB (direct, indexed, extended)
    )
    def instruction_ST8(self, opcode, ea, register):
        """
        Writes the contents of an 8-bit register into a memory location.

        source code forms: STA P; STB P

        CC bits "HNZVC": -aa0-
        """
        value = register.get()
        log.debug("$%x ST8 store value $%x from %s at $%x \t| %s" % (
            self.program_counter,
            value, register.name, ea,
            self.cfg.mem_info.get_shortest(ea)
        ))
        self.cc.update_NZ0_8(value)
        self.memory.write_byte(ea, value)

    @opcode(# Subtract memory from D accumulator
        0x83, 0x93, 0xa3, 0xb3, # SUBD (immediate, direct, indexed, extended)
    )
    def instruction_SUB16(self, opcode, ea, register):
        """
        Subtracts the value in memory location M:M+1 from the contents of a
        designated 16-bit register. The C (carry) bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SUBD P

        CC bits "HNZVC": -aaaa
        """
        raise NotImplementedError("$%x SUB16" % opcode)
        # self.cc.update_NZVC_16(a, b, r)

    @opcode(# Subtract memory from accumulator
        0x80, 0x90, 0xa0, 0xb0, # SUBA (immediate, direct, indexed, extended)
        0xc0, 0xd0, 0xe0, 0xf0, # SUBB (immediate, direct, indexed, extended)
    )
    def instruction_SUB8(self, opcode, ea, m, register):
        """
        Subtracts the value in memory location M from the contents of a
        designated 8-bit register. The C (carry) bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SUBA P; SUBB P

        CC bits "HNZVC": uaaaa
        """
        x1 = register.get()
        x2 = signed8(x1)
        r1 = x2 - m
        r2 = unsigned8(r1)
        register.set(r2)
        log.debug("$%x SUB8 %s: %i - %i = %i (unsigned: %i)" % (
            self.program_counter,
            register.name,
            x2, m, r1, r2,
        ))
        self.cc.clear_NZVC()
#         self.cc.update_NZVC_8(x1, m, r2)
        self.cc.update_NZVC_8(x1, m, r1)

    @opcode(# Software interrupt (absolute indirect)
        0x3f, # SWI (inherent)
    )
    def instruction_SWI(self, opcode):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt vector. Both the normal and
        fast interrupts are masked (disabled).

        source code forms: SWI

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x SWI" % opcode)

    @opcode(# Software interrupt (absolute indirect)
        0x103f, # SWI2 (inherent)
    )
    def instruction_SWI2(self, opcode, ea, m):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt 2 vector. This interrupt is
        available to the end user and must not be used in packaged software.
        This interrupt does not mask (disable) the normal and fast interrupts.

        source code forms: SWI2

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x SWI2" % opcode)

    @opcode(# Software interrupt (absolute indirect)
        0x113f, # SWI3 (inherent)
    )
    def instruction_SWI3(self, opcode, ea, m):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt 3 vector. This interrupt does
        not mask (disable) the normal and fast interrupts.

        source code forms: SWI3

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x SWI3" % opcode)

    @opcode(# Synchronize with interrupt line
        0x13, # SYNC (inherent)
    )
    def instruction_SYNC(self, opcode):
        """
        FAST SYNC WAIT FOR DATA Interrupt! LDA DISC DATA FROM DISC AND CLEAR
        INTERRUPT STA ,X+ PUT IN BUFFER DECB COUNT IT, DONE? BNE FAST GO AGAIN
        IF NOT.

        source code forms: SYNC

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("$%x SYNC" % opcode)

    @opcode(0x1f) # TFR (immediate)
    def instruction_TFR(self, opcode, ea, m):
        """
        0000 = A:B
        1000 = A
        0001 = X
        1001 = B
        0010 = Y
        1010 = CCR
        0011 = US
        1011 = DPR
        0100 = SP
        1100 = Undefined
        0101 = PC
        1101 = Undefined
        0110 = Undefined
        1110 = Undefined
        0111 = Undefined
        1111 = Undefined

        source code forms: TFR R1, R2

        CC bits "HNZVC": ccccc
        """
        high, low = divmod(m, 16)
        log.debug("$%x TFR: post byte: $%x -> high: $%x low: $%x" % (
            self.program_counter, m, high, low
        ))
        # TODO: check if source and dest has the same size?
        source = self.get_register(high)
        self.set_register(low, source)

        # TODO: Update CC bits: ccccc ?


    @opcode(# Test accumulator
        0x4d, # TSTA (inherent)
        0x5d, # TSTB (inherent)
    )
    def instruction_TST_register(self, opcode, register):
        """
        Set the N (negative) and Z (zero) bits according to the contents of
        accumulator A or B, and clear the V (overflow) bit. The TST instruction
        provides only minimum information when testing unsigned values; since no
        unsigned value is less than zero, BLO and BLS have no utility. While BHI
        could be used after TST, it provides exactly the same control as BNE,
        which is preferred. The signed branches are available.

        The MC6800 processor clears the C (carry) bit.

        source code forms: TST Q; TSTA; TSTB

        CC bits "HNZVC": -aa0-
        """
        x = register.get()
        self.cc.update_NZ0_8(x)

    @opcode(0xd, 0x6d) # TST (direct, indexed)
    def instruction_TST_memory_8(self, opcode, ea, m):
        """ Test memory location 8-Bit """
        self.cc.update_NZ0_8(m)

    @opcode(0x7d) # TST extended
    def instruction_TST_memory_16(self, opcode, ea, m):
        """ Test memory location 16-Bit """
        self.cc.update_NZ0_16(m)


def test_run():
    import subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
        "--verbosity=5",
#         "--verbosity=20",
#         "--verbosity=30",
#         "--verbosity=50",
#         "--area_debug_active=5:bb79-ffff",
#         "--cfg=Simple6809Cfg",
        "--cfg=Dragon32Cfg",
#         "--max=1",
        "--max=46041",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args).wait()
    sys.exit(0)


if __name__ == "__main__":
    cli = DragonPyCLI()
    cli.setup_cfg()

    if not cli.cfg.use_bus:
        test_run()
        print "DragonPy cpu core"
        print "Run DragonPy_CLI.py instead"
        sys.exit(0)

    bus_socket_addr = cli.cfg.bus_socket_addr

    print "Connect to internal socket bus I/O %s" % repr(bus_socket_addr)
    assert isinstance(bus_socket_addr, tuple)
    bus = socket.socket()
    bus.connect(bus_socket_addr)
    assert bus is not None
    cli.cfg.bus = bus

    cpu = CPU(cli.cfg)
    cpu.reset()
    try:
        cpu.run()
    except:
        print_exc_plus()

