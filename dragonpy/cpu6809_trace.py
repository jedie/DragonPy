#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Create trace lines for every OP call.

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonpy.cpu6809 import Instruction
import sys
import logging


log = logging.getLogger("DragonPy.cpu6809.trace")


class InstructionTrace(Instruction):
    def __init__(self, *args, **kwargs):
        super(InstructionTrace, self).__init__(*args, **kwargs)
        self.cfg = self.cpu.cfg
        self.get_mem_info = self.cpu.cfg.mem_info.get_shortest

    def call_instr_func(self, *args, **kwargs):
        super(InstructionTrace, self).call_instr_func(*args, **kwargs)

        if self.opcode in (0x10, 0x11):
            log.debug("Skip PAGE 2 and PAGE 3 instruction in trace")
            return

        op_address = self.cpu.last_op_address

        ob_bytes = self.data["bytes"]

        op_bytes = "".join([
            "%02x" % value
            for __, value in self.cpu.memory.iter_bytes(op_address, op_address + ob_bytes)
        ])

        kwargs_info = []
        if "register" in self.op_kwargs:
            kwargs_info.append(str(self.op_kwargs["register"]))
        if "ea" in self.op_kwargs:
            kwargs_info.append("ea:%04x" % self.op_kwargs["ea"])
        if "m" in self.op_kwargs:
            kwargs_info.append("m:%x" % self.op_kwargs["m"])

        msg = "%(op_address)04x| %(op_bytes)-11s %(mnemonic)-7s %(kwargs)-19s %(cpu)s | %(cc)s | %(mem)s\n" % {
            "op_address": op_address,
            "op_bytes": op_bytes,
            "mnemonic": self.data["mnemonic"],
            "kwargs": " ".join(kwargs_info),
            "cpu": self.cpu.get_info,
            "cc": self.cpu.cc.get_info,
            "mem": self.get_mem_info(op_address)
        }
        sys.stdout.write(msg)

        if not op_bytes.startswith("%02x" % self.opcode):
            self.cpu.memory.print_dump(op_address, op_address + ob_bytes)
            self.cpu.memory.print_dump(op_address - 10, op_address + ob_bytes + 10)
        assert op_bytes.startswith("%02x" % self.opcode), "%s doesn't start with %02x" % (
            op_bytes, self.opcode
        )


def test_run():
    import subprocess
    cmd_args = [
        sys.executable,
#         "/usr/bin/pypy",
#         os.path.join("..", "DragonPy_CLI.py"),
        "DragonPy_CLI.py",
#        "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL

        "--trace",

        "--cfg=Simple6809",
#         "--max=500000",
#         "--max=20000",
        "--max=1",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
