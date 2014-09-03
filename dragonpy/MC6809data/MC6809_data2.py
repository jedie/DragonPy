#!/usr/bin/env python

"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    merged data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    Note:
    * read_from_memory: it's "excluded" the address modes routines.
        So if the address mode will fetch the memory to get the
        effective address, but the content of the memory is not needed in
        the instruction them self, the read_from_memory must be set to False.

    Generated data is online here:
    https://docs.google.com/spreadsheet/ccc?key=0Alhtym6D6yKjdFBtNmF0UVR5OW05S3psaURnUTNtSFE

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import pprint
import sys
import os
import csv

# old data
from .MC6809_data_raw import INSTRUCTION_INFO, OP_DATA, OP_CATEGORIES


class Tee(object):
    def __init__(self, filepath, origin_out, to_stdout):
        self.filepath = filepath
        self.origin_out = origin_out
        self.to_stdout = to_stdout
        self.f = file(filepath, "w")

    def write(self, *args):
        txt = " ".join(args)
        if self.to_stdout:
            self.origin_out.write(txt)
        self.f.write(txt)

    def close(self):
        self.f.close()
        sys.stdout = self.origin_out


def get_global_keys(ignore_keys):
    # Hack:
    d = dict(globals()) # a copy!
    for key in ignore_keys:
        del(d[key])
    if "ignore_keys" in d:
        del(d["ignore_keys"])
    return d

ignore_keys = list(globals().keys()) # hack

BYTE = 8
WORD = 16

WIDTH_DICT = get_global_keys(ignore_keys)
WIDTH_DICT2 = dict((v, k) for k, v in list(WIDTH_DICT.items()))
WIDTHS = list(WIDTH_DICT.keys())


ignore_keys = list(globals().keys()) # hack


IMMEDIATE = "IMMEDIATE"
IMMEDIATE_WORD = "IMMEDIATE_WORD"
RELATIVE = "RELATIVE"
RELATIVE_WORD = "RELATIVE_WORD"
EXTENDED = "EXTENDED"
DIRECT = "DIRECT"
INDEXED = "INDEXED"
INHERENT = "INHERENT"

ADDR_MODE_DICT = get_global_keys(ignore_keys)
ADDR_MODES = list(ADDR_MODE_DICT.keys())
ADDR_MODES.sort()

ignore_keys = list(globals().keys()) # hack

ABX = "ABX"
ADC = "ADC"
ADD = "ADD"
AND = "AND"
ASR = "ASR"
BEQ = "BEQ"
BGE = "BGE"
BGT = "BGT"
BHI = "BHI"
BHS = "BHS"
BIT = "BIT"
BLE = "BLE"
BLO = "BLO"
BLS = "BLS"
BLT = "BLT"
BMI = "BMI"
BNE = "BNE"
BPL = "BPL"
BRA = "BRA"
BRN = "BRN"
BSR = "BSR"
BVC = "BVC"
BVS = "BVS"
CLR = "CLR"
CMP = "CMP"
COM = "COM"
CWAI = "CWAI"
DAA = "DAA"
DEC = "DEC"
EOR = "EOR"
EXG = "EXG"
INC = "INC"
JMP = "JMP"
JSR = "JSR"
LD = "LD"
LEA = "LEA"
LSL = "LSL"
LSR = "LSR"
MUL = "MUL"
NEG = "NEG"
NOP = "NOP"
OR = "OR"
PSHS = "PSHS"
PSHU = "PSHU"
PULS = "PULS"
PULU = "PULU"
ROL = "ROL"
ROR = "ROR"
RTI = "RTI"
RTS = "RTS"
SBC = "SBC"
SEX = "SEX"
ST = "ST"
SUB = "SUB"
SWI = "SWI"
SWI2 = "SWI2"
SWI3 = "SWI3"
SYNC = "SYNC"
TFR = "TFR"
TST = "TST"
FIRQ = "FIRQ"
IRQ = "IRQ"
NMI = "NMI"
RESET = "RESET"

PAGE = "PAGE"

INSTRUCTION_DICT = get_global_keys(ignore_keys)
INSTRUCTIONS = list(INSTRUCTION_DICT.keys())
INSTRUCTIONS.sort()


ignore_keys = list(globals().keys()) # hack

# registers:
REG_A = "A"
REG_PC = "PC"
REG_S = "S"
REG_B = "B"
REG_U = "U"
REG_D = "D"
REG_Y = "Y"
REG_X = "X"
REG_CC = "CC"
REG_DP = "DP"

REGISTER_DICT = get_global_keys(ignore_keys)
REGISTERS = list(REGISTER_DICT.keys())
REGISTERS.sort()

REGISTER_DICT2 = dict((v, k) for k, v in list(REGISTER_DICT.items()))


REGISTER_INFO = {
    REG_D: (16, "0000", "concatenated register (A+B)"),
    REG_X: (16, "0001", "index register"),
    REG_Y: (16, "0010", "index register"),
    REG_U: (16, "0011", "user-stack pointer"),
    REG_S: (16, "0100", "system-stack pointer"),
    REG_PC: (16, "0101", "program counter register"),
    REG_A: (8, "1000", "accumulator"),
    REG_B: (8, "1001", "accumulator"),
    REG_CC: (8, "1010", "condition code register as flags"),
    REG_DP: (8, "1011", "direct page register"),
}


op_info_dict = {
    0x0: ("NEG", DIRECT),
    0x3: ("COM", DIRECT),
    0x4: ("LSR", DIRECT),
    0x6: ("ROR", DIRECT),
    0x7: ("ASR", DIRECT),
    0x8: ("LSL", DIRECT),
    0x9: ("ROL", DIRECT),
    0xa: ("DEC", DIRECT),
    0xc: ("INC", DIRECT),
    0xd: ("TST", DIRECT),
    0xe: ("JMP", DIRECT),
    0xf: ("CLR", DIRECT),

    0x10: ("PAGE 1", None),
    0x11: ("PAGE 2", None),

    0x12: ("NOP", INHERENT),
    0x13: ("SYNC", INHERENT),
    0x16: ("LBRA", RELATIVE_WORD),
    0x17: ("LBSR", RELATIVE_WORD),
    0x19: ("DAA", INHERENT),
    0x1a: ("ORCC", IMMEDIATE),
    0x1c: ("ANDCC", IMMEDIATE),
    0x1d: ("SEX", INHERENT),
    0x1e: ("EXG", IMMEDIATE),
    0x1f: ("TFR", IMMEDIATE),
    0x20: ("BRA", RELATIVE),
    0x21: ("BRN", RELATIVE),
    0x22: ("BHI", RELATIVE),
    0x23: ("BLS", RELATIVE),
    0x24: ("BCC", RELATIVE),
    0x25: ("BLO", RELATIVE),
    0x26: ("BNE", RELATIVE),
    0x27: ("BEQ", RELATIVE),
    0x28: ("BVC", RELATIVE),
    0x29: ("BVS", RELATIVE),
    0x2a: ("BPL", RELATIVE),
    0x2b: ("BMI", RELATIVE),
    0x2c: ("BGE", RELATIVE),
    0x2d: ("BLT", RELATIVE),
    0x2e: ("BGT", RELATIVE),
    0x2f: ("BLE", RELATIVE),
    0x30: ("LEAX", INDEXED),
    0x31: ("LEAY", INDEXED),
    0x32: ("LEAS", INDEXED),
    0x33: ("LEAU", INDEXED),
    0x34: ("PSHS", IMMEDIATE),
    0x35: ("PULS", IMMEDIATE),
    0x36: ("PSHU", IMMEDIATE),
    0x37: ("PULU", IMMEDIATE),
    0x39: ("RTS", INHERENT),
    0x3a: ("ABX", INHERENT),
    0x3b: ("RTI", INHERENT),
    0x3c: ("CWAI", IMMEDIATE),
    0x3d: ("MUL", INHERENT),
    0x3e: ("RESET", None), # undocumented opcode
    0x3f: ("SWI", INHERENT),
    0x40: ("NEGA", INHERENT),
    0x43: ("COMA", INHERENT),
    0x44: ("LSRA", INHERENT),
    0x46: ("RORA", INHERENT),
    0x47: ("ASRA", INHERENT),
    0x48: ("LSLA", INHERENT),
    0x49: ("ROLA", INHERENT),
    0x4a: ("DECA", INHERENT),
    0x4c: ("INCA", INHERENT),
    0x4d: ("TSTA", INHERENT),
    0x4f: ("CLRA", INHERENT),
    0x50: ("NEGB", INHERENT),
    0x53: ("COMB", INHERENT),
    0x54: ("LSRB", INHERENT),
    0x56: ("RORB", INHERENT),
    0x57: ("ASRB", INHERENT),
    0x58: ("LSLB", INHERENT),
    0x59: ("ROLB", INHERENT),
    0x5a: ("DECB", INHERENT),
    0x5c: ("INCB", INHERENT),
    0x5d: ("TSTB", INHERENT),
    0x5f: ("CLRB", INHERENT),
    0x60: ("NEG", INDEXED),
    0x63: ("COM", INDEXED),
    0x64: ("LSR", INDEXED),
    0x66: ("ROR", INDEXED),
    0x67: ("ASR", INDEXED),
    0x68: ("LSL", INDEXED),
    0x69: ("ROL", INDEXED),
    0x6a: ("DEC", INDEXED),
    0x6c: ("INC", INDEXED),
    0x6d: ("TST", INDEXED),
    0x6e: ("JMP", INDEXED),
    0x6f: ("CLR", INDEXED),
    0x70: ("NEG", EXTENDED),
    0x73: ("COM", EXTENDED),
    0x74: ("LSR", EXTENDED),
    0x76: ("ROR", EXTENDED),
    0x77: ("ASR", EXTENDED),
    0x78: ("LSL", EXTENDED),
    0x79: ("ROL", EXTENDED),
    0x7a: ("DEC", EXTENDED),
    0x7c: ("INC", EXTENDED),
    0x7d: ("TST", EXTENDED),
    0x7e: ("JMP", EXTENDED),
    0x7f: ("CLR", EXTENDED),
    0x80: ("SUBA", IMMEDIATE),
    0x81: ("CMPA", IMMEDIATE),
    0x82: ("SBCA", IMMEDIATE),
    0x83: ("SUBD", IMMEDIATE_WORD),
    0x84: ("ANDA", IMMEDIATE),
    0x85: ("BITA", IMMEDIATE),
    0x86: ("LDA", IMMEDIATE),
    0x88: ("EORA", IMMEDIATE),
    0x89: ("ADCA", IMMEDIATE),
    0x8a: ("ORA", IMMEDIATE),
    0x8b: ("ADDA", IMMEDIATE),
    0x8c: ("CMPX", IMMEDIATE_WORD),
    0x8d: ("BSR", RELATIVE),
    0x8e: ("LDX", IMMEDIATE_WORD),
    0x90: ("SUBA", DIRECT),
    0x91: ("CMPA", DIRECT),
    0x92: ("SBCA", DIRECT),
    0x93: ("SUBD", DIRECT),
    0x94: ("ANDA", DIRECT),
    0x95: ("BITA", DIRECT),
    0x96: ("LDA", DIRECT),
    0x97: ("STA", DIRECT),
    0x98: ("EORA", DIRECT),
    0x99: ("ADCA", DIRECT),
    0x9a: ("ORA", DIRECT),
    0x9b: ("ADDA", DIRECT),
    0x9c: ("CMPX", DIRECT),
    0x9d: ("JSR", DIRECT),
    0x9e: ("LDX", DIRECT),
    0x9f: ("STX", DIRECT),
    0xa0: ("SUBA", INDEXED),
    0xa1: ("CMPA", INDEXED),
    0xa2: ("SBCA", INDEXED),
    0xa3: ("SUBD", INDEXED),
    0xa4: ("ANDA", INDEXED),
    0xa5: ("BITA", INDEXED),
    0xa6: ("LDA", INDEXED),
    0xa7: ("STA", INDEXED),
    0xa8: ("EORA", INDEXED),
    0xa9: ("ADCA", INDEXED),
    0xaa: ("ORA", INDEXED),
    0xab: ("ADDA", INDEXED),
    0xac: ("CMPX", INDEXED),
    0xad: ("JSR", INDEXED),
    0xae: ("LDX", INDEXED),
    0xaf: ("STX", INDEXED),
    0xb0: ("SUBA", EXTENDED),
    0xb1: ("CMPA", EXTENDED),
    0xb2: ("SBCA", EXTENDED),
    0xb3: ("SUBD", EXTENDED),
    0xb4: ("ANDA", EXTENDED),
    0xb5: ("BITA", EXTENDED),
    0xb6: ("LDA", EXTENDED),
    0xb7: ("STA", EXTENDED),
    0xb8: ("EORA", EXTENDED),
    0xb9: ("ADCA", EXTENDED),
    0xba: ("ORA", EXTENDED),
    0xbb: ("ADDA", EXTENDED),
    0xbc: ("CMPX", EXTENDED),
    0xbd: ("JSR", EXTENDED),
    0xbe: ("LDX", EXTENDED),
    0xbf: ("STX", EXTENDED),
    0xc0: ("SUBB", IMMEDIATE),
    0xc1: ("CMPB", IMMEDIATE),
    0xc2: ("SBCB", IMMEDIATE),
    0xc3: ("ADDD", IMMEDIATE_WORD),
    0xc4: ("ANDB", IMMEDIATE),
    0xc5: ("BITB", IMMEDIATE),
    0xc6: ("LDB", IMMEDIATE),
    0xc8: ("EORB", IMMEDIATE),
    0xc9: ("ADCB", IMMEDIATE),
    0xca: ("ORB", IMMEDIATE),
    0xcb: ("ADDB", IMMEDIATE),
    0xcc: ("LDD", IMMEDIATE_WORD),
    0xce: ("LDU", IMMEDIATE_WORD),
    0xd0: ("SUBB", DIRECT),
    0xd1: ("CMPB", DIRECT),
    0xd2: ("SBCB", DIRECT),
    0xd3: ("ADDD", DIRECT),
    0xd4: ("ANDB", DIRECT),
    0xd5: ("BITB", DIRECT),
    0xd6: ("LDB", DIRECT),
    0xd7: ("STB", DIRECT),
    0xd8: ("EORB", DIRECT),
    0xd9: ("ADCB", DIRECT),
    0xda: ("ORB", DIRECT),
    0xdb: ("ADDB", DIRECT),
    0xdc: ("LDD", DIRECT),
    0xdd: ("STD", DIRECT),
    0xde: ("LDU", DIRECT),
    0xdf: ("STU", DIRECT),
    0xe0: ("SUBB", INDEXED),
    0xe1: ("CMPB", INDEXED),
    0xe2: ("SBCB", INDEXED),
    0xe3: ("ADDD", INDEXED),
    0xe4: ("ANDB", INDEXED),
    0xe5: ("BITB", INDEXED),
    0xe6: ("LDB", INDEXED),
    0xe7: ("STB", INDEXED),
    0xe8: ("EORB", INDEXED),
    0xe9: ("ADCB", INDEXED),
    0xea: ("ORB", INDEXED),
    0xeb: ("ADDB", INDEXED),
    0xec: ("LDD", INDEXED),
    0xed: ("STD", INDEXED),
    0xee: ("LDU", INDEXED),
    0xef: ("STU", INDEXED),
    0xf0: ("SUBB", EXTENDED),
    0xf1: ("CMPB", EXTENDED),
    0xf2: ("SBCB", EXTENDED),
    0xf3: ("ADDD", EXTENDED),
    0xf4: ("ANDB", EXTENDED),
    0xf5: ("BITB", EXTENDED),
    0xf6: ("LDB", EXTENDED),
    0xf7: ("STB", EXTENDED),
    0xf8: ("EORB", EXTENDED),
    0xf9: ("ADCB", EXTENDED),
    0xfa: ("ORB", EXTENDED),
    0xfb: ("ADDB", EXTENDED),
    0xfc: ("LDD", EXTENDED),
    0xfd: ("STD", EXTENDED),
    0xfe: ("LDU", EXTENDED),
    0xff: ("STU", EXTENDED),

    0x1021: ("LBRN", RELATIVE_WORD),
    0x1022: ("LBHI", RELATIVE_WORD),
    0x1023: ("LBLS", RELATIVE_WORD),
    0x1024: ("LBCC", RELATIVE_WORD),
    0x1025: ("LBCS", RELATIVE_WORD),
    0x1026: ("LBNE", RELATIVE_WORD),
    0x1027: ("LBEQ", RELATIVE_WORD),
    0x1028: ("LBVC", RELATIVE_WORD),
    0x1029: ("LBVS", RELATIVE_WORD),
    0x102a: ("LBPL", RELATIVE_WORD),
    0x102b: ("LBMI", RELATIVE_WORD),
    0x102c: ("LBGE", RELATIVE_WORD),
    0x102d: ("LBLT", RELATIVE_WORD),
    0x102e: ("LBGT", RELATIVE_WORD),
    0x102f: ("LBLE", RELATIVE_WORD),
    0x103f: ("SWI2", INHERENT),
    0x1083: ("CMPD", IMMEDIATE_WORD),
    0x108c: ("CMPY", IMMEDIATE_WORD),
    0x108e: ("LDY", IMMEDIATE_WORD),
    0x1093: ("CMPD", DIRECT),
    0x109c: ("CMPY", DIRECT),
    0x109e: ("LDY", DIRECT),
    0x109f: ("STY", DIRECT),
    0x10a3: ("CMPD", INDEXED),
    0x10ac: ("CMPY", INDEXED),
    0x10ae: ("LDY", INDEXED),
    0x10af: ("STY", INDEXED),
    0x10b3: ("CMPD", EXTENDED),
    0x10bc: ("CMPY", EXTENDED),
    0x10be: ("LDY", EXTENDED),
    0x10bf: ("STY", EXTENDED),
    0x10ce: ("LDS", IMMEDIATE_WORD),
    0x10de: ("LDS", DIRECT),
    0x10df: ("STS", DIRECT),
    0x10ee: ("LDS", INDEXED),
    0x10ef: ("STS", INDEXED),
    0x10fe: ("LDS", EXTENDED),
    0x10ff: ("STS", EXTENDED),

    0x113f: ("SWI3", INHERENT),
    0x1183: ("CMPU", IMMEDIATE_WORD),
    0x118c: ("CMPS", IMMEDIATE_WORD),
    0x1193: ("CMPU", DIRECT),
    0x119c: ("CMPS", DIRECT),
    0x11a3: ("CMPU", INDEXED),
    0x11ac: ("CMPS", INDEXED),
    0x11b3: ("CMPU", EXTENDED),
    0x11bc: ("CMPS", EXTENDED),
}

ALIAS = {
    "ASL": "LSL",
    "ASLA": "LSLA",
    "ASLB": "LSLB",
    "BCC": "BHS",
    "BCS": "BLO",
    "LBCC": "LBHS",
    "LBCS": "LBLO",
}

SHORT_DESC = {
    "ABX":"X = B+X (Unsigned)",
    "ADCA":"A = A+M+C",
    "ADCB":"B = B+M+C",
    "ADDA":"A = A+M",
    "ADDB":"B = B+M",
    "ADDD":"D = D+M:M+1",
    "ANDA":"A = A && M",
    "ANDB":"B = B && M",
    "ANDCC":"C = CC && IMM",
    "ASLA":"A = Arithmetic shift A left",
    "ASLB":"B = Arithmetic shift B left",
    "ASL":"M = Arithmetic shift M left",
    "ASRA":"A = Arithmetic shift A right",
    "ASRB":"B = Arithmetic shift B right",
    "ASR":"M = Arithmetic shift M right",
    "BITA":"Bit Test A (M&&A)",
    "BITB":"Bit Test B (M&&B)",
    "CLRA":"A = 0",
    "CLRB":"B = 0",
    "CLR":"M = 0",
    "CMPA":"Compare M from A",
    "CMPB":"Compare M from B",
    "CMPD":"Compare M:M+1 from D",
    "CMPS":"Compare M:M+1 from S",
    "CMPU":"Compare M:M+1 from U",
    "CMPX":"Compare M:M+1 from X",
    "CMPY":"Compare M:M+1 from Y",
    "COMA":"A = complement(A)",
    "COMB":"B = complement(B)",
    "COM":"M = complement(M)",
    "CWAI":"CC = CC ^ IMM; (Wait for Interrupt)",
    "DAA":"Decimal Adjust A",
    "DECA":"A = A - 1",
    "DECB":"B = B - 1",
    "DEC":"M = M - 1",
    "EORA":"A = A XOR M",
    "EORB":"B = M XOR B",
    "EXG":"exchange R1,R2",
    "INCA":"A = A + 1",
    "INCB":"B = B + 1",
    "INC":"M = M + 1",
    "JMP":"pc = EA",
    "JSR":"jump to subroutine",
    "LDA":"A = M",
    "LDB":"B = M",
    "LDD":"D = M:M+1",
    "LDS":"S = M:M+1",
    "LDU":"U = M:M+1",
    "LDX":"X = M:M+1",
    "LDY":"Y = M:M+1",
    "LEAS":"S = EA",
    "LEAU":"U = EA",
    "LEAX":"X = EA",
    "LEAY":"Y = EA",
    "LSLA":"A = Logical shift A left",
    "LSLB":"B = Logical shift B left",
    "LSL":"M = Logical shift M left",
    "LSRA":"A = Logical shift A right",
    "LSRB":"B = Logical shift B right",
    "LSR":"M = Logical shift M right",
    "MUL":"D = A*B (Unsigned)",
    "NEGA":"A = !A + 1",
    "NEGB":"B = !B + 1",
    "NEG":"M = !M + 1",
    "NOP":"No Operation",
    "ORA":"A = A || M",
    "ORB":"B = B || M",
    "ORCC":"C = CC || IMM",
    "PSHS":"S -= 1: MEM(S) = R; Push Register on S Stack",
    "PSHU":"U -= 1: MEM(U) = R; Push Register on U Stack",
    "PULS":"R=MEM(S) : S += 1; Pull register from S Stack",
    "PULU":"R=MEM(U) : U += 1; Pull register from U Stack",
    "ROLA":"A = Rotate A left thru carry",
    "ROLB":"B = Rotate B left thru carry",
    "ROL":"M = Rotate M left thru carry",
    "RORA":"A = Rotate A Right thru carry",
    "RORB":"B = Rotate B Right thru carry",
    "ROR":"M = Rotate M Right thru carry",
    "RTI":"Return from Interrupt",
    "RTS":"Return from subroutine",
    "SBCA":"A = A - M - C",
    "SBCB":"B = B - M - C",
    "SEX":"Sign extend B into A",
    "STA":"M = A",
    "STB":"M = B",
    "STD":"M:M+1 = D",
    "STS":"M:M+1 = S",
    "STU":"M:M+1 = U",
    "STX":"M:M+1 = X",
    "STY":"M:M+1 = Y",
    "SUBA":"A = A - M",
    "SUBB":"B = B - M",
    "SUBD":"D = D - M:M+1",
    "SWI":"Software interrupt 1",
    "SWI2":"Software interrupt 2",
    "SWI3":"Software interrupt 3",
    "SYNC":"Synchronize to Interrupt",
    "R1,R2":"Transfer R2 = R1",
    "TSTA":"Test A",
    "TSTB":"Test B",
    "TST":"Test M",

    "RESET":"Undocumented opcode",

    "PAGE 1":"Page 1 Instructions prefix",
    "PAGE 2":"Page 2 Instructions prefix",
}

NO_MEM_READ = (
    "PSHS", "PSHU", "PULS", "PULU",
)

MEM_READ = {
    "BITA":8,
    "BITB":8,

    "EXG":8,
    "TFR":8,
    "TST":8,

    "CMPA":8,
    "CMPB":8,
    "CMPD":16,
    "CMPS":16,
    "CMPU":16,
    "CMPX":16,
    "CMPY":16,
}

NEEDS_EA = (
    "CLR",
    "STA",
    "STB",
    "STD",
    "STS",
    "STU",
    "STX",
    "STY",

    # Branch ops:
    "BCC", "BHS",
    "BCS", "BLO",
    "BHI",
    "BLS",
    "BNE",
    "BEQ",
    "BGE",
    "BLT",
    "BGT",
    "BLE",
    "BPL",
    "BMI",
    "BVC",
    "BVS",
    "BRA",
    "BRN",
    "BSR",
    "JSR",
    "LBCC",
    "LBCS",
    "LBEQ",
    "LBGE",
    "LBGT",
    "LBHI",
    "LBLE",
    "LBLS",
    "LBLT",
    "LBMI",
    "LBNE",
    "LBPL",
    "LBRA",
    "LBRN",
    "LBSR",
    "LBVC",
    "LBVS",
)

INST_INFO_MERGE = {
    "PSHS": "PSH",
    "PSHU": "PSH",
    "PULS": "PUL",
    "PULU": "PUL",
}


# op_types = {
#     0x0: ("True", DIRECT),
#     0x4: ("False", REG_A),
#     0x5: ("False", REG_B),
#     0x6: ("True", INDEXED),
#     0x7: ("True", EXTENDED),
# }
#
# OVERWRITE_DATA = {}
# for op in ops:
#     t = (op >> 4) & 0xf
#     op_type = op_types[t]
# #     print hex(op)", op_type
#     OVERWRITE_DATA[op] = op_type


# for op_data in OP_DATA:
#     mnemonic = op_data["mnemonic"]
#     if "/" in mnemonic:
#         m = mnemonic.split("/")
#         print '    "%s": "%s",' % (m[1], m[0])



def get_instruction(mnemonic):
    if mnemonic in ALIAS:
        mnemonic = ALIAS[mnemonic]
    for inst in INSTRUCTIONS:
        if mnemonic.startswith(inst):
            return inst

    if mnemonic.startswith("L"):
        mnemonic = mnemonic[1:]
        return get_instruction(mnemonic)




def add_the_same(d, key, value):
    if key in d:
        assert d[key] == value, "key: %s - value: %s - d:%s" % (key, value, repr(d))
    else:
        d[key] = value



OP_DATA_DICT = dict([(op["opcode"], op) for op in OP_DATA])

def verbose(value):
    if value is None:
        return ""
    if value is True:
        return "yes"
    if value is False:
        return ""
    return value


with open("MC6809_data_raw2.csv", 'wb') as csvfile:
    w = csv.writer(csvfile,
        delimiter=';',
        quotechar='"', quoting=csv.QUOTE_MINIMAL
    )

    w.writerow([
        "instr.", "opcode", "dez", "mnemonic", "register",
        "needs ea", "read", "write", "addr.mode", "H", "N", "Z", "V", "C", "desc", "category",
    ])


    MC6809_DATA = {}
    for op_code, op_info in sorted(list(op_info_dict.items()), key=lambda i: i[1]):
        mnemonic, addr_mode = op_info
    #     if mnemonic.startswith("LB"):
    #         print '"%s",' % mnemonic
    #     continue

        instruction = get_instruction(mnemonic)
        if not instruction:
            raise KeyError("Error with %s" % mnemonic)

        if instruction in INST_INFO_MERGE:
            instruction = INST_INFO_MERGE[instruction]

        if mnemonic.startswith(instruction):
            register = mnemonic[len(instruction):].strip()
    #         print mnemonic, register
            if register.isdigit() or register == "":
                register = None
            else:
                register = REGISTER_DICT2[register.upper()]
        else:
            register = None

        desc = SHORT_DESC.get(mnemonic, None)

        needs_ea = False
        if mnemonic in NEEDS_EA:
            needs_ea = True

        read_from_memory = None
        write_to_memory = None
        if desc is not None:
            if "=" in desc:
                right = desc.split("=")[1]
                if "M:M" in right:
                    read_from_memory = "WORD"
                elif "M" in right:
                    read_from_memory = "BYTE"
                elif "EA" in right:
                    needs_ea = True

            if desc.startswith("M:M"):
                write_to_memory = "WORD"
            elif desc.startswith("M ="):
                write_to_memory = "BYTE"

        if write_to_memory is not None:
            needs_ea = True

        if mnemonic in MEM_READ:
            width = MEM_READ[mnemonic]
            read_from_memory = WIDTH_DICT2[width]

        if read_from_memory is not None:
            if read_from_memory == "WORD":
                if not addr_mode.endswith("WORD"):
                    addr_mode += "_WORD" # XXX: really?

        if instruction not in MC6809_DATA:
            try:
                inst_info = INSTRUCTION_INFO[instruction]
            except KeyError:
                try:
                    # Was splitted into byte/word
                    inst_info = INSTRUCTION_INFO[instruction + "8"]
                except KeyError:
                    # e.g.: PULS, PULU -> merge together
                    inst_info = INSTRUCTION_INFO[mnemonic]

            MC6809_DATA[instruction] = inst_info

        old_info = OP_DATA_DICT[op_code]
        CC_info = old_info["HNZVC"]

        category_id = old_info["category"]
        category = OP_CATEGORIES[category_id]
        row = (
            instruction, "$%02x" % op_code, op_code, mnemonic,
            verbose(register), verbose(needs_ea),
            verbose(read_from_memory), verbose(write_to_memory), verbose(addr_mode),
            CC_info[0], CC_info[1], CC_info[2], CC_info[3], CC_info[4],
            desc, category
        )
        w.writerow(row)
        print("\t".join([repr(i).strip("'") for i in row]))
        

        instr_dict = MC6809_DATA[instruction]
        instr_dict['description'] = instr_dict.get('description', "").strip()

        mnemonic_dict1 = instr_dict.setdefault("mnemonic", {})
        mnemonic_dict = mnemonic_dict1.setdefault(mnemonic, {})

        add_the_same(mnemonic_dict, "desc", desc)
        add_the_same(mnemonic_dict, "register", register)
        add_the_same(mnemonic_dict, "needs_ea", needs_ea)

        add_the_same(mnemonic_dict, "read_from_memory", read_from_memory)
        add_the_same(mnemonic_dict, "write_to_memory", write_to_memory)

        add_the_same(mnemonic_dict, "HNZVC", CC_info)

        ops_dict = mnemonic_dict.setdefault("ops", {})

        ops_dict[op_code] = {
            "addr_mode": addr_mode,
        }
        for key in ("cycles", "bytes"):
            ops_dict[op_code][key] = old_info[key]




sys.stdout = Tee("MC6809_data_raw2.py", sys.stdout,
    to_stdout=True
#     to_stdout=False
)


def print_constants(keys, d):
    for k in keys:
        print('%s = "%s"' % (k, d[k]))
    print()

print("#!/usr/bin/env python")
print()
print('"""%s"""' % __doc__)

print()
print("# this file was generated with %s" % os.path.split(__file__)[1])
print()

print_constants(WIDTHS, WIDTH_DICT)

print("\n# Address modes:")
print_constants(ADDR_MODES, ADDR_MODE_DICT)

print("\n# Registers:")
print_constants(REGISTERS, REGISTER_DICT)

print("\n# Instructions:")
print_constants(INSTRUCTIONS, INSTRUCTION_DICT)



print("\n"*2)

CONSTANTS = ADDR_MODES[:]
CONSTANTS += INSTRUCTIONS
CONSTANTS += REGISTERS
CONSTANTS += WIDTHS

class HexPrettyPrinter(pprint.PrettyPrinter, object):
    """ print values in hex """
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, int):
            if level == 5: # XXX: Only opcode should be hex()
                return hex(obj), True, False

        if obj in CONSTANTS:
            return obj, True, False
        return super(HexPrettyPrinter, self).format(obj, context, maxlevels, level)

printer = HexPrettyPrinter(indent=0, width=1)
print("OP_DATA = %s" % printer.pformat(MC6809_DATA))


# pprint.pprint(CONSTANTS_DICT)




# for instruction, inst_data in sorted(MC6809_DATA.items()):
#     print "%s: {" % instruction
#     for inst_info_key, inst_info_data in sorted(inst_data.items()):
#         spaces = " "*4
#         if inst_info_key != "mnemonic":
#             print '%s"%s": {' % (spaces, inst_info_key)
#     print "}"
#     break


sys.stdout.close()
print(" -- END -- ")
