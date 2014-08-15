#!/usr/bin/env python
# encoding:utf-8

"""
    Simple6809 Play
    ~~~~~~~~~~~~~~~

    Just for devloper to play a little bit with the BASIC Interpreter.

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from contextlib import contextmanager
import logging
import os
import sys

from dragonpy.tests.test_base import Test6809_BASIC_simple6809_Base
from dragonlib.utils.logging_utils import setup_logging


log = logging.getLogger("DragonPy")


def log2file(filename_suffix):
    setup_logging(log,
#         level=1, # hardcore debug ;)
#         level=10, # DEBUG
        level=20, # INFO
#         level=30, # WARNING
#         level=40, # ERROR
#         level=50, # CRITICAL/FATAL
        handler=logging.FileHandler(
            filename="Simple6809Play_%s.log" % filename_suffix,
            mode='w'
        )
    )


@contextmanager
def stdout_into_file(filename):
    old_stdout = sys.stdout
    try:
        with open(filename, "w") as f:
            sys.stdout = f
            yield None
    finally:
        sys.stdout = old_stdout


class Test_simple6809_BASIC(Test6809_BASIC_simple6809_Base):
#     def __init__(self):
# #         os.remove(self.TEMP_FILE);print "Delete CPU date file!"
#         cmd_args = UnittestCmdArgs
# #         cmd_args.trace = True
#         self.setUpClass(cmd_args)

    def hello_world(self):
        self.setUp() # restore CPU/Periphery state to a fresh startup.

        self.periphery.add_to_input_queue('PRINT "HELLO WORLD!"\r\n')
        op_call_count, cycles, output = self._run_until_OK()
        print op_call_count, cycles, output

    def play(self):
        self.setUp() # restore CPU/Periphery state to a fresh startup.

#         self.periphery.add_to_input_queue('?1.5\r\n')
        self.periphery.add_to_input_queue('?5\r\n')

#         log2file(filename_suffix="negative_number")
        with stdout_into_file("Simple6809Play_PRINT1.5.log"):
            op_call_count, cycles, output = self._run_until_OK(max_ops=100000)
        print op_call_count, cycles, output



if __name__ == '__main__':
    setup_logging(log,
#         level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
        level=40 # ERROR
#        level=50 # CRITICAL/FATAL
    )


    c = Test_simple6809_BASIC()

#     print "-"*79
#     c.hello_world()
    print "-"*79
    c.play()
    print "-"*79

    print " --- END --- "
