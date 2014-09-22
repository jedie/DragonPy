#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



class InstructionBase(object):
    def __init__(self, cpu, instr_func):
        self.cpu = cpu
        self.instr_func = instr_func
        self.memory = cpu.memory

    def special(self, opcode):
        # e.g: RESET and PAGE 1/2
        return self.instr_func(opcode)


