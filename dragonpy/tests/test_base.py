#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import hashlib
import logging
import os
import pickle as pickle
import queue
import sys
import tempfile
import time

from dragonlib.tests.test_base import BaseTestCase
from MC6809.components.cpu6809 import CPU

from dragonpy.components.memory import Memory
from dragonpy.core.machine import Machine
from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.periphery_dragon import Dragon32PeripheryUnittest
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.periphery import SBC09PeripheryUnittest
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809PeripheryUnittest
from dragonpy.tests.test_config import TestCfg


log = logging.getLogger(__name__)


class BaseCPUTestCase(BaseTestCase):
    UNITTEST_CFG_DICT = {
        "verbosity": None,
        "display_cycle": False,
        "trace": None,
        "bus_socket_host": None,
        "bus_socket_port": None,
        "ram": None,
        "rom": None,
        "max_ops": None,
        "use_bus": False,
    }

    def setUp(self):
        cfg = TestCfg(self.UNITTEST_CFG_DICT)
        memory = Memory(cfg)
        self.cpu = CPU(memory, cfg)
        memory.cpu = self.cpu  # FIXME
        self.cpu.cc.set(0x00)

    def cpu_test_run(self, start, end, mem):
        for cell in mem:
            self.assertLess(-1, cell, f"${cell:x} < 0")
            self.assertGreater(0x100, cell, f"${cell:x} > 0xff")
        log.debug("memory load at $%x: %s", start,
                  ", ".join(["$%x" % i for i in mem])
                  )
        self.cpu.memory.load(start, mem)
        if end is None:
            end = start + len(mem)
        self.cpu.test_run(start, end)
    cpu_test_run.__test__ = False  # Exclude from nose

    def cpu_test_run2(self, start, count, mem):
        for cell in mem:
            self.assertLess(-1, cell, f"${cell:x} < 0")
            self.assertGreater(0x100, cell, f"${cell:x} > 0xff")
        self.cpu.memory.load(start, mem)
        self.cpu.test_run2(start, count)
    cpu_test_run2.__test__ = False  # Exclude from nose

    def assertMemory(self, start, mem):
        for index, should_byte in enumerate(mem):
            address = start + index
            is_byte = self.cpu.memory.read_byte(address)

            msg = f"${is_byte:02x} is not ${should_byte:02x} at address ${address:04x} (index: {index:d})"
            self.assertEqual(is_byte, should_byte, msg)


class BaseStackTestCase(BaseCPUTestCase):
    INITIAL_SYSTEM_STACK_ADDR = 0x1000
    INITIAL_USER_STACK_ADDR = 0x2000

    def setUp(self):
        super().setUp()
        self.cpu.system_stack_pointer.set(self.INITIAL_SYSTEM_STACK_ADDR)
        self.cpu.user_stack_pointer.set(self.INITIAL_USER_STACK_ADDR)


# class TestCPU(object):
#     def __init__(self):
#         self.accu_a = ValueStorage8Bit("A", 0) # A - 8 bit accumulator
#         self.accu_b = ValueStorage8Bit("B", 0) # B - 8 bit accumulator
#         # 8 bit condition code register bits: E F H I N Z V C
#         self.cc = ConditionCodeRegister()


def print_cpu_state_data(state):
    print(f"cpu state data {state.__class__.__name__!r} (ID:{id(state):d}):")
    for k, v in sorted(state.items()):
        if k == "RAM":
            # v = ",".join(["$%x" % i for i in v])
            print("\tSHA from RAM:", hashlib.sha224(repr(v)).hexdigest())
            continue
        if isinstance(v, int):
            v = f"${v:x}"
        print(f"\t{k!r}: {v}")

# -----------------------------------------------------------------------------


class Test6809_BASIC_simple6809_Base(BaseCPUTestCase):
    """
    Run tests with the BASIC Interpreter from simple6809 ROM.
    """
    TEMP_FILE = os.path.join(
        tempfile.gettempdir(),
        f"DragonPy_simple6809_unittests_Py{sys.version_info[0]:d}.dat"
    )

    @classmethod
    def setUpClass(cls, cmd_args=None):
        """
        prerun ROM to complete initiate and ready for user input.
        save the CPU state to speedup unittest
        """
        super().setUpClass()

        log.info(f"CPU state pickle file: {cls.TEMP_FILE!r}")
#         if os.path.isfile(cls.TEMP_FILE):os.remove(cls.TEMP_FILE);print "Delete CPU data file!"

        cfg = Simple6809Cfg(cls.UNITTEST_CFG_DICT)

        cls.user_input_queue = queue.Queue()

        cls.machine = Machine(
            cfg,
            periphery_class=Simple6809PeripheryUnittest,
            display_callback=None,
            user_input_queue=cls.user_input_queue,
        )
        cls.cpu = cls.machine.cpu
        cls.periphery = cls.machine.periphery
        cls.periphery.setUp()

        if os.path.isfile(cls.TEMP_FILE):
            log.info(f"Load CPU init state from: {cls.TEMP_FILE!r}")
            with open(cls.TEMP_FILE, "rb") as temp_file:
                cls.__init_state = pickle.load(temp_file)
        else:
            log.info("init machine...")
            init_start = time.time()
            cls.cpu.test_run(
                start=cls.cpu.program_counter.value,
                end=cfg.STARTUP_END_ADDR,
                max_ops=500000,
            )
            duration = time.time() - init_start
            log.info("done in %iSec. it's %.2f cycles/sec. (current cycle: %i)" % (
                duration, float(cls.cpu.cycles / duration), cls.cpu.cycles
            ))

            # Check if machine is ready
            assert cls.periphery.output == (
                '6809 EXTENDED BASIC\r\n'
                '(C) 1982 BY MICROSOFT\r\n'
                '\r\n'
                'OK\r\n'
            ), f"Outlines are: {repr(cls.periphery.output_lines)}"
            # Save CPU state
            init_state = cls.cpu.get_state()
            with open(cls.TEMP_FILE, "wb") as f:
                pickle.dump(init_state, f)
                log.info(f"Save CPU init state to: {cls.TEMP_FILE!r}")
            cls.__init_state = init_state

#        print_cpu_state_data(cls.__init_state)

    def setUp(self):
        """ restore CPU/Periphery state to a fresh startup. """
        self.periphery.setUp()
        self.cpu.set_state(self.__init_state)
#         print_cpu_state_data(self.cpu.get_state())

    def _run_until_OK(self, OK_count=1, max_ops=5000):
        old_cycles = self.cpu.cycles
        last_output_len = 0
        existing_OK_count = 0
        for op_call_count in range(max_ops):
            self.cpu.get_and_call_next_op()

            if self.periphery.output_len > last_output_len:
                last_output_len = self.periphery.output_len

#                 log.critical("output: %s", repr(self.periphery.output))

                if self.periphery.output.endswith("OK\r\n"):
                    existing_OK_count += 1

                    if existing_OK_count >= OK_count:
                        cycles = self.cpu.cycles - old_cycles
                        output_lines = self.periphery.output.splitlines(True)  # with keepends
                        return op_call_count, cycles, output_lines

        msg = "ERROR: Abort after %i op calls (%i cycles)" % (
            op_call_count, (self.cpu.cycles - old_cycles)
        )
        raise self.failureException(msg)

# -----------------------------------------------------------------------------


class Test6809_sbc09_Base(BaseCPUTestCase):
    """
    Run tests with the sbc09 ROM.
    """
    TEMP_FILE = os.path.join(
        tempfile.gettempdir(),
        f"DragonPy_sbc09_unittests_Py{sys.version_info[0]:d}.dat"
    )

    @classmethod
    def setUpClass(cls, cmd_args=None):
        """
        prerun ROM to complete initiate and ready for user input.
        save the CPU state to speedup unittest
        """
        super().setUpClass()

        log.info(f"CPU state pickle file: {cls.TEMP_FILE!r}")
#        if os.path.isfile(cls.TEMP_FILE):
#            print("Delete CPU date file!")
#            os.remove(cls.TEMP_FILE)

        cfg = SBC09Cfg(cls.UNITTEST_CFG_DICT)

        cls.user_input_queue = queue.Queue()
        cls.display_callback = queue.Queue()

        cls.machine = Machine(
            cfg,
            periphery_class=SBC09PeripheryUnittest,
            display_callback=cls.display_callback,
            user_input_queue=cls.user_input_queue,
        )
        cls.cpu = cls.machine.cpu
        cls.periphery = cls.machine.periphery
        cls.periphery.setUp()

        try:
            temp_file = open(cls.TEMP_FILE, "rb")
        except OSError:
            log.info("init machine...")
            init_start = time.time()
            cls.cpu.test_run(
                start=cls.cpu.program_counter.value,
                end=cfg.STARTUP_END_ADDR,
            )
            duration = time.time() - init_start
            log.info("done in %iSec. it's %.2f cycles/sec. (current cycle: %i)" % (
                duration, float(cls.cpu.cycles / duration), cls.cpu.cycles
            ))

            # Check if machine is ready
            assert cls.periphery.output == (
                'Welcome to BUGGY version 1.0\r\n'
            ), f"Outlines are: {repr(cls.periphery.output)}"
            # Save CPU state
            init_state = cls.cpu.get_state()
            with open(cls.TEMP_FILE, "wb") as f:
                pickle.dump(init_state, f)
                log.info(f"Save CPU init state to: {cls.TEMP_FILE!r}")
            cls.__init_state = init_state
        else:
            log.info(f"Load CPU init state from: {cls.TEMP_FILE!r}")
            cls.__init_state = pickle.load(temp_file)
            temp_file.close()

#         print_cpu_state_data(cls.__init_state)

    def setUp(self):
        """ restore CPU/Periphery state to a fresh startup. """
        self.periphery.setUp()
        self.cpu.set_state(self.__init_state)
#         print_cpu_state_data(self.cpu.get_state())

    def _run_until(self, terminator, count, max_ops):
        old_cycles = self.cpu.cycles
        last_output_len = 0
        is_count = 0
        for op_call_count in range(max_ops):
            self.cpu.get_and_call_next_op()

            if self.periphery.output_len > last_output_len:
                last_output_len = self.periphery.output_len

#                 log.critical("output: %s", repr(self.periphery.output))

                if self.periphery.output.endswith(terminator):
                    is_count += 1

                    if is_count >= count:
                        cycles = self.cpu.cycles - old_cycles
                        output_lines = self.periphery.output.splitlines(True)  # with keepends
                        return op_call_count, cycles, output_lines

        msg = "ERROR: Abort after %i op calls (%i cycles) %i %r found." % (
            op_call_count, (self.cpu.cycles - old_cycles),
            is_count, terminator,
        )
        raise self.failureException(msg)

    def _run_until_OK(self, OK_count=1, max_ops=5000):
        return self._run_until(terminator="OK\r\n", count=OK_count, max_ops=max_ops)

    def _run_until_newlines(self, newline_count=1, max_ops=5000):
        return self._run_until(terminator="\n", count=newline_count, max_ops=max_ops)


# -----------------------------------------------------------------------------


class Test6809_Dragon32_Base(BaseCPUTestCase):
    """
    Run tests with the Dragon32 ROM.
    """
    TEMP_FILE = os.path.join(
        tempfile.gettempdir(),
        f"DragonPy_Dragon32_unittests_Py{sys.version_info[0]:d}.dat"
    )

    @classmethod
    def setUpClass(cls, cmd_args=None):
        """
        prerun ROM to complete initiate and ready for user input.
        save the CPU state to speedup unittest
        """
        super().setUpClass()

        log.info(f"CPU state pickle file: {cls.TEMP_FILE!r}")
#         os.remove(cls.TEMP_FILE);print "Delete CPU date file!"

        cfg = Dragon32Cfg(cls.UNITTEST_CFG_DICT)

        cls.user_input_queue = queue.Queue()

        cls.machine = Machine(
            cfg,
            periphery_class=Dragon32PeripheryUnittest,
            display_callback=None,
            user_input_queue=cls.user_input_queue,
        )
        cls.cpu = cls.machine.cpu
        cls.periphery = cls.machine.periphery
        cls.periphery.setUp()

#        os.remove(cls.TEMP_FILE)
        try:
            temp_file = open(cls.TEMP_FILE, "rb")
        except OSError:
            log.info("init machine...")
            init_start = time.time()
            cls.cpu.test_run(
                start=cls.cpu.program_counter.value,
                end=cfg.STARTUP_END_ADDR,
            )
            duration = time.time() - init_start
            log.info("done in %iSec. it's %.2f cycles/sec. (current cycle: %i)" % (
                duration, float(cls.cpu.cycles / duration), cls.cpu.cycles
            ))

            # Check if machine is ready
            output = cls.periphery.striped_output()[:5]
            assert output == [
                '(C) 1982 DRAGON DATA LTD',
                '16K BASIC INTERPRETER 1.0',
                '(C) 1982 BY MICROSOFT',
                '', 'OK'
            ]
            # Save CPU state
            init_state = cls.cpu.get_state()
            with open(cls.TEMP_FILE, "wb") as f:
                pickle.dump(init_state, f)
                log.info(f"Save CPU init state to: {cls.TEMP_FILE!r}")
            cls.__init_state = init_state
        else:
            log.info(f"Load CPU init state from: {cls.TEMP_FILE!r}")
            cls.__init_state = pickle.load(temp_file)
            temp_file.close()

#        print "cls.__init_state:", ;print_cpu_state_data(cls.__init_state)

    def setUp(self):
        """ restore CPU/Periphery state to a fresh startup. """
        self.periphery.setUp()
#        print "self.__init_state:", ;print_cpu_state_data(self.__init_state)
        self.cpu.set_state(self.__init_state)
#        print "self.cpu.get_state():", ;print_cpu_state_data(self.cpu.get_state())

    def _run_until_OK(self, OK_count=1, max_ops=5000):
        old_cycles = self.cpu.cycles
        existing_OK_count = 0
        for op_call_count in range(max_ops):
            try:
                self.cpu.get_and_call_next_op()
            except Exception as err:
                log.critical("Execute Error: %s", err)
                cycles = self.cpu.cycles - old_cycles
                return op_call_count, cycles, self.periphery.striped_output()

            output_lines = self.periphery.output_lines
            if output_lines[-1] == "OK":
                existing_OK_count += 1
            if existing_OK_count >= OK_count:
                cycles = self.cpu.cycles - old_cycles
                return op_call_count, cycles, self.periphery.striped_output()

        msg = "ERROR: Abort after %i op calls (%i cycles)" % (
            op_call_count, (self.cpu.cycles - old_cycles)
        )
        raise self.failureException(msg)

    def _run_until_response(self, max_ops=10000):
        old_cycles = self.cpu.cycles
        for op_call_count in range(max_ops):
            self.cpu.get_and_call_next_op()
            try:
                result = self.response_queue.get(block=False)
            except queue.Empty:
                continue
            else:
                cycles = self.cpu.cycles - old_cycles
                return op_call_count, cycles, result

        msg = "ERROR: Abort after %i op calls (%i cycles)" % (
            op_call_count, (self.cpu.cycles - old_cycles)
        )
        raise self.failureException(msg)
