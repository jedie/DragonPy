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


log = logging.getLogger("DragonPy")


class Test6809_BASIC_simple6809_Base(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(Test6809_BASIC_simple6809_Base, cls).setUpClass()

        log.setLevel(
#            1
#            10 # DEBUG
#            20 # INFO
#            30 # WARNING
#            40 # ERROR
            50 # CRITICAL/FATAL
        )
        log.addHandler(logging.StreamHandler())

        cmd_args = UnittestCmdArgs

        cfg = Simple6809Cfg(cmd_args)

        cls.periphery = Simple6809TestPeriphery(cfg)
        cfg.periphery = cls.periphery

        cpu = CPU(cfg)
        cpu.reset()
        print "init machine...",
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
        print cpu
        # TODO: Save CPU state

    def setUp(self):
        # TODO: Reset CPU state
        pass

    def test_init(self):
        print "TODO"
        #self.periphery
        print self.cpu
        print self.cpu.get_info
        print self.cpu.cc.get_info
        print "pc:", self.cpu.program_counter

        print "XXX", self.periphery.output

#        self.periphery.add_to_input_queue('? "FOO"\r\n')
#        self.cpu.

#        self.cpu.cc.C = 1
#        self.cpu_test_run2(start=0x1000, count=1, mem=[
#            0x24, 0xf4, # BCC -12
#        ])
#        self.assertEqualHex(self.cpu.program_counter, 0x1002)


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
