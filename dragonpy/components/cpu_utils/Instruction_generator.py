#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import sys

from dragonpy.components.MC6809data.MC6809_op_data import (
    OP_DATA, BYTE, WORD, REG_A, REG_B, REG_CC, REG_D , REG_DP, REG_PC,
    REG_S, REG_U, REG_X, REG_Y
)
from dragonpy.components.MC6809data.MC6809_data_utils import MC6809OP_DATA_DICT


SPECIAL_FUNC_NAME = "special"

REGISTER_DICT = {
    REG_X:"index_x",
    REG_Y:"index_y",

    REG_U:"user_stack_pointer",
    REG_S:"system_stack_pointer",

    REG_PC:"program_counter",

    REG_A:"accu_a",
    REG_B:"accu_b",
    REG_D:"accu_d",

    REG_DP:"direct_page",
    REG_CC:"cc",

    #undefined_reg.name:"undefined_reg", # for TFR", EXG
}


if __doc__:
    DOC = __doc__.rsplit("=", 1)[1]
else:
    DOC = "" # e.g.: run with --OO

INIT_CODE = '''
"""
    This file was generated with: "%s"
    Please doen't change it directly ;)
    %s
"""


from dragonpy.components.cpu_utils.instruction_base import InstructionBase

class PrepagedInstructions(InstructionBase):

''' % (os.path.basename(__file__), DOC)



def build_func_name(addr_mode, ea, register, read, write):
#    print addr_mode, ea, register, read, write

    if addr_mode is None:
        return SPECIAL_FUNC_NAME

    func_name = addr_mode.lower()

    if ea:
        func_name += "_ea"
    if register:
        func_name += "_%s" % register
    if read:
        func_name += "_read%s" % read
    if write:
        func_name += "_write%s" % write

#    print func_name
    return func_name


def func_name_from_op_code(op_code):
    op_code_data = MC6809OP_DATA_DICT[op_code]
    addr_mode = op_code_data["addr_mode"]
    ea = op_code_data["needs_ea"]
    register = op_code_data["register"]
    read = op_code_data["read_from_memory"]
    write = op_code_data["write_to_memory"]
    return build_func_name(addr_mode, ea, register, read, write)


def generate_code(f):
    variants = set()
    for instr_data in list(OP_DATA.values()):
        for mnemonic, mnemonic_data in list(instr_data["mnemonic"].items()):
            read_from_memory = mnemonic_data["read_from_memory"]
            write_to_memory = mnemonic_data["write_to_memory"]
            needs_ea = mnemonic_data["needs_ea"]
            register = mnemonic_data["register"]
            for op_code, op_data in list(mnemonic_data["ops"].items()):
                addr_mode = op_data["addr_mode"]
#                print hex(op_code),
                variants.add(
                    (addr_mode, needs_ea, register, read_from_memory, write_to_memory)
                )
#                if (addr_mode and  needs_ea and  register and  read_from_memory and  write_to_memory) is None:
                if addr_mode is None:
                    print(mnemonic, op_data)

#    for no, data in enumerate(sorted(variants)):
#        print no, data
#    print"+++++++++++++"

    for line in INIT_CODE.splitlines():
        f.write("%s\n" % line)

    for addr_mode, ea, register, read, write in sorted(variants):
        if not addr_mode:
            # special function (RESET/ PAGE1,2) defined in InstructionBase
            continue

        func_name = build_func_name(addr_mode, ea, register, read, write)

        f.write("    def %s(self, opcode):\n" % func_name)

        code = []

        if ea and read:
            code.append("ea, m = self.cpu.get_ea_m_%s()" % addr_mode.lower())

        if write:
            code.append("ea, value = self.instr_func(")
        else:
            code.append("self.instr_func(")
        code.append("    opcode = opcode,")

        if ea and read:
            code.append("    ea = ea,")
            code.append("    m = m,")
        elif ea:
            code.append("    ea = self.cpu.get_ea_%s()," % addr_mode.lower())
        elif read:
            code.append("    m = self.cpu.get_m_%s()," % addr_mode.lower())

        if register:
            code.append(
                "    register = self.cpu.%s," % REGISTER_DICT[register]
            )

        code.append(")")

        if write == BYTE:
            code.append("self.memory.write_byte(ea, value)")
        elif write == WORD:
            code.append("self.memory.write_word(ea, value)")

        for line in code:
            f.write("        %s\n" % line)

        f.write("\n")


def generate(filename):
    with open(filename, "w") as f:
#        generate_code(sys.stdout)
        generate_code(f)
    sys.stderr.write("New %r generated.\n" % filename)





def test_run():
    import subprocess
    cmd_args = [
        sys.executable,
#         "/usr/bin/pypy",
        os.path.join("..", "DragonPy_CLI.py"),
#        "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL

#        "--trace",

#        "--machine=Simple6809",
        "--machine=sbc09",
#         "--max=500000",
#         "--max=20000",
        "--max=1",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    generate("instruction_call.py")
    test_run()



