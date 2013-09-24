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
import textwrap

from MC6809_data_raw import OP_CATEGORIES, INSTRUCTION_INFO, OP_DATA, ADDRES_MODE_DICT

HNZVC_FUNC_MAP = {
    "-aa0-": "NZ0",

    "uaaaa": "NZVC",
    "-aaaa": "NZVC",
    "naaas": "NZVC",
    "-aaas": "NZVC",

    "aaaaa": "HNZVC",

    "uaa-s": "NZC",
    "-aa-s": "NZC",

    "-aaa-": "NZV",

    "-aa01": "NZ01",
    "-0a-s": "0ZC",
    "-0100": "0100",
}

SPLIT_MNEMONIC = {
    "LEAS": "LEA_pointer",
    "LEAU": "LEA_pointer",
    "LEAX": "LEA_register",
    "LEAY": "LEA_register",
}

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
print '''
def opcode(*opcodes):
    """A decorator for opcodes"""
    def decorator(func):
        setattr(func, "_is_opcode", True)
        setattr(func, "_opcodes", opcodes)
        return func
    return decorator
'''
print "class CPU6809Skeleton(object):"


def get_ops_by_instr_key(instr_key):
    ops = []
    for op_data in OP_DATA:
        if op_data["instr_info_key"] == instr_key:
            ops.append(op_data)
    return ops

def print_doc(instr_data, key, prefix=""):
    raw_txt = prefix + instr_data.get(key, "")
    w = textwrap.TextWrapper(width=80,
        initial_indent="        ",
        subsequent_indent="        ",
    )
    txt = w.fill(raw_txt)
    if txt:
        print txt
        print

def print_func(func_name, ops):
    op_info = {}
    has_operant = False
    has_ea = False
    for op in ops:
        if op["operand"] is not None:
            has_operant = True
        if op["bytes"] > 1:
            has_ea = True
        mnemonic = op["mnemonic"]
        if mnemonic not in op_info:
            op_info[mnemonic] = {"opcodes": [op["opcode"]], "addr_modes": [op["addr_mode"]]}
        else:
            op_info[mnemonic]["opcodes"].append(op["opcode"])
            op_info[mnemonic]["addr_modes"].append(op["addr_mode"])

    if "short_desc" in instr_data:
        print '    @opcode( # %s' % instr_data["short_desc"]
    else:
        print '    @opcode('


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

    print '    )'

    func_line = "    def instruction_%s(self, opcode" % func_name
    if has_ea:
        func_line += ", ea=None"
    if has_operant:
        func_line += ", operand=None"
    func_line += "):"
    print func_line

    print '        """'
    print_doc(instr_data, "description")
    print_doc(instr_data, "comment")
    print_doc(instr_data, "source form", "source code forms: ")
    for line in instr_data.get("HNZVC", "").split("\n"):
        print '        CC bits "HNZVC": %s' % line
    print '        """'


added_ops = []
no_ops = []
# very ineffective, but hey, must only run one time ;)
for instr_key, instr_data in sorted(INSTRUCTION_INFO.items()):
    ops = get_ops_by_instr_key(instr_key)
    if not ops:
        no_ops.append((instr_key, instr_data))
        continue

#     SPLIT_MNEMONIC
    splitted_ops = {}
    for op in ops:
        mnemonic = op["mnemonic"]
        if mnemonic in SPLIT_MNEMONIC:
            d = splitted_ops.setdefault(SPLIT_MNEMONIC[mnemonic], [])
            op
        else:
            d = splitted_ops.setdefault(instr_key, [])
        d.append(op)

    for func_name, ops in sorted(splitted_ops.items()):
        print_func(func_name, ops)

        print '        raise NotImplementedError("TODO: $%%x %s" %% opcode)' % func_name

        cc_bits = instr_data["HNZVC"]
        try:
            cc_func = HNZVC_FUNC_MAP[cc_bits]
        except KeyError:
            if cc_bits != "-----":
                print "        # Update CC bits: %s" % cc_bits
        else:

            cc_call_line = '        self.cc.update_%s' % cc_func
            if instr_key.endswith("16"):
                cc_call_line += "_16"
            elif instr_key.endswith("8"):
                cc_call_line += "_8"

            if cc_bits[3] in ("a", "d") or cc_bits[0] in ("a", "d"):
                cc_call_line += "(a, b, r)"
            else:
                cc_call_line += "()"
            print cc_call_line
        print

print '"""'
print "No ops for:"
for instr_key, instr_data in no_ops:
    print instr_key
    pprint.pprint(instr_data)
print '"""'

sys.stdout.close()
print "%i opcodes" % len(added_ops)

