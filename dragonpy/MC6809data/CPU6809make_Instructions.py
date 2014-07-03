#!/usr/bin/env python

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

from appendix_a import INSTRUCTION_INFO

INSTRUCTION_INFO.update({
    'PAGE': {'addressing mode': 'VARIANT', 'description': 'Page 1/2 instructions'},
    'RESET': {'addressing mode': 'INHERENT',
        'description': ' Build the ASSIST09 vector table and setup monitor defaults, then invoke the monitor startup routine.'
    },
})

# overwrite the examples for push/pull register:
INSTRUCTION_INFO['PSHS']['operation'] = "Push Registers on S Stack: S -= 1: MEM(S) = Reg."
INSTRUCTION_INFO['PSHU']['operation'] = "Push Registers on U Stack: U -= 1: MEM(U) = Reg."
INSTRUCTION_INFO['PULS']['operation'] = "Pull Registers from S Stack: Reg. = MEM(S): S += 1"
INSTRUCTION_INFO['PULU']['operation'] = "Pull Registers from U Stack: Reg. = MEM(U): U += 1"
INSTRUCTION_INFO['DAA']['operation'] = "Decimal Adjust A"


OpDescriptions = {}
categories = {
    0: "8-Bit Accumulator and Memory Instructions",
    1: "16-Bit Accumulator and Memory Instructions Instruction",
    2: "Index/Stack Pointer Instructions",
    3: "Simple Branch Instructions",
    4: "Signed Branch Instructions",
    5: "Unsigned Branch Instructions",
    6: "other Branch Instructions",
    7: "Miscellaneous Instructions",
    8: "other",
}

OTHER_INSTRUCTIONS = "OTHER_INSTRUCTIONS"
CHANGE_INSTRUCTIONS = {
    "PAGE1+": "PAGE",
    "PAGE2+": "PAGE",
    "SWI2": "SWI",
    "SWI3": "SWI",
    "RESET*": "RESET",

#     "BHS/BCC": "BCC",
}
CHANGED_INSTRUCTIONS = tuple(CHANGE_INSTRUCTIONS.values())

EXTENDED = "EXTENDED"
VARIANT = "VARIANT"
DIRECT = "DIRECT"
IMMEDIATE = "IMMEDIATE"
RELATIVE = "RELATIVE"
INDEXED = "INDEXED"
INHERENT = "INHERENT"

ADDRES_MODES = (EXTENDED, VARIANT, DIRECT, IMMEDIATE, RELATIVE, INDEXED, INHERENT)
ADDRES_MODE_DICT = dict([(i, i) for i in ADDRES_MODES])

MEM_ACCESS_BYTE = "MEM_ACCESS_BYTE"
MEM_ACCESS_WORD = "MEM_ACCESS_WORD"

INSTRUCTIONS = (
    "ABX", "ADC", "ADD", "AND", "ASL", "ASR", "BCC", "BCS", "BEQ", "BGE", "BGT", "BHI", "BHS",
    "BIT", "BLE", "BLO", "BLS", "BLT", "BMI", "BNE", "BPL", "BRA", "BRN", "BSR", "BVC", "BVS",
    "CLR", "CMP", "COM", "CWAI", "DAA", "DEC", "EOR", "EXG", "INC", "JMP", "JSR", "LD", "LEA",
    "LSL", "LSR", "MUL", "NEG", "NOP", "OR", "PSHS", "PSHU", "PULS", "PULU", "ROL", "ROR",
    "RTI", "RTS", "SBC", "SEX", "ST", "SUB", "SWI", "SWI2", "SWI3", "SYNC", "TFR", "TST",
    "FIRQ", "IRQ", "NMI", "RESET"
)
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
REGISTERS = REGISTER_INFO.keys()

#------------------------------------------------------------------------------

ops = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0f,
    0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4f,
    0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5f,
    0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6f,
    0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7f
]

op_types = {
    0x0: (True, DIRECT),
    0x4: (False, REG_A),
    0x5: (False, REG_B),
    0x6: (True, INDEXED),
    0x7: (True, EXTENDED),
}

OVERWRITE_DATA = {}
for op in ops:
    t = (op >> 4) & 0xf
    op_type = op_types[t]
#     print hex(op), op_type
    OVERWRITE_DATA[op] = op_type

#------------------------------------------------------------------------------

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
    "DECA":"A = A  1",
    "DECB":"B = B  1",
    "DEC":"M = M  1",
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

    "PAGE1+":"Page 1 Instructions prefix",
    "PAGE2+":"Page 2 Instructions prefix",
}

NO_MEM_READ = (
    "PSHS", "PSHU", "PULS", "PULU",
)

#------------------------------------------------------------------------------


illegal = []

def add(category_id, txt):
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ops, desc = line.split("\t")
        except ValueError:
            ops, desc = line.split(" ", 1)
            ops = ops.strip()
            desc = desc.strip()
        ops = [o.strip() for o in ops.split(",")]
        for op in ops:
            OpDescriptions[op] = (category_id, desc)


add(0, """ADCA, ADCB	Add memory to accumulator with carry
ADDA, ADDB	Add memory to accumulator
ANDA, ANDB	AND memory with accumulator
ASL, ASLA, ASLB	Arithmetic shift of accumulator or memory left
ASR, ASRA, ASRB	Arithmetic shift of accumulator or memory right
BITA, BITB	Bit test memory with accumulator
CLR, CLRA, CLRB	Clear accumulator or memory location
CMPA, CMPB	Compare memory from accumulator
COM, COMA, COMB	Complement accumulator or memory location
DAA	Decimal adjust A accumulator
DEC, DECA, DECB	Decrement accumulator or memory location
EORA, EORB	Exclusive OR memory with accumulator
EXG 	Exchange Rl with R2
INC, INCA, INCB	Increment accumulator or memory location
LDA, LDB	Load accumulator from memory
LSL, LSLA, LSLB	Logical shift left accumulator or memory location
LSR, LSRA, LSRB	Logical shift right accumulator or memory location
MUL	Unsigned multiply (A * B ? D)
NEG, NEGA, NEGB	Negate accumulator or memory
ORA, ORB	OR memory with accumulator
ROL, ROLA, ROLB	Rotate accumulator or memory left
ROR, RORA, RORB	Rotate accumulator or memory right
SBCA, SBCB	Subtract memory from accumulator with borrow
STA, STB	Store accumulator to memroy
SUBA, SUBB	Subtract memory from accumulator
TST, TSTA, TSTB	Test accumulator or memory location
TFR 	Transfer R1 to R2
""")

add(1, """
ADDD	Add memory to D accumulator
CMPD	Compare memory from D accumulator
LDD	Load D accumulator from memory
SEX	Sign Extend B accumulator into A accumulator
STD	Store D accumulator to memory
SUBD	Subtract memory from D accumulator
""")

add(2, """
CMPS, CMPU	Compare memory from stack pointer
CMPX, CMPY	Compare memory from index register
LEAS, LEAU	Load effective address into stack pointer
LEAX, LEAY	Load effective address into index register
LDS, LDU	Load stack pointer from memory
LDX, LDY	Load index register from memory
PSHS	Push A, B, CC, DP, D, X, Y, U, or PC onto hardware stack
PSHU	Push A, B, CC, DP, D, X, Y, S, or PC onto user stack
PULS	Pull A, B, CC, DP, D, X, Y, U, or PC from hardware stack
PULU	Pull A, B, CC, DP, D, X, Y, S, or PC from hardware stack
STS, STU	Store stack pointer to memory
STX, STY	Store index register to memory
ABX	Add B accumulator to X (unsigned)
""")

add(3, """
BEQ, LBEQ	Branch if equal
BNE, LBNE	Branch if not equal
BMI, LBMI	Branch if minus
BPL, LBPL	Branch if plus
BCS, LBCS	Branch if carry set
BCC, LBCC	Branch if carry clear
BVS, LBVS	Branch if overflow set
BVC, LBVC	Branch if overflow clear
""")

add(4, """
BGT, LBGT	Branch if greater (signed)
BVS, LBVS	Branch if invalid twos complement result
BGE, LBGE	Branch if greater than or equal (signed)
BEQ, LBEQ	Branch if equal
BNE, LBNE	Branch if not equal
BLE, LBLE	Branch if less than or equal (signed)
BVC, LBVC	Branch if valid twos complement result
BLT, LBLT	Branch if less than (signed)
""")

add(5, """
BHI, LBHI	Branch if higher (unsigned)
BCC, LBCC	Branch if higher or same (unsigned)
BHS, LBHS	Branch if higher or same (unsigned)
BEQ, LBEQ	Branch if equal
BNE, LBNE	Branch if not equal
BLS, LBLS	Branch if lower or same (unsigned)
BCS, LBCS	Branch if lower (unsigned)
BLO, LBLO	Branch if lower (unsigned)
""")

add(6, """
BSR, LBSR	Branch to subroutine
BRA, LBRA	Branch always
BRN, LBRN	Branch never
""")

add(7, """
ANDCC	AND condition code register
CWAI	AND condition code register, then wait for interrupt
NOP	No operation
ORCC	OR condition code register
JMP	Jump
JSR	Jump to subroutine
RTI	Return from interrupt
RTS	Return from subroutine
SWI, SWI2, SWI3	Software interrupt (absolute indirect)
SYNC	Synchronize with interrupt line
""")

add(8, """
PAGE1+    Page 1 Instructions prefix
PAGE2+    Page 2 Instructions prefix
""")

txt = """ +-----------------------------------------------------------------+
 |                       Page 0 Instructions                       |
 +------------+-------------+--------------+---------------+-------+
 | Opcode     |             | Addressing   |               |       |
 | Hex   Dec  | Instruction | Mode         | Cycles  Bytes | HNZVC |
 +------------+-------------+--------------+-------+-------+-------+
 | 00    0000 | NEG         | DIRECT       |   6   |   2   | uaaaa |
 | 01    0001 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 02    0002 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 03    0003 | COM         | DIRECT       |   6   |   2   | -aa01 |
 | 04    0004 | LSR         | DIRECT       |   6   |   2   | -0a-s |
 | 05    0005 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 06    0006 | ROR         | DIRECT       |   6   |   2   | -aa-s |
 | 07    0007 | ASR         | DIRECT       |   6   |   2   | uaa-s |
 | 08    0008 | LSL/ASL     | DIRECT       |   6   |   2   | naaas |
 | 09    0009 | ROL         | DIRECT       |   6   |   2   | -aaas |
 | 0A    0010 | DEC         | DIRECT       |   6   |   2   | -aaa- |
 | 0B    0011 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 0C    0012 | INC         | DIRECT       |   6   |   2   | -aaa- |
 | 0D    0013 | TST         | DIRECT       |   6   |   2   | -aa0- |
 | 0E    0014 | JMP         | DIRECT       |   3   |   2   | ----- |
 | 0F    0015 | CLR         | DIRECT       |   6   |   2   | -0100 |
 | 10    0016 | PAGE1+      | VARIANT      |   1   |   1   | +++++ |
 | 11    0017 | PAGE2+      | VARIANT      |   1   |   1   | +++++ |
 | 12    0018 | NOP         | INHERENT     |   2   |   1   | ----- |
 | 13    0019 | SYNC        | INHERENT     |   2   |   1   | ----- |
 | 14    0020 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 15    0021 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 16    0022 | LBRA        | RELATIVE     |   5   |   3   | ----- |
 | 17    0023 | LBSR        | RELATIVE     |   9   |   3   | ----- |
 | 18    0024 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 19    0025 | DAA         | INHERENT     |   2   |   1   | -aa0a |
 | 1A    0026 | ORCC        | IMMEDIATE    |   3   |   2   | ddddd |
 | 1B    0027 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 1C    0028 | ANDCC       | IMMEDIATE    |   3   |   2   | ddddd |
 | 1D    0029 | SEX         | INHERENT     |   2   |   1   | -aa0- |
 | 1E    0030 | EXG         | Immediate    |   8   |   2   | ccccc |
 | 1F    0031 | TFR         | Immediate    |   7   |   2   | ccccc |
 | 20    0032 | BRA         | RELATIVE     |   3   |   2   | ----- |
 | 21    0033 | BRN         | RELATIVE     |   3   |   2   | ----- |
 | 22    0034 | BHI         | RELATIVE     |   3   |   2   | ----- |
 | 23    0035 | BLS         | RELATIVE     |   3   |   2   | ----- |
 | 24    0036 | BHS/BCC     | RELATIVE     |   3   |   2   | ----- |
 | 25    0037 | BLO/BCS     | RELATIVE     |   3   |   2   | ----- |
 | 26    0038 | BNE         | RELATIVE     |   3   |   2   | ----- |
 | 27    0039 | BEQ         | RELATIVE     |   3   |   2   | ----- |
 | 28    0040 | BVC         | RELATIVE     |   3   |   2   | ----- |
 | 29    0041 | BVS         | RELATIVE     |   3   |   2   | ----- |
 | 2A    0042 | BPL         | RELATIVE     |   3   |   2   | ----- |
 | 2B    0043 | BMI         | RELATIVE     |   3   |   2   | ----- |
 | 2C    0044 | BGE         | RELATIVE     |   3   |   2   | ----- |
 | 2D    0045 | BLT         | RELATIVE     |   3   |   2   | ----- |
 | 2E    0046 | BGT         | RELATIVE     |   3   |   2   | ----- |
 | 2F    0047 | BLE         | RELATIVE     |   3   |   2   | ----- |
 | 30    0048 | LEAX        | INDEXED      |   4   |   2   | --a-- |
 | 31    0049 | LEAY        | INDEXED      |   4   |   2   | --a-- |
 | 32    0050 | LEAS        | INDEXED      |   4   |   2   | ----- |
 | 33    0051 | LEAU        | INDEXED      |   4   |   2   | ----- |
 | 34    0052 | PSHS        | Immediate    |   5   |   2   | ----- |
 | 35    0053 | PULS        | Immediate    |   5   |   2   | ccccc |
 | 36    0054 | PSHU        | Immediate    |   5   |   2   | ----- |
 | 37    0055 | PULU        | Immediate    |   5   |   2   | ccccc |
 | 38    0056 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 39    0057 | RTS         | INHERENT     |   5   |   1   | ----- |
 | 3A    0058 | ABX         | INHERENT     |   3   |   1   | ----- |
 | 3B    0059 | RTI         | INHERENT     | 6/15  |   1   | ----- |
 | 3C    0060 | CWAI        | Immediate    |  21   |   2   | ddddd |
 | 3D    0061 | MUL         | INHERENT     |  11   |   1   | --a-a |
 | 3E    0062 | RESET       | INHERENT     |   *   |   1   | ***** |
 | 3F    0063 | SWI         | INHERENT     |  19   |   1   | ----- |
 | 40    0064 | NEGA        | INHERENT     |   2   |   1   | uaaaa |
 | 41    0065 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 42    0066 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 43    0067 | COMA        | INHERENT     |   2   |   1   | -aa01 |
 | 44    0068 | LSRA        | INHERENT     |   2   |   1   | -0a-s |
 | 45    0069 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 46    0070 | RORA        | INHERENT     |   2   |   1   | -aa-s |
 | 47    0071 | ASRA        | INHERENT     |   2   |   1   | uaa-s |
 | 48    0072 | LSLA/ASLA   | INHERENT     |   2   |   1   | naaas |
 | 49    0073 | ROLA        | INHERENT     |   2   |   1   | -aaas |
 | 4A    0074 | DECA        | INHERENT     |   2   |   1   | -aaa- |
 | 4B    0075 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 4C    0076 | INCA        | INHERENT     |   2   |   1   | -aaa- |
 | 4D    0077 | TSTA        | INHERENT     |   2   |   1   | -aa0- |
 | 4E    0078 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 4F    0079 | CLRA        | INHERENT     |   2   |   1   | -0100 |
 | 50    0080 | NEGB        | INHERENT     |   2   |   1   | uaaaa |
 | 51    0081 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 52    0082 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 53    0083 | COMB        | INHERENT     |   2   |   1   | -aa01 |
 | 54    0084 | LSRB        | INHERENT     |   2   |   1   | -0a-s |
 | 55    0085 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 56    0086 | RORB        | INHERENT     |   2   |   1   | -aa-s |
 | 57    0087 | ASRB        | INHERENT     |   2   |   1   | uaa-s |
 | 58    0088 | LSLB/ASLB   | INHERENT     |   2   |   1   | naaas |
 | 59    0089 | ROLB        | INHERENT     |   2   |   1   | -aaas |
 | 5A    0090 | DECB        | INHERENT     |   2   |   1   | -aaa- |
 | 5B    0091 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 5C    0092 | INCB        | INHERENT     |   2   |   1   | -aaa- |
 | 5D    0093 | TSTB        | INHERENT     |   2   |   1   | -aa0- |
 | 5E    0094 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 5F    0095 | CLRB        | INHERENT     |   2   |   1   | -0100 |
 | 60    0096 | NEG         | INDEXED      |   6   |   2   | uaaaa |
 | 61    0097 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 62    0098 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 63    0099 | COM         | INDEXED      |   6   |   2   | -aa01 |
 | 64    0100 | LSR         | INDEXED      |   6   |   2   | -0a-s |
 | 65    0101 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 66    0102 | ROR         | INDEXED      |   6   |   2   | -aa-s |
 | 67    0103 | ASR         | INDEXED      |   6   |   2   | uaa-s |
 | 68    0104 | LSL/ASL     | INDEXED      |   6   |   2   | naaas |
 | 69    0105 | ROL         | INDEXED      |   6   |   2   | -aaas |
 | 6A    0106 | DEC         | INDEXED      |   6   |   2   | -aaa- |
 | 6B    0107 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 6C    0108 | INC         | INDEXED      |   6   |   2   | -aaa- |
 | 6D    0109 | TST         | INDEXED      |   6   |   2   | -aa0- |
 | 6E    0110 | JMP         | INDEXED      |   3   |   2   | ----- |
 | 6F    0111 | CLR         | INDEXED      |   6   |   2   | -0100 |
 | 70    0112 | NEG         | EXTENDED     |   7   |   3   | uaaaa |
 | 71    0113 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 72    0114 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 73    0115 | COM         | EXTENDED     |   7   |   3   | -aa01 |
 | 74    0116 | LSR         | EXTENDED     |   7   |   3   | -0a-s |
 | 75    0117 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 76    0118 | ROR         | EXTENDED     |   7   |   3   | -aa-s |
 | 77    0119 | ASR         | EXTENDED     |   7   |   3   | uaa-s |
 | 78    0120 | LSL/ASL     | EXTENDED     |   7   |   3   | naaas |
 | 79    0121 | ROL         | EXTENDED     |   7   |   3   | -aaas |
 | 7A    0122 | DEC         | EXTENDED     |   7   |   3   | -aaa- |
 | 7B    0123 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 7C    0124 | INC         | EXTENDED     |   7   |   3   | -aaa- |
 | 7D    0125 | TST         | EXTENDED     |   7   |   3   | -aa0- |
 | 7E    0126 | JMP         | EXTENDED     |   3   |   3   | ----- |
 | 7F    0127 | CLR         | EXTENDED     |   7   |   3   | -0100 |
 | 80    0128 | SUBA        | IMMEDIATE    |   2   |   2   | uaaaa |
 | 81    0129 | CMPA        | IMMEDIATE    |   2   |   2   | uaaaa |
 | 82    0130 | SBCA        | IMMEDIATE    |   2   |   2   | uaaaa |
 | 83    0131 | SUBD        | IMMEDIATE    |   4   |   3   | -aaaa |
 | 84    0132 | ANDA        | IMMEDIATE    |   2   |   2   | -aa0- |
 | 85    0133 | BITA        | IMMEDIATE    |   2   |   2   | -aa0- |
 | 86    0134 | LDA         | IMMEDIATE    |   2   |   2   | -aa0- |
 | 87    0135 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 88    0136 | EORA        | IMMEDIATE    |   2   |   2   | -aa0- |
 | 89    0137 | ADCA        | IMMEDIATE    |   2   |   2   | aaaaa |
 | 8A    0138 | ORA         | IMMEDIATE    |   2   |   2   | -aa0- |
 | 8B    0139 | ADDA        | IMMEDIATE    |   2   |   2   | aaaaa |
 | 8C    0140 | CMPX        | IMMEDIATE    |   4   |   3   | -aaaa |
 | 8D    0141 | BSR         | RELATIVE     |   7   |   2   | ----- |
 | 8E    0142 | LDX         | IMMEDIATE    |   3   |   3   | -aa0- |
 | 8F    0143 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | 90    0144 | SUBA        | DIRECT       |   4   |   2   | uaaaa |
 | 91    0145 | CMPA        | DIRECT       |   4   |   2   | uaaaa |
 | 92    0146 | SBCA        | DIRECT       |   4   |   2   | uaaaa |
 | 93    0147 | SUBD        | DIRECT       |   6   |   2   | -aaaa |
 | 94    0148 | ANDA        | DIRECT       |   4   |   2   | -aa0- |
 | 95    0149 | BITA        | DIRECT       |   4   |   2   | -aa0- |
 | 96    0150 | LDA         | DIRECT       |   4   |   2   | -aa0- |
 | 97    0151 | STA         | DIRECT       |   4   |   2   | -aa0- |
 | 98    0152 | EORA        | DIRECT       |   4   |   2   | -aa0- |
 | 99    0153 | ADCA        | DIRECT       |   4   |   2   | aaaaa |
 | 9A    0154 | ORA         | DIRECT       |   4   |   2   | -aa0- |
 | 9B    0155 | ADDA        | DIRECT       |   4   |   2   | aaaaa |
 | 9C    0156 | CMPX        | DIRECT       |   6   |   2   | -aaaa |
 | 9D    0157 | JSR         | DIRECT       |   7   |   2   | ----- |
 | 9E    0158 | LDX         | DIRECT       |   5   |   2   | -aa0- |
 | 9F    0159 | STX         | DIRECT       |   5   |   2   | -aa0- |
 | A0    0160 | SUBA        | INDEXED      |   4   |   2   | uaaaa |
 | A1    0161 | CMPA        | INDEXED      |   4   |   2   | uaaaa |
 | A2    0162 | SBCA        | INDEXED      |   4   |   2   | uaaaa |
 | A3    0163 | SUBD        | INDEXED      |   6   |   2   | -aaaa |
 | A4    0164 | ANDA        | INDEXED      |   4   |   2   | -aa0- |
 | A5    0165 | BITA        | INDEXED      |   4   |   2   | -aa0- |
 | A6    0166 | LDA         | INDEXED      |   4   |   2   | -aa0- |
 | A7    0167 | STA         | INDEXED      |   4   |   2   | -aa0- |
 | A8    0168 | EORA        | INDEXED      |   4   |   2   | -aa0- |
 | A9    0169 | ADCA        | INDEXED      |   4   |   2   | aaaaa |
 | AA    0170 | ORA         | INDEXED      |   4   |   2   | -aa0- |
 | AB    0171 | ADDA        | INDEXED      |   4   |   2   | aaaaa |
 | AC    0172 | CMPX        | INDEXED      |   6   |   2   | -aaaa |
 | AD    0173 | JSR         | INDEXED      |   7   |   2   | ----- |
 | AE    0174 | LDX         | INDEXED      |   5   |   2   | -aa0- |
 | AF    0175 | STX         | INDEXED      |   5   |   2   | -aa0- |
 | B0    0176 | SUBA        | EXTENDED     |   5   |   3   | uaaaa |
 | B1    0177 | CMPA        | EXTENDED     |   5   |   3   | uaaaa |
 | B2    0178 | SBCA        | EXTENDED     |   5   |   3   | uaaaa |
 | B3    0179 | SUBD        | EXTENDED     |   7   |   3   | -aaaa |
 | B4    0180 | ANDA        | EXTENDED     |   5   |   3   | -aa0- |
 | B5    0181 | BITA        | EXTENDED     |   5   |   3   | -aa0- |
 | B6    0182 | LDA         | EXTENDED     |   5   |   3   | -aa0- |
 | B7    0183 | STA         | EXTENDED     |   5   |   3   | -aa0- |
 | B8    0184 | EORA        | EXTENDED     |   5   |   3   | -aa0- |
 | B9    0185 | ADCA        | EXTENDED     |   5   |   3   | aaaaa |
 | BA    0186 | ORA         | EXTENDED     |   5   |   3   | -aa0- |
 | BB    0187 | ADDA        | EXTENDED     |   5   |   3   | aaaaa |
 | BC    0188 | CMPX        | EXTENDED     |   7   |   3   | -aaaa |
 | BD    0189 | JSR         | EXTENDED     |   8   |   3   | ----- |
 | BE    0190 | LDX         | EXTENDED     |   6   |   3   | -aa0- |
 | BF    0191 | STX         | EXTENDED     |   6   |   3   | -aa0- |
 | C0    0192 | SUBB        | IMMEDIATE    |   2   |   2   | uaaaa |
 | C1    0193 | CMPB        | IMMEDIATE    |   2   |   2   | uaaaa |
 | C2    0194 | SBCB        | IMMEDIATE    |   2   |   2   | uaaaa |
 | C3    0195 | ADDD        | IMMEDIATE    |   4   |   3   | -aaaa |
 | C4    0196 | ANDB        | IMMEDIATE    |   2   |   2   | -aa0- |
 | C5    0197 | BITB        | IMMEDIATE    |   2   |   2   | -aa0- |
 | C6    0198 | LDB         | IMMEDIATE    |   2   |   2   | -aa0- |
 | C7    0199 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | C8    0200 | EORB        | IMMEDIATE    |   2   |   2   | -aa0- |
 | C9    0201 | ADCB        | IMMEDIATE    |   2   |   2   | aaaaa |
 | CA    0202 | ORB         | IMMEDIATE    |   2   |   2   | -aa0- |
 | CB    0203 | ADDB        | IMMEDIATE    |   2   |   2   | aaaaa |
 | CC    0204 | LDD         | IMMEDIATE    |   3   |   3   | -aa0- |
 | CD    0205 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | CE    0206 | LDU         | IMMEDIATE    |   3   |   3   | -aa0- |
 | CF    0207 | ILLEGAL     | ILLEGAL      |   1   |   1   | uuuuu |
 | D0    0208 | SUBB        | DIRECT       |   4   |   2   | uaaaa |
 | D1    0209 | CMPB        | DIRECT       |   4   |   2   | uaaaa |
 | D2    0210 | SBCB        | DIRECT       |   4   |   2   | uaaaa |
 | D3    0211 | ADDD        | DIRECT       |   6   |   2   | -aaaa |
 | D4    0212 | ANDB        | DIRECT       |   4   |   2   | -aa0- |
 | D5    0213 | BITB        | DIRECT       |   4   |   2   | -aa0- |
 | D6    0214 | LDB         | DIRECT       |   4   |   2   | -aa0- |
 | D7    0215 | STB         | DIRECT       |   4   |   2   | -aa0- |
 | D8    0216 | EORB        | DIRECT       |   4   |   2   | -aa0- |
 | D9    0217 | ADCB        | DIRECT       |   4   |   2   | aaaaa |
 | DA    0218 | ORB         | DIRECT       |   4   |   2   | -aa0- |
 | DB    0219 | ADDB        | DIRECT       |   4   |   2   | aaaaa |
 | DC    0220 | LDD         | DIRECT       |   5   |   2   | -aa0- |
 | DD    0221 | STD         | DIRECT       |   5   |   2   | -aa0- |
 | DE    0222 | LDU         | DIRECT       |   5   |   2   | -aa0- |
 | DF    0223 | STU         | DIRECT       |   5   |   2   | -aa0- |
 | E0    0224 | SUBB        | INDEXED      |   4   |   2   | uaaaa |
 | E1    0225 | CMPB        | INDEXED      |   4   |   2   | uaaaa |
 | E2    0226 | SBCB        | INDEXED      |   4   |   2   | uaaaa |
 | E3    0227 | ADDD        | INDEXED      |   6   |   2   | -aaaa |
 | E4    0228 | ANDB        | INDEXED      |   4   |   2   | -aa0- |
 | E5    0229 | BITB        | INDEXED      |   4   |   2   | -aa0- |
 | E6    0230 | LDB         | INDEXED      |   4   |   2   | -aa0- |
 | E7    0231 | STB         | INDEXED      |   4   |   2   | -aa0- |
 | E8    0232 | EORB        | INDEXED      |   4   |   2   | -aa0- |
 | E9    0233 | ADCB        | INDEXED      |   4   |   2   | aaaaa |
 | EA    0234 | ORB         | INDEXED      |   4   |   2   | -aa0- |
 | EB    0235 | ADDB        | INDEXED      |   4   |   2   | aaaaa |
 | EC    0236 | LDD         | INDEXED      |   5   |   2   | -aa0- |
 | ED    0237 | STD         | INDEXED      |   5   |   2   | -aa0- |
 | EE    0238 | LDU         | INDEXED      |   5   |   2   | -aa0- |
 | EF    0239 | STU         | INDEXED      |   5   |   2   | -aa0- |
 | F0    0240 | SUBB        | EXTENDED     |   5   |   3   | uaaaa |
 | F1    0241 | CMPB        | EXTENDED     |   5   |   3   | uaaaa |
 | F2    0242 | SBCB        | EXTENDED     |   5   |   3   | uaaaa |
 | F3    0243 | ADDD        | EXTENDED     |   7   |   3   | -aaaa |
 | F4    0244 | ANDB        | EXTENDED     |   5   |   3   | -aa0- |
 | F5    0245 | BITB        | EXTENDED     |   5   |   3   | -aa0- |
 | F6    0246 | LDB         | EXTENDED     |   5   |   3   | -aa0- |
 | F7    0247 | STB         | EXTENDED     |   5   |   3   | -aa0- |
 | F8    0248 | EORB        | EXTENDED     |   5   |   3   | -aa0- |
 | F9    0249 | ADCB        | EXTENDED     |   5   |   3   | aaaaa |
 | FA    0250 | ORB         | EXTENDED     |   5   |   3   | -aa0- |
 | FB    0251 | ADDB        | EXTENDED     |   5   |   3   | aaaaa |
 | FC    0252 | LDD         | EXTENDED     |   6   |   3   | -aa0- |
 | FD    0253 | STD         | EXTENDED     |   6   |   3   | -aa0- |
 | FE    0254 | LDU         | EXTENDED     |   6   |   3   | -aa0- |
 | FF    0255 | STU         | EXTENDED     |   6   |   3   | -aa0- |
 +------------+-------------+--------------+-------+-------+-------+

 +-----------------------------------------------------------------+
 |                       Page 1 Instructions^                      |
 +------------+-------------+--------------+---------------+-------+
 | Opcode     |             | Addressing   |               |       |
 | Hex   Dec  | Instruction | Mode         | Cycles  Bytes | HNZVC |
 +------------+-------------+--------------+-------+-------+-------+
 | 1021  4129 | LBRN        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1022  4130 | LBHI        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1023  4131 | LBLS        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1024  4132 | LBHS/LBCC   | RELATIVE     | 5(6)  |   4   | ----- |
 | 1025  4133 | LBLO/LBCS   | RELATIVE     | 5(6)  |   4   | ----- |
 | 1026  4134 | LBNE        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1027  4135 | LBEQ        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1028  4136 | LBVC        | RELATIVE     | 5(6)  |   4   | ----- |
 | 1029  4137 | LBVS        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102A  4138 | LBPL        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102B  4139 | LBMI        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102C  4140 | LBGE        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102D  4141 | LBLT        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102E  4142 | LBGT        | RELATIVE     | 5(6)  |   4   | ----- |
 | 102F  4143 | LBLE        | RELATIVE     | 5(6)  |   4   | ----- |
 | 103F  4159 | SWI2        | INHERENT     |  20   |   2   | ----- |
 | 1083  4227 | CMPD        | IMMEDIATE    |   5   |   4   | -aaaa |
 | 108C  4236 | CMPY        | IMMEDIATE    |   5   |   4   | -aaaa |
 | 108E  4238 | LDY         | IMMEDIATE    |   4   |   4   | -aa0- |
 | 1093  4243 | CMPD        | DIRECT       |   7   |   3   | -aaaa |
 | 109C  4252 | CMPY        | DIRECT       |   7   |   3   | -aaaa |
 | 109E  4254 | LDY         | DIRECT       |   6   |   3   | -aa0- |
 | 109F  4255 | STY         | DIRECT       |   6   |   3   | -aa0- |
 | 10A3  4259 | CMPD        | INDEXED      |   7   |   3   | -aaaa |
 | 10AC  4268 | CMPY        | INDEXED      |   7   |   3   | -aaaa |
 | 10AE  4270 | LDY         | INDEXED      |   6   |   3   | -aa0- |
 | 10AF  4271 | STY         | INDEXED      |   6   |   3   | -aa0- |
 | 10B3  4275 | CMPD        | EXTENDED     |   8   |   4   | -aaaa |
 | 10BC  4284 | CMPY        | EXTENDED     |   8   |   4   | -aaaa |
 | 10BE  4286 | LDY         | EXTENDED     |   7   |   4   | -aa0- |
 | 10BF  4287 | STY         | EXTENDED     |   7   |   4   | -aa0- |
 | 10CE  4302 | LDS         | IMMEDIATE    |   4   |   4   | -aa0- |
 | 10DE  4318 | LDS         | DIRECT       |   6   |   3   | -aa0- |
 | 10DF  4319 | STS         | DIRECT       |   6   |   3   | -aa0- |
 | 10EE  4334 | LDS         | INDEXED      |   6   |   3   | -aa0- |
 | 10EF  4335 | STS         | INDEXED      |   6   |   3   | -aa0- |
 | 10FE  4350 | LDS         | EXTENDED     |   7   |   4   | -aa0- |
 | 10FF  4351 | STS         | EXTENDED     |   7   |   4   | -aa0- |
 +------------+-------------+--------------+-------+-------+-------+

 +-----------------------------------------------------------------+
 |                       Page 2 Instructions^                      |
 +------------+-------------+--------------+---------------+-------+
 | Opcode     |             | Addressing   |               |       |
 | Hex   Dec  | Instruction | Mode         | Cycles  Bytes | HNZVC |
 +------------+-------------+--------------+-------+-------+-------+
 | 113F  4415 | SWI3        | INHERENT     |  20   |   2   | ----- |
 | 1183  4483 | CMPU        | IMMEDIATE    |   5   |   4   | -aaaa |
 | 118C  4492 | CMPS        | IMMEDIATE    |   5   |   4   | -aaaa |
 | 1193  4499 | CMPU        | DIRECT       |   7   |   3   | -aaaa |
 | 119C  4508 | CMPS        | DIRECT       |   7   |   3   | -aaaa |
 | 11A3  4515 | CMPU        | INDEXED      |   7   |   3   | -aaaa |
 | 11AC  4524 | CMPS        | INDEXED      |   7   |   3   | -aaaa |
 | 11B3  4531 | CMPU        | EXTENDED     |   8   |   4   | -aaaa |
 | 11BC  4540 | CMPS        | EXTENDED     |   8   |   4   | -aaaa |
 +------------+-------------+--------------+-------+-------+-------+"""


DONT_USE_ORIGIN_ACCESS_MODE = ("NEG")

instr_info_keys = INSTRUCTION_INFO.keys()


def get_instr_info(mnemonic, instruction):
    for instr_info_key, instr_info in INSTRUCTION_INFO.items():
        if mnemonic == instr_info_key:
            return instr_info_key, instr_info

    for instr_info_key, instr_info in INSTRUCTION_INFO.items():
        if not instr_info_key.startswith(instruction):
            continue

        try:
            source_forms = instr_info['source form']
        except KeyError:
            continue

        if mnemonic in source_forms:
            return instr_info_key, instr_info

    for instr_info_key, instr_info in INSTRUCTION_INFO.items():
        if instr_info_key.startswith(instruction):
            print "Use %s for %s (%s)" % (instr_info_key, mnemonic, instruction)
            return instr_info_key, instr_info

    test_mnemonic = mnemonic[1:]
    for instr_info_key, instr_info in INSTRUCTION_INFO.items():
        if instr_info_key == test_mnemonic:
            print "Use %s for %s (%s)" % (instr_info_key, mnemonic, instruction)
            return instr_info_key, instr_info

    return None, None


HNZVC_dict = {}

opcodes = []
categoriesed_opcodes = {}
for line in txt.splitlines():
    sections = line.split("|")
    if len(sections) != 8:
        continue
#     print line
    sections = [s.strip() for s in sections if s.strip()]
    # ~ print sections
    raw_hex, raw_dec = sections[0].split(" ", 1)
    opcode = int(raw_hex, 16)
    op_dec = int(raw_dec)
    # ~ print hex(opcode), op_dec
    if not opcode == op_dec:
        print "ERROR!"

    mnemonic = sections[1]

    if mnemonic == "ILLEGAL":
        illegal.append(opcode)
        continue

    if "/" in mnemonic:
        # duplicate assembly-language mnemonic
        mnemonic_single = mnemonic.split("/")[0]
    else:
        mnemonic_single = mnemonic

    try:
        category_id, instr_desc = OpDescriptions[mnemonic_single]
    except KeyError:
        print "***", mnemonic
        category_id = 8 # other
        instr_desc = ""

    register = None
    instruction = mnemonic
    if instruction in CHANGE_INSTRUCTIONS:
        instruction = CHANGE_INSTRUCTIONS[instruction]
    for instr in INSTRUCTIONS:
        if mnemonic == instr:
            break

        if mnemonic.startswith(instr):
            instruction = instr
            if "/" in mnemonic:
                test_mnemonic = mnemonic.split("/")[0]
            else:
                test_mnemonic = mnemonic
            operand_test = test_mnemonic[len(instruction):]
            if operand_test in REGISTERS:
                register = operand_test
            print " **** ", mnemonic, instruction, operand_test, register
            break

    instr_info_key, instr_info = get_instr_info(mnemonic, instruction)
    if instr_info is None:
        if instruction in CHANGED_INSTRUCTIONS:
            instr_info_key = instruction
            instr_info = INSTRUCTION_INFO[instruction]
        else:
            instr_info_key = OTHER_INSTRUCTIONS
            print "no INSTRUCTION_INFO found for %s" % repr(instruction)
            instr_info = INSTRUCTION_INFO.setdefault(OTHER_INSTRUCTIONS, {})
    elif not (instr_info_key.startswith(instruction) or instruction.endswith(instr_info_key)):
        print "ERROR:", instr_info_key
        pprint.pprint(instr_info)
        print "%r - $%x - %r - %s" % (instr_info_key, opcode, instruction, mnemonic)
        raise AssertionError

    instr_info["instr_desc"] = instr_desc

    print mnemonic, "%02x" % opcode

    cc_HNZVC = sections[5]

    try:
        mnemonic_desc = SHORT_DESC[mnemonic_single]
    except KeyError:
        mnemonic_desc = instr_desc


    write = read = False
    try:
        before, after = mnemonic_desc.split("=", 1)
    except ValueError:
        if "M" in mnemonic_desc:
            read = True
    else:
        if "M" in before:
            write = True

        if "M" in after and instruction not in NO_MEM_READ:
            read = True

    print mnemonic_desc, "read: %s - write: %s" % (read, write)


    raw_cycles = sections[3]
    try:
        cycles = int(raw_cycles)
    except ValueError, err:
        try:
            cycles = int(raw_cycles[0])
        except ValueError, err:
            print "Error: %s" % err
            print line
            cycles = -1
        else:
            print "Use sycles %i from %r" % (cycles, raw_cycles)

    bytes = int(sections[4])
    mem_access = False

    try:
        operation_example = instr_info['operation']
    except KeyError:
        operation_example = None
        print "No operation for", mnemonic
    else:
        if "M" in operation_example:
            print "mem_access=BYTE, because 'M' in example: %s" % repr(operation_example)
            mem_access = MEM_ACCESS_BYTE

    addr_mode = ADDRES_MODE_DICT[sections[2].upper()]

    if addr_mode == IMMEDIATE:
        read = True
        mem_access = MEM_ACCESS_BYTE

    if opcode in OVERWRITE_DATA:
        op_type = OVERWRITE_DATA[opcode]
        print "overwrite data with:", op_type
        mem_access = op_type[0]
        if mem_access == False:
            register = op_type[1]
        else:
            mem_access = MEM_ACCESS_BYTE
            addr_mode = op_type[1]

    if mem_access and register is not None:
        if bytes == 2 and addr_mode == IMMEDIATE:
            mem_access = MEM_ACCESS_BYTE
        else:
            reg_info = REGISTER_INFO[register]
            reg_width = reg_info[0]
            if reg_width == 8:
                mem_access = MEM_ACCESS_BYTE
            elif reg_width == 16:
                mem_access = MEM_ACCESS_WORD
            else:
                raise ValueError
            
    """
    TODO:
        e.g.: STD:
         'addr_mode': 'DIRECT',
         'ea_width': 8, # add: width of addr_mode function
         'mem_read': 0, # change: doesn't read memory
         'mem_write': 16, # change: write a word
    """

    if addr_mode == EXTENDED:
        mem_access = MEM_ACCESS_WORD

    if mnemonic.startswith("LB"):
        # long branches
        assert "Branch" in mnemonic_desc
        mnemonic_desc = mnemonic_desc.replace("Branch", "Long branch")
        mem_access = MEM_ACCESS_WORD

    assert mem_access in (False, MEM_ACCESS_BYTE, MEM_ACCESS_WORD)

    opcode_data = {
        "opcode": opcode,
        "category": category_id,
        "instruction": instruction,
        "mnemonic": mnemonic,
        "register": register,
        "addr_mode": addr_mode,
        "mem_access": mem_access,
        "mem_read": read,
        "mem_write": write,
        "example": operation_example,
        "cycles": cycles,
        "bytes": bytes,
        "HNZVC":cc_HNZVC,
        "desc":mnemonic_desc,
        "instr_info_key": instr_info_key,
    }
    pprint.pprint(opcode_data)
    pprint.pprint(instr_info)
    if bytes == 1:
        assert mem_access == False

    if mem_access == False:
        assert read == False

    print "-"*79
    opcodes.append(opcode_data)
    categoriesed_opcodes.setdefault(category_id, []).append(opcode_data)



# sys.exit()

existing_instr = set([o["instr_info_key"] for o in opcodes])
keys = INSTRUCTION_INFO.keys()
for key in keys:
    if key not in existing_instr:
        print "Instr.Data %r doesn't habe a op code:" % key
        pprint.pprint(INSTRUCTION_INFO[key])
        print "remove it!"
        del(INSTRUCTION_INFO[key])


for key, data in sorted(INSTRUCTION_INFO.items()):
    if key == OTHER_INSTRUCTIONS:
        continue

    try:
        addr_modes = data["addressing mode"]
    except KeyError, err:
        print "WARNING: no %s for %s" % (err, key)
        pprint.pprint(data)

    addr_mode_ids = []
    for addr_mode in addr_modes.split(" "):
        addr_mode = addr_mode.upper()
        try:
            addr_mode_ids.append(ADDRES_MODE_DICT[addr_mode])
        except KeyError, err:
            print "ERROR: unknown addr. mode: %s from: %s" % (err, repr(addr_modes))
            print "data:",
            pprint.pprint(data)
            continue

    for opcode in opcodes:
#         print "***"
#         pprint.pprint(opcode)
        if opcode["instr_info_key"] != key:
            continue
        if not opcode["addr_mode"] in addr_mode_ids:
            print "ERROR: addr mode missmatch: $%x - IDs: %s" % (
                opcode["opcode"], repr(addr_mode_ids)
            ),
            if opcode["mnemonic"] in DONT_USE_ORIGIN_ACCESS_MODE:
                print " - Skip, ok."
            else:
                print
                print "data:",
                pprint.pprint(data)
                print "opcode:",
                pprint.pprint(opcode)
                raise AssertionError

    if "addressing mode" in data:
        del(data["addressing mode"])

# sys.exit()

def pformat(item):
    txt = pprint.pformat(item, indent=4, width=80)
    txt = "\n  ".join(txt.split(" ", 1))
    return txt

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


sys.stdout = Tee("MC6809_data_raw.py", sys.stdout,
#     to_stdout = True
    to_stdout=False
)


# ADDRES_MODE_DICT = dict(zip(ADDR_MODES.values(), ADDR_MODES.keys()))
# ADDRES_MODES = sorted(ADDR_MODES.values())

print '"""%s"""' % __doc__
print
print "OP_CATEGORIES = ", pformat(categories)
print
for addr_mode in ADDRES_MODES:
    print '%s = "%s"' % (addr_mode, addr_mode)
print
print '# operands:'
for register in REGISTERS:
    print 'REG_%(op)s = "%(op)s"' % {"op":register}
print
print
print "REGISTER_INFO = {"
for k, v in REGISTER_INFO.items():
    print "    REG_%s: %s," % (k, v)
print "}"
print
print "MEM_ACCESS_BYTE = 8"
print "MEM_ACCESS_WORD = 16"
print
print '# illegal opcode:'
print 'ILLEGAL_OPS = (%s)' % ",".join([hex(i) for i in illegal])
print
print '# other instructions'
print 'OTHER_INSTRUCTIONS = "OTHER_INSTRUCTIONS"'
print

print
print "# instruction info keys:"
for key in sorted(INSTRUCTION_INFO.keys()):
    print '%s="%s"' % (key, key)
print


print "INSTRUCTION_INFO = {"
for key, data in sorted(INSTRUCTION_INFO.items()):
    print '    %s: {' % key
    print " %s" % pprint.pformat(data, indent=8).strip("{}")
    print '    },'
print "}"
print


processed_opcodes = []
print
print "OP_DATA = ("
for category_id, category in categories.items():
    print
    print "    #### %s" % category
    print
    for opcode in categoriesed_opcodes[category_id]:
#         print pprint.pformat(opcode, indent=8)
        code = opcode["opcode"]
        assert code not in processed_opcodes, repr(opcode)
        processed_opcodes.append(code)

        print '    {'
        print '        "opcode": 0x%x, "instruction": "%s", "mnemonic": "%s",' % (
            opcode["opcode"], opcode["instruction"], opcode["mnemonic"]
        )

        print '        "desc": "%s",' % (
            opcode["desc"]
        )

        print '        "addr_mode": %s, "cycles": %i, "bytes": %i,' % (
            ADDRES_MODE_DICT[opcode["addr_mode"]], opcode["cycles"], opcode["bytes"]
        )


        mem_access = opcode["mem_access"]
        if mem_access != False:
            operation_example = opcode["example"]
            if not operation_example:
                example = ""
            else:
                example = " # %s" % operation_example.replace("\n", ";")
            print '        "mem_access": %s,%s' % (
                mem_access, example,
            )

        print '        "mem_read": %s, "mem_write": %s,' % (
            opcode["mem_read"], opcode["mem_write"]
        )
        print '        "HNZVC": "%s",' % (
            opcode["HNZVC"],
        )


        register = opcode["register"]
        if register:
            register_info = REGISTER_INFO[register]
            # e.g: (16, "0000", "concatenated register (A+B)")
            print '        "register": REG_%s, # %i Bit %s %s' % (
                register, register_info[0], register_info[2], register
            )

        print '        "category": %i, "instr_info_key": %s,' % (
            category_id, opcode["instr_info_key"]
        )
        print '    },'
print ")"

sys.stdout.close()

print "%i opcodes saved." % len(processed_opcodes)
