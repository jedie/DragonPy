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

OP_CATEGORIES =  {
    0: '8-Bit Accumulator and Memory Instructions',
    1: '16-Bit Accumulator and Memory Instructions Instruction',
    2: 'Index/Stack Pointer Instructions',
    3: 'Simple Branch Instructions',
    4: 'Signed Branch Instructions',
    5: 'Unsigned Branch Instructions',
    6: 'other Branch Instructions',
    7: 'Miscellaneous Instructions',
    8: 'other'}

EXTENDED = "EXTENDED"
VARIANT = "VARIANT"
DIRECT = "DIRECT"
IMMEDIATE = "IMMEDIATE"
RELATIVE = "RELATIVE"
INDEXED = "INDEXED"
INHERENT = "INHERENT"

# operands:
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
    REG_A: (8, '1000', 'accumulator'),
    REG_PC: (16, '0101', 'program counter register'),
    REG_S: (16, '0100', 'system-stack pointer'),
    REG_B: (8, '1001', 'accumulator'),
    REG_U: (16, '0011', 'user-stack pointer'),
    REG_D: (16, '0000', 'concatenated register (A+B)'),
    REG_Y: (16, '0010', 'index register'),
    REG_X: (16, '0001', 'index register'),
    REG_CC: (8, '1010', 'condition code register as flags'),
    REG_DP: (8, '1011', 'direct page register'),
}

MEM_ACCESS_BYTE = 8
MEM_ACCESS_WORD = 16

# illegal opcode:
ILLEGAL_OPS = (0x1,0x2,0x5,0xb,0x14,0x15,0x18,0x1b,0x38,0x41,0x42,0x45,0x4b,0x4e,0x51,0x52,0x55,0x5b,0x5e,0x61,0x62,0x65,0x6b,0x71,0x72,0x75,0x7b,0x87,0x8f,0xc7,0xcd,0xcf)

# other instructions
OTHER_INSTRUCTIONS = "OTHER_INSTRUCTIONS"


# instruction info keys:
ABX="ABX"
ADC="ADC"
ADD16="ADD16"
ADD8="ADD8"
AND="AND"
ANDCC="ANDCC"
ASR="ASR"
BEQ="BEQ"
BGE="BGE"
BGT="BGT"
BHI="BHI"
BHS="BHS"
BIT="BIT"
BLE="BLE"
BLO="BLO"
BLS="BLS"
BLT="BLT"
BMI="BMI"
BNE="BNE"
BPL="BPL"
BRA="BRA"
BRN="BRN"
BSR="BSR"
BVC="BVC"
BVS="BVS"
CLR="CLR"
CMP16="CMP16"
CMP8="CMP8"
COM="COM"
CWAI="CWAI"
DAA="DAA"
DEC="DEC"
EOR="EOR"
EXG="EXG"
INC="INC"
JMP="JMP"
JSR="JSR"
LD16="LD16"
LD8="LD8"
LEA="LEA"
LSL="LSL"
LSR="LSR"
MUL="MUL"
NEG="NEG"
NOP="NOP"
OR="OR"
ORCC="ORCC"
OTHER_INSTRUCTIONS="OTHER_INSTRUCTIONS"
PAGE="PAGE"
PSHS="PSHS"
PSHU="PSHU"
PULS="PULS"
PULU="PULU"
RESET="RESET"
ROL="ROL"
ROR="ROR"
RTI="RTI"
RTS="RTS"
SBC="SBC"
SEX="SEX"
ST16="ST16"
ST8="ST8"
SUB16="SUB16"
SUB8="SUB8"
SWI="SWI"
SWI2="SWI2"
SWI3="SWI3"
SYNC="SYNC"
TFR="TFR"
TST="TST"

INSTRUCTION_INFO = {
    ABX: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Add the 8-bit unsigned value in accumulator B into index register X.',
        'instr_desc': 'Add B accumulator to X (unsigned)',
        'operation': "IX' = IX + ACCB",
        'source form': 'ABX'
    },
    ADC: {
        'HNZVC': 'aaaaa',
        'condition code': 'H - Set if a half-carry is generated; cleared otherwise.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the contents of the C (carry) bit and the memory byte into an 8-bit accumulator.',
        'instr_desc': 'Add memory to accumulator with carry',
        'operation': "R' = R + M + C",
        'source form': 'ADCA P; ADCB P'
    },
    ADD16: {
        'HNZVC': '-aaaa',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the 16-bit memory value into the 16-bit accumulator',
        'instr_desc': 'Add memory to D accumulator',
        'operation': "R' = R + M:M+1",
        'source form': 'ADDD P'
    },
    ADD8: {
        'HNZVC': 'aaaaa',
        'condition code': 'H - Set if a half-carry is generated; cleared otherwise.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the memory byte into an 8-bit accumulator.',
        'instr_desc': 'Add memory to accumulator',
        'operation': "R' = R + M",
        'source form': 'ADDA P; ADDB P'
    },
    AND: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs the logical AND operation between the contents of an accumulator and the contents of memory location M and the result is stored in the accumulator.',
        'instr_desc': 'AND memory with accumulator',
        'operation': "R' = R AND M",
        'source form': 'ANDA P; ANDB P'
    },
    ANDCC: {
        'HNZVC': 'ddddd',
        'condition code': 'Affected according to the operation.',
        'description': 'Performs a logical AND between the condition code register and the immediate byte specified in the instruction and places the result in the condition code register.',
        'instr_desc': 'AND condition code register',
        'operation': "R' = R AND MI",
        'source form': 'ANDCC #xx'
    },
    ASR: {
        'HNZVC': 'uaa-s',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the original operand.',
        'description': 'Shifts all bits of the operand one place to the right. Bit seven is held constant. Bit zero is shifted into the C (carry) bit.',
        'instr_desc': 'Arithmetic shift of accumulator or memory right',
        'operation': 'b7 -> -> C\nb7 -> b0',
        'source form': 'ASR Q; ASRA; ASRB'
    },
    BEQ: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the Z (zero) bit and causes a branch if it is set.\nWhen used after a subtract or compare operation, this instruction will branch if the compared values, signed or unsigned, were exactly the same.',
        'instr_desc': 'Branch if equal',
        'operation': "TEMP = MI IFF Z = 1 then PC' = PC + TEMP",
        'source form': 'BEQ dd; LBEQ DDDD'
    },
    BGE: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the N (negative) bit and the V (overflow) bit are either both set or both clear.\nThat is, branch if the sign of a valid twos complement result is, or would be, positive.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than or equal to the memory operand.',
        'instr_desc': 'Branch if greater than or equal (signed)',
        'operation': "TEMP = MI IFF [N XOR V] = 0 then PC' = PC + TEMP",
        'source form': 'BGE dd; LBGE DDDD'
    },
    BGT: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the N (negative) bit and V (overflow) bit are either both set or both clear and the Z (zero) bit is clear.\nIn other words, branch if the sign of a valid twos complement result is, or would be, positive and not zero.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than the memory operand.',
        'instr_desc': 'Branch if greater (signed)',
        'operation': "TEMP = MI IFF Z AND [N XOR V] = 0 then PC' = PC + TEMP",
        'source form': 'BGT dd; LBGT DDDD'
    },
    BHI: {
        'HNZVC': '-----',
        'comment': 'Generally not useful after INC/DEC, LD/TST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the previous operation caused neither a carry nor a zero result.\nWhen used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was higher than the memory operand.',
        'instr_desc': 'Branch if higher (unsigned)',
        'operation': "TEMP = MI IFF [ C OR Z ] = 0 then PC' = PC + TEMP",
        'source form': 'BHI dd; LBHI DDDD'
    },
    BHS: {
        'HNZVC': '-----',
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction BCC.\nGenerally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is clear.\nWhen used after a subtract or compare on unsigned binary values, this instruction will branch if the register was higher than or the same as the memory operand.',
        'instr_desc': 'Branch if higher or same (unsigned)',
        'operation': "TEMP = MI IFF C = 0 then PC' = PC + MI",
        'source form': 'BHS dd; LBHS DDDD'
    },
    BIT: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs the logical AND of the contents of accumulator A or B and the contents of memory location M and modifies the condition codes accordingly.\nThe contents of accumulator A or B and memory location M are not affected.',
        'instr_desc': 'Bit test memory with accumulator',
        'operation': 'TEMP = R AND M',
        'source form': 'Bit P'
    },
    BLE: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the exclusive OR of the N (negative) and V (overflow) bits is 1 or if the Z (zero) bit is set.\nThat is, branch if the sign of a valid twos complement result is, or would be, negative.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was less than or equal to the memory operand.',
        'instr_desc': 'Branch if less than or equal (signed)',
        'operation': "TEMP = MI IFF Z OR [ N XOR V ] = 1 then PC' = PC + TEMP",
        'source form': 'BLE dd; LBLE DDDD'
    },
    BLO: {
        'HNZVC': '-----',
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction BCS.\nGenerally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is set.\nWhen used after a subtract or compare on unsigned binary values, this instruction will branch if the register was lower than the memory operand.',
        'instr_desc': 'Branch if lower (unsigned)',
        'operation': "TEMP = MI IFF C = 1 then PC' = PC + TEMP",
        'source form': 'BLO dd; LBLO DDDD'
    },
    BLS: {
        'HNZVC': '-----',
        'comment': 'Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the previous operation caused either a carry or a zero result.\nWhen used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was lower than or the same as the memory operand.',
        'instr_desc': 'Branch if lower or same (unsigned)',
        'operation': "TEMP = MI IFF (C OR Z) = 1 then PC' = PC + TEMP",
        'source form': 'BLS dd; LBLS DDDD'
    },
    BLT: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if either, but not both, of the N (negative) or V (overflow) bits is set.\nThat is, branch if the sign of a valid twos complement result is, or would be, negative.\nWhen used after a subtract or compare operation on twos complement binary values, this instruction will branch if the register was less than the memory operand.',
        'instr_desc': 'Branch if less than (signed)',
        'operation': "TEMP = MI IFF [ N XOR V ] = 1 then PC' = PC + TEMP",
        'source form': 'BLT dd; LBLT DDDD'
    },
    BMI: {
        'HNZVC': '-----',
        'comment': 'When used after an operation on signed binary values, this instruction will branch if the result is minus.\nIt is generally preferred to use the LBLT instruction after signed operations.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the N (negative) bit and causes a branch if set.\nThat is, branch if the sign of the twos complement result is negative.',
        'instr_desc': 'Branch if minus',
        'operation': "TEMP = MI IFF N = 1 then PC' = PC + TEMP",
        'source form': 'BMI dd; LBMI DDDD'
    },
    BNE: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the Z (zero) bit and causes a branch if it is clear.\nWhen used after a subtract or compare operation on any binary values, this instruction will branch if the register is, or would be, not equal to the memory operand.',
        'instr_desc': 'Branch if not equal',
        'operation': "TEMP = MI IFF Z = 0 then PC' = PC + TEMP",
        'source form': 'BNE dd; LBNE DDDD'
    },
    BPL: {
        'HNZVC': '-----',
        'comment': 'When used after an operation on signed binary values, this instruction will branch if the result (possibly invalid) is positive.\nIt is generally preferred to use the BGE instruction after signed operations.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the N (negative) bit and causes a branch if it is clear.\nThat is, branch if the sign of the twos complement result is positive.',
        'instr_desc': 'Branch if plus',
        'operation': "TEMP = MI IFF N = 0 then PC' = PC + TEMP",
        'source form': 'BPL dd; LBPL DDDD'
    },
    BRA: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Causes an unconditional branch.',
        'instr_desc': 'Branch always',
        'operation': "TEMP = MI PC' = PC + TEMP",
        'source form': 'BRA dd; LBRA DDDD'
    },
    BRN: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Does not cause a branch.\nThis instruction is essentially a no operation, but has a bit pattern logically related to branch always.',
        'instr_desc': 'Branch never',
        'operation': 'TEMP = MI',
        'source form': 'BRN dd; LBRN DDDD'
    },
    BSR: {
        'HNZVC': '-----',
        'comment': 'A return from subroutine (RTS) instruction is used to reverse this process and must be the last instruction executed in a subroutine.',
        'condition code': 'Not affected.',
        'description': 'The program counter is pushed onto the stack.\nThe program counter is then loaded with the sum of the program counter and the offset.',
        'instr_desc': 'Branch to subroutine',
        'operation': "TEMP = MI SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' = PC + TEMP",
        'source form': 'BSR dd; LBSR DDDD'
    },
    BVC: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the V (overflow) bit and causes a branch if it is clear.\nThat is, branch if the twos complement result was valid.\nWhen used after an operation on twos complement binary values, this instruction will branch if there was no overflow.',
        'instr_desc': 'Branch if valid twos complement result',
        'operation': "TEMP = MI IFF V = 0 then PC' = PC + TEMP",
        'source form': 'BVC dd; LBVC DDDD'
    },
    BVS: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the V (overflow) bit and causes a branch if it is set.\nThat is, branch if the twos complement result was invalid.\nWhen used after an operation on twos complement binary values, this instruction will branch if there was an overflow.',
        'instr_desc': 'Branch if invalid twos complement result',
        'operation': "TEMP' = MI IFF V = 1 then PC' = PC + TEMP",
        'source form': 'BVS dd; LBVS DDDD'
    },
    CLR: {
        'HNZVC': '-0100',
        'condition code': 'H - Not affected.\nN - Always cleared.\nZ - Always set.\nV - Always cleared.\nC - Always cleared.',
        'description': 'Accumulator A or B or memory location M is loaded with 00000000 2 .\nNote that the EA is read during this operation.',
        'instr_desc': 'Clear accumulator or memory location',
        'operation': 'TEMP = M M = 00 16',
        'source form': 'CLR Q'
    },
    CMP16: {
        'HNZVC': '-aaaa',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Compares the 16-bit contents of the concatenated memory locations M:M+1 to the contents of the specified register and sets the appropriate condition codes.\nNeither the memory locations nor the specified register is modified unless autoincrement or autodecrement are used.\nThe carry flag represents a borrow and is set to the inverse of the resulting binary carry.',
        'instr_desc': 'Compare memory from stack pointer',
        'operation': 'TEMP = R - M:M+1',
        'source form': 'CMPD P; CMPX P; CMPY P; CMPU P; CMPS P'
    },
    CMP8: {
        'HNZVC': 'uaaaa',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Compares the contents of memory location to the contents of the specified register and sets the appropriate condition codes.\nNeither memory location M nor the specified register is modified.\nThe carry flag represents a borrow and is set to the inverse of the resulting binary carry.',
        'instr_desc': 'Compare memory from accumulator',
        'operation': 'TEMP = R - M',
        'source form': 'CMPA P; CMPB P'
    },
    COM: {
        'HNZVC': '-aa01',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Always set.',
        'description': 'Replaces the contents of memory location M or accumulator A or B with its logical complement.\nWhen operating on unsigned values, only BEQ and BNE branches can be expected to behave properly following a COM instruction.\nWhen operating on twos complement values, all signed branches are available.',
        'instr_desc': 'Complement accumulator or memory location',
        'operation': "M' = 0 + M",
        'source form': 'COM Q; COMA; COMB'
    },
    CWAI: {
        'HNZVC': 'ddddd',
        'comment': 'The following immediate values will have the following results: FF = enable neither EF = enable IRQ BF = enable FIRQ AF = enable both',
        'condition code': 'Affected according to the operation.',
        'description': 'This instruction ANDs an immediate byte with the condition code register which may clear the interrupt mask bits I and F, stacks the entire machine state on the hardware stack and then looks for an interrupt.\nWhen a non-masked interrupt occurs, no further machine state information need be saved before vectoring to the interrupt handling routine.\nThis instruction replaced the MC6800 CLI WAI sequence, but does not place the buses in a high-impedance state.\nA FIRQ (fast interrupt request) may enter its interrupt handler with its entire machine state saved.\nThe RTI (return from interrupt) instruction will automatically return the entire machine state after testing the E (entire) bit of the recovered condition code register.',
        'instr_desc': 'AND condition code register, then wait for interrupt',
        'operation': "CCR = CCR AND MI (Possibly clear masks) Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR",
        'source form': 'CWAI #$XX E F H I N Z V C'
    },
    DAA: {
        'HNZVC': '-aa0a',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Undefined.\nC - Set if a carry is generated or if the carry bit was set before the operation; cleared otherwise.',
        'description': 'The sequence of a single-byte add instruction on accumulator A (either ADDA or ADCA) and a following decimal addition adjust instruction results in a BCD addition with an appropriate carry bit.\nBoth values to be added must be in proper BCD form (each nibble such that: 0 <= nibble <= 9).\nMultiple-precision addition must add the carry generated by this decimal addition adjust into the next higher digit during the add operation (ADCA) immediately prior to the next decimal addition adjust.',
        'instr_desc': 'Decimal adjust A accumulator',
        'operation': 'Decimal Adjust A',
        'source form': 'DAA'
    },
    DEC: {
        'HNZVC': '-aaa-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 10000000 2 ; cleared otherwise.\nC - Not affected.',
        'description': 'Subtract one from the operand.\nThe carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\nWhen operating on unsigned values, only BEQ and BNE branches can be expected to behave consistently.\nWhen operating on twos complement values, all signed branches are available.',
        'instr_desc': 'Decrement accumulator or memory location',
        'operation': "M' = M - 1",
        'source form': 'DEC Q; DECA; DECB'
    },
    EOR: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'The contents of memory location M is exclusive ORed into an 8-bit register.',
        'instr_desc': 'Exclusive OR memory with accumulator',
        'operation': "R' = R XOR M",
        'source form': 'EORA P; EORB P'
    },
    EXG: {
        'HNZVC': 'ccccc',
        'condition code': 'Not affected (unless one of the registers is the condition code\nregister).',
        'description': '0000 = A:B 1000 = A\n0001 = X 1001 = B\n0010 = Y 1010 = CCR\n0011 = US 1011 = DPR\n0100 = SP 1100 = Undefined\n0101 = PC 1101 = Undefined\n0110 = Undefined 1110 = Undefined\n0111 = Undefined 1111 = Undefined',
        'instr_desc': 'Exchange Rl with R2',
        'operation': 'R1 <-> R2',
        'source form': 'EXG R1,R2'
    },
    INC: {
        'HNZVC': '-aaa-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 01111111 2 ; cleared otherwise.\nC - Not affected.',
        'description': 'Adds to the operand.\nThe carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\nWhen operating on unsigned values, only the BEQ and BNE branches can be expected to behave consistently.\nWhen operating on twos complement values, all signed branches are correctly available.',
        'instr_desc': 'Increment accumulator or memory location',
        'operation': "M' = M + 1",
        'source form': 'INC Q; INCA; INCB'
    },
    JMP: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Program control is transferred to the effective address.',
        'instr_desc': 'Jump',
        'operation': "PC' = EA",
        'source form': 'JMP EA'
    },
    JSR: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Program control is transferred to the effective address after storing the return address on the hardware stack.\nA RTS instruction should be the last executed instruction of the subroutine.',
        'instr_desc': 'Jump to subroutine',
        'operation': "SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' =EA",
        'source form': 'JSR EA'
    },
    LD16: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the loaded data is negative; cleared otherwise.\nZ - Set if the loaded data is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Load the contents of the memory location M:M+1 into the designated 16-bit register.',
        'instr_desc': 'Load stack pointer from memory',
        'operation': "R' = M:M+1",
        'source form': 'LDD P; LDX P; LDY P; LDS P; LDU P'
    },
    LD8: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the loaded data is negative; cleared otherwise.\nZ - Set if the loaded data is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Loads the contents of memory location M into the designated register.',
        'instr_desc': 'Load accumulator from memory',
        'operation': "R' = M",
        'source form': 'LDA P; LDB P'
    },
    LEA: {
        'HNZVC': '-----',
        'comment': "Instruction Operation Comment\nInstruction\n\nOperation\n\nComment\nLEAX 10,X X+10 -> X Adds 5-bit constant 10 to X\nLEAX 500,X X+500 -> X Adds 16-bit constant 500 to X\nLEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y\nLEAY D,Y Y+D -> Y Adds 16-bit D accumulator to Y\nLEAU -10,U U-10 -> U Subtracts 10 from U\nLEAS -10,S S-10 -> S Used to reserve area on stack\nLEAS 10,S S+10 -> S Used to 'clean up' stack\nLEAX 5,S S+5 -> X Transfers as well as adds",
        'condition code': 'H - Not affected.\nN - Not affected.\nZ - LEAX, LEAY: Set if the result is zero; cleared otherwise. LEAS, LEAU: Not affected.\nV - Not affected.\nC - Not affected.',
        'description': 'Calculates the effective address from the indexed addressing mode and places the address in an indexable register. LEAX and LEAY affect the Z (zero) bit to allow use of these registers as counters and for MC6800 INX/DEX compatibility. LEAU and LEAS do not affect the Z bit to allow cleaning up the stack while returning the Z bit as a parameter to a calling routine, and also for MC6800 INS/DES compatibility.',
        'instr_desc': 'Load effective address into stack pointer',
        'operation': "R' = EA",
        'source form': 'LEAX, LEAY, LEAS, LEAU'
    },
    LSL: {
        'HNZVC': 'naaas',
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction ASL.',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\nC - Loaded with bit seven of the original operand.',
        'description': 'Shifts all bits of accumulator A or B or memory location M one place to the left.\nBit zero is loaded with a zero.\nBit seven of accumulator A or B or memory location M is shifted into the C (carry) bit.',
        'instr_desc': 'Logical shift left accumulator or memory location',
        'operation': 'C = = 0\nb7 = b0',
        'source form': 'LSL Q; LSLA; LSLB'
    },
    LSR: {
        'HNZVC': '-0a-s',
        'condition code': 'H - Not affected.\nN - Always cleared.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the original operand.',
        'description': 'Performs a logical shift right on the operand.\nShifts a zero into bit seven and bit zero into the C (carry) bit.',
        'instr_desc': 'Logical shift right accumulator or memory location',
        'operation': '0 -> -> C\nb7 -> b0',
        'source form': 'LSR Q; LSRA; LSRB'
    },
    MUL: {
        'HNZVC': '--a-a',
        'comment': 'The C (carry) bit allows rounding the most-significant byte through the sequence: MUL, ADCA #0.',
        'condition code': 'H - Not affected.\nN - Not affected.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Set if ACCB bit 7 of result is set; cleared otherwise.',
        'description': 'Multiply the unsigned binary numbers in the accumulators and place the result in both accumulators (ACCA contains the most-significant byte of the result).\nUnsigned multiply allows multiple-precision operations.',
        'instr_desc': 'Unsigned multiply (A * B ? D)',
        'operation': "ACCA':ACCB' = ACCA * ACCB",
        'source form': 'MUL'
    },
    NEG: {
        'HNZVC': 'uaaaa',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 10000000 2 .\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Replaces the operand with its twos complement.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.\nNote that 80 16 is replaced by itself and only in this case is the V (overflow) bit set.\nThe value 00 16 is also replaced by itself, and only in this case is the C (carry) bit cleared.',
        'instr_desc': 'Negate accumulator or memory',
        'operation': "M' = 0 - M",
        'source form': 'NEG Q; NEGA; NEG B'
    },
    NOP: {
        'HNZVC': '-----',
        'condition code': 'This instruction causes only the program counter to be incremented.\nNo other registers or memory locations are affected.',
        'instr_desc': 'No operation',
        'operation': 'Not affected.',
        'source form': 'NOP'
    },
    OR: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs an inclusive OR operation between the contents of accumulator A or B and the contents of memory location M and the result is stored in accumulator A or B.',
        'instr_desc': 'OR memory with accumulator',
        'operation': "R' = R OR M",
        'source form': 'ORA P; ORB P'
    },
    ORCC: {
        'HNZVC': 'ddddd',
        'condition code': 'Affected according to the operation.',
        'description': 'Performs an inclusive OR operation between the contents of the condition code registers and the immediate value, and the result is placed in the condition code register.\nThis instruction may be used to set interrupt masks (disable interrupts) or any other bit(s).',
        'instr_desc': 'OR condition code register',
        'operation': "R' = R OR MI",
        'source form': 'ORCC #XX'
    },
    OTHER_INSTRUCTIONS: {
        'HNZVC': '-----', 'instr_desc': 'Branch if lower (unsigned)'
    },
    PAGE: {
        'HNZVC': '+++++',
        'description': 'Page 1/2 instructions',
        'instr_desc': 'Page 2 Instructions prefix'
    },
    PSHS: {
        'HNZVC': '-----',
        'comment': 'A single register may be placed on the stack with the condition codes set by doing an autodecrement store onto the stack (example: STX ,--S).',
        'condition code': 'Not affected.',
        'description': 'All, some, or none of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself).',
        'instr_desc': 'Push A, B, CC, DP, D, X, Y, U, or PC onto hardware stack',
        'operation': 'Push Registers on S Stack: S -= 1: MEM(S) = Reg.',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC U Y X DP B A CC\npush order ->'
    },
    PSHU: {
        'HNZVC': '-----',
        'comment': 'A single register may be placed on the stack with the condition codes set by doing an autodecrement store onto the stack (example: STX ,--U).',
        'condition code': 'Not affected.',
        'description': 'All, some, or none of the processor registers are pushed onto the user stack (with the exception of the user stack pointer itself).',
        'instr_desc': 'Push A, B, CC, DP, D, X, Y, S, or PC onto user stack',
        'operation': 'Push Registers on U Stack: U -= 1: MEM(U) = Reg.',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC S Y X DP B A CC\npush order ->'
    },
    PULS: {
        'HNZVC': 'ccccc',
        'comment': 'A single register may be pulled from the stack with condition codes set by doing an autoincrement load from the stack (example: LDX ,S++).',
        'condition code': 'May be pulled from stack; not affected otherwise.',
        'description': 'All, some, or none of the processor registers are pulled from the hardware stack (with the exception of the hardware stack pointer itself).',
        'instr_desc': 'Pull A, B, CC, DP, D, X, Y, U, or PC from hardware stack',
        'operation': 'Pull Registers from S Stack: Reg. = MEM(S): S += 1',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC U Y X DP B A CC\n= pull order'
    },
    PULU: {
        'HNZVC': 'ccccc',
        'comment': 'A single register may be pulled from the stack with condition codes set by doing an autoincrement load from the stack (example: LDX ,U++).',
        'condition code': 'May be pulled from stack; not affected otherwise.',
        'description': 'All, some, or none of the processor registers are pulled from the user stack (with the exception of the user stack pointer itself).',
        'instr_desc': 'Pull A, B, CC, DP, D, X, Y, S, or PC from hardware stack',
        'operation': 'Pull Registers from U Stack: Reg. = MEM(U): U += 1',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC S Y X DP B A CC\n= pull order'
    },
    RESET: {
        'HNZVC': '*****',
        'description': ' Build the ASSIST09 vector table and setup monitor defaults, then invoke the monitor startup routine.',
        'instr_desc': ''
    },
    ROL: {
        'HNZVC': '-aaas',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\nC - Loaded with bit seven of the original operand.',
        'description': 'Rotates all bits of the operand one place left through the C (carry) bit.\nThis is a 9-bit rotation.',
        'instr_desc': 'Rotate accumulator or memory left',
        'operation': 'C = = C\nb7 = b0',
        'source form': 'ROL Q; ROLA; ROLB'
    },
    ROR: {
        'HNZVC': '-aa-s',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the previous operand.',
        'description': 'Rotates all bits of the operand one place right through the C (carry) bit.\nThis is a 9-bit rotation.',
        'instr_desc': 'Rotate accumulator or memory right',
        'operation': 'C -> -> C\nb7 -> b0',
        'source form': 'ROR Q; RORA; RORB'
    },
    RTI: {
        'HNZVC': '-----',
        'condition code': 'Recovered from the stack.',
        'description': 'The saved machine state is recovered from the hardware stack and control is returned to the interrupted program.\nIf the recovered E (entire) bit is clear, it indicates that only a subset of the machine state was saved (return address and condition codes) and only that subset is recovered.',
        'instr_desc': 'Return from interrupt',
        'operation': "IFF CCR bit E is set, then: ACCA' ACCB' DPR' IXH' IXL' IYH' IYL' USH' USL' PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1\nIFF CCR bit E is clear, then: PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1",
        'source form': 'RTI'
    },
    RTS: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'Program control is returned from the subroutine to the calling program.\nThe return address is pulled from the stack.',
        'instr_desc': 'Return from subroutine',
        'operation': "PCH' = (SP), SP' = SP+1 PCL' = (SP), SP' = SP+1",
        'source form': 'RTS'
    },
    SBC: {
        'HNZVC': 'uaaaa',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the contents of memory location M and the borrow (in the C (carry) bit) from the contents of the designated 8-bit register, and places the result in that register.\nThe C bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'instr_desc': 'Subtract memory from accumulator with borrow',
        'operation': "R' = R - M - C",
        'source form': 'SBCA P; SBCB P'
    },
    SEX: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Not affected.',
        'description': 'This instruction transforms a twos complement 8-bit value in accumulator B into a twos complement 16-bit value in the D accumulator.',
        'instr_desc': 'Sign Extend B accumulator into A accumulator',
        'operation': "If bit seven of ACCB is set then ACCA' = FF 16 else ACCA' = 00 16",
        'source form': 'SEX'
    },
    ST16: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Writes the contents of a 16-bit register into two consecutive memory locations.',
        'instr_desc': 'Store stack pointer to memory',
        'operation': "M':M+1' = R",
        'source form': 'STD P; STX P; STY P; STS P; STU P'
    },
    ST8: {
        'HNZVC': '-aa0-',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Writes the contents of an 8-bit register into a memory location.',
        'instr_desc': 'Store accumulator to memroy',
        'operation': "M' = R",
        'source form': 'STA P; STB P'
    },
    SUB16: {
        'HNZVC': '-aaaa',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the value in memory location M:M+1 from the contents of a designated 16-bit register.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'instr_desc': 'Subtract memory from D accumulator',
        'operation': "R' = R - M:M+1",
        'source form': 'SUBD P'
    },
    SUB8: {
        'HNZVC': 'uaaaa',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the value in memory location M from the contents of a designated 8-bit register.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'instr_desc': 'Subtract memory from accumulator',
        'operation': "R' = R - M",
        'source form': 'SUBA P; SUBB P'
    },
    SWI: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt vector.\nBoth the normal and fast interrupts are masked (disabled).',
        'instr_desc': 'Software interrupt (absolute indirect)',
        'operation': "Set E (entire state will be saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR Set I, F (mask interrupts) PC' = (FFFA):(FFFB)",
        'source form': 'SWI'
    },
    SWI2: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt 2 vector.\nThis interrupt is available to the end user and must not be used in packaged software.\nThis interrupt does not mask (disable) the normal and fast interrupts.',
        'instr_desc': 'Software interrupt (absolute indirect)',
        'operation': "Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR PC' = (FFF4):(FFF5)",
        'source form': 'SWI2'
    },
    SWI3: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt 3 vector.\nThis interrupt does not mask (disable) the normal and fast interrupts.',
        'instr_desc': 'Software interrupt (absolute indirect)',
        'operation': "Set E (entire state will be saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR PC' = (FFF2):(FFF3)",
        'source form': 'SWI3'
    },
    SYNC: {
        'HNZVC': '-----',
        'condition code': 'Not affected.',
        'description': 'FAST SYNC WAIT FOR DATA\nInterrupt!\nLDA DISC DATA FROM DISC AND CLEAR INTERRUPT\nSTA ,X+ PUT IN BUFFER\nDECB COUNT IT, DONE?\nBNE FAST GO AGAIN IF NOT.',
        'instr_desc': 'Synchronize with interrupt line',
        'operation': 'Stop processing instructions',
        'source form': 'SYNC'
    },
    TFR: {
        'HNZVC': 'ccccc',
        'condition code': 'Not affected unless R2 is the condition code register.',
        'description': '0000 = A:B 1000 = A\n0001 = X 1001 = B\n0010 = Y 1010 = CCR\n0011 = US 1011 = DPR\n0100 = SP 1100 = Undefined\n0101 = PC 1101 = Undefined\n0110 = Undefined 1110 = Undefined\n0111 = Undefined 1111 = Undefined',
        'instr_desc': 'Transfer R1 to R2',
        'operation': 'R1 -> R2',
        'source form': 'TFR R1, R2'
    },
    TST: {
        'HNZVC': '-aa0-',
        'comment': 'The MC6800 processor clears the C (carry) bit.',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Set the N (negative) and Z (zero) bits according to the contents of memory location M, and clear the V (overflow) bit.\nThe TST instruction provides only minimum information when testing unsigned values; since no unsigned value is less than zero, BLO and BLS have no utility.\nWhile BHI could be used after TST, it provides exactly the same control as BNE, which is preferred.\nThe signed branches are available.',
        'instr_desc': 'Test accumulator or memory location',
        'operation': 'TEMP = M - 0',
        'source form': 'TST Q; TSTA; TSTB'
    },
}


OP_DATA = (

    #### 8-Bit Accumulator and Memory Instructions

    {
        "opcode": 0x0, "instruction": "NEG", "mnemonic": "NEG",
        "desc": "M = !M + 1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = 0 - M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x3, "instruction": "COM", "mnemonic": "COM",
        "desc": "M = complement(M)",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = 0 + M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x4, "instruction": "LSR", "mnemonic": "LSR",
        "desc": "M = Logical shift M right",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # 0 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x6, "instruction": "ROR", "mnemonic": "ROR",
        "desc": "M = Rotate M Right thru carry",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x7, "instruction": "ASR", "mnemonic": "ASR",
        "desc": "M = Arithmetic shift M right",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # b7 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x8, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "desc": "M = Logical shift M left",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C = = 0;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSL,
    },
    {
        "opcode": 0x9, "instruction": "ROL", "mnemonic": "ROL",
        "desc": "M = Rotate M left thru carry",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C = = C;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0xa, "instruction": "DEC", "mnemonic": "DEC",
        "desc": "M = M  1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = M - 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0xc, "instruction": "INC", "mnemonic": "INC",
        "desc": "M = M + 1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = M + 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0xd, "instruction": "TST", "mnemonic": "TST",
        "desc": "Test M",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = M - 0
        "mem_read": True, "mem_write": False,
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0xf, "instruction": "CLR", "mnemonic": "CLR",
        "desc": "M = 0",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = M M = 00 16
        "mem_read": False, "mem_write": True,
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x19, "instruction": "DAA", "mnemonic": "DAA",
        "desc": "Decimal Adjust A",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 0, "instr_info_key": DAA,
    },
    {
        "opcode": 0x1e, "instruction": "EXG", "mnemonic": "EXG",
        "desc": "exchange R1,R2",
        "addr_mode": IMMEDIATE, "cycles": 8, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R1 <-> R2
        "mem_read": True, "mem_write": False,
        "category": 0, "instr_info_key": EXG,
    },
    {
        "opcode": 0x1f, "instruction": "TFR", "mnemonic": "TFR",
        "desc": "Transfer R1 to R2",
        "addr_mode": IMMEDIATE, "cycles": 7, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R1 -> R2
        "mem_read": True, "mem_write": False,
        "category": 0, "instr_info_key": TFR,
    },
    {
        "opcode": 0x3d, "instruction": "MUL", "mnemonic": "MUL",
        "desc": "D = A*B (Unsigned)",
        "addr_mode": INHERENT, "cycles": 11, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 0, "instr_info_key": MUL,
    },
    {
        "opcode": 0x40, "instruction": "NEG", "mnemonic": "NEGA",
        "desc": "A = !A + 1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x43, "instruction": "COM", "mnemonic": "COMA",
        "desc": "A = complement(A)",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x44, "instruction": "LSR", "mnemonic": "LSRA",
        "desc": "A = Logical shift A right",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x46, "instruction": "ROR", "mnemonic": "RORA",
        "desc": "A = Rotate A Right thru carry",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x47, "instruction": "ASR", "mnemonic": "ASRA",
        "desc": "A = Arithmetic shift A right",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x48, "instruction": "LSL", "mnemonic": "LSLA/ASLA",
        "desc": "A = Logical shift A left",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LSL,
    },
    {
        "opcode": 0x49, "instruction": "ROL", "mnemonic": "ROLA",
        "desc": "A = Rotate A left thru carry",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x4a, "instruction": "DEC", "mnemonic": "DECA",
        "desc": "A = A  1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x4c, "instruction": "INC", "mnemonic": "INCA",
        "desc": "A = A + 1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x4d, "instruction": "TST", "mnemonic": "TSTA",
        "desc": "Test A",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x4f, "instruction": "CLR", "mnemonic": "CLRA",
        "desc": "A = 0",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x50, "instruction": "NEG", "mnemonic": "NEGB",
        "desc": "B = !B + 1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x53, "instruction": "COM", "mnemonic": "COMB",
        "desc": "B = complement(B)",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x54, "instruction": "LSR", "mnemonic": "LSRB",
        "desc": "B = Logical shift B right",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x56, "instruction": "ROR", "mnemonic": "RORB",
        "desc": "B = Rotate B Right thru carry",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x57, "instruction": "ASR", "mnemonic": "ASRB",
        "desc": "B = Arithmetic shift B right",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x58, "instruction": "LSL", "mnemonic": "LSLB/ASLB",
        "desc": "B = Logical shift B left",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LSL,
    },
    {
        "opcode": 0x59, "instruction": "ROL", "mnemonic": "ROLB",
        "desc": "B = Rotate B left thru carry",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x5a, "instruction": "DEC", "mnemonic": "DECB",
        "desc": "B = B  1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x5c, "instruction": "INC", "mnemonic": "INCB",
        "desc": "B = B + 1",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x5d, "instruction": "TST", "mnemonic": "TSTB",
        "desc": "Test B",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x5f, "instruction": "CLR", "mnemonic": "CLRB",
        "desc": "B = 0",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x60, "instruction": "NEG", "mnemonic": "NEG",
        "desc": "M = !M + 1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = 0 - M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x63, "instruction": "COM", "mnemonic": "COM",
        "desc": "M = complement(M)",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = 0 + M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x64, "instruction": "LSR", "mnemonic": "LSR",
        "desc": "M = Logical shift M right",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # 0 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x66, "instruction": "ROR", "mnemonic": "ROR",
        "desc": "M = Rotate M Right thru carry",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x67, "instruction": "ASR", "mnemonic": "ASR",
        "desc": "M = Arithmetic shift M right",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # b7 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x68, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "desc": "M = Logical shift M left",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C = = 0;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSL,
    },
    {
        "opcode": 0x69, "instruction": "ROL", "mnemonic": "ROL",
        "desc": "M = Rotate M left thru carry",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # C = = C;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x6a, "instruction": "DEC", "mnemonic": "DEC",
        "desc": "M = M  1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = M - 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x6c, "instruction": "INC", "mnemonic": "INC",
        "desc": "M = M + 1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = M + 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x6d, "instruction": "TST", "mnemonic": "TST",
        "desc": "Test M",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = M - 0
        "mem_read": True, "mem_write": False,
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x6f, "instruction": "CLR", "mnemonic": "CLR",
        "desc": "M = 0",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = M M = 00 16
        "mem_read": False, "mem_write": True,
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x70, "instruction": "NEG", "mnemonic": "NEG",
        "desc": "M = !M + 1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = 0 - M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x73, "instruction": "COM", "mnemonic": "COM",
        "desc": "M = complement(M)",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = 0 + M
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x74, "instruction": "LSR", "mnemonic": "LSR",
        "desc": "M = Logical shift M right",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # 0 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x76, "instruction": "ROR", "mnemonic": "ROR",
        "desc": "M = Rotate M Right thru carry",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # C -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x77, "instruction": "ASR", "mnemonic": "ASR",
        "desc": "M = Arithmetic shift M right",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # b7 -> -> C;b7 -> b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x78, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "desc": "M = Logical shift M left",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # C = = 0;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": LSL,
    },
    {
        "opcode": 0x79, "instruction": "ROL", "mnemonic": "ROL",
        "desc": "M = Rotate M left thru carry",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # C = = C;b7 = b0
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x7a, "instruction": "DEC", "mnemonic": "DEC",
        "desc": "M = M  1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = M - 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x7c, "instruction": "INC", "mnemonic": "INC",
        "desc": "M = M + 1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = M + 1
        "mem_read": True, "mem_write": True,
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x7d, "instruction": "TST", "mnemonic": "TST",
        "desc": "Test M",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = M - 0
        "mem_read": True, "mem_write": False,
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x7f, "instruction": "CLR", "mnemonic": "CLR",
        "desc": "M = 0",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = M M = 00 16
        "mem_read": False, "mem_write": True,
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x80, "instruction": "SUB", "mnemonic": "SUBA",
        "desc": "A = A - M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0x81, "instruction": "CMP", "mnemonic": "CMPA",
        "desc": "Compare M from A",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0x82, "instruction": "SBC", "mnemonic": "SBCA",
        "desc": "A = A - M - C",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0x84, "instruction": "AND", "mnemonic": "ANDA",
        "desc": "A = A && M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0x85, "instruction": "BIT", "mnemonic": "BITA",
        "desc": "Bit Test A (M&&A)",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0x86, "instruction": "LD", "mnemonic": "LDA",
        "desc": "A = M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0x88, "instruction": "EOR", "mnemonic": "EORA",
        "desc": "A = A XOR M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0x89, "instruction": "ADC", "mnemonic": "ADCA",
        "desc": "A = A+M+C",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0x8a, "instruction": "OR", "mnemonic": "ORA",
        "desc": "A = A || M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0x8b, "instruction": "ADD", "mnemonic": "ADDA",
        "desc": "A = A+M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0x90, "instruction": "SUB", "mnemonic": "SUBA",
        "desc": "A = A - M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0x91, "instruction": "CMP", "mnemonic": "CMPA",
        "desc": "Compare M from A",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0x92, "instruction": "SBC", "mnemonic": "SBCA",
        "desc": "A = A - M - C",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0x94, "instruction": "AND", "mnemonic": "ANDA",
        "desc": "A = A && M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0x95, "instruction": "BIT", "mnemonic": "BITA",
        "desc": "Bit Test A (M&&A)",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0x96, "instruction": "LD", "mnemonic": "LDA",
        "desc": "A = M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0x97, "instruction": "ST", "mnemonic": "STA",
        "desc": "M = A",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0x98, "instruction": "EOR", "mnemonic": "EORA",
        "desc": "A = A XOR M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0x99, "instruction": "ADC", "mnemonic": "ADCA",
        "desc": "A = A+M+C",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0x9a, "instruction": "OR", "mnemonic": "ORA",
        "desc": "A = A || M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0x9b, "instruction": "ADD", "mnemonic": "ADDA",
        "desc": "A = A+M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xa0, "instruction": "SUB", "mnemonic": "SUBA",
        "desc": "A = A - M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xa1, "instruction": "CMP", "mnemonic": "CMPA",
        "desc": "Compare M from A",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xa2, "instruction": "SBC", "mnemonic": "SBCA",
        "desc": "A = A - M - C",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xa4, "instruction": "AND", "mnemonic": "ANDA",
        "desc": "A = A && M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xa5, "instruction": "BIT", "mnemonic": "BITA",
        "desc": "Bit Test A (M&&A)",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xa6, "instruction": "LD", "mnemonic": "LDA",
        "desc": "A = M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xa7, "instruction": "ST", "mnemonic": "STA",
        "desc": "M = A",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xa8, "instruction": "EOR", "mnemonic": "EORA",
        "desc": "A = A XOR M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xa9, "instruction": "ADC", "mnemonic": "ADCA",
        "desc": "A = A+M+C",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xaa, "instruction": "OR", "mnemonic": "ORA",
        "desc": "A = A || M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xab, "instruction": "ADD", "mnemonic": "ADDA",
        "desc": "A = A+M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xb0, "instruction": "SUB", "mnemonic": "SUBA",
        "desc": "A = A - M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xb1, "instruction": "CMP", "mnemonic": "CMPA",
        "desc": "Compare M from A",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xb2, "instruction": "SBC", "mnemonic": "SBCA",
        "desc": "A = A - M - C",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xb4, "instruction": "AND", "mnemonic": "ANDA",
        "desc": "A = A && M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xb5, "instruction": "BIT", "mnemonic": "BITA",
        "desc": "Bit Test A (M&&A)",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xb6, "instruction": "LD", "mnemonic": "LDA",
        "desc": "A = M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xb7, "instruction": "ST", "mnemonic": "STA",
        "desc": "M = A",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xb8, "instruction": "EOR", "mnemonic": "EORA",
        "desc": "A = A XOR M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xb9, "instruction": "ADC", "mnemonic": "ADCA",
        "desc": "A = A+M+C",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xba, "instruction": "OR", "mnemonic": "ORA",
        "desc": "A = A || M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xbb, "instruction": "ADD", "mnemonic": "ADDA",
        "desc": "A = A+M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_A, # 8 Bit accumulator A
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xc0, "instruction": "SUB", "mnemonic": "SUBB",
        "desc": "B = B - M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xc1, "instruction": "CMP", "mnemonic": "CMPB",
        "desc": "Compare M from B",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xc2, "instruction": "SBC", "mnemonic": "SBCB",
        "desc": "B = B - M - C",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xc4, "instruction": "AND", "mnemonic": "ANDB",
        "desc": "B = B && M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xc5, "instruction": "BIT", "mnemonic": "BITB",
        "desc": "Bit Test B (M&&B)",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xc6, "instruction": "LD", "mnemonic": "LDB",
        "desc": "B = M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xc8, "instruction": "EOR", "mnemonic": "EORB",
        "desc": "B = M XOR B",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xc9, "instruction": "ADC", "mnemonic": "ADCB",
        "desc": "B = B+M+C",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xca, "instruction": "OR", "mnemonic": "ORB",
        "desc": "B = B || M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xcb, "instruction": "ADD", "mnemonic": "ADDB",
        "desc": "B = B+M",
        "addr_mode": IMMEDIATE, "cycles": 2, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xd0, "instruction": "SUB", "mnemonic": "SUBB",
        "desc": "B = B - M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xd1, "instruction": "CMP", "mnemonic": "CMPB",
        "desc": "Compare M from B",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xd2, "instruction": "SBC", "mnemonic": "SBCB",
        "desc": "B = B - M - C",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xd4, "instruction": "AND", "mnemonic": "ANDB",
        "desc": "B = B && M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xd5, "instruction": "BIT", "mnemonic": "BITB",
        "desc": "Bit Test B (M&&B)",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xd6, "instruction": "LD", "mnemonic": "LDB",
        "desc": "B = M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xd7, "instruction": "ST", "mnemonic": "STB",
        "desc": "M = B",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xd8, "instruction": "EOR", "mnemonic": "EORB",
        "desc": "B = M XOR B",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xd9, "instruction": "ADC", "mnemonic": "ADCB",
        "desc": "B = B+M+C",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xda, "instruction": "OR", "mnemonic": "ORB",
        "desc": "B = B || M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xdb, "instruction": "ADD", "mnemonic": "ADDB",
        "desc": "B = B+M",
        "addr_mode": DIRECT, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xe0, "instruction": "SUB", "mnemonic": "SUBB",
        "desc": "B = B - M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xe1, "instruction": "CMP", "mnemonic": "CMPB",
        "desc": "Compare M from B",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xe2, "instruction": "SBC", "mnemonic": "SBCB",
        "desc": "B = B - M - C",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xe4, "instruction": "AND", "mnemonic": "ANDB",
        "desc": "B = B && M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xe5, "instruction": "BIT", "mnemonic": "BITB",
        "desc": "Bit Test B (M&&B)",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xe6, "instruction": "LD", "mnemonic": "LDB",
        "desc": "B = M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xe7, "instruction": "ST", "mnemonic": "STB",
        "desc": "M = B",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xe8, "instruction": "EOR", "mnemonic": "EORB",
        "desc": "B = M XOR B",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xe9, "instruction": "ADC", "mnemonic": "ADCB",
        "desc": "B = B+M+C",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xea, "instruction": "OR", "mnemonic": "ORB",
        "desc": "B = B || M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xeb, "instruction": "ADD", "mnemonic": "ADDB",
        "desc": "B = B+M",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xf0, "instruction": "SUB", "mnemonic": "SUBB",
        "desc": "B = B - M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xf1, "instruction": "CMP", "mnemonic": "CMPB",
        "desc": "Compare M from B",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xf2, "instruction": "SBC", "mnemonic": "SBCB",
        "desc": "B = B - M - C",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M - C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xf4, "instruction": "AND", "mnemonic": "ANDB",
        "desc": "B = B && M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xf5, "instruction": "BIT", "mnemonic": "BITB",
        "desc": "Bit Test B (M&&B)",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R AND M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": BIT,
    },
    {
        "opcode": 0xf6, "instruction": "LD", "mnemonic": "LDB",
        "desc": "B = M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xf7, "instruction": "ST", "mnemonic": "STB",
        "desc": "M = B",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M' = R
        "mem_read": False, "mem_write": True,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xf8, "instruction": "EOR", "mnemonic": "EORB",
        "desc": "B = M XOR B",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R XOR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xf9, "instruction": "ADC", "mnemonic": "ADCB",
        "desc": "B = B+M+C",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M + C
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xfa, "instruction": "OR", "mnemonic": "ORB",
        "desc": "B = B || M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R OR M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xfb, "instruction": "ADD", "mnemonic": "ADDB",
        "desc": "B = B+M",
        "addr_mode": EXTENDED, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M
        "mem_read": True, "mem_write": False,
        "register": REG_B, # 8 Bit accumulator B
        "category": 0, "instr_info_key": ADD8,
    },

    #### 16-Bit Accumulator and Memory Instructions Instruction

    {
        "opcode": 0x1d, "instruction": "SEX", "mnemonic": "SEX",
        "desc": "Sign extend B into A",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 1, "instr_info_key": SEX,
    },
    {
        "opcode": 0x83, "instruction": "SUB", "mnemonic": "SUBD",
        "desc": "D = D - M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 4, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0x93, "instruction": "SUB", "mnemonic": "SUBD",
        "desc": "D = D - M:M+1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xa3, "instruction": "SUB", "mnemonic": "SUBD",
        "desc": "D = D - M:M+1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xb3, "instruction": "SUB", "mnemonic": "SUBD",
        "desc": "D = D - M:M+1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xc3, "instruction": "ADD", "mnemonic": "ADDD",
        "desc": "D = D+M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 4, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xcc, "instruction": "LD", "mnemonic": "LDD",
        "desc": "D = M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 3, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xd3, "instruction": "ADD", "mnemonic": "ADDD",
        "desc": "D = D+M:M+1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xdc, "instruction": "LD", "mnemonic": "LDD",
        "desc": "D = M:M+1",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xdd, "instruction": "ST", "mnemonic": "STD",
        "desc": "M:M+1 = D",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0xe3, "instruction": "ADD", "mnemonic": "ADDD",
        "desc": "D = D+M:M+1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xec, "instruction": "LD", "mnemonic": "LDD",
        "desc": "D = M:M+1",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xed, "instruction": "ST", "mnemonic": "STD",
        "desc": "M:M+1 = D",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0xf3, "instruction": "ADD", "mnemonic": "ADDD",
        "desc": "D = D+M:M+1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = R + M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xfc, "instruction": "LD", "mnemonic": "LDD",
        "desc": "D = M:M+1",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xfd, "instruction": "ST", "mnemonic": "STD",
        "desc": "M:M+1 = D",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0x1083, "instruction": "CMP", "mnemonic": "CMPD",
        "desc": "Compare M:M+1 from D",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x1093, "instruction": "CMP", "mnemonic": "CMPD",
        "desc": "Compare M:M+1 from D",
        "addr_mode": DIRECT, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10a3, "instruction": "CMP", "mnemonic": "CMPD",
        "desc": "Compare M:M+1 from D",
        "addr_mode": INDEXED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10b3, "instruction": "CMP", "mnemonic": "CMPD",
        "desc": "Compare M:M+1 from D",
        "addr_mode": EXTENDED, "cycles": 8, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_D, # 16 Bit concatenated register (A+B) D
        "category": 1, "instr_info_key": CMP16,
    },

    #### Index/Stack Pointer Instructions

    {
        "opcode": 0x30, "instruction": "LEA", "mnemonic": "LEAX",
        "desc": "X = EA",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x31, "instruction": "LEA", "mnemonic": "LEAY",
        "desc": "Y = EA",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x32, "instruction": "LEA", "mnemonic": "LEAS",
        "desc": "S = EA",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x33, "instruction": "LEA", "mnemonic": "LEAU",
        "desc": "U = EA",
        "addr_mode": INDEXED, "cycles": 4, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x34, "instruction": "PSHS", "mnemonic": "PSHS",
        "desc": "S -= 1: MEM(S) = R; Push Register on S Stack",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # Push Registers on S Stack: S -= 1: MEM(S) = Reg.
        "mem_read": True, "mem_write": False,
        "category": 2, "instr_info_key": PSHS,
    },
    {
        "opcode": 0x35, "instruction": "PULS", "mnemonic": "PULS",
        "desc": "R=MEM(S) : S += 1; Pull register from S Stack",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # Pull Registers from S Stack: Reg. = MEM(S): S += 1
        "mem_read": True, "mem_write": False,
        "category": 2, "instr_info_key": PULS,
    },
    {
        "opcode": 0x36, "instruction": "PSHU", "mnemonic": "PSHU",
        "desc": "U -= 1: MEM(U) = R; Push Register on U Stack",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # Push Registers on U Stack: U -= 1: MEM(U) = Reg.
        "mem_read": True, "mem_write": False,
        "category": 2, "instr_info_key": PSHU,
    },
    {
        "opcode": 0x37, "instruction": "PULU", "mnemonic": "PULU",
        "desc": "R=MEM(U) : U += 1; Pull register from U Stack",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # Pull Registers from U Stack: Reg. = MEM(U): U += 1
        "mem_read": True, "mem_write": False,
        "category": 2, "instr_info_key": PULU,
    },
    {
        "opcode": 0x3a, "instruction": "ABX", "mnemonic": "ABX",
        "desc": "X = B+X (Unsigned)",
        "addr_mode": INHERENT, "cycles": 3, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 2, "instr_info_key": ABX,
    },
    {
        "opcode": 0x8c, "instruction": "CMP", "mnemonic": "CMPX",
        "desc": "Compare M:M+1 from X",
        "addr_mode": IMMEDIATE, "cycles": 4, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x8e, "instruction": "LD", "mnemonic": "LDX",
        "desc": "X = M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 3, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x9c, "instruction": "CMP", "mnemonic": "CMPX",
        "desc": "Compare M:M+1 from X",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x9e, "instruction": "LD", "mnemonic": "LDX",
        "desc": "X = M:M+1",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x9f, "instruction": "ST", "mnemonic": "STX",
        "desc": "M:M+1 = X",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xac, "instruction": "CMP", "mnemonic": "CMPX",
        "desc": "Compare M:M+1 from X",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0xae, "instruction": "LD", "mnemonic": "LDX",
        "desc": "X = M:M+1",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xaf, "instruction": "ST", "mnemonic": "STX",
        "desc": "M:M+1 = X",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xbc, "instruction": "CMP", "mnemonic": "CMPX",
        "desc": "Compare M:M+1 from X",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0xbe, "instruction": "LD", "mnemonic": "LDX",
        "desc": "X = M:M+1",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xbf, "instruction": "ST", "mnemonic": "STX",
        "desc": "M:M+1 = X",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_X, # 16 Bit index register X
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xce, "instruction": "LD", "mnemonic": "LDU",
        "desc": "U = M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 3, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xde, "instruction": "LD", "mnemonic": "LDU",
        "desc": "U = M:M+1",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xdf, "instruction": "ST", "mnemonic": "STU",
        "desc": "M:M+1 = U",
        "addr_mode": DIRECT, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xee, "instruction": "LD", "mnemonic": "LDU",
        "desc": "U = M:M+1",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xef, "instruction": "ST", "mnemonic": "STU",
        "desc": "M:M+1 = U",
        "addr_mode": INDEXED, "cycles": 5, "bytes": 2,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xfe, "instruction": "LD", "mnemonic": "LDU",
        "desc": "U = M:M+1",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xff, "instruction": "ST", "mnemonic": "STU",
        "desc": "M:M+1 = U",
        "addr_mode": EXTENDED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x108c, "instruction": "CMP", "mnemonic": "CMPY",
        "desc": "Compare M:M+1 from Y",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x108e, "instruction": "LD", "mnemonic": "LDY",
        "desc": "Y = M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 4, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x109c, "instruction": "CMP", "mnemonic": "CMPY",
        "desc": "Compare M:M+1 from Y",
        "addr_mode": DIRECT, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x109e, "instruction": "LD", "mnemonic": "LDY",
        "desc": "Y = M:M+1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x109f, "instruction": "ST", "mnemonic": "STY",
        "desc": "M:M+1 = Y",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ac, "instruction": "CMP", "mnemonic": "CMPY",
        "desc": "Compare M:M+1 from Y",
        "addr_mode": INDEXED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10ae, "instruction": "LD", "mnemonic": "LDY",
        "desc": "Y = M:M+1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10af, "instruction": "ST", "mnemonic": "STY",
        "desc": "M:M+1 = Y",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10bc, "instruction": "CMP", "mnemonic": "CMPY",
        "desc": "Compare M:M+1 from Y",
        "addr_mode": EXTENDED, "cycles": 8, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10be, "instruction": "LD", "mnemonic": "LDY",
        "desc": "Y = M:M+1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10bf, "instruction": "ST", "mnemonic": "STY",
        "desc": "M:M+1 = Y",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_Y, # 16 Bit index register Y
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ce, "instruction": "LD", "mnemonic": "LDS",
        "desc": "S = M:M+1",
        "addr_mode": IMMEDIATE, "cycles": 4, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10de, "instruction": "LD", "mnemonic": "LDS",
        "desc": "S = M:M+1",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10df, "instruction": "ST", "mnemonic": "STS",
        "desc": "M:M+1 = S",
        "addr_mode": DIRECT, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ee, "instruction": "LD", "mnemonic": "LDS",
        "desc": "S = M:M+1",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10ef, "instruction": "ST", "mnemonic": "STS",
        "desc": "M:M+1 = S",
        "addr_mode": INDEXED, "cycles": 6, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10fe, "instruction": "LD", "mnemonic": "LDS",
        "desc": "S = M:M+1",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # R' = M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10ff, "instruction": "ST", "mnemonic": "STS",
        "desc": "M:M+1 = S",
        "addr_mode": EXTENDED, "cycles": 7, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # M':M+1' = R
        "mem_read": False, "mem_write": True,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x1183, "instruction": "CMP", "mnemonic": "CMPU",
        "desc": "Compare M:M+1 from U",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x118c, "instruction": "CMP", "mnemonic": "CMPS",
        "desc": "Compare M:M+1 from S",
        "addr_mode": IMMEDIATE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x1193, "instruction": "CMP", "mnemonic": "CMPU",
        "desc": "Compare M:M+1 from U",
        "addr_mode": DIRECT, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x119c, "instruction": "CMP", "mnemonic": "CMPS",
        "desc": "Compare M:M+1 from S",
        "addr_mode": DIRECT, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11a3, "instruction": "CMP", "mnemonic": "CMPU",
        "desc": "Compare M:M+1 from U",
        "addr_mode": INDEXED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11ac, "instruction": "CMP", "mnemonic": "CMPS",
        "desc": "Compare M:M+1 from S",
        "addr_mode": INDEXED, "cycles": 7, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11b3, "instruction": "CMP", "mnemonic": "CMPU",
        "desc": "Compare M:M+1 from U",
        "addr_mode": EXTENDED, "cycles": 8, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_U, # 16 Bit user-stack pointer U
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11bc, "instruction": "CMP", "mnemonic": "CMPS",
        "desc": "Compare M:M+1 from S",
        "addr_mode": EXTENDED, "cycles": 8, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = R - M:M+1
        "mem_read": True, "mem_write": False,
        "register": REG_S, # 16 Bit system-stack pointer S
        "category": 2, "instr_info_key": CMP16,
    },

    #### Simple Branch Instructions

    {
        "opcode": 0x2a, "instruction": "BPL", "mnemonic": "BPL",
        "desc": "Branch if plus",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF N = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 3, "instr_info_key": BPL,
    },
    {
        "opcode": 0x2b, "instruction": "BMI", "mnemonic": "BMI",
        "desc": "Branch if minus",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF N = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 3, "instr_info_key": BMI,
    },
    {
        "opcode": 0x102a, "instruction": "LBPL", "mnemonic": "LBPL",
        "desc": "Long branch if plus",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF N = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 3, "instr_info_key": BPL,
    },
    {
        "opcode": 0x102b, "instruction": "LBMI", "mnemonic": "LBMI",
        "desc": "Long branch if minus",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF N = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 3, "instr_info_key": BMI,
    },

    #### Signed Branch Instructions

    {
        "opcode": 0x28, "instruction": "BVC", "mnemonic": "BVC",
        "desc": "Branch if valid twos complement result",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF V = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BVC,
    },
    {
        "opcode": 0x29, "instruction": "BVS", "mnemonic": "BVS",
        "desc": "Branch if invalid twos complement result",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP' = MI IFF V = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BVS,
    },
    {
        "opcode": 0x2c, "instruction": "BGE", "mnemonic": "BGE",
        "desc": "Branch if greater than or equal (signed)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF [N XOR V] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BGE,
    },
    {
        "opcode": 0x2d, "instruction": "BLT", "mnemonic": "BLT",
        "desc": "Branch if less than (signed)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF [ N XOR V ] = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BLT,
    },
    {
        "opcode": 0x2e, "instruction": "BGT", "mnemonic": "BGT",
        "desc": "Branch if greater (signed)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF Z AND [N XOR V] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BGT,
    },
    {
        "opcode": 0x2f, "instruction": "BLE", "mnemonic": "BLE",
        "desc": "Branch if less than or equal (signed)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF Z OR [ N XOR V ] = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BLE,
    },
    {
        "opcode": 0x1028, "instruction": "LBVC", "mnemonic": "LBVC",
        "desc": "Long branch if valid twos complement result",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF V = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BVC,
    },
    {
        "opcode": 0x1029, "instruction": "LBVS", "mnemonic": "LBVS",
        "desc": "Long branch if invalid twos complement result",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP' = MI IFF V = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BVS,
    },
    {
        "opcode": 0x102c, "instruction": "LBGE", "mnemonic": "LBGE",
        "desc": "Long branch if greater than or equal (signed)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF [N XOR V] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BGE,
    },
    {
        "opcode": 0x102d, "instruction": "LBLT", "mnemonic": "LBLT",
        "desc": "Long branch if less than (signed)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF [ N XOR V ] = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BLT,
    },
    {
        "opcode": 0x102e, "instruction": "LBGT", "mnemonic": "LBGT",
        "desc": "Long branch if greater (signed)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF Z AND [N XOR V] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BGT,
    },
    {
        "opcode": 0x102f, "instruction": "LBLE", "mnemonic": "LBLE",
        "desc": "Long branch if less than or equal (signed)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF Z OR [ N XOR V ] = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 4, "instr_info_key": BLE,
    },

    #### Unsigned Branch Instructions

    {
        "opcode": 0x22, "instruction": "BHI", "mnemonic": "BHI",
        "desc": "Branch if higher (unsigned)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF [ C OR Z ] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BHI,
    },
    {
        "opcode": 0x23, "instruction": "BLS", "mnemonic": "BLS",
        "desc": "Branch if lower or same (unsigned)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF (C OR Z) = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BLS,
    },
    {
        "opcode": 0x24, "instruction": "BHS", "mnemonic": "BHS/BCC",
        "desc": "Branch if higher or same (unsigned)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF C = 0 then PC' = PC + MI
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BHS,
    },
    {
        "opcode": 0x25, "instruction": "BLO", "mnemonic": "BLO/BCS",
        "desc": "Branch if lower (unsigned)",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF C = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BLO,
    },
    {
        "opcode": 0x26, "instruction": "BNE", "mnemonic": "BNE",
        "desc": "Branch if not equal",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF Z = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BNE,
    },
    {
        "opcode": 0x27, "instruction": "BEQ", "mnemonic": "BEQ",
        "desc": "Branch if equal",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI IFF Z = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BEQ,
    },
    {
        "opcode": 0x1022, "instruction": "LBHI", "mnemonic": "LBHI",
        "desc": "Long branch if higher (unsigned)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF [ C OR Z ] = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BHI,
    },
    {
        "opcode": 0x1023, "instruction": "LBLS", "mnemonic": "LBLS",
        "desc": "Long branch if lower or same (unsigned)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF (C OR Z) = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BLS,
    },
    {
        "opcode": 0x1024, "instruction": "LBHS/LBCC", "mnemonic": "LBHS/LBCC",
        "desc": "Long branch if higher or same (unsigned)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD,
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1025, "instruction": "LBLO/LBCS", "mnemonic": "LBLO/LBCS",
        "desc": "Long branch if lower (unsigned)",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD,
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1026, "instruction": "LBNE", "mnemonic": "LBNE",
        "desc": "Long branch if not equal",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF Z = 0 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BNE,
    },
    {
        "opcode": 0x1027, "instruction": "LBEQ", "mnemonic": "LBEQ",
        "desc": "Long branch if equal",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI IFF Z = 1 then PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 5, "instr_info_key": BEQ,
    },

    #### other Branch Instructions

    {
        "opcode": 0x16, "instruction": "LBRA", "mnemonic": "LBRA",
        "desc": "Long branch always",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BRA,
    },
    {
        "opcode": 0x17, "instruction": "LBSR", "mnemonic": "LBSR",
        "desc": "Long branch to subroutine",
        "addr_mode": RELATIVE, "cycles": 9, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BSR,
    },
    {
        "opcode": 0x20, "instruction": "BRA", "mnemonic": "BRA",
        "desc": "Branch always",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BRA,
    },
    {
        "opcode": 0x21, "instruction": "BRN", "mnemonic": "BRN",
        "desc": "Branch never",
        "addr_mode": RELATIVE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BRN,
    },
    {
        "opcode": 0x8d, "instruction": "BSR", "mnemonic": "BSR",
        "desc": "Branch to subroutine",
        "addr_mode": RELATIVE, "cycles": 7, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # TEMP = MI SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' = PC + TEMP
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BSR,
    },
    {
        "opcode": 0x1021, "instruction": "LBRN", "mnemonic": "LBRN",
        "desc": "Long branch never",
        "addr_mode": RELATIVE, "cycles": 5, "bytes": 4,
        "mem_access": MEM_ACCESS_WORD, # TEMP = MI
        "mem_read": False, "mem_write": False,
        "category": 6, "instr_info_key": BRN,
    },

    #### Miscellaneous Instructions

    {
        "opcode": 0xe, "instruction": "JMP", "mnemonic": "JMP",
        "desc": "pc = EA",
        "addr_mode": DIRECT, "cycles": 3, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x12, "instruction": "NOP", "mnemonic": "NOP",
        "desc": "No Operation",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": NOP,
    },
    {
        "opcode": 0x13, "instruction": "SYNC", "mnemonic": "SYNC",
        "desc": "Synchronize to Interrupt",
        "addr_mode": INHERENT, "cycles": 2, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": SYNC,
    },
    {
        "opcode": 0x1a, "instruction": "OR", "mnemonic": "ORCC",
        "desc": "C = CC || IMM",
        "addr_mode": IMMEDIATE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R OR MI
        "mem_read": True, "mem_write": False,
        "register": REG_CC, # 8 Bit condition code register as flags CC
        "category": 7, "instr_info_key": ORCC,
    },
    {
        "opcode": 0x1c, "instruction": "AND", "mnemonic": "ANDCC",
        "desc": "C = CC && IMM",
        "addr_mode": IMMEDIATE, "cycles": 3, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # R' = R AND MI
        "mem_read": True, "mem_write": False,
        "register": REG_CC, # 8 Bit condition code register as flags CC
        "category": 7, "instr_info_key": ANDCC,
    },
    {
        "opcode": 0x39, "instruction": "RTS", "mnemonic": "RTS",
        "desc": "Return from subroutine",
        "addr_mode": INHERENT, "cycles": 5, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": RTS,
    },
    {
        "opcode": 0x3b, "instruction": "RTI", "mnemonic": "RTI",
        "desc": "Return from Interrupt",
        "addr_mode": INHERENT, "cycles": 6, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": RTI,
    },
    {
        "opcode": 0x3c, "instruction": "CWAI", "mnemonic": "CWAI",
        "desc": "CC = CC ^ IMM; (Wait for Interrupt)",
        "addr_mode": IMMEDIATE, "cycles": 21, "bytes": 2,
        "mem_access": MEM_ACCESS_BYTE, # CCR = CCR AND MI (Possibly clear masks) Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR
        "mem_read": True, "mem_write": False,
        "category": 7, "instr_info_key": CWAI,
    },
    {
        "opcode": 0x3f, "instruction": "SWI", "mnemonic": "SWI",
        "desc": "Software interrupt 1",
        "addr_mode": INHERENT, "cycles": 19, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": SWI,
    },
    {
        "opcode": 0x6e, "instruction": "JMP", "mnemonic": "JMP",
        "desc": "pc = EA",
        "addr_mode": INDEXED, "cycles": 3, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x7e, "instruction": "JMP", "mnemonic": "JMP",
        "desc": "pc = EA",
        "addr_mode": EXTENDED, "cycles": 3, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # PC' = EA
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x9d, "instruction": "JSR", "mnemonic": "JSR",
        "desc": "jump to subroutine",
        "addr_mode": DIRECT, "cycles": 7, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0xad, "instruction": "JSR", "mnemonic": "JSR",
        "desc": "jump to subroutine",
        "addr_mode": INDEXED, "cycles": 7, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0xbd, "instruction": "JSR", "mnemonic": "JSR",
        "desc": "jump to subroutine",
        "addr_mode": EXTENDED, "cycles": 8, "bytes": 3,
        "mem_access": MEM_ACCESS_WORD, # SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' =EA
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0x103f, "instruction": "SWI", "mnemonic": "SWI2",
        "desc": "Software interrupt 2",
        "addr_mode": INHERENT, "cycles": 20, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": SWI2,
    },
    {
        "opcode": 0x113f, "instruction": "SWI", "mnemonic": "SWI3",
        "desc": "Software interrupt 3",
        "addr_mode": INHERENT, "cycles": 20, "bytes": 2,
        "mem_read": False, "mem_write": False,
        "category": 7, "instr_info_key": SWI3,
    },

    #### other

    {
        "opcode": 0x10, "instruction": "PAGE", "mnemonic": "PAGE1+",
        "desc": "Page 1 Instructions prefix",
        "addr_mode": VARIANT, "cycles": 1, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 8, "instr_info_key": PAGE,
    },
    {
        "opcode": 0x11, "instruction": "PAGE", "mnemonic": "PAGE2+",
        "desc": "Page 2 Instructions prefix",
        "addr_mode": VARIANT, "cycles": 1, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 8, "instr_info_key": PAGE,
    },
    {
        "opcode": 0x3e, "instruction": "RESET", "mnemonic": "RESET",
        "desc": "",
        "addr_mode": INHERENT, "cycles": -1, "bytes": 1,
        "mem_read": False, "mem_write": False,
        "category": 8, "instr_info_key": RESET,
    },
)
