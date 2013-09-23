"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import pprint
import sys

from MC6809_data_raw import OP_CATEGORIES, INSTRUCTION_INFO, OP_DATA, ADDRES_MODE_DICT


class Tee(object):
    def __init__(self, filepath, origin_out):
        self.filepath = filepath
        self.origin_out = origin_out
        self.f = file(filepath, "w")

    def write(self, *args):
        txt = " ".join(args)
        self.origin_out.write(txt)
        self.f.write(txt)

    def close(self):
        self.f.close()
        sys.stdout = self.origin_out


sys.stdout = Tee("MC6809_skeleton.py", sys.stdout)


print '"""%s"""' % __doc__
print
print "def opcode(): raise NotImplementedError"
print
print "class CPU6809Skeleton(object):"


added_ops = []
# very ineffective, but hey, must only run one time ;)
for instr_key, instr_data in sorted(INSTRUCTION_INFO.items()):
    ops = []
    for op_data in OP_DATA:
        if op_data["instr_info_key"] == instr_key:
            ops.append(op_data)

    if not ops:
        continue

    op_info = {}
    for op in ops:
        mnemonic = op["mnemonic"]
        if mnemonic not in op_info:
            op_info[mnemonic] = {"opcodes": [op["opcode"]], "addr_modes": [op["addr_mode"]]}
        else:
            op_info[mnemonic]["opcodes"].append(op["opcode"])
            op_info[mnemonic]["addr_modes"].append(op["addr_mode"])

    if "short_desc" in instr_data:
        print '    @opcode(( # %s' % instr_data["short_desc"]
    else:
        print '    @opcode(('

    for mnemonic, ops in sorted(op_info.items()):
        line = "        "
        opcodes = []
        for opcode in ops["opcodes"]:
            assert opcode not in added_ops, repr(op)
            opcodes.append(opcode)
        line += "".join(["0x%x, " % i for i in opcodes])
        line += "# %s (" % mnemonic
        line += ", ".join(
            [ADDRES_MODE_DICT[addr_mode].lower() for addr_mode in ops["addr_modes"]]
        )
        line += ")"
        print line

    print '    ))'
    print "    def op_%s(self, op, ea=None, operant=None):" % instr_key
    print '        """'
    for line in instr_data.get("description", "").split("\n"):
        print '        %s' % line
    for line in instr_data.get("comment", "").split("\n"):
        print '        %s' % line
    for line in instr_data.get("source form", "").split("\n"):
        print '        %s' % line
    print '        """'
    print '        raise NotImplementedError("TODO: $%%x %s") %% op' % instr_key
    print


sys.stdout.close()
print "%i opcodes" % len(added_ops)

