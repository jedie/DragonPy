#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import cPickle as pickle
import logging
import os
import sys
import tempfile
import time
import unittest
import Queue

from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809TestPeriphery
from dragonpy.cpu6809 import CPU
from dragonpy.cpu_utils.MC6809_registers import ConditionCodeRegister, ValueStorage8Bit
from dragonpy.tests.test_config import TestCfg


log = logging.getLogger("DragonPy")


class UnittestCmdArgs(object):
    bus_socket_host = None
    bus_socket_port = None
    ram = None
    rom = None
    verbosity = None
    max = None
    trace = False

    # print CPU cycle/sec while running
    display_cycle = False


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        cmd_args = UnittestCmdArgs
        cfg = TestCfg(cmd_args)
        self.cpu = CPU(cfg)
        self.cpu.cc.set(0x00)

    def assertEqualHex(self, hex1, hex2, msg=None):
        first = "$%x" % hex1
        second = "$%x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

    def assertIsByteRange(self, value):
        self.assertTrue(0x0 <= value, "Value (dez: %i - hex: %x) is negative!" % (value, value))
        self.assertTrue(0xff >= value, "Value (dez: %i - hex: %x) is greater than 0xff!" % (value, value))

    def assertIsWordRange(self, value):
        self.assertTrue(0x0 <= value, "Value (dez: %i - hex: %x) is negative!" % (value, value))
        self.assertTrue(0xffff >= value, "Value (dez: %i - hex: %x) is greater than 0xffff!" % (value, value))

    def assertEqualHexByte(self, hex1, hex2, msg=None):
        self.assertIsByteRange(hex1)
        self.assertIsByteRange(hex2)
        first = "$%02x" % hex1
        second = "$%02x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

    def assertEqualHexWord(self, hex1, hex2, msg=None):
        self.assertIsWordRange(hex1)
        self.assertIsWordRange(hex2)
        first = "$%04x" % hex1
        second = "$%04x" % hex2
        if msg is None:
            msg = "%s != %s" % (first, second)
        self.assertEqual(first, second, msg)

    def cpu_test_run(self, start, end, mem):
        for cell in mem:
            self.assertLess(-1, cell, "$%x < 0" % cell)
            self.assertGreater(0x100, cell, "$%x > 0xff" % cell)
        log.debug("memory load at $%x: %s", start,
            ", ".join(["$%x" % i for i in mem])
        )
        self.cpu.memory.load(start, mem)
        if end is None:
            end = start + len(mem)
        self.cpu.test_run(start, end)

    def cpu_test_run2(self, start, count, mem):
        for cell in mem:
            self.assertLess(-1, cell, "$%x < 0" % cell)
            self.assertGreater(0x100, cell, "$%x > 0xff" % cell)
        self.cpu.memory.load(start, mem)
        self.cpu.test_run2(start, count)

    def assertMemory(self, start, mem):
        for index, should_byte in enumerate(mem):
            address = start + index
            is_byte = self.cpu.memory.read_byte(address)

            msg = "$%02x is not $%02x at address $%04x (index: %i)" % (
                is_byte, should_byte, address, index
            )
            self.assertEqual(is_byte, should_byte, msg)


class BaseStackTestCase(BaseTestCase):
    INITIAL_SYSTEM_STACK_ADDR = 0x1000
    INITIAL_USER_STACK_ADDR = 0x2000
    def setUp(self):
        super(BaseStackTestCase, self).setUp()
        self.cpu._system_stack_pointer.set(self.INITIAL_SYSTEM_STACK_ADDR)
        self.cpu.user_stack_pointer.set(self.INITIAL_USER_STACK_ADDR)


class TextTestResult2(unittest.TextTestResult):
    def startTest(self, test):
        if not self.showAll:
            super(TextTestResult2, self).startTest(test)
            return
        print
        print "_"*70
        self.showAll = False
        print self.getDescription(test), "..."
        super(TextTestResult2, self).startTest(test)
        self.showAll = True

class TextTestRunner2(unittest.TextTestRunner):
    resultclass = TextTestResult2


class TestCPU(object):
    def __init__(self):
        self.accu_a = ValueStorage8Bit("A", 0) # A - 8 bit accumulator
        self.accu_b = ValueStorage8Bit("B", 0) # B - 8 bit accumulator
        # 8 bit condition code register bits: E F H I N Z V C
        self.cc = ConditionCodeRegister()




def print_cpu_state_data(state):
    for k, v in sorted(state.items()):
        if k == "RAM":
            v = ",".join(["$%x" % i for i in v])
        print "%r: %s" % (k, v)


class Test6809_BASIC_simple6809_Base(BaseTestCase):
    """
    Run tests with the BASIC Interpreter from simple6809 ROM.
    """
    TEMP_FILE = os.path.join(tempfile.gettempdir(), "BASIC_simple6809_unittests.dat")
    print "CPU state pickle file: %r" % TEMP_FILE
    # os.remove(TEMP_FILE);print "Delete CPU date file!"

    @classmethod
    def setUpClass(cls, cmd_args=None):
        """
        prerun ROM to complete initiate and ready for user input.
        save the CPU state to speedup unittest
        """
        super(Test6809_BASIC_simple6809_Base, cls).setUpClass()

        if cmd_args is None:
            cmd_args = UnittestCmdArgs
        cfg = Simple6809Cfg(cmd_args)

        cls.periphery = Simple6809TestPeriphery(cfg)
        cfg.periphery = cls.periphery

        cpu = CPU(cfg)
        cpu.reset()
        cls.cpu = cpu

        try:
            temp_file = open(cls.TEMP_FILE, "rb")
        except IOError:
            print "init machine..."
            init_start = time.time()
            cpu.test_run(
                start=cpu.program_counter,
                end=cfg.STARTUP_END_ADDR,
            )
            duration = time.time() - init_start
            print "done in %iSec. it's %.2f cycles/sec. (current cycle: %i)" % (
                duration, float(cpu.cycles / duration), cpu.cycles
            )

            # Check if machine is ready
            assert cls.periphery.out_lines == [
                '6809 EXTENDED BASIC\r\n',
                '(C) 1982 BY MICROSOFT\r\n',
                '\r\n',
                'OK\r\n'
            ]
            # Save CPU state
            init_state = cpu.get_state()
            with open(cls.TEMP_FILE, "wb") as f:
                pickle.dump(init_state, f)
                print "Save CPU init state to: %r" % cls.TEMP_FILE
            cls._init_state = init_state
        else:
            print "Load CPU init state from: %r" % cls.TEMP_FILE
            cls._init_state = pickle.load(temp_file)

#        print_cpu_state_data(cls._init_state)

    def setUp(self):
        """ restore CPU/Periphery state to a fresh startup. """
        self.periphery.user_input_queue = Queue.Queue()
        self.periphery.output_queue = Queue.Queue()
        self.periphery.out_lines = []
        self.cpu.set_state(self._init_state)
#         print_cpu_state_data(self.cpu.get_state())

    def _run_until_OK(self, OK_count=1, max_ops=5000):
        old_cycles = self.cpu.cycles
        output = []
        existing_OK_count = 0
        for op_call_count in xrange(max_ops):
            self.cpu.get_and_call_next_op()
            out_lines = self.periphery.out_lines
            if out_lines:
                output += out_lines
                if out_lines[-1] == "OK\r\n":
                    existing_OK_count += 1
                if existing_OK_count >= OK_count:
                    cycles = self.cpu.cycles - old_cycles
                    return op_call_count, cycles, output
                self.periphery.out_lines = []

        msg = "ERROR: Abort after %i op calls (%i cycles)" % (
            op_call_count, (self.cpu.cycles - old_cycles)
        )
        raise self.failureException(msg)




if __name__ == '__main__':
    log.setLevel(
#        1
#        10 # DEBUG
#         20 # INFO
#        30 # WARNING
#         40 # ERROR
        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    unittest.main(
        argv=(
            sys.argv[0],
            "BaseCPUTestCase",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
