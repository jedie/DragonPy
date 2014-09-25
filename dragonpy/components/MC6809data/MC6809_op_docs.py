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

    :copyleft: 2013-2014 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

OP_DOC={'ABX': {'condition code': 'Not affected.',
       'description': 'Add the 8-bit unsigned value in accumulator B into index register X.',
       'instr_desc': 'Add B accumulator to X (unsigned)',
       'mnemonic': {'ABX': {'HNZVC': '-----',
                          'desc': 'X = B+X (Unsigned)'}},
       'operation': "IX' = IX + ACCB",
       'source form': 'ABX'},
'ADC': {'condition code': (
                         'H - Set if a half-carry is generated; cleared otherwise.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if an overflow is generated; cleared otherwise.\n'
                         'C - Set if a carry is generated; cleared otherwise.'
                         ),
       'description': 'Adds the contents of the C (carry) bit and the memory byte into an 8-bit accumulator.',
       'instr_desc': 'Add memory to accumulator with carry',
       'mnemonic': {'ADCA': {'HNZVC': 'aaaaa',
                           'desc': 'A = A+M+C'},
                   'ADCB': {'HNZVC': 'aaaaa',
                           'desc': 'B = B+M+C'}},
       'operation': "R' = R + M + C",
       'source form': 'ADCA P; ADCB P'},
'ADD': {'condition code': (
                         'H - Set if a half-carry is generated; cleared otherwise.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if an overflow is generated; cleared otherwise.\n'
                         'C - Set if a carry is generated; cleared otherwise.'
                         ),
       'description': 'Adds the memory byte into an 8-bit accumulator.',
       'instr_desc': 'Add memory to accumulator',
       'mnemonic': {'ADDA': {'HNZVC': 'aaaaa',
                           'desc': 'A = A+M'},
                   'ADDB': {'HNZVC': 'aaaaa',
                           'desc': 'B = B+M'},
                   'ADDD': {'HNZVC': '-aaaa',
                           'desc': 'D = D+M:M+1'}},
       'operation': "R' = R + M",
       'source form': 'ADDA P; ADDB P'},
'AND': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Always cleared.\n'
                         'C - Not affected.'
                         ),
       'description': 'Performs the logical AND operation between the contents of an accumulator and the contents of memory location M and the result is stored in the accumulator.',
       'instr_desc': 'AND memory with accumulator',
       'mnemonic': {'ANDA': {'HNZVC': '-aa0-',
                           'desc': 'A = A && M'},
                   'ANDB': {'HNZVC': '-aa0-',
                           'desc': 'B = B && M'},
                   'ANDCC': {'HNZVC': 'ddddd',
                            'desc': 'C = CC && IMM'}},
       'operation': "R' = R AND M",
       'source form': 'ANDA P; ANDB P'},
'ASR': {'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Not affected.\n'
                         'C - Loaded with bit zero of the original operand.'
                         ),
       'description': 'Shifts all bits of the operand one place to the right. Bit seven is held constant. Bit zero is shifted into the C (carry) bit.',
       'instr_desc': 'Arithmetic shift of accumulator or memory right',
       'mnemonic': {'ASR': {'HNZVC': 'uaa-s',
                          'desc': 'M = Arithmetic shift M right'},
                   'ASRA': {'HNZVC': 'uaa-s',
                           'desc': 'A = Arithmetic shift A right'},
                   'ASRB': {'HNZVC': 'uaa-s',
                           'desc': 'B = Arithmetic shift B right'}},
       'operation': (
                    'b7 -> -> C\n'
                    'b7 -> b0'
                    ),
       'source form': 'ASR Q; ASRA; ASRB'},
'BEQ': {'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the Z (zero) bit and causes a branch if it is set.\n'
                      'When used after a subtract or compare operation, this instruction will branch if the compared values, signed or unsigned, were exactly the same.'
                      ),
       'instr_desc': 'Branch if equal',
       'mnemonic': {'BEQ': {'HNZVC': '-----',
                          'desc': None},
                   'LBEQ': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF Z = 1 then PC' = PC + TEMP",
       'source form': 'BEQ dd; LBEQ DDDD'},
'BGE': {'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if the N (negative) bit and the V (overflow) bit are either both set or both clear.\n'
                      'That is, branch if the sign of a valid twos complement result is, or would be, positive.\n'
                      'When used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than or equal to the memory operand.'
                      ),
       'instr_desc': 'Branch if greater than or equal (signed)',
       'mnemonic': {'BGE': {'HNZVC': '-----',
                          'desc': None},
                   'LBGE': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF [N XOR V] = 0 then PC' = PC + TEMP",
       'source form': 'BGE dd; LBGE DDDD'},
'BGT': {'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if the N (negative) bit and V (overflow) bit are either both set or both clear and the Z (zero) bit is clear.\n'
                      'In other words, branch if the sign of a valid twos complement result is, or would be, positive and not zero.\n'
                      'When used after a subtract or compare operation on twos complement values, this instruction will branch if the register was greater than the memory operand.'
                      ),
       'instr_desc': 'Branch if greater (signed)',
       'mnemonic': {'BGT': {'HNZVC': '-----',
                          'desc': None},
                   'LBGT': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF Z AND [N XOR V] = 0 then PC' = PC + TEMP",
       'source form': 'BGT dd; LBGT DDDD'},
'BHI': {'comment': 'Generally not useful after INC/DEC, LD/TST, and TST/CLR/COM instructions.',
       'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if the previous operation caused neither a carry nor a zero result.\n'
                      'When used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was higher than the memory operand.'
                      ),
       'instr_desc': 'Branch if higher (unsigned)',
       'mnemonic': {'BHI': {'HNZVC': '-----',
                          'desc': None},
                   'LBHI': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF [ C OR Z ] = 0 then PC' = PC + TEMP",
       'source form': 'BHI dd; LBHI DDDD'},
'BHS': {'comment': (
                  'This is a duplicate assembly-language mnemonic for the single machine instruction BCC.\n'
                  'Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.'
                  ),
       'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the C (carry) bit and causes a branch if it is clear.\n'
                      'When used after a subtract or compare on unsigned binary values, this instruction will branch if the register was higher than or the same as the memory operand.'
                      ),
       'instr_desc': 'Branch if higher or same (unsigned)',
       'mnemonic': {'BCC': {'HNZVC': '-----',
                          'desc': None},
                   'LBCC': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF C = 0 then PC' = PC + MI",
       'source form': 'BHS dd; LBHS DDDD'},
'BIT': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Always cleared.\n'
                         'C - Not affected.'
                         ),
       'description': (
                      'Performs the logical AND of the contents of accumulator A or B and the contents of memory location M and modifies the condition codes accordingly.\n'
                      'The contents of accumulator A or B and memory location M are not affected.'
                      ),
       'instr_desc': 'Bit test memory with accumulator',
       'mnemonic': {'BITA': {'HNZVC': '-aa0-',
                           'desc': 'Bit Test A (M&&A)'},
                   'BITB': {'HNZVC': '-aa0-',
                           'desc': 'Bit Test B (M&&B)'}},
       'operation': 'TEMP = R AND M',
       'source form': 'BITA P; BITB P'},
'BLE': {'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if the exclusive OR of the N (negative) and V (overflow) bits is 1 or if the Z (zero) bit is set.\n'
                      'That is, branch if the sign of a valid twos complement result is, or would be, negative.\n'
                      'When used after a subtract or compare operation on twos complement values, this instruction will branch if the register was less than or equal to the memory operand.'
                      ),
       'instr_desc': 'Branch if less than or equal (signed)',
       'mnemonic': {'BLE': {'HNZVC': '-----',
                          'desc': None},
                   'LBLE': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF Z OR [ N XOR V ] = 1 then PC' = PC + TEMP",
       'source form': 'BLE dd; LBLE DDDD'},
'BLO': {'comment': (
                  'This is a duplicate assembly-language mnemonic for the single machine instruction BCS.\n'
                  'Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.'
                  ),
       'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the C (carry) bit and causes a branch if it is set.\n'
                      'When used after a subtract or compare on unsigned binary values, this instruction will branch if the register was lower than the memory operand.'
                      ),
       'instr_desc': 'Branch if lower (unsigned)',
       'mnemonic': {'BLO': {'HNZVC': '-----',
                          'desc': None},
                   'LBCS': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF C = 1 then PC' = PC + TEMP",
       'source form': 'BLO dd; LBLO DDDD'},
'BLS': {'comment': 'Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.',
       'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if the previous operation caused either a carry or a zero result.\n'
                      'When used after a subtract or compare operation on unsigned binary values, this instruction will branch if the register was lower than or the same as the memory operand.'
                      ),
       'instr_desc': 'Branch if lower or same (unsigned)',
       'mnemonic': {'BLS': {'HNZVC': '-----',
                          'desc': None},
                   'LBLS': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF (C OR Z) = 1 then PC' = PC + TEMP",
       'source form': 'BLS dd; LBLS DDDD'},
'BLT': {'condition code': 'Not affected.',
       'description': (
                      'Causes a branch if either, but not both, of the N (negative) or V (overflow) bits is set.\n'
                      'That is, branch if the sign of a valid twos complement result is, or would be, negative.\n'
                      'When used after a subtract or compare operation on twos complement binary values, this instruction will branch if the register was less than the memory operand.'
                      ),
       'instr_desc': 'Branch if less than (signed)',
       'mnemonic': {'BLT': {'HNZVC': '-----',
                          'desc': None},
                   'LBLT': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF [ N XOR V ] = 1 then PC' = PC + TEMP",
       'source form': 'BLT dd; LBLT DDDD'},
'BMI': {'comment': (
                  'When used after an operation on signed binary values, this instruction will branch if the result is minus.\n'
                  'It is generally preferred to use the LBLT instruction after signed operations.'
                  ),
       'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the N (negative) bit and causes a branch if set.\n'
                      'That is, branch if the sign of the twos complement result is negative.'
                      ),
       'instr_desc': 'Branch if minus',
       'mnemonic': {'BMI': {'HNZVC': '-----',
                          'desc': None},
                   'LBMI': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF N = 1 then PC' = PC + TEMP",
       'source form': 'BMI dd; LBMI DDDD'},
'BNE': {'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the Z (zero) bit and causes a branch if it is clear.\n'
                      'When used after a subtract or compare operation on any binary values, this instruction will branch if the register is, or would be, not equal to the memory operand.'
                      ),
       'instr_desc': 'Branch if not equal',
       'mnemonic': {'BNE': {'HNZVC': '-----',
                          'desc': None},
                   'LBNE': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF Z = 0 then PC' = PC + TEMP",
       'source form': 'BNE dd; LBNE DDDD'},
'BPL': {'comment': (
                  'When used after an operation on signed binary values, this instruction will branch if the result (possibly invalid) is positive.\n'
                  'It is generally preferred to use the BGE instruction after signed operations.'
                  ),
       'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the N (negative) bit and causes a branch if it is clear.\n'
                      'That is, branch if the sign of the twos complement result is positive.'
                      ),
       'instr_desc': 'Branch if plus',
       'mnemonic': {'BPL': {'HNZVC': '-----',
                          'desc': None},
                   'LBPL': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF N = 0 then PC' = PC + TEMP",
       'source form': 'BPL dd; LBPL DDDD'},
'BRA': {'condition code': 'Not affected.',
       'description': 'Causes an unconditional branch.',
       'instr_desc': 'Branch always',
       'mnemonic': {'BRA': {'HNZVC': '-----',
                          'desc': None},
                   'LBRA': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI PC' = PC + TEMP",
       'source form': 'BRA dd; LBRA DDDD'},
'BRN': {'condition code': 'Not affected.',
       'description': (
                      'Does not cause a branch.\n'
                      'This instruction is essentially a no operation, but has a bit pattern logically related to branch always.'
                      ),
       'instr_desc': 'Branch never',
       'mnemonic': {'BRN': {'HNZVC': '-----',
                          'desc': None},
                   'LBRN': {'HNZVC': '-----',
                           'desc': None}},
       'operation': 'TEMP = MI',
       'source form': 'BRN dd; LBRN DDDD'},
'BSR': {'comment': 'A return from subroutine (RTS) instruction is used to reverse this process and must be the last instruction executed in a subroutine.',
       'condition code': 'Not affected.',
       'description': (
                      'The program counter is pushed onto the stack.\n'
                      'The program counter is then loaded with the sum of the program counter and the offset.'
                      ),
       'instr_desc': 'Branch to subroutine',
       'mnemonic': {'BSR': {'HNZVC': '-----',
                          'desc': None},
                   'LBSR': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' = PC + TEMP",
       'source form': 'BSR dd; LBSR DDDD'},
'BVC': {'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the V (overflow) bit and causes a branch if it is clear.\n'
                      'That is, branch if the twos complement result was valid.\n'
                      'When used after an operation on twos complement binary values, this instruction will branch if there was no overflow.'
                      ),
       'instr_desc': 'Branch if valid twos complement result',
       'mnemonic': {'BVC': {'HNZVC': '-----',
                          'desc': None},
                   'LBVC': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP = MI IFF V = 0 then PC' = PC + TEMP",
       'source form': 'BVC dd; LBVC DDDD'},
'BVS': {'condition code': 'Not affected.',
       'description': (
                      'Tests the state of the V (overflow) bit and causes a branch if it is set.\n'
                      'That is, branch if the twos complement result was invalid.\n'
                      'When used after an operation on twos complement binary values, this instruction will branch if there was an overflow.'
                      ),
       'instr_desc': 'Branch if invalid twos complement result',
       'mnemonic': {'BVS': {'HNZVC': '-----',
                          'desc': None},
                   'LBVS': {'HNZVC': '-----',
                           'desc': None}},
       'operation': "TEMP' = MI IFF V = 1 then PC' = PC + TEMP",
       'source form': 'BVS dd; LBVS DDDD'},
'CLR': {'condition code': (
                         'H - Not affected.\n'
                         'N - Always cleared.\n'
                         'Z - Always set.\n'
                         'V - Always cleared.\n'
                         'C - Always cleared.'
                         ),
       'description': (
                      'Accumulator A or B or memory location M is loaded with 00000000 2 .\n'
                      'Note that the EA is read during this operation.'
                      ),
       'instr_desc': 'Clear accumulator or memory location',
       'mnemonic': {'CLR': {'HNZVC': '-0100',
                          'desc': 'M = 0'},
                   'CLRA': {'HNZVC': '-0100',
                           'desc': 'A = 0'},
                   'CLRB': {'HNZVC': '-0100',
                           'desc': 'B = 0'}},
       'operation': 'TEMP = M M = 00 16',
       'source form': 'CLR Q'},
'CMP': {'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if an overflow is generated; cleared otherwise.\n'
                         'C - Set if a borrow is generated; cleared otherwise.'
                         ),
       'description': (
                      'Compares the contents of memory location to the contents of the specified register and sets the appropriate condition codes.\n'
                      'Neither memory location M nor the specified register is modified.\n'
                      'The carry flag represents a borrow and is set to the inverse of the resulting binary carry.'
                      ),
       'instr_desc': 'Compare memory from accumulator',
       'mnemonic': {'CMPA': {'HNZVC': 'uaaaa',
                           'desc': 'Compare M from A'},
                   'CMPB': {'HNZVC': 'uaaaa',
                           'desc': 'Compare M from B'},
                   'CMPD': {'HNZVC': '-aaaa',
                           'desc': 'Compare M:M+1 from D'},
                   'CMPS': {'HNZVC': '-aaaa',
                           'desc': 'Compare M:M+1 from S'},
                   'CMPU': {'HNZVC': '-aaaa',
                           'desc': 'Compare M:M+1 from U'},
                   'CMPX': {'HNZVC': '-aaaa',
                           'desc': 'Compare M:M+1 from X'},
                   'CMPY': {'HNZVC': '-aaaa',
                           'desc': 'Compare M:M+1 from Y'}},
       'operation': 'TEMP = R - M',
       'source form': 'CMPA P; CMPB P'},
'COM': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Always cleared.\n'
                         'C - Always set.'
                         ),
       'description': (
                      'Replaces the contents of memory location M or accumulator A or B with its logical complement.\n'
                      'When operating on unsigned values, only BEQ and BNE branches can be expected to behave properly following a COM instruction.\n'
                      'When operating on twos complement values, all signed branches are available.'
                      ),
       'instr_desc': 'Complement accumulator or memory location',
       'mnemonic': {'COM': {'HNZVC': '-aa01',
                          'desc': 'M = complement(M)'},
                   'COMA': {'HNZVC': '-aa01',
                           'desc': 'A = complement(A)'},
                   'COMB': {'HNZVC': '-aa01',
                           'desc': 'B = complement(B)'}},
       'operation': "M' = 0 + M",
       'source form': 'COM Q; COMA; COMB'},
'CWAI': {'comment': 'The following immediate values will have the following results: FF = enable neither EF = enable IRQ BF = enable FIRQ AF = enable both',
        'condition code': 'Affected according to the operation.',
        'description': (
                       'This instruction ANDs an immediate byte with the condition code register which may clear the interrupt mask bits I and F, stacks the entire machine state on the hardware stack and then looks for an interrupt.\n'
                       'When a non-masked interrupt occurs, no further machine state information need be saved before vectoring to the interrupt handling routine.\n'
                       'This instruction replaced the MC6800 CLI WAI sequence, but does not place the buses in a high-impedance state.\n'
                       'A FIRQ (fast interrupt request) may enter its interrupt handler with its entire machine state saved.\n'
                       'The RTI (return from interrupt) instruction will automatically return the entire machine state after testing the E (entire) bit of the recovered condition code register.'
                       ),
        'instr_desc': 'AND condition code register, then wait for interrupt',
        'mnemonic': {'CWAI': {'HNZVC': 'ddddd',
                            'desc': 'CC = CC ^ IMM; (Wait for Interrupt)'}},
        'operation': "CCR = CCR AND MI (Possibly clear masks) Set E (entire state saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR",
        'source form': 'CWAI #$XX E F H I N Z V C'},
'DAA': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Undefined.\n'
                         'C - Set if a carry is generated or if the carry bit was set before the operation; cleared otherwise.'
                         ),
       'description': (
                      'The sequence of a single-byte add instruction on accumulator A (either ADDA or ADCA) and a following decimal addition adjust instruction results in a BCD addition with an appropriate carry bit.\n'
                      'Both values to be added must be in proper BCD form (each nibble such that: 0 <= nibble <= 9).\n'
                      'Multiple-precision addition must add the carry generated by this decimal addition adjust into the next higher digit during the add operation (ADCA) immediately prior to the next decimal addition adjust.'
                      ),
       'instr_desc': 'Decimal adjust A accumulator',
       'mnemonic': {'DAA': {'HNZVC': '-aa0a',
                          'desc': 'Decimal Adjust A'}},
       'operation': 'Decimal Adjust A',
       'source form': 'DAA'},
'DEC': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if the original operand was 10000000 2 ; cleared otherwise.\n'
                         'C - Not affected.'
                         ),
       'description': (
                      'Subtract one from the operand.\n'
                      'The carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\n'
                      'When operating on unsigned values, only BEQ and BNE branches can be expected to behave consistently.\n'
                      'When operating on twos complement values, all signed branches are available.'
                      ),
       'instr_desc': 'Decrement accumulator or memory location',
       'mnemonic': {'DEC': {'HNZVC': '-aaa-',
                          'desc': 'M = M - 1'},
                   'DECA': {'HNZVC': '-aaa-',
                           'desc': 'A = A - 1'},
                   'DECB': {'HNZVC': '-aaa-',
                           'desc': 'B = B - 1'}},
       'operation': "M' = M - 1",
       'source form': 'DEC Q; DECA; DECB'},
'EOR': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Always cleared.\n'
                         'C - Not affected.'
                         ),
       'description': 'The contents of memory location M is exclusive ORed into an 8-bit register.',
       'instr_desc': 'Exclusive OR memory with accumulator',
       'mnemonic': {'EORA': {'HNZVC': '-aa0-',
                           'desc': 'A = A XOR M'},
                   'EORB': {'HNZVC': '-aa0-',
                           'desc': 'B = M XOR B'}},
       'operation': "R' = R XOR M",
       'source form': 'EORA P; EORB P'},
'EXG': {'condition code': (
                         'Not affected (unless one of the registers is the condition code\n'
                         'register).'
                         ),
       'description': (
                      '0000 = A:B 1000 = A\n'
                      '0001 = X 1001 = B\n'
                      '0010 = Y 1010 = CCR\n'
                      '0011 = US 1011 = DPR\n'
                      '0100 = SP 1100 = Undefined\n'
                      '0101 = PC 1101 = Undefined\n'
                      '0110 = Undefined 1110 = Undefined\n'
                      '0111 = Undefined 1111 = Undefined'
                      ),
       'instr_desc': 'Exchange Rl with R2',
       'mnemonic': {'EXG': {'HNZVC': 'ccccc',
                          'desc': 'exchange R1,R2'}},
       'operation': 'R1 <-> R2',
       'source form': 'EXG R1,R2'},
'INC': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if the original operand was 01111111 2 ; cleared otherwise.\n'
                         'C - Not affected.'
                         ),
       'description': (
                      'Adds to the operand.\n'
                      'The carry bit is not affected, thus allowing this instruction to be used as a loop counter in multiple-precision computations.\n'
                      'When operating on unsigned values, only the BEQ and BNE branches can be expected to behave consistently.\n'
                      'When operating on twos complement values, all signed branches are correctly available.'
                      ),
       'instr_desc': 'Increment accumulator or memory location',
       'mnemonic': {'INC': {'HNZVC': '-aaa-',
                          'desc': 'M = M + 1'},
                   'INCA': {'HNZVC': '-aaa-',
                           'desc': 'A = A + 1'},
                   'INCB': {'HNZVC': '-aaa-',
                           'desc': 'B = B + 1'}},
       'operation': "M' = M + 1",
       'source form': 'INC Q; INCA; INCB'},
'JMP': {'condition code': 'Not affected.',
       'description': 'Program control is transferred to the effective address.',
       'instr_desc': 'Jump',
       'mnemonic': {'JMP': {'HNZVC': '-----',
                          'desc': 'pc = EA'}},
       'operation': "PC' = EA",
       'source form': 'JMP EA'},
'JSR': {'condition code': 'Not affected.',
       'description': (
                      'Program control is transferred to the effective address after storing the return address on the hardware stack.\n'
                      'A RTS instruction should be the last executed instruction of the subroutine.'
                      ),
       'instr_desc': 'Jump to subroutine',
       'mnemonic': {'JSR': {'HNZVC': '-----',
                          'desc': 'jump to subroutine'}},
       'operation': "SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH PC' =EA",
       'source form': 'JSR EA'},
'LD': {'condition code': (
                        'H - Not affected.\n'
                        'N - Set if the loaded data is negative; cleared otherwise.\n'
                        'Z - Set if the loaded data is zero; cleared otherwise.\n'
                        'V - Always cleared.\n'
                        'C - Not affected.'
                        ),
      'description': 'Loads the contents of memory location M into the designated register.',
      'instr_desc': 'Load accumulator from memory',
      'mnemonic': {'LDA': {'HNZVC': '-aa0-',
                         'desc': 'A = M'},
                  'LDB': {'HNZVC': '-aa0-',
                         'desc': 'B = M'},
                  'LDD': {'HNZVC': '-aa0-',
                         'desc': 'D = M:M+1'},
                  'LDS': {'HNZVC': '-aa0-',
                         'desc': 'S = M:M+1'},
                  'LDU': {'HNZVC': '-aa0-',
                         'desc': 'U = M:M+1'},
                  'LDX': {'HNZVC': '-aa0-',
                         'desc': 'X = M:M+1'},
                  'LDY': {'HNZVC': '-aa0-',
                         'desc': 'Y = M:M+1'}},
      'operation': "R' = M",
      'source form': 'LDA P; LDB P'},
'LEA': {'comment': (
                  'Instruction Operation Comment\n'
                  'Instruction\n'
                  '\n'
                  'Operation\n'
                  '\n'
                  'Comment\n'
                  'LEAX 10,X X+10 -> X Adds 5-bit constant 10 to X\n'
                  'LEAX 500,X X+500 -> X Adds 16-bit constant 500 to X\n'
                  'LEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y\n'
                  'LEAY D,Y Y+D -> Y Adds 16-bit D accumulator to Y\n'
                  'LEAU -10,U U-10 -> U Subtracts 10 from U\n'
                  'LEAS -10,S S-10 -> S Used to reserve area on stack\n'
                  "LEAS 10,S S+10 -> S Used to 'clean up' stack\n"
                  'LEAX 5,S S+5 -> X Transfers as well as adds'
                  ),
       'condition code': (
                         'H - Not affected.\n'
                         'N - Not affected.\n'
                         'Z - LEAX, LEAY: Set if the result is zero; cleared otherwise. LEAS, LEAU: Not affected.\n'
                         'V - Not affected.\n'
                         'C - Not affected.'
                         ),
       'description': 'Calculates the effective address from the indexed addressing mode and places the address in an indexable register. LEAX and LEAY affect the Z (zero) bit to allow use of these registers as counters and for MC6800 INX/DEX compatibility. LEAU and LEAS do not affect the Z bit to allow cleaning up the stack while returning the Z bit as a parameter to a calling routine, and also for MC6800 INS/DES compatibility.',
       'instr_desc': 'Load effective address into stack pointer',
       'mnemonic': {'LEAS': {'HNZVC': '-----',
                           'desc': 'S = EA'},
                   'LEAU': {'HNZVC': '-----',
                           'desc': 'U = EA'},
                   'LEAX': {'HNZVC': '--a--',
                           'desc': 'X = EA'},
                   'LEAY': {'HNZVC': '--a--',
                           'desc': 'Y = EA'}},
       'operation': "R' = EA",
       'source form': 'LEAX, LEAY, LEAS, LEAU'},
'LSL': {'comment': 'This is a duplicate assembly-language mnemonic for the single machine instruction ASL.',
       'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\n'
                         'C - Loaded with bit seven of the original operand.'
                         ),
       'description': (
                      'Shifts all bits of accumulator A or B or memory location M one place to the left.\n'
                      'Bit zero is loaded with a zero.\n'
                      'Bit seven of accumulator A or B or memory location M is shifted into the C (carry) bit.'
                      ),
       'instr_desc': 'Logical shift left accumulator or memory location',
       'mnemonic': {'LSL': {'HNZVC': 'naaas',
                          'desc': 'M = Logical shift M left'},
                   'LSLA': {'HNZVC': 'naaas',
                           'desc': 'A = Logical shift A left'},
                   'LSLB': {'HNZVC': 'naaas',
                           'desc': 'B = Logical shift B left'}},
       'operation': (
                    'C = = 0\n'
                    'b7 = b0'
                    ),
       'source form': 'LSL Q; LSLA; LSLB'},
'LSR': {'condition code': (
                         'H - Not affected.\n'
                         'N - Always cleared.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Not affected.\n'
                         'C - Loaded with bit zero of the original operand.'
                         ),
       'description': (
                      'Performs a logical shift right on the operand.\n'
                      'Shifts a zero into bit seven and bit zero into the C (carry) bit.'
                      ),
       'instr_desc': 'Logical shift right accumulator or memory location',
       'mnemonic': {'LSR': {'HNZVC': '-0a-s',
                          'desc': 'M = Logical shift M right'},
                   'LSRA': {'HNZVC': '-0a-s',
                           'desc': 'A = Logical shift A right'},
                   'LSRB': {'HNZVC': '-0a-s',
                           'desc': 'B = Logical shift B right'}},
       'operation': (
                    '0 -> -> C\n'
                    'b7 -> b0'
                    ),
       'source form': 'LSR Q; LSRA; LSRB'},
'MUL': {'comment': 'The C (carry) bit allows rounding the most-significant byte through the sequence: MUL, ADCA #0.',
       'condition code': (
                         'H - Not affected.\n'
                         'N - Not affected.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Not affected.\n'
                         'C - Set if ACCB bit 7 of result is set; cleared otherwise.'
                         ),
       'description': (
                      'Multiply the unsigned binary numbers in the accumulators and place the result in both accumulators (ACCA contains the most-significant byte of the result).\n'
                      'Unsigned multiply allows multiple-precision operations.'
                      ),
       'instr_desc': 'Unsigned multiply (A * B ? D)',
       'mnemonic': {'MUL': {'HNZVC': '--a-a',
                          'desc': 'D = A*B (Unsigned)'}},
       'operation': "ACCA':ACCB' = ACCA * ACCB",
       'source form': 'MUL'},
'NEG': {'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if the original operand was 10000000 2 .\n'
                         'C - Set if a borrow is generated; cleared otherwise.'
                         ),
       'description': (
                      'Replaces the operand with its twos complement.\n'
                      'The C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.\n'
                      'Note that 80 16 is replaced by itself and only in this case is the V (overflow) bit set.\n'
                      'The value 00 16 is also replaced by itself, and only in this case is the C (carry) bit cleared.'
                      ),
       'instr_desc': 'Negate accumulator or memory',
       'mnemonic': {'NEG': {'HNZVC': 'uaaaa',
                          'desc': 'M = !M + 1'},
                   'NEGA': {'HNZVC': 'uaaaa',
                           'desc': 'A = !A + 1'},
                   'NEGB': {'HNZVC': 'uaaaa',
                           'desc': 'B = !B + 1'}},
       'operation': "M' = 0 - M",
       'source form': 'NEG Q; NEGA; NEG B'},
'NOP': {'condition code': (
                         'This instruction causes only the program counter to be incremented.\n'
                         'No other registers or memory locations are affected.'
                         ),
       'description': '',
       'instr_desc': 'No operation',
       'mnemonic': {'NOP': {'HNZVC': '-----',
                          'desc': 'No Operation'}},
       'operation': 'Not affected.',
       'source form': 'NOP'},
'OR': {'condition code': (
                        'H - Not affected.\n'
                        'N - Set if the result is negative; cleared otherwise.\n'
                        'Z - Set if the result is zero; cleared otherwise.\n'
                        'V - Always cleared.\n'
                        'C - Not affected.'
                        ),
      'description': 'Performs an inclusive OR operation between the contents of accumulator A or B and the contents of memory location M and the result is stored in accumulator A or B.',
      'instr_desc': 'OR memory with accumulator',
      'mnemonic': {'ORA': {'HNZVC': '-aa0-',
                         'desc': 'A = A || M'},
                  'ORB': {'HNZVC': '-aa0-',
                         'desc': 'B = B || M'},
                  'ORCC': {'HNZVC': 'ddddd',
                          'desc': 'C = CC || IMM'}},
      'operation': "R' = R OR M",
      'source form': 'ORA P; ORB P'},
'PAGE': {'description': 'Page 1/2 instructions',
        'instr_desc': 'Page 2 Instructions prefix',
        'mnemonic': {'PAGE 1': {'HNZVC': '+++++',
                              'desc': 'Page 1 Instructions prefix'},
                    'PAGE 2': {'HNZVC': '+++++',
                              'desc': 'Page 2 Instructions prefix'}}},
'PSH': {'comment': 'A single register may be placed on the stack with the condition codes set by doing an autodecrement store onto the stack (example: STX ,--S).',
       'condition code': 'Not affected.',
       'description': 'All, some, or none of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself).',
       'instr_desc': 'Push A, B, CC, DP, D, X, Y, U, or PC onto hardware stack',
       'mnemonic': {'PSHS': {'HNZVC': '-----',
                           'desc': 'S -= 1: MEM(S) = R; Push Register on S Stack'},
                   'PSHU': {'HNZVC': '-----',
                           'desc': 'U -= 1: MEM(U) = R; Push Register on U Stack'}},
       'operation': 'Push Registers on S Stack: S -= 1: MEM(S) = Reg.',
       'source form': (
                      'b7 b6 b5 b4 b3 b2 b1 b0\n'
                      'PC U Y X DP B A CC\n'
                      'push order ->'
                      )},
'PUL': {'comment': 'A single register may be pulled from the stack with condition codes set by doing an autoincrement load from the stack (example: LDX ,S++).',
       'condition code': 'May be pulled from stack; not affected otherwise.',
       'description': 'All, some, or none of the processor registers are pulled from the hardware stack (with the exception of the hardware stack pointer itself).',
       'instr_desc': 'Pull A, B, CC, DP, D, X, Y, U, or PC from hardware stack',
       'mnemonic': {'PULS': {'HNZVC': 'ccccc',
                           'desc': 'R=MEM(S) : S += 1; Pull register from S Stack'},
                   'PULU': {'HNZVC': 'ccccc',
                           'desc': 'R=MEM(U) : U += 1; Pull register from U Stack'}},
       'operation': 'Pull Registers from S Stack: Reg. = MEM(S): S += 1',
       'source form': (
                      'b7 b6 b5 b4 b3 b2 b1 b0\n'
                      'PC U Y X DP B A CC\n'
                      '= pull order'
                      )},
'RESET': {'description': 'Build the ASSIST09 vector table and setup monitor defaults, then invoke the monitor startup routine.',
         'instr_desc': '',
         'mnemonic': {'RESET': {'HNZVC': '*****',
                              'desc': 'Undocumented opcode'}}},
'ROL': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Loaded with the result of the exclusive OR of bits six and seven of the original operand.\n'
                         'C - Loaded with bit seven of the original operand.'
                         ),
       'description': (
                      'Rotates all bits of the operand one place left through the C (carry) bit.\n'
                      'This is a 9-bit rotation.'
                      ),
       'instr_desc': 'Rotate accumulator or memory left',
       'mnemonic': {'ROL': {'HNZVC': '-aaas',
                          'desc': 'M = Rotate M left thru carry'},
                   'ROLA': {'HNZVC': '-aaas',
                           'desc': 'A = Rotate A left thru carry'},
                   'ROLB': {'HNZVC': '-aaas',
                           'desc': 'B = Rotate B left thru carry'}},
       'operation': (
                    'C = = C\n'
                    'b7 = b0'
                    ),
       'source form': 'ROL Q; ROLA; ROLB'},
'ROR': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Not affected.\n'
                         'C - Loaded with bit zero of the previous operand.'
                         ),
       'description': (
                      'Rotates all bits of the operand one place right through the C (carry) bit.\n'
                      'This is a 9-bit rotation.'
                      ),
       'instr_desc': 'Rotate accumulator or memory right',
       'mnemonic': {'ROR': {'HNZVC': '-aa-s',
                          'desc': 'M = Rotate M Right thru carry'},
                   'RORA': {'HNZVC': '-aa-s',
                           'desc': 'A = Rotate A Right thru carry'},
                   'RORB': {'HNZVC': '-aa-s',
                           'desc': 'B = Rotate B Right thru carry'}},
       'operation': (
                    'C -> -> C\n'
                    'b7 -> b0'
                    ),
       'source form': 'ROR Q; RORA; RORB'},
'RTI': {'condition code': 'Recovered from the stack.',
       'description': (
                      'The saved machine state is recovered from the hardware stack and control is returned to the interrupted program.\n'
                      'If the recovered E (entire) bit is clear, it indicates that only a subset of the machine state was saved (return address and condition codes) and only that subset is recovered.'
                      ),
       'instr_desc': 'Return from interrupt',
       'mnemonic': {'RTI': {'HNZVC': '-----',
                          'desc': 'Return from Interrupt'}},
       'operation': (
                    "IFF CCR bit E is set, then: ACCA' ACCB' DPR' IXH' IXL' IYH' IYL' USH' USL' PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1 = (SP), SP' = SP+1\n"
                    "IFF CCR bit E is clear, then: PCH' PCL' = (SP), SP' = SP+1 = (SP), SP' = SP+1"
                    ),
       'source form': 'RTI'},
'RTS': {'condition code': 'Not affected.',
       'description': (
                      'Program control is returned from the subroutine to the calling program.\n'
                      'The return address is pulled from the stack.'
                      ),
       'instr_desc': 'Return from subroutine',
       'mnemonic': {'RTS': {'HNZVC': '-----',
                          'desc': 'Return from subroutine'}},
       'operation': "PCH' = (SP), SP' = SP+1 PCL' = (SP), SP' = SP+1",
       'source form': 'RTS'},
'SBC': {'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if an overflow is generated; cleared otherwise.\n'
                         'C - Set if a borrow is generated; cleared otherwise.'
                         ),
       'description': (
                      'Subtracts the contents of memory location M and the borrow (in the C (carry) bit) from the contents of the designated 8-bit register, and places the result in that register.\n'
                      'The C bit represents a borrow and is set to the inverse of the resulting binary carry.'
                      ),
       'instr_desc': 'Subtract memory from accumulator with borrow',
       'mnemonic': {'SBCA': {'HNZVC': 'uaaaa',
                           'desc': 'A = A - M - C'},
                   'SBCB': {'HNZVC': 'uaaaa',
                           'desc': 'B = B - M - C'}},
       'operation': "R' = R - M - C",
       'source form': 'SBCA P; SBCB P'},
'SEX': {'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Not affected.\n'
                         'C - Not affected.'
                         ),
       'description': 'This instruction transforms a twos complement 8-bit value in accumulator B into a twos complement 16-bit value in the D accumulator.',
       'instr_desc': 'Sign Extend B accumulator into A accumulator',
       'mnemonic': {'SEX': {'HNZVC': '-aa0-',
                          'desc': 'Sign extend B into A'}},
       'operation': "If bit seven of ACCB is set then ACCA' = FF 16 else ACCA' = 00 16",
       'source form': 'SEX'},
'ST': {'condition code': (
                        'H - Not affected.\n'
                        'N - Set if the result is negative; cleared otherwise.\n'
                        'Z - Set if the result is zero; cleared otherwise.\n'
                        'V - Always cleared.\n'
                        'C - Not affected.'
                        ),
      'description': 'Writes the contents of an 8-bit register into a memory location.',
      'instr_desc': 'Store accumulator to memroy',
      'mnemonic': {'STA': {'HNZVC': '-aa0-',
                         'desc': 'M = A'},
                  'STB': {'HNZVC': '-aa0-',
                         'desc': 'M = B'},
                  'STD': {'HNZVC': '-aa0-',
                         'desc': 'M:M+1 = D'},
                  'STS': {'HNZVC': '-aa0-',
                         'desc': 'M:M+1 = S'},
                  'STU': {'HNZVC': '-aa0-',
                         'desc': 'M:M+1 = U'},
                  'STX': {'HNZVC': '-aa0-',
                         'desc': 'M:M+1 = X'},
                  'STY': {'HNZVC': '-aa0-',
                         'desc': 'M:M+1 = Y'}},
      'operation': "M' = R",
      'source form': 'STA P; STB P'},
'SUB': {'condition code': (
                         'H - Undefined.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Set if the overflow is generated; cleared otherwise.\n'
                         'C - Set if a borrow is generated; cleared otherwise.'
                         ),
       'description': (
                      'Subtracts the value in memory location M from the contents of a designated 8-bit register.\n'
                      'The C (carry) bit represents a borrow and is set to the inverse of the resulting binary carry.'
                      ),
       'instr_desc': 'Subtract memory from accumulator',
       'mnemonic': {'SUBA': {'HNZVC': 'uaaaa',
                           'desc': 'A = A - M'},
                   'SUBB': {'HNZVC': 'uaaaa',
                           'desc': 'B = B - M'},
                   'SUBD': {'HNZVC': '-aaaa',
                           'desc': 'D = D - M:M+1'}},
       'operation': "R' = R - M",
       'source form': 'SUBA P; SUBB P'},
'SWI': {'condition code': 'Not affected.',
       'description': (
                      'All of the processor registers are pushed onto the hardware stack (with the exception of the hardware stack pointer itself), and control is transferred through the software interrupt vector.\n'
                      'Both the normal and fast interrupts are masked (disabled).'
                      ),
       'instr_desc': 'Software interrupt (absolute indirect)',
       'mnemonic': {'SWI': {'HNZVC': '-----',
                          'desc': 'Software interrupt 1'},
                   'SWI2': {'HNZVC': '-----',
                           'desc': 'Software interrupt 2'},
                   'SWI3': {'HNZVC': '-----',
                           'desc': 'Software interrupt 3'}},
       'operation': "Set E (entire state will be saved) SP' = SP-1, (SP) = PCL SP' = SP-1, (SP) = PCH SP' = SP-1, (SP) = USL SP' = SP-1, (SP) = USH SP' = SP-1, (SP) = IYL SP' = SP-1, (SP) = IYH SP' = SP-1, (SP) = IXL SP' = SP-1, (SP) = IXH SP' = SP-1, (SP) = DPR SP' = SP-1, (SP) = ACCB SP' = SP-1, (SP) = ACCA SP' = SP-1, (SP) = CCR Set I, F (mask interrupts) PC' = (FFFA):(FFFB)",
       'source form': 'SWI'},
'SYNC': {'condition code': 'Not affected.',
        'description': (
                       'FAST SYNC WAIT FOR DATA\n'
                       'Interrupt!\n'
                       'LDA DISC DATA FROM DISC AND CLEAR INTERRUPT\n'
                       'STA ,X+ PUT IN BUFFER\n'
                       'DECB COUNT IT, DONE?\n'
                       'BNE FAST GO AGAIN IF NOT.'
                       ),
        'instr_desc': 'Synchronize with interrupt line',
        'mnemonic': {'SYNC': {'HNZVC': '-----',
                            'desc': 'Synchronize to Interrupt'}},
        'operation': 'Stop processing instructions',
        'source form': 'SYNC'},
'TFR': {'condition code': 'Not affected unless R2 is the condition code register.',
       'description': (
                      '0000 = A:B 1000 = A\n'
                      '0001 = X 1001 = B\n'
                      '0010 = Y 1010 = CCR\n'
                      '0011 = US 1011 = DPR\n'
                      '0100 = SP 1100 = Undefined\n'
                      '0101 = PC 1101 = Undefined\n'
                      '0110 = Undefined 1110 = Undefined\n'
                      '0111 = Undefined 1111 = Undefined'
                      ),
       'instr_desc': 'Transfer R1 to R2',
       'mnemonic': {'TFR': {'HNZVC': 'ccccc',
                          'desc': None}},
       'operation': 'R1 -> R2',
       'source form': 'TFR R1, R2'},
'TST': {'comment': 'The MC6800 processor clears the C (carry) bit.',
       'condition code': (
                         'H - Not affected.\n'
                         'N - Set if the result is negative; cleared otherwise.\n'
                         'Z - Set if the result is zero; cleared otherwise.\n'
                         'V - Always cleared.\n'
                         'C - Not affected.'
                         ),
       'description': (
                      'Set the N (negative) and Z (zero) bits according to the contents of memory location M, and clear the V (overflow) bit.\n'
                      'The TST instruction provides only minimum information when testing unsigned values; since no unsigned value is less than zero, BLO and BLS have no utility.\n'
                      'While BHI could be used after TST, it provides exactly the same control as BNE, which is preferred.\n'
                      'The signed branches are available.'
                      ),
       'instr_desc': 'Test accumulator or memory location',
       'mnemonic': {'TST': {'HNZVC': '-aa0-',
                          'desc': 'Test M'},
                   'TSTA': {'HNZVC': '-aa0-',
                           'desc': 'Test A'},
                   'TSTB': {'HNZVC': '-aa0-',
                           'desc': 'Test B'}},
       'operation': 'TEMP = M - 0',
       'source form': 'TST Q; TSTA; TSTB'}}
