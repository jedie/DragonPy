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

IMMEDIATE=0
DIRECT=1
INDEXED=2
EXTENDED=3
INHERENT=4
RELATIVE=5
VARIANT=6

ADDRES_MODE_DICT = {
    IMMEDIATE: "IMMEDIATE",
    DIRECT: "DIRECT",
    INDEXED: "INDEXED",
    EXTENDED: "EXTENDED",
    INHERENT: "INHERENT",
    RELATIVE: "RELATIVE",
    VARIANT: "VARIANT",
}

# operants:
X = "X"
Y = "Y"
U = "U"
S = "S"
A = "A"
B = "B"
D = "D"
CC = "CC"

OPERANT_DICT = {
    X: "X (16 bit index register)",
    Y: "Y (16 bit index register)",
    U: "U (16 bit user stack pointer)",
    S: "S (16 bit system stack pointer)",
    A: "A (8 bit accumulator)",
    B: "B (8 bit accumulator)",
    D: "D (16 bit concatenated register A + B)",
    CC: "CC (8 bit condition code register bits)",
}

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
ASL="ASL"
ASR="ASR"
BCC="BCC"
BCS="BCS"
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
FIRQ="FIRQ"
INC="INC"
IRQ="IRQ"
JMP="JMP"
JSR="JSR"
LD16="LD16"
LD8="LD8"
LEA="LEA"
LSL="LSL"
LSR="LSR"
MUL="MUL"
NEG="NEG"
NMI="NMI"
NOP="NOP"
OR="OR"
ORCC="ORCC"
OTHER_INSTRUCTIONS="OTHER_INSTRUCTIONS"
PSHS="PSHS"
PSHU="PSHU"
PULS="PULS"
PULU="PULU"
RESTART="RESTART"
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
        'condition code': 'Not affected.',
        'description': 'Add the 8-bit unsigned value in accumulator B into index register X.',
        'operation': "IX' = IX + ACCB",
        'short_desc': 'Add B accumulator to X (unsigned)',
        'source form': 'ABX'
    },
    ADC: {
        'condition code': 'H - Set if a half-carry is generated; cleared otherwise.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the contents of the C (carry) bit and the memory byte into an 8-bit accumulator.',
        'operation': "R' = R + M + C",
        'short_desc': 'Add memory to accumulator with carry',
        'source form': 'ADCA P; ADCB P'
    },
    ADD16: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the 16-bit memory value into the 16-bit accumulator',
        'operation': "R' = R + M:M+1",
        'short_desc': 'Add memory to D accumulator',
        'source form': 'ADDD P'
    },
    ADD8: {
        'condition code': 'H - Set if a half-carry is generated; cleared otherwise.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a carry is generated; cleared otherwise.',
        'description': 'Adds the memory byte into an 8-bit accumulator.',
        'operation': "R' = R + M",
        'short_desc': 'Add memory to accumulator',
        'source form': 'ADDA P; ADDB P'
    },
    AND: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs the logical AND operation between the contents of an accumulator and the contents of memory location M and the result is stored in the accumulator.',
        'operation': "R' = R AND M",
        'short_desc': 'AND memory with accumulator',
        'source form': 'ANDA P; ANDB P'
    },
    ANDCC: {
        'condition code': 'Affected according to the operation.',
        'description': 'Performs a logical AND between the condition code register and the immediate byte specified in the instruction and places the result in the condition code register.',
        'operation': "R' = R AND MI",
        'short_desc': 'AND condition code register',
        'source form': 'ANDCC #xx'
    },
    ASL: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\nC - Loaded with bit seven of the original operand.',
        'description': 'Shifts all bits of the operand one place to the left. Bit zero is loaded with a zero. Bit seven is shifted into the C (carry) bit.',
        'operation': 'C = = 0\nb7 = b0',
        'source form': 'ASL Q; ASLA; ASLB'
    },
    ASR: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the original operand.',
        'description': 'Shifts all bits of the operand one place to the right. Bit seven is held constant. Bit zero is shifted into the C (carry) bit.',
        'operation': 'b7 -> -> C\nb7 -> b0',
        'short_desc': 'Arithmetic shift of accumulator or memory right',
        'source form': 'ASR Q; ASRA; ASRB'
    },
    BCC: {
        'comment': 'Equivalent to BHS dd; LBHS DDDD',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is clear.',
        'operation': "TEMP = MI IFF C = 0 then PC' = PC + TEMP",
        'source form': 'BCC dd; LBCC DDDD'
    },
    BCS: {
        'comment': 'Equivalent to BLO dd; LBLO DDDD',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is set.',
        'operation': "TEMP = MI IFF C = 1 then PC' = PC + TEMP",
        'source form': 'BCS dd; LBCS DDDD'
    },
    BEQ: {
        'condition code': 'Not affected.',
        'description': 'Tests the state of the Z (zero) bit and causes a branch if it is set.\nWhen used after a subtract or compare operation, this instruction will branch if the compared values, signed or unsigned, were exactly the same.',
        'operation': "TEMP = MI IFF Z = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if equal',
        'source form': 'BEQ dd; LBEQ DDDD'
    },
    BGE: {
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the N (negative) bit and the V (overflow) bit are either both set or both clear.\nThat is, branch if the sign of a valid twos complement result is, or would be, positive.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than or equal to the memory operand.',
        'operation': "TEMP = MI IFF [N XOR V] = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if greater than or equal (signed)',
        'source form': 'BGE dd; LBGE DDDD'
    },
    BGT: {
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the N (negative) bit and V (overflow) bit are either both set or both clear and the Z (zero) bit is clear.\nIn other words, branch if the sign of a valid twos complement result is, or would be, positive and not zero.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than the memory operand.',
        'operation': "TEMP = MI IFF Z AND [N XOR V] = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if greater (signed)',
        'source form': 'BGT dd; LBGT DDDD'
    },
    BHI: {
        'comment': 'Generally not useful after INC/DEC, LD/TST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the previous operation caused neither a carry nor a zero result.\nWhen used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was higher than the memory operand.',
        'operation': "TEMP = MI IFF [ C OR Z ] = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if higher (unsigned)',
        'source form': 'BHI dd; LBHI DDDD'
    },
    BHS: {
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction BCC.\nGenerally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is clear.\nWhen used after a subtract or compare on unsigned binary values, this instruction will branch if the register was higher than or the same as the memory operand.',
        'operation': "TEMP = MI IFF C = 0 then PC' = PC + MI",
        'source form': 'BHS dd; LBHS DDDD'
    },
    BIT: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs the logical AND of the contents of accumulator A or B and the contents of memory location M and modifies the condition codes accordingly.\nThe contents of accumulator A or B and memory location M are not affected.',
        'operation': 'TEMP = R AND M',
        'source form': 'Bit P'
    },
    BLE: {
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the exclusive OR of the N (negative) and V (overflow) bits is 1 or if the Z (zero) bit is set.\nThat is, branch if the sign of a valid twos complement result is, or would be, negative.\nWhen used after a subtract or compare operation on twos complement values, this instruction will branch if the register was less than or equal to the memory operand.',
        'operation': "TEMP = MI IFF Z OR [ N XOR V ] = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if less than or equal (signed)',
        'source form': 'BLE dd; LBLE DDDD'
    },
    BLO: {
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction BCS.\nGenerally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the C (carry) bit and causes a branch if it is set.\nWhen used after a subtract or compare on unsigned binary values, this instruction will branch if the register was lower than the memory operand.',
        'operation': "TEMP = MI IFF C = 1 then PC' = PC + TEMP",
        'source form': 'BLO dd; LBLO DDDD'
    },
    BLS: {
        'comment': 'Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
        'condition code': 'Not affected.',
        'description': 'Causes a branch if the previous operation caused either a carry or a zero result.\nWhen used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was lower than or the same as the memory operand.',
        'operation': "TEMP = MI IFF (C OR Z) = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if lower or same (unsigned)',
        'source form': 'BLS dd; LBLS DDDD'
    },
    BLT: {
        'condition code': 'Not affected.',
        'description': 'Causes a branch if either, but not both, of the N (negative) or V (overflow) bits is set.\nThat is, branch if the sign of a valid twos complement result is, or would be, negative.\nWhen used after a subtract or compare operation on twos complement binary values, this instruction will branch if the register was less than the memory operand.',
        'operation': "TEMP = MI IFF [ N XOR V ] = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if less than (signed)',
        'source form': 'BLT dd; LBLT DDDD'
    },
    BMI: {
        'comment': 'When used after an operation on signed binary values, this instruction will branch if the result is minus.\nIt is generally preferred to use the LBLT instruction after signed operations.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the N (negative) bit and causes a branch if set.\nThat is, branch if the sign of the twos complement result is negative.',
        'operation': "TEMP = MI IFF N = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if minus',
        'source form': 'BMI dd; LBMI DDDD'
    },
    BNE: {
        'condition code': 'Not affected.',
        'description': 'Tests the state of the Z (zero) bit and causes a branch if it is clear.\nWhen used after a subtract or compare operation on any binary values, this instruction will branch if the register is, or would be, not equal to the memory operand.',
        'operation': "TEMP = MI IFF Z = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if not equal',
        'source form': 'BNE dd; LBNE DDDD'
    },
    BPL: {
        'comment': 'When used after an operation on signed binary values, this instruction will branch if the result (possibly invalid) is positive.\nIt is generally preferred to use the BGE instruction after signed operations.',
        'condition code': 'Not affected.',
        'description': 'Tests the state of the N (negative) bit and causes a branch if it is clear.\nThat is, branch if the sign of the twos complement result is positive.',
        'operation': "TEMP = MI IFF N = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if plus',
        'source form': 'BPL dd; LBPL DDDD'
    },
    BRA: {
        'condition code': 'Not affected.',
        'description': 'Causes an unconditional branch.',
        'operation': "TEMP = MI PC' = PC + TEMP",
        'short_desc': 'Branch always',
        'source form': 'BRA dd; LBRA DDDD'
    },
    BRN: {
        'condition code': 'Not affected.',
        'description': 'Does not cause a branch.\nThis instruction is essentially a no operation, but has a bit pattern logically related to branch always.',
        'operation': 'TEMP = MI',
        'short_desc': 'Branch never',
        'source form': 'BRN dd; LBRN DDDD'
    },
    BSR: {
        'comment': 'A return from subroutine (RTS) instruction is used to reverse this process and must be the last instruction executed in a subroutine.',
        'condition code': 'Not affected.',
        'description': 'The program counter is pushed onto the stack.\nThe program counter is then loaded with the sum of the program counter and the offset.',
        'operation': "TEMP = MI SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' = PC + TEMP",
        'short_desc': 'Branch to subroutine',
        'source form': 'BSR dd; LBSR DDDD'
    },
    BVC: {
        'condition code': 'Not affected.',
        'description': 'Tests the state of the V (overflow) bit and causes a branch if it is clear.\nThat is, branch if the twos complement result was valid.\nWhen used after an operation on twos complement binary values, this instruction will branch if there was no overflow.',
        'operation': "TEMP = MI IFF V = 0 then PC' = PC + TEMP",
        'short_desc': 'Branch if valid twos complement result',
        'source form': 'BVC dd; LBVC DDDD'
    },
    BVS: {
        'condition code': 'Not affected.',
        'description': 'Tests the state of the V (overflow) bit and causes a branch if it is set.\nThat is, branch if the twos complement result was invalid.\nWhen used after an operation on twos complement binary values, this instruction will branch if there was an overflow.',
        'operation': "TEMP' = MI IFF V = 1 then PC' = PC + TEMP",
        'short_desc': 'Branch if invalid twos complement result',
        'source form': 'BVS dd; LBVS DDDD'
    },
    CLR: {
        'condition code': 'H - Not affected.\nN - Always cleared.\nZ - Always set.\nV - Always cleared.\nC - Always cleared.',
        'description': 'Accumulator A or B or memory location M is loaded with 00000000 2 .\nNote that the EA is read during this operation.',
        'operation': 'TEMP = M M = 00 16',
        'short_desc': 'Clear accumulator or memory location',
        'source form': 'CLR Q'
    },
    CMP16: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Compares the 16-bit contents of the concatenated memory locations M:M+1 to the contents of the specified register and sets the appropriate condition codes.\nNeither the memory locations nor the specified register is modified unless autoincrement or autodecrement are used.\nThe carry flag represents a borrow and is set to the inverse of the resulting binary carry.',
        'operation': 'TEMP = R - M:M+1',
        'short_desc': 'Compare memory from stack pointer',
        'source form': 'CMPD P; CMPX P; CMPY P; CMPU P; CMPS P'
    },
    CMP8: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Compares the contents of memory location to the contents of the specified register and sets the appropriate condition codes.\nNeither memory location M nor the specified register is modified.\nThe carry flag represents a borrow and is set to the inverse of the resulting binary carry.',
        'operation': 'TEMP = R - M',
        'short_desc': 'Compare memory from accumulator',
        'source form': 'CMPA P; CMPB P'
    },
    COM: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Always set.',
        'description': 'Replaces the contents of memory location M or accumulator A or B with its logical complement.\nWhen operating on unsigned values, only BEQ and BNE branches can be expected to behave properly following a COM instruction.\nWhen operating on twos complement values, all signed branches are available.',
        'operation': "M' = 0 + M",
        'short_desc': 'Complement accumulator or memory location',
        'source form': 'COM Q; COMA; COMB'
    },
    CWAI: {
        'comment': 'The following immediate values will have the following results: FF = enable neither EF = enable IRQ BF = enable FIRQ AF = enable both',
        'condition code': 'Affected according to the operation.',
        'description': 'This instruction ANDs an immediate byte with the condition code register which may clear the interrupt mask bits I and F, stacks the entire machine state on the hardware stack and then looks for an interrupt.\nWhen a non-masked interrupt occurs, no further machine state information need be saved before vectoring to the interrupt handling routine.\nThis instruction replaced the MC6800 CLI WAI sequence, but does not place the buses in a high-impedance state.\nA FIRQ (fast interrupt request) may enter its interrupt handler with its entire machine state saved.\nThe RTI (return from interrupt) instruction will automatically return the entire machine state after testing the E (entire) bit of the recovered condition code register.',
        'operation': "CCR = CCR AND MI (Possibly clear masks) Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR",
        'short_desc': 'AND condition code register, then wait for interrupt',
        'source form': 'CWAI #$XX E F H I N Z V C'
    },
    DAA: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Undefined.\nC - Set if a carry is generated or if the carry bit was set before the operation; cleared otherwise.',
        'description': 'The sequence of a single-byte add instruction on accumulator A (either ADDA or ADCA) and a following decimal addition adjust instruction results in a BCD addition with an appropriate carry bit.\nBoth values to be added must be in proper BCD form (each nibble such that: 0 <= nibble <= 9).\nMultiple-precision addition must add the carry generated by this decimal addition adjust into the next higher digit during the add operation (ADCA) immediately prior to the next decimal addition adjust.',
        'operation': 'Least Significant Nibble\nLeast Significant Nibble\nCF(LSN) = 6 IFF 1) C = 1\nor 2) LSN > 9\nMost Significant Nibble\nMost Significant Nibble\nCF(MSN) = 6 IFF 1) C = 1\nor 2) MSN > 9\nor 3) MSN > 8 and LSN > 9',
        'short_desc': 'Decimal adjust A accumulator',
        'source form': 'DAA'
    },
    DEC: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 10000000 2 ; cleared otherwise.\nC - Not affected.',
        'description': 'Subtract one from the operand.\nThe carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\nWhen operating on unsigned values, only BEQ and BNE branches can be expected to behave consistently.\nWhen operating on twos complement values, all signed branches are available.',
        'operation': "M' = M - 1",
        'short_desc': 'Decrement accumulator or memory location',
        'source form': 'DEC Q; DECA; DECB'
    },
    EOR: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'The contents of memory location M is exclusive ORed into an 8-bit register.',
        'operation': "R' = R XOR M",
        'short_desc': 'Exclusive OR memory with accumulator',
        'source form': 'EORA P; EORB P'
    },
    EXG: {
        'condition code': 'Not affected (unless one of the registers is the condition code\nregister).',
        'description': '0000 = A:B 1000 = A\n0001 = X 1001 = B\n0010 = Y 1010 = CCR\n0011 = US 1011 = DPR\n0100 = SP 1100 = Undefined\n0101 = PC 1101 = Undefined\n0110 = Undefined 1110 = Undefined\n0111 = Undefined 1111 = Undefined',
        'operation': 'R1 <-> R2',
        'short_desc': 'Exchange Rl with R2',
        'source form': 'EXG R1,R2'
    },
    FIRQ: {
        'condition code': 'Not affected.',
        'description': 'A FIRQ (fast interrupt request) with the F (fast interrupt request mask) bit clear causes this interrupt sequence to occur at the end of the current instruction.\nThe program counter and condition code register are pushed onto the hardware stack.\nProgram control is transferred through the fast interrupt request vector.\nAn RTI (return from interrupt) instruction returns the processor to the original task.\nIt is possible to enter the fast interrupt request routine with the entire machine state saved if the fast interrupt request occurs after a clear and wait for interrupt instruction.\nA normal interrupt request has lower priority than the fast interrupt request and is prevented from interrupting the fast interrupt request routine by automatic setting of the I (interrupt request mask) bit.\nThis mask bit could then be reset during the interrupt routine if priority was not desired.\nThe fast interrupt request allows operations on memory, TST, INC, DEC, etc. instructions without the overhead of saving the entire machine state on the stack.',
        'operation': "IFF F bit clear, then: SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH Clear E (subset state is saved) SP' = SP-1, (SP) = CCR Set F, I (mask further interrupts) PC' = (FFF6):(FFF7)"
    },
    INC: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 01111111 2 ; cleared otherwise.\nC - Not affected.',
        'description': 'Adds to the operand.\nThe carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\nWhen operating on unsigned values, only the BEQ and BNE branches can be expected to behave consistently.\nWhen operating on twos complement values, all signed branches are correctly available.',
        'operation': "M' = M + 1",
        'short_desc': 'Increment accumulator or memory location',
        'source form': 'INC Q; INCA; INCB'
    },
    IRQ: {
        'condition code': 'Not affected.',
        'description': 'If the I (interrupt request mask) bit is clear, a low level on the IRQ input causes this interrupt sequence to occur at the end of the current instruction.\nControl is returned to the interrupted program using a RTI (return from interrupt) instruction.\nA FIRQ (fast interrupt request) may interrupt a normal IRQ (interrupt request) routine and be recognized anytime after the interrupt vector is taken.',
        'operation': "IFF I bit clear, then: SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA Set E (entire state saved) SP' = SP-1, (SP) = CCR Set I (mask further IRQ interrupts) PC' = (FFF8):(FFF9)"
    },
    JMP: {
        'condition code': 'Not affected.',
        'description': 'Program control is transferred to the effective address.',
        'operation': "PC' = EA",
        'short_desc': 'Jump',
        'source form': 'JMP EA'
    },
    JSR: {
        'condition code': 'Not affected.',
        'description': 'Program control is transferred to the effective address after storing the return address on the hardware stack.\nA RTS instruction should be the last executed instruction of the subroutine.',
        'operation': "SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' =EA",
        'short_desc': 'Jump to subroutine',
        'source form': 'JSR EA'
    },
    LD16: {
        'condition code': 'H - Not affected.\nN - Set if the loaded data is negative; cleared otherwise.\nZ - Set if the loaded data is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Load the contents of the memory location M:M+1 into the designated 16-bit register.',
        'operation': "R' = M:M+1",
        'short_desc': 'Load stack pointer from memory',
        'source form': 'LDD P; LDX P; LDY P; LDS P; LDU P'
    },
    LD8: {
        'condition code': 'H - Not affected.\nN - Set if the loaded data is negative; cleared otherwise.\nZ - Set if the loaded data is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Loads the contents of memory location M into the designated register.',
        'operation': "R' = M",
        'short_desc': 'Load accumulator from memory',
        'source form': 'LDA P; LDB P'
    },
    LEA: {
        'comment': "Instruction Operation Comment\nInstruction\n\nOperation\n\nComment\nLEAX 10,X X+10 -> X Adds 5-bit constant 10 to X\nLEAX 500,X X+500 -> X Adds 16-bit constant 500 to X\nLEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y\nLEAY D,Y Y+D -> Y Adds 16-bit D accumulator to Y\nLEAU -10,U U-10 -> U Subtracts 10 from U\nLEAS -10,S S-10 -> S Used to reserve area on stack\nLEAS 10,S S+10 -> S Used to 'clean up' stack\nLEAX 5,S S+5 -> X Transfers as well as adds",
        'condition code': 'H - Not affected.\nN - Not affected.\nZ - LEAX, LEAY: Set if the result is zero; cleared otherwise. LEAS, LEAU: Not affected.\nV - Not affected.\nC - Not affected.',
        'description': 'Calculates the effective address from the indexed addressing mode and places the address in an indexable register. LEAX and LEAY affect the Z (zero) bit to allow use of these registers as counters and for MC6800 INX/DEX compatibility. LEAU and LEAS do not affect the Z bit to allow cleaning up the stack while returning the Z bit as a parameter to a calling routine, and also for MC6800 INS/DES compatibility.',
        'operation': "R' = EA",
        'short_desc': 'Load effective address into stack pointer',
        'source form': 'LEAX, LEAY, LEAS, LEAU'
    },
    LSL: {
        'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction ASL.',
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\nC - Loaded with bit seven of the original operand.',
        'description': 'Shifts all bits of accumulator A or B or memory location M one place to the left.\nBit zero is loaded with a zero.\nBit seven of accumulator A or B or memory location M is shifted into the C (carry) bit.',
        'operation': 'C = = 0\nb7 = b0',
        'source form': 'LSL Q; LSLA; LSLB'
    },
    LSR: {
        'condition code': 'H - Not affected.\nN - Always cleared.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the original operand.',
        'description': 'Performs a logical shift right on the operand.\nShifts a zero into bit seven and bit zero into the C (carry) bit.',
        'operation': '0 -> -> C\nb7 -> b0',
        'short_desc': 'Logical shift right accumulator or memory location',
        'source form': 'LSR Q; LSRA; LSRB'
    },
    MUL: {
        'comment': 'The C (carry) bit allows rounding the most-significant byte through the sequence: MUL, ADCA #0.',
        'condition code': 'H - Not affected.\nN - Not affected.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Set if ACCB bit 7 of result is set; cleared otherwise.',
        'description': 'Multiply the unsigned binary numbers in the accumulators and place the result in both accumulators (ACCA contains the most-significant byte of the result).\nUnsigned multiply allows multiple-precision operations.',
        'operation': "ACCA':ACCB' = ACCA * ACCB",
        'short_desc': 'Unsigned multiply (A * B ? D)',
        'source form': 'MUL'
    },
    NEG: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the original operand was 10000000 2 .\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Replaces the operand with its twos complement.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.\nNote that 80 16 is replaced by itself and only in this case is the V (overflow) bit set.\nThe value 00 16 is also replaced by itself, and only in this case is the C (carry) bit cleared.',
        'operation': "M' = 0 - M",
        'short_desc': 'Negate accumulator or memory',
        'source form': 'NEG Q; NEGA; NEG B'
    },
    NMI: {
        'condition code': 'Not affected.',
        'description': "A negative edge on the NMI (non-maskable interrupt) input causes all of the processor's registers (except the hardware stack pointer) to be pushed onto the hardware stack, starting at the end of the current instruction.\nProgram control is transferred through the NMI vector.\nSuccessive negative edges on the NMI input will cause successive NMI operations.\nNon-maskable interrupt operation can be internally blocked by a RESET operation and any non-maskable interrupt that occurs will be latched.\nIf this happens, the non-maskable interrupt operation will occur after the first load into the stack pointer (LDS; TFR r,s; EXG r,s; etc.) after RESET .",
        'operation': "SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA Set E (entire state save) SP' = SP-1, (SP) = CCR Set I, F (mask interrupts) PC' = (FFFC):(FFFD)"
    },
    NOP: {
        'condition code': 'This instruction causes only the program counter to be incremented.\nNo other registers or memory locations are affected.',
        'operation': 'Not affected.',
        'short_desc': 'No operation',
        'source form': 'NOP'
    },
    OR: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Performs an inclusive OR operation between the contents of accumulator A or B and the contents of memory location M and the result is stored in accumulator A or B.',
        'operation': "R' = R OR M",
        'short_desc': 'OR memory with accumulator',
        'source form': 'ORA P; ORB P'
    },
    ORCC: {
        'condition code': 'Affected according to the operation.',
        'description': 'Performs an inclusive OR operation between the contents of the condition code registers and the immediate value, and the result is placed in the condition code register.\nThis instruction may be used to set interrupt masks (disable interrupts) or any other bit(s).',
        'operation': "R' = R OR MI",
        'short_desc': 'OR condition code register',
        'source form': 'ORCC #XX'
    },
    OTHER_INSTRUCTIONS: {
        'short_desc': 'Branch if less than or equal (signed)'
    },
    PSHS: {
        'comment': 'A single register may be placed on the stack with the condition codes set by doing an autodecrement store onto the stack (example: STX ,--S).',
        'condition code': 'Not affected.',
        'description': 'All, some, or none of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself).',
        'operation': "IFF b7 of postbyte set, then: SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH\nIFF b6 of postbyte set, then: SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH\nIFF b5 of postbyte set, then: SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH\nIFF b4 of postbyte set, then: SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH\nIFF b3 of postbyte set, then: SP' = SP-1, (SP) = DPR\nIFF b2 of postbyte set, then: SP' = SP-1, (SP) = ACCB\nIFF b1 of postbyte set, then: SP' = SP-1, (SP) = ACCA\nIFF b0 of postbyte set, then: SP' = SP-1, (SP) = CCR",
        'short_desc': 'Push A, B, CC, DP, D, X, Y, U, or PC onto hardware stack',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC U Y X DP B A CC\npush order ->'
    },
    PSHU: {
        'comment': 'A single register may be placed on the stack with the condition codes set by doing an autodecrement store onto the stack (example: STX ,--U).',
        'condition code': 'Not affected.',
        'description': 'All, some, or none of the processor registers are pushed onto the user stack (with the exception of the user stack pointer itself).',
        'operation': "IFF b7 of postbyte set, then: US' = US-1, (US) = PCL US' = US-1, (US) = PCH\nIFF b6 of postbyte set, then: US' = US-1, (US) = SPL US' = US-1, (US) = SPH\nIFF b5 of postbyte set, then: US' = US-1, (US) = IYL US' = US-1, (US) = IYH\nIFF b4 of postbyte set, then: US' = US-1, (US) = IXL US' = US-1, (US) = IXH\nIFF b3 of postbyte set, then: US' = US-1, (US) = DPR\nIFF b2 of postbyte set, then: US' = US-1, (US) = ACCB\nIFF b1 of postbyte set, then: US' = US-1, (US) = ACCA\nIFF b0 of postbyte set, then: US' = US-1, (US) = CCR",
        'short_desc': 'Push A, B, CC, DP, D, X, Y, S, or PC onto user stack',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC S Y X DP B A CC\npush order ->'
    },
    PULS: {
        'comment': 'A single register may be pulled from the stack with condition codes set by doing an autoincrement load from the stack (example: LDX ,S++).',
        'condition code': 'May be pulled from stack; not affected otherwise.',
        'description': 'All, some, or none of the processor registers are pulled from the hardware stack (with the exception of the hardware stack pointer itself).',
        'operation': "IFF b0 of postbyte set, then: CCR' = (SP), SP' = SP+1\nIFF b1 of postbyte set, then: ACCA' = (SP), SP' = SP+1\nIFF b2 of postbyte set, then: ACCB' = (SP), SP' = SP+1\nIFF b3 of postbyte set, then: DPR' = (SP), SP'  = SP+1\nIFF b4 of postbyte set, then: IXH' IXL' = (SP), SP' = SP+1 = (SP), SP' = SP+1\nIFF b5 of postbyte set, then: IYH' IYL' = (SP), SP' = SP+1 = (SP), SP' = SP+1\nIFF b6 of postbyte set, then: USH' USL' = (SP), SP' = SP+1 = (SP), SP' = SP+1\nIFF b7 of postbyte set, then: PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1",
        'short_desc': 'Pull A, B, CC, DP, D, X, Y, U, or PC from hardware stack',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC U Y X DP B A CC\n= pull order'
    },
    PULU: {
        'comment': 'A single register may be pulled from the stack with condition codes set by doing an autoincrement load from the stack (example: LDX ,U++).',
        'condition code': 'May be pulled from stack; not affected otherwise.',
        'description': 'All, some, or none of the processor registers are pulled from the user stack (with the exception of the user stack pointer itself).',
        'operation': "IFF b0 of postbyte set, then: CCR' = (US), US' = US+1\nIFF b1 of postbyte set, then: ACCA' = (US), US' = US+1\nIFF b2 of postbyte set, then: ACCB' = (US), US' = US+1\nIFF b3 of postbyte set, then: DPR' = (US), US' = US+1\nIFF b4 of postbyte set, then: IXH' IXL' = (US), US' = US+1 = (US), US' = US+1\nIFF b5 of postbyte set, then: IYH' IYL' = (US), US' = US+1 = (US), US' = US+1\nIFF b6 of postbyte set, then: SPH' SPL' = (US), US' = US+1 = (US), US' = US+1\nIFF b7 of postbyte set, then: PCH' PCL' = (US), US' = US+1 = (US), US' = US+1",
        'short_desc': 'Pull A, B, CC, DP, D, X, Y, S, or PC from hardware stack',
        'source form': 'b7 b6 b5 b4 b3 b2 b1 b0\nPC S Y X DP B A CC\n= pull order'
    },
    RESTART: {
        'condition code': 'Not affected.',
        'description': 'The processor is initialized (required after power-on) to start program execution.\nThe starting address is fetched from the restart vector.',
        'operation': "CCR' = X1X1XXXX DPR' = 00 16 PC' = (FFFE):(FFFF)"
    },
    ROL: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\nC - Loaded with bit seven of the original operand.',
        'description': 'Rotates all bits of the operand one place left through the C (carry) bit.\nThis is a 9-bit rotation.',
        'operation': 'C = = C\nb7 = b0',
        'short_desc': 'Rotate accumulator or memory left',
        'source form': 'ROL Q; ROLA; ROLB'
    },
    ROR: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Loaded with bit zero of the previous operand.',
        'description': 'Rotates all bits of the operand one place right through the C (carry) bit.\nThis is a 9-bit rotation.',
        'operation': 'C -> -> C\nb7 -> b0',
        'short_desc': 'Rotate accumulator or memory right',
        'source form': 'ROR Q; RORA; RORB'
    },
    RTI: {
        'condition code': 'Recovered from the stack.',
        'description': 'The saved machine state is recovered from the hardware stack and control is returned to the interrupted program.\nIf the recovered E (entire) bit is clear, it indicates that only a subset of the machine state was saved (return address and condition codes) and only that subset is recovered.',
        'operation': "IFF CCR bit E is set, then: ACCA' ACCB' DPR' IXH' IXL' IYH' IYL' USH' USL' PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1\nIFF CCR bit E is clear, then: PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1",
        'short_desc': 'Return from interrupt',
        'source form': 'RTI'
    },
    RTS: {
        'condition code': 'Not affected.',
        'description': 'Program control is returned from the subroutine to the calling program.\nThe return address is pulled from the stack.',
        'operation': "PCH' = (SP), SP' = SP+1 PCL' = (SP), SP' = SP+1",
        'short_desc': 'Return from subroutine',
        'source form': 'RTS'
    },
    SBC: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if an overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the contents of memory location M and the borrow (in the C (carry) bit) from the contents of the designated 8-bit register, and places the result in that register.\nThe C bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'operation': "R' = R - M - C",
        'short_desc': 'Subtract memory from accumulator with borrow',
        'source form': 'SBCA P; SBCB P'
    },
    SEX: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Not affected.\nC - Not affected.',
        'description': 'This instruction transforms a twos complement 8-bit value in accumulator B into a twos complement 16-bit value in the D accumulator.',
        'operation': "If bit seven of ACCB is set then ACCA' = FF 16 else ACCA' = 00 16",
        'short_desc': 'Sign Extend B accumulator into A accumulator',
        'source form': 'SEX'
    },
    ST16: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Writes the contents of a 16-bit register into two consecutive memory locations.',
        'operation': "M':M+1' = R",
        'short_desc': 'Store stack pointer to memory',
        'source form': 'STD P; STX P; STY P; STS P; STU P'
    },
    ST8: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Writes the contents of an 8-bit register into a memory location.',
        'operation': "M' = R",
        'short_desc': 'Store accumulator to memroy',
        'source form': 'STA P; STB P'
    },
    SUB16: {
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the value in memory location M:M+1 from the contents of a designated 16-bit register.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'operation': "R' = R - M:M+1",
        'short_desc': 'Subtract memory from D accumulator',
        'source form': 'SUBD P'
    },
    SUB8: {
        'condition code': 'H - Undefined.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Set if the overflow is generated; cleared otherwise.\nC - Set if a borrow is generated; cleared otherwise.',
        'description': 'Subtracts the value in memory location M from the contents of a designated 8-bit register.\nThe C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.',
        'operation': "R' = R - M",
        'short_desc': 'Subtract memory from accumulator',
        'source form': 'SUBA P; SUBB P'
    },
    SWI: {
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt vector.\nBoth the normal and fast interrupts are masked (disabled).',
        'operation': "Set E (entire state will be saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR Set I, F (mask interrupts) PC' = (FFFA):(FFFB)",
        'short_desc': 'Software interrupt (absolute indirect)',
        'source form': 'SWI'
    },
    SWI2: {
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt 2 vector.\nThis interrupt is available to the end user and must not be used in packaged software.\nThis interrupt does not mask (disable) the normal and fast interrupts.',
        'operation': "Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR PC' = (FFF4):(FFF5)",
        'short_desc': 'Software interrupt (absolute indirect)',
        'source form': 'SWI2'
    },
    SWI3: {
        'condition code': 'Not affected.',
        'description': 'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt 3 vector.\nThis interrupt does not mask (disable) the normal and fast interrupts.',
        'operation': "Set E (entire state will be saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR PC' = (FFF2):(FFF3)",
        'short_desc': 'Software interrupt (absolute indirect)',
        'source form': 'SWI3'
    },
    SYNC: {
        'condition code': 'Not affected.',
        'description': 'FAST SYNC WAIT FOR DATA\nInterrupt!\nLDA DISC DATA FROM DISC AND CLEAR INTERRUPT\nSTA ,X+ PUT IN BUFFER\nDECB COUNT IT, DONE?\nBNE FAST GO AGAIN IF NOT.',
        'operation': 'Stop processing instructions',
        'short_desc': 'Synchronize with interrupt line',
        'source form': 'SYNC'
    },
    TFR: {
        'condition code': 'Not affected unless R2 is the condition code register.',
        'description': '0000 = A:B 1000 = A\n0001 = X 1001 = B\n0010 = Y 1010 = CCR\n0011 = US 1011 = DPR\n0100 = SP 1100 = Undefined\n0101 = PC 1101 = Undefined\n0110 = Undefined 1110 = Undefined\n0111 = Undefined 1111 = Undefined',
        'operation': 'R1 -> R2',
        'short_desc': 'Transfer R1 to R2',
        'source form': 'TFR R1, R2'
    },
    TST: {
        'comment': 'The MC6800 processor clears the C (carry) bit.',
        'condition code': 'H - Not affected.\nN - Set if the result is negative; cleared otherwise.\nZ - Set if the result is zero; cleared otherwise.\nV - Always cleared.\nC - Not affected.',
        'description': 'Set the N (negative) and Z (zero) bits according to the contents of memory location M, and clear the V (overflow) bit.\nThe TST instruction provides only minimum information when testing unsigned values; since no unsigned value is less than zero, BLO and BLS have no utility.\nWhile BHI could be used after TST, it provides exactly the same control as BNE, which is preferred.\nThe signed branches are available.',
        'operation': 'TEMP = M - 0',
        'short_desc': 'Test accumulator or memory location',
        'source form': 'TST Q; TSTA; TSTB'
    },
}


OP_DATA = (

    #### 8-Bit Accumulator and Memory Instructions

    {
        "opcode": 0x0, "instruction": "NEG", "mnemonic": "NEG",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x3, "instruction": "COM", "mnemonic": "COM",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa01",
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x4, "instruction": "LSR", "mnemonic": "LSR",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-0a-s",
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x6, "instruction": "ROR", "mnemonic": "ROR",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa-s",
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x7, "instruction": "ASR", "mnemonic": "ASR",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "uaa-s",
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x8, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "naaas",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x9, "instruction": "ROL", "mnemonic": "ROL",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaas",
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0xa, "instruction": "DEC", "mnemonic": "DEC",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0xc, "instruction": "INC", "mnemonic": "INC",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0xd, "instruction": "TST", "mnemonic": "TST",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0xf, "instruction": "CLR", "mnemonic": "CLR",
        "addr_mode": 1, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-0100",
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x19, "instruction": "DAA", "mnemonic": "DAA",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa0a",
        "category": 0, "instr_info_key": DAA,
    },
    {
        "opcode": 0x1e, "instruction": "EXG", "mnemonic": "EXG",
        "addr_mode": 0, "operant": None,
        "cycles": "8", "bytes": "2", "HNZVC": "ccccc",
        "category": 0, "instr_info_key": EXG,
    },
    {
        "opcode": 0x1f, "instruction": "TFR", "mnemonic": "TFR",
        "addr_mode": 0, "operant": None,
        "cycles": "7", "bytes": "2", "HNZVC": "ccccc",
        "category": 0, "instr_info_key": TFR,
    },
    {
        "opcode": 0x3d, "instruction": "MUL", "mnemonic": "MUL",
        "addr_mode": 4, "operant": None,
        "cycles": "11", "bytes": "1", "HNZVC": "--a-a",
        "category": 0, "instr_info_key": MUL,
    },
    {
        "opcode": 0x40, "instruction": "NEG", "mnemonic": "NEGA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x43, "instruction": "COM", "mnemonic": "COMA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa01",
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x44, "instruction": "LSR", "mnemonic": "LSRA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-0a-s",
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x46, "instruction": "ROR", "mnemonic": "RORA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa-s",
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x47, "instruction": "ASR", "mnemonic": "ASRA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "uaa-s",
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x48, "instruction": "LSL", "mnemonic": "LSLA/ASLA",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "naaas",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x49, "instruction": "ROL", "mnemonic": "ROLA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaas",
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x4a, "instruction": "DEC", "mnemonic": "DECA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x4c, "instruction": "INC", "mnemonic": "INCA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x4d, "instruction": "TST", "mnemonic": "TSTA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x4f, "instruction": "CLR", "mnemonic": "CLRA",
        "addr_mode": 4, "operant": A,
        "cycles": "2", "bytes": "1", "HNZVC": "-0100",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x50, "instruction": "NEG", "mnemonic": "NEGB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x53, "instruction": "COM", "mnemonic": "COMB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa01",
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x54, "instruction": "LSR", "mnemonic": "LSRB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-0a-s",
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x56, "instruction": "ROR", "mnemonic": "RORB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa-s",
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x57, "instruction": "ASR", "mnemonic": "ASRB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "uaa-s",
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x58, "instruction": "LSL", "mnemonic": "LSLB/ASLB",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "naaas",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x59, "instruction": "ROL", "mnemonic": "ROLB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaas",
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x5a, "instruction": "DEC", "mnemonic": "DECB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x5c, "instruction": "INC", "mnemonic": "INCB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x5d, "instruction": "TST", "mnemonic": "TSTB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x5f, "instruction": "CLR", "mnemonic": "CLRB",
        "addr_mode": 4, "operant": B,
        "cycles": "2", "bytes": "1", "HNZVC": "-0100",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x60, "instruction": "NEG", "mnemonic": "NEG",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x63, "instruction": "COM", "mnemonic": "COM",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa01",
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x64, "instruction": "LSR", "mnemonic": "LSR",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-0a-s",
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x66, "instruction": "ROR", "mnemonic": "ROR",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa-s",
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x67, "instruction": "ASR", "mnemonic": "ASR",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "uaa-s",
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x68, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "naaas",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x69, "instruction": "ROL", "mnemonic": "ROL",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaas",
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x6a, "instruction": "DEC", "mnemonic": "DEC",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x6c, "instruction": "INC", "mnemonic": "INC",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x6d, "instruction": "TST", "mnemonic": "TST",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x6f, "instruction": "CLR", "mnemonic": "CLR",
        "addr_mode": 2, "operant": None,
        "cycles": "6", "bytes": "2", "HNZVC": "-0100",
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x70, "instruction": "NEG", "mnemonic": "NEG",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": NEG,
    },
    {
        "opcode": 0x73, "instruction": "COM", "mnemonic": "COM",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aa01",
        "category": 0, "instr_info_key": COM,
    },
    {
        "opcode": 0x74, "instruction": "LSR", "mnemonic": "LSR",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-0a-s",
        "category": 0, "instr_info_key": LSR,
    },
    {
        "opcode": 0x76, "instruction": "ROR", "mnemonic": "ROR",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aa-s",
        "category": 0, "instr_info_key": ROR,
    },
    {
        "opcode": 0x77, "instruction": "ASR", "mnemonic": "ASR",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "uaa-s",
        "category": 0, "instr_info_key": ASR,
    },
    {
        "opcode": 0x78, "instruction": "LSL", "mnemonic": "LSL/ASL",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "naaas",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x79, "instruction": "ROL", "mnemonic": "ROL",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaas",
        "category": 0, "instr_info_key": ROL,
    },
    {
        "opcode": 0x7a, "instruction": "DEC", "mnemonic": "DEC",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": DEC,
    },
    {
        "opcode": 0x7c, "instruction": "INC", "mnemonic": "INC",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaa-",
        "category": 0, "instr_info_key": INC,
    },
    {
        "opcode": 0x7d, "instruction": "TST", "mnemonic": "TST",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": TST,
    },
    {
        "opcode": 0x7f, "instruction": "CLR", "mnemonic": "CLR",
        "addr_mode": 3, "operant": None,
        "cycles": "7", "bytes": "3", "HNZVC": "-0100",
        "category": 0, "instr_info_key": CLR,
    },
    {
        "opcode": 0x80, "instruction": "SUB", "mnemonic": "SUBA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0x81, "instruction": "CMP", "mnemonic": "CMPA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0x82, "instruction": "SBC", "mnemonic": "SBCA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0x84, "instruction": "AND", "mnemonic": "ANDA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0x85, "instruction": "BIT", "mnemonic": "BITA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x86, "instruction": "LD", "mnemonic": "LDA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0x88, "instruction": "EOR", "mnemonic": "EORA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0x89, "instruction": "ADC", "mnemonic": "ADCA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0x8a, "instruction": "OR", "mnemonic": "ORA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0x8b, "instruction": "ADD", "mnemonic": "ADDA",
        "addr_mode": 0, "operant": A,
        "cycles": "2", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0x90, "instruction": "SUB", "mnemonic": "SUBA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0x91, "instruction": "CMP", "mnemonic": "CMPA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0x92, "instruction": "SBC", "mnemonic": "SBCA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0x94, "instruction": "AND", "mnemonic": "ANDA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0x95, "instruction": "BIT", "mnemonic": "BITA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x96, "instruction": "LD", "mnemonic": "LDA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0x97, "instruction": "ST", "mnemonic": "STA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0x98, "instruction": "EOR", "mnemonic": "EORA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0x99, "instruction": "ADC", "mnemonic": "ADCA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0x9a, "instruction": "OR", "mnemonic": "ORA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0x9b, "instruction": "ADD", "mnemonic": "ADDA",
        "addr_mode": 1, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xa0, "instruction": "SUB", "mnemonic": "SUBA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xa1, "instruction": "CMP", "mnemonic": "CMPA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xa2, "instruction": "SBC", "mnemonic": "SBCA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xa4, "instruction": "AND", "mnemonic": "ANDA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xa5, "instruction": "BIT", "mnemonic": "BITA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xa6, "instruction": "LD", "mnemonic": "LDA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xa7, "instruction": "ST", "mnemonic": "STA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xa8, "instruction": "EOR", "mnemonic": "EORA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xa9, "instruction": "ADC", "mnemonic": "ADCA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xaa, "instruction": "OR", "mnemonic": "ORA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xab, "instruction": "ADD", "mnemonic": "ADDA",
        "addr_mode": 2, "operant": A,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xb0, "instruction": "SUB", "mnemonic": "SUBA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xb1, "instruction": "CMP", "mnemonic": "CMPA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xb2, "instruction": "SBC", "mnemonic": "SBCA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xb4, "instruction": "AND", "mnemonic": "ANDA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xb5, "instruction": "BIT", "mnemonic": "BITA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xb6, "instruction": "LD", "mnemonic": "LDA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xb7, "instruction": "ST", "mnemonic": "STA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xb8, "instruction": "EOR", "mnemonic": "EORA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xb9, "instruction": "ADC", "mnemonic": "ADCA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xba, "instruction": "OR", "mnemonic": "ORA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xbb, "instruction": "ADD", "mnemonic": "ADDA",
        "addr_mode": 3, "operant": A,
        "cycles": "5", "bytes": "3", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xc0, "instruction": "SUB", "mnemonic": "SUBB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xc1, "instruction": "CMP", "mnemonic": "CMPB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xc2, "instruction": "SBC", "mnemonic": "SBCB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xc4, "instruction": "AND", "mnemonic": "ANDB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xc5, "instruction": "BIT", "mnemonic": "BITB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xc6, "instruction": "LD", "mnemonic": "LDB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xc8, "instruction": "EOR", "mnemonic": "EORB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xc9, "instruction": "ADC", "mnemonic": "ADCB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xca, "instruction": "OR", "mnemonic": "ORB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xcb, "instruction": "ADD", "mnemonic": "ADDB",
        "addr_mode": 0, "operant": B,
        "cycles": "2", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xd0, "instruction": "SUB", "mnemonic": "SUBB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xd1, "instruction": "CMP", "mnemonic": "CMPB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xd2, "instruction": "SBC", "mnemonic": "SBCB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xd4, "instruction": "AND", "mnemonic": "ANDB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xd5, "instruction": "BIT", "mnemonic": "BITB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xd6, "instruction": "LD", "mnemonic": "LDB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xd7, "instruction": "ST", "mnemonic": "STB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xd8, "instruction": "EOR", "mnemonic": "EORB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xd9, "instruction": "ADC", "mnemonic": "ADCB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xda, "instruction": "OR", "mnemonic": "ORB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xdb, "instruction": "ADD", "mnemonic": "ADDB",
        "addr_mode": 1, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xe0, "instruction": "SUB", "mnemonic": "SUBB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xe1, "instruction": "CMP", "mnemonic": "CMPB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xe2, "instruction": "SBC", "mnemonic": "SBCB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xe4, "instruction": "AND", "mnemonic": "ANDB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xe5, "instruction": "BIT", "mnemonic": "BITB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xe6, "instruction": "LD", "mnemonic": "LDB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xe7, "instruction": "ST", "mnemonic": "STB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xe8, "instruction": "EOR", "mnemonic": "EORB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xe9, "instruction": "ADC", "mnemonic": "ADCB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xea, "instruction": "OR", "mnemonic": "ORB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xeb, "instruction": "ADD", "mnemonic": "ADDB",
        "addr_mode": 2, "operant": B,
        "cycles": "4", "bytes": "2", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },
    {
        "opcode": 0xf0, "instruction": "SUB", "mnemonic": "SUBB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SUB8,
    },
    {
        "opcode": 0xf1, "instruction": "CMP", "mnemonic": "CMPB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": CMP8,
    },
    {
        "opcode": 0xf2, "instruction": "SBC", "mnemonic": "SBCB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "uaaaa",
        "category": 0, "instr_info_key": SBC,
    },
    {
        "opcode": 0xf4, "instruction": "AND", "mnemonic": "ANDB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": AND,
    },
    {
        "opcode": 0xf5, "instruction": "BIT", "mnemonic": "BITB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0xf6, "instruction": "LD", "mnemonic": "LDB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": LD8,
    },
    {
        "opcode": 0xf7, "instruction": "ST", "mnemonic": "STB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": ST8,
    },
    {
        "opcode": 0xf8, "instruction": "EOR", "mnemonic": "EORB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": EOR,
    },
    {
        "opcode": 0xf9, "instruction": "ADC", "mnemonic": "ADCB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADC,
    },
    {
        "opcode": 0xfa, "instruction": "OR", "mnemonic": "ORB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "-aa0-",
        "category": 0, "instr_info_key": OR,
    },
    {
        "opcode": 0xfb, "instruction": "ADD", "mnemonic": "ADDB",
        "addr_mode": 3, "operant": B,
        "cycles": "5", "bytes": "3", "HNZVC": "aaaaa",
        "category": 0, "instr_info_key": ADD8,
    },

    #### 16-Bit Accumulator and Memory Instructions Instruction

    {
        "opcode": 0x1d, "instruction": "SEX", "mnemonic": "SEX",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": SEX,
    },
    {
        "opcode": 0x83, "instruction": "SUB", "mnemonic": "SUBD",
        "addr_mode": 0, "operant": D,
        "cycles": "4", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0x93, "instruction": "SUB", "mnemonic": "SUBD",
        "addr_mode": 1, "operant": D,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xa3, "instruction": "SUB", "mnemonic": "SUBD",
        "addr_mode": 2, "operant": D,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xb3, "instruction": "SUB", "mnemonic": "SUBD",
        "addr_mode": 3, "operant": D,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": SUB16,
    },
    {
        "opcode": 0xc3, "instruction": "ADD", "mnemonic": "ADDD",
        "addr_mode": 0, "operant": D,
        "cycles": "4", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xcc, "instruction": "LD", "mnemonic": "LDD",
        "addr_mode": 0, "operant": D,
        "cycles": "3", "bytes": "3", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xd3, "instruction": "ADD", "mnemonic": "ADDD",
        "addr_mode": 1, "operant": D,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xdc, "instruction": "LD", "mnemonic": "LDD",
        "addr_mode": 1, "operant": D,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xdd, "instruction": "ST", "mnemonic": "STD",
        "addr_mode": 1, "operant": D,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0xe3, "instruction": "ADD", "mnemonic": "ADDD",
        "addr_mode": 2, "operant": D,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xec, "instruction": "LD", "mnemonic": "LDD",
        "addr_mode": 2, "operant": D,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xed, "instruction": "ST", "mnemonic": "STD",
        "addr_mode": 2, "operant": D,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0xf3, "instruction": "ADD", "mnemonic": "ADDD",
        "addr_mode": 3, "operant": D,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": ADD16,
    },
    {
        "opcode": 0xfc, "instruction": "LD", "mnemonic": "LDD",
        "addr_mode": 3, "operant": D,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": LD16,
    },
    {
        "opcode": 0xfd, "instruction": "ST", "mnemonic": "STD",
        "addr_mode": 3, "operant": D,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 1, "instr_info_key": ST16,
    },
    {
        "opcode": 0x1083, "instruction": "CMP", "mnemonic": "CMPD",
        "addr_mode": 0, "operant": D,
        "cycles": "5", "bytes": "4", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x1093, "instruction": "CMP", "mnemonic": "CMPD",
        "addr_mode": 1, "operant": D,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10a3, "instruction": "CMP", "mnemonic": "CMPD",
        "addr_mode": 2, "operant": D,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10b3, "instruction": "CMP", "mnemonic": "CMPD",
        "addr_mode": 3, "operant": D,
        "cycles": "8", "bytes": "4", "HNZVC": "-aaaa",
        "category": 1, "instr_info_key": CMP16,
    },

    #### Index/Stack Pointer Instructions

    {
        "opcode": 0x30, "instruction": "LEA", "mnemonic": "LEAX",
        "addr_mode": 2, "operant": X,
        "cycles": "4", "bytes": "2", "HNZVC": "--a--",
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x31, "instruction": "LEA", "mnemonic": "LEAY",
        "addr_mode": 2, "operant": Y,
        "cycles": "4", "bytes": "2", "HNZVC": "--a--",
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x32, "instruction": "LEA", "mnemonic": "LEAS",
        "addr_mode": 2, "operant": S,
        "cycles": "4", "bytes": "2", "HNZVC": "-----",
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x33, "instruction": "LEA", "mnemonic": "LEAU",
        "addr_mode": 2, "operant": U,
        "cycles": "4", "bytes": "2", "HNZVC": "-----",
        "category": 2, "instr_info_key": LEA,
    },
    {
        "opcode": 0x34, "instruction": "PSH", "mnemonic": "PSHS",
        "addr_mode": 0, "operant": S,
        "cycles": "5", "bytes": "2", "HNZVC": "-----",
        "category": 2, "instr_info_key": PSHS,
    },
    {
        "opcode": 0x35, "instruction": "PUL", "mnemonic": "PULS",
        "addr_mode": 0, "operant": S,
        "cycles": "5", "bytes": "2", "HNZVC": "ccccc",
        "category": 2, "instr_info_key": PULS,
    },
    {
        "opcode": 0x36, "instruction": "PSH", "mnemonic": "PSHU",
        "addr_mode": 0, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "-----",
        "category": 2, "instr_info_key": PSHU,
    },
    {
        "opcode": 0x37, "instruction": "PUL", "mnemonic": "PULU",
        "addr_mode": 0, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "ccccc",
        "category": 2, "instr_info_key": PULU,
    },
    {
        "opcode": 0x3a, "instruction": "ABX", "mnemonic": "ABX",
        "addr_mode": 4, "operant": None,
        "cycles": "3", "bytes": "1", "HNZVC": "-----",
        "category": 2, "instr_info_key": ABX,
    },
    {
        "opcode": 0x8c, "instruction": "CMP", "mnemonic": "CMPX",
        "addr_mode": 0, "operant": X,
        "cycles": "4", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x8e, "instruction": "LD", "mnemonic": "LDX",
        "addr_mode": 0, "operant": X,
        "cycles": "3", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x9c, "instruction": "CMP", "mnemonic": "CMPX",
        "addr_mode": 1, "operant": X,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x9e, "instruction": "LD", "mnemonic": "LDX",
        "addr_mode": 1, "operant": X,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x9f, "instruction": "ST", "mnemonic": "STX",
        "addr_mode": 1, "operant": X,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xac, "instruction": "CMP", "mnemonic": "CMPX",
        "addr_mode": 2, "operant": X,
        "cycles": "6", "bytes": "2", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0xae, "instruction": "LD", "mnemonic": "LDX",
        "addr_mode": 2, "operant": X,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xaf, "instruction": "ST", "mnemonic": "STX",
        "addr_mode": 2, "operant": X,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xbc, "instruction": "CMP", "mnemonic": "CMPX",
        "addr_mode": 3, "operant": X,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0xbe, "instruction": "LD", "mnemonic": "LDX",
        "addr_mode": 3, "operant": X,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xbf, "instruction": "ST", "mnemonic": "STX",
        "addr_mode": 3, "operant": X,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xce, "instruction": "LD", "mnemonic": "LDU",
        "addr_mode": 0, "operant": U,
        "cycles": "3", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xde, "instruction": "LD", "mnemonic": "LDU",
        "addr_mode": 1, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xdf, "instruction": "ST", "mnemonic": "STU",
        "addr_mode": 1, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xee, "instruction": "LD", "mnemonic": "LDU",
        "addr_mode": 2, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xef, "instruction": "ST", "mnemonic": "STU",
        "addr_mode": 2, "operant": U,
        "cycles": "5", "bytes": "2", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0xfe, "instruction": "LD", "mnemonic": "LDU",
        "addr_mode": 3, "operant": U,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0xff, "instruction": "ST", "mnemonic": "STU",
        "addr_mode": 3, "operant": U,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x108c, "instruction": "CMP", "mnemonic": "CMPY",
        "addr_mode": 0, "operant": Y,
        "cycles": "5", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x108e, "instruction": "LD", "mnemonic": "LDY",
        "addr_mode": 0, "operant": Y,
        "cycles": "4", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x109c, "instruction": "CMP", "mnemonic": "CMPY",
        "addr_mode": 1, "operant": Y,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x109e, "instruction": "LD", "mnemonic": "LDY",
        "addr_mode": 1, "operant": Y,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x109f, "instruction": "ST", "mnemonic": "STY",
        "addr_mode": 1, "operant": Y,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ac, "instruction": "CMP", "mnemonic": "CMPY",
        "addr_mode": 2, "operant": Y,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10ae, "instruction": "LD", "mnemonic": "LDY",
        "addr_mode": 2, "operant": Y,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10af, "instruction": "ST", "mnemonic": "STY",
        "addr_mode": 2, "operant": Y,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10bc, "instruction": "CMP", "mnemonic": "CMPY",
        "addr_mode": 3, "operant": Y,
        "cycles": "8", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x10be, "instruction": "LD", "mnemonic": "LDY",
        "addr_mode": 3, "operant": Y,
        "cycles": "7", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10bf, "instruction": "ST", "mnemonic": "STY",
        "addr_mode": 3, "operant": Y,
        "cycles": "7", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ce, "instruction": "LD", "mnemonic": "LDS",
        "addr_mode": 0, "operant": S,
        "cycles": "4", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10de, "instruction": "LD", "mnemonic": "LDS",
        "addr_mode": 1, "operant": S,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10df, "instruction": "ST", "mnemonic": "STS",
        "addr_mode": 1, "operant": S,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10ee, "instruction": "LD", "mnemonic": "LDS",
        "addr_mode": 2, "operant": S,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10ef, "instruction": "ST", "mnemonic": "STS",
        "addr_mode": 2, "operant": S,
        "cycles": "6", "bytes": "3", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x10fe, "instruction": "LD", "mnemonic": "LDS",
        "addr_mode": 3, "operant": S,
        "cycles": "7", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": LD16,
    },
    {
        "opcode": 0x10ff, "instruction": "ST", "mnemonic": "STS",
        "addr_mode": 3, "operant": S,
        "cycles": "7", "bytes": "4", "HNZVC": "-aa0-",
        "category": 2, "instr_info_key": ST16,
    },
    {
        "opcode": 0x1183, "instruction": "CMP", "mnemonic": "CMPU",
        "addr_mode": 0, "operant": U,
        "cycles": "5", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x118c, "instruction": "CMP", "mnemonic": "CMPS",
        "addr_mode": 0, "operant": S,
        "cycles": "5", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x1193, "instruction": "CMP", "mnemonic": "CMPU",
        "addr_mode": 1, "operant": U,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x119c, "instruction": "CMP", "mnemonic": "CMPS",
        "addr_mode": 1, "operant": S,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11a3, "instruction": "CMP", "mnemonic": "CMPU",
        "addr_mode": 2, "operant": U,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11ac, "instruction": "CMP", "mnemonic": "CMPS",
        "addr_mode": 2, "operant": S,
        "cycles": "7", "bytes": "3", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11b3, "instruction": "CMP", "mnemonic": "CMPU",
        "addr_mode": 3, "operant": U,
        "cycles": "8", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },
    {
        "opcode": 0x11bc, "instruction": "CMP", "mnemonic": "CMPS",
        "addr_mode": 3, "operant": S,
        "cycles": "8", "bytes": "4", "HNZVC": "-aaaa",
        "category": 2, "instr_info_key": CMP16,
    },

    #### Simple Branch Instructions

    {
        "opcode": 0x2a, "instruction": "BPL", "mnemonic": "BPL",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 3, "instr_info_key": BPL,
    },
    {
        "opcode": 0x2b, "instruction": "BMI", "mnemonic": "BMI",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 3, "instr_info_key": BMI,
    },
    {
        "opcode": 0x102a, "instruction": "LBPL", "mnemonic": "LBPL",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 3, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x102b, "instruction": "LBMI", "mnemonic": "LBMI",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 3, "instr_info_key": OTHER_INSTRUCTIONS,
    },

    #### Signed Branch Instructions

    {
        "opcode": 0x28, "instruction": "BVC", "mnemonic": "BVC",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BVC,
    },
    {
        "opcode": 0x29, "instruction": "BVS", "mnemonic": "BVS",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BVS,
    },
    {
        "opcode": 0x2c, "instruction": "BGE", "mnemonic": "BGE",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BGE,
    },
    {
        "opcode": 0x2d, "instruction": "BLT", "mnemonic": "BLT",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BLT,
    },
    {
        "opcode": 0x2e, "instruction": "BGT", "mnemonic": "BGT",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BGT,
    },
    {
        "opcode": 0x2f, "instruction": "BLE", "mnemonic": "BLE",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 4, "instr_info_key": BLE,
    },
    {
        "opcode": 0x1028, "instruction": "LBVC", "mnemonic": "LBVC",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1029, "instruction": "LBVS", "mnemonic": "LBVS",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x102c, "instruction": "LBGE", "mnemonic": "LBGE",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x102d, "instruction": "LBLT", "mnemonic": "LBLT",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x102e, "instruction": "LBGT", "mnemonic": "LBGT",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x102f, "instruction": "LBLE", "mnemonic": "LBLE",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 4, "instr_info_key": OTHER_INSTRUCTIONS,
    },

    #### Unsigned Branch Instructions

    {
        "opcode": 0x22, "instruction": "BHI", "mnemonic": "BHI",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": BHI,
    },
    {
        "opcode": 0x23, "instruction": "BLS", "mnemonic": "BLS",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": BLS,
    },
    {
        "opcode": 0x24, "instruction": "BHS/BCC", "mnemonic": "BHS/BCC",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x25, "instruction": "BLO/BCS", "mnemonic": "BLO/BCS",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x26, "instruction": "BNE", "mnemonic": "BNE",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": BNE,
    },
    {
        "opcode": 0x27, "instruction": "BEQ", "mnemonic": "BEQ",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 5, "instr_info_key": BEQ,
    },
    {
        "opcode": 0x1022, "instruction": "LBHI", "mnemonic": "LBHI",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1023, "instruction": "LBLS", "mnemonic": "LBLS",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1024, "instruction": "LBHS/LBCC", "mnemonic": "LBHS/LBCC",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1025, "instruction": "LBLO/LBCS", "mnemonic": "LBLO/LBCS",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1026, "instruction": "LBNE", "mnemonic": "LBNE",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x1027, "instruction": "LBEQ", "mnemonic": "LBEQ",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 5, "instr_info_key": OTHER_INSTRUCTIONS,
    },

    #### other Branch Instructions

    {
        "opcode": 0x16, "instruction": "LBRA", "mnemonic": "LBRA",
        "addr_mode": 5, "operant": None,
        "cycles": "5", "bytes": "3", "HNZVC": "-----",
        "category": 6, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x17, "instruction": "LBSR", "mnemonic": "LBSR",
        "addr_mode": 5, "operant": None,
        "cycles": "9", "bytes": "3", "HNZVC": "-----",
        "category": 6, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x20, "instruction": "BRA", "mnemonic": "BRA",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 6, "instr_info_key": BRA,
    },
    {
        "opcode": 0x21, "instruction": "BRN", "mnemonic": "BRN",
        "addr_mode": 5, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 6, "instr_info_key": BRN,
    },
    {
        "opcode": 0x8d, "instruction": "BSR", "mnemonic": "BSR",
        "addr_mode": 5, "operant": None,
        "cycles": "7", "bytes": "2", "HNZVC": "-----",
        "category": 6, "instr_info_key": BSR,
    },
    {
        "opcode": 0x1021, "instruction": "LBRN", "mnemonic": "LBRN",
        "addr_mode": 5, "operant": None,
        "cycles": "5(6)", "bytes": "4", "HNZVC": "-----",
        "category": 6, "instr_info_key": OTHER_INSTRUCTIONS,
    },

    #### Miscellaneous Instructions

    {
        "opcode": 0xe, "instruction": "JMP", "mnemonic": "JMP",
        "addr_mode": 1, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x12, "instruction": "NOP", "mnemonic": "NOP",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "-----",
        "category": 7, "instr_info_key": NOP,
    },
    {
        "opcode": 0x13, "instruction": "SYNC", "mnemonic": "SYNC",
        "addr_mode": 4, "operant": None,
        "cycles": "2", "bytes": "1", "HNZVC": "-----",
        "category": 7, "instr_info_key": SYNC,
    },
    {
        "opcode": 0x1a, "instruction": "OR", "mnemonic": "ORCC",
        "addr_mode": 0, "operant": CC,
        "cycles": "3", "bytes": "2", "HNZVC": "ddddd",
        "category": 7, "instr_info_key": ORCC,
    },
    {
        "opcode": 0x1c, "instruction": "AND", "mnemonic": "ANDCC",
        "addr_mode": 0, "operant": CC,
        "cycles": "3", "bytes": "2", "HNZVC": "ddddd",
        "category": 7, "instr_info_key": ANDCC,
    },
    {
        "opcode": 0x39, "instruction": "RTS", "mnemonic": "RTS",
        "addr_mode": 4, "operant": None,
        "cycles": "5", "bytes": "1", "HNZVC": "-----",
        "category": 7, "instr_info_key": RTS,
    },
    {
        "opcode": 0x3b, "instruction": "RTI", "mnemonic": "RTI",
        "addr_mode": 4, "operant": None,
        "cycles": "6/15", "bytes": "1", "HNZVC": "-----",
        "category": 7, "instr_info_key": RTI,
    },
    {
        "opcode": 0x3c, "instruction": "CWAI", "mnemonic": "CWAI",
        "addr_mode": 0, "operant": None,
        "cycles": "21", "bytes": "2", "HNZVC": "ddddd",
        "category": 7, "instr_info_key": CWAI,
    },
    {
        "opcode": 0x3f, "instruction": "SWI", "mnemonic": "SWI",
        "addr_mode": 4, "operant": None,
        "cycles": "19", "bytes": "1", "HNZVC": "-----",
        "category": 7, "instr_info_key": SWI,
    },
    {
        "opcode": 0x6e, "instruction": "JMP", "mnemonic": "JMP",
        "addr_mode": 2, "operant": None,
        "cycles": "3", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x7e, "instruction": "JMP", "mnemonic": "JMP",
        "addr_mode": 3, "operant": None,
        "cycles": "3", "bytes": "3", "HNZVC": "-----",
        "category": 7, "instr_info_key": JMP,
    },
    {
        "opcode": 0x9d, "instruction": "JSR", "mnemonic": "JSR",
        "addr_mode": 1, "operant": None,
        "cycles": "7", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0xad, "instruction": "JSR", "mnemonic": "JSR",
        "addr_mode": 2, "operant": None,
        "cycles": "7", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0xbd, "instruction": "JSR", "mnemonic": "JSR",
        "addr_mode": 3, "operant": None,
        "cycles": "8", "bytes": "3", "HNZVC": "-----",
        "category": 7, "instr_info_key": JSR,
    },
    {
        "opcode": 0x103f, "instruction": "SWI", "mnemonic": "SWI2",
        "addr_mode": 4, "operant": None,
        "cycles": "20", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": SWI2,
    },
    {
        "opcode": 0x113f, "instruction": "SWI", "mnemonic": "SWI3",
        "addr_mode": 4, "operant": None,
        "cycles": "20", "bytes": "2", "HNZVC": "-----",
        "category": 7, "instr_info_key": SWI3,
    },

    #### other

    {
        "opcode": 0x10, "instruction": "PAGE1+", "mnemonic": "PAGE1+",
        "addr_mode": 6, "operant": None,
        "cycles": "1", "bytes": "1", "HNZVC": "+++++",
        "category": 8, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x11, "instruction": "PAGE2+", "mnemonic": "PAGE2+",
        "addr_mode": 6, "operant": None,
        "cycles": "1", "bytes": "1", "HNZVC": "+++++",
        "category": 8, "instr_info_key": OTHER_INSTRUCTIONS,
    },
    {
        "opcode": 0x3e, "instruction": "RESET*", "mnemonic": "RESET*",
        "addr_mode": 4, "operant": None,
        "cycles": "*", "bytes": "1", "HNZVC": "*****",
        "category": 8, "instr_info_key": OTHER_INSTRUCTIONS,
    },
)
