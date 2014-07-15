#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect

from dragonpy.MC6809data.MC6809_data_utils import MC6809OP_DATA_DICT
from dragonpy.cpu6809_trace import InstructionTrace
from dragonpy.cpu_utils.Instruction_generator import func_name_from_op_code
from dragonpy.cpu_utils.instruction_call import PrepagedInstructions


class OpCollection(object):
    def __init__(self, cpu):
        self.cpu = cpu
        self.opcode_dict = {}
        self.collect_ops()

    def get_opcode_dict(self):
        return self.opcode_dict

    def collect_ops(self):
        # Get the members not from class instance, so that's possible to
        # exclude properties without "activate" them.
        cls = type(self.cpu)
        for name, cls_method in inspect.getmembers(cls):
            if name.startswith("_") or isinstance(cls_method, property):
                continue

            try:
                opcodes = getattr(cls_method, "_opcodes")
            except AttributeError:
                continue

            instr_func = getattr(self.cpu, name)
            self._add_ops(opcodes, instr_func)

    def _add_ops(self, opcodes, instr_func):
#         log.debug("%20s: %s" % (
#             instr_func.__name__, ",".join(["$%x" % c for c in opcodes])
#         ))
        for op_code in opcodes:
            assert op_code not in self.opcode_dict, \
                "Opcode $%x (%s) defined more then one time!" % (
                    op_code, instr_func.__name__
            )

            op_code_data = MC6809OP_DATA_DICT[op_code]

            func_name = func_name_from_op_code(op_code)

            if self.cpu.cfg.trace:
                InstructionClass = InstructionTrace
            else:
                InstructionClass = PrepagedInstructions

            instrution_class = InstructionClass(self.cpu, instr_func)
            func = getattr(instrution_class, func_name)

            self.opcode_dict[op_code] = (op_code_data["cycles"], func)
