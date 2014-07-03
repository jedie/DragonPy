#!/usr/bin/env python
# encoding:utf-8

"""
    6809 unittests
    ~~~~~~~~~~~~~~

    Test CPU with BASIC Interpreter from simple6809

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import unittest
import time

from dragonpy.tests.test_base import TextTestRunner2, BaseTestCase, \
    UnittestCmdArgs
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809TestPeriphery
from dragonpy.cpu6809 import CPU
import Queue


log = logging.getLogger("DragonPy")

def print_cpu_state_data(state):
    for k, v in sorted(state.items()):
        if k == "RAM":
            v = ",".join(["$%x" % i for i in v])
        print "%r: %s" % (k, v)

class Test6809_BASIC_simple6809_Base(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        """
        prerun ROM to complete initiate and ready for user input.
        save the CPU state to speedup unittest
        """
        super(Test6809_BASIC_simple6809_Base, cls).setUpClass()

        cmd_args = UnittestCmdArgs
        cfg = Simple6809Cfg(cmd_args)

        cls.periphery = Simple6809TestPeriphery(cfg)
        cfg.periphery = cls.periphery

        cpu = CPU(cfg)
        cpu.reset()
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
        cls.cpu = cpu

        # Check if machine is ready
        assert cls.periphery.out_lines == [
            '6809 EXTENDED BASIC\r\n',
            '(C) 1982 BY MICROSOFT\r\n',
            '\r\n',
            'OK\r\n'
        ]
        # Save CPU state
        cls._init_state = cpu.get_state()
#         print_cpu_state_data(cls._init_state)

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

    def test_print01(self):
        self.assertEqual(self.cpu.get_info,
            "cc=54 a=0d b=00 dp=00 x=deae y=0000 u=deab s=0334"
        )
        self.assertEqual(self.cpu.cc.get_info, ".F.I.Z..")
        self.assertEqual(self.cpu.program_counter, 57131)

        self.periphery.add_to_input_queue('? "FOO"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['? "FOO"\r\n', 'FOO\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1085)
        self.assertEqual(cycles, 7354) # TODO: cycles are probably not set corrent in CPU, yet!

    def test_print02(self):
        self.assertEqual(self.cpu.get_info,
            "cc=54 a=0d b=00 dp=00 x=deae y=0000 u=deab s=0334"
        )
        self.assertEqual(self.cpu.cc.get_info, ".F.I.Z..")
        self.assertEqual(self.cpu.program_counter, 57131)

        self.periphery.add_to_input_queue('PRINT "BAR"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['PRINT "BAR"\r\n', 'BAR\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1424)

    def test_print03(self):
        self.periphery.add_to_input_queue('PRINT 0\r\n')
        op_call_count, cycles, output = self._run_until_OK()
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['PRINT 0\r\n', ' 0 \r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 1366)

    def test_STR(self):
        self.periphery.add_to_input_queue(
            'A=0\r\n'
            '? "A="+STR$(A)\r\n'
        )
        op_call_count, cycles, output = self._run_until_OK(
            OK_count=2, max_ops=12000
        )
#         print op_call_count, cycles, output
        self.assertEqual(output,
            ['A=0\r\n', 'OK\r\n', '? "A="+STR$(A)\r\n', 'A= 0\r\n', 'OK\r\n']
        )
        self.assertEqual(op_call_count, 11229)

#     def test_MUL(self): # will faile, yet...
#         self.periphery.add_to_input_queue('? 2*3\r\n')
#         op_call_count, cycles, output = self._run_until_OK()
# #         print op_call_count, cycles, output
#         self.assertEqual(output,
#             ['? 2*3\r\n', ' 6\r\n', 'OK\r\n']
#         )
#         self.assertEqual(op_call_count, 11229)

#     def test_PRINT04(self):  # will faile, yet...
#         self.periphery.add_to_input_queue('?2\r\n')
#         op_call_count, cycles, output = self._run_until_OK(max_ops=100000)
# #         print op_call_count, cycles, output
#         self.assertEqual(output,
#             ['?2\r\n', ' 2 \r\n', 'OK\r\n']
#         )
# #         self.assertEqual(op_call_count, 11229)


if __name__ == '__main__':
    log.setLevel(
#        1
#        10 # DEBUG
#         20 # INFO
#         30 # WARNING
#         40 # ERROR
        50 # CRITICAL/FATAL
    )
    log.addHandler(logging.StreamHandler())

    unittest.main(
        argv=(
            sys.argv[0],
#            "Test6809_Program.test_crc16_01",
        ),
        testRunner=TextTestRunner2,
#         verbosity=1,
        verbosity=2,
#         failfast=True,
    )
