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

def opcode(): raise NotImplementedError

class CPU6809Skeleton(object):
    @opcode( # Add B accumulator to X (unsigned)
        0x3a, # ABX (inherent)
    )
    def instruction_ABX(self, opcode):
        """
        Add the 8-bit unsigned value in accumulator B into index register X.

        source code forms: ABX

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x ABX" % opcode)

    @opcode( # Add memory to accumulator with carry
        0x89, 0x99, 0xa9, 0xb9, # ADCA (immediate, direct, indexed, extended)
        0xc9, 0xd9, 0xe9, 0xf9, # ADCB (immediate, direct, indexed, extended)
    )
    def instruction_ADC(self, opcode, ea=None, operand=None):
        """
        Adds the contents of the C (carry) bit and the memory byte into an 8-bit
        accumulator.

        source code forms: ADCA P; ADCB P

        CC bits "HNZVC": aaaaa
        """
        raise NotImplementedError("TODO: $%x ADC" % opcode)
        self.cc.update_HNZVC(a, b, r)

    @opcode( # Add memory to D accumulator
        0xc3, 0xd3, 0xe3, 0xf3, # ADDD (immediate, direct, indexed, extended)
    )
    def instruction_ADD16(self, opcode, ea=None, operand=None):
        """
        Adds the 16-bit memory value into the 16-bit accumulator

        source code forms: ADDD P

        CC bits "HNZVC": -aaaa
        """
        raise NotImplementedError("TODO: $%x ADD16" % opcode)
        self.cc.update_NZVC_16(a, b, r)

    @opcode( # Add memory to accumulator
        0x8b, 0x9b, 0xab, 0xbb, # ADDA (immediate, direct, indexed, extended)
        0xcb, 0xdb, 0xeb, 0xfb, # ADDB (immediate, direct, indexed, extended)
    )
    def instruction_ADD8(self, opcode, ea=None, operand=None):
        """
        Adds the memory byte into an 8-bit accumulator.

        source code forms: ADDA P; ADDB P

        CC bits "HNZVC": aaaaa
        """
        raise NotImplementedError("TODO: $%x ADD8" % opcode)
        self.cc.update_HNZVC(a, b, r)

    @opcode( # AND memory with accumulator
        0x84, 0x94, 0xa4, 0xb4, # ANDA (immediate, direct, indexed, extended)
        0xc4, 0xd4, 0xe4, 0xf4, # ANDB (immediate, direct, indexed, extended)
    )
    def instruction_AND(self, opcode, ea=None, operand=None):
        """
        Performs the logical AND operation between the contents of an
        accumulator and the contents of memory location M and the result is
        stored in the accumulator.

        source code forms: ANDA P; ANDB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x AND" % opcode)
        self.cc.update_NZ0()

    @opcode( # AND condition code register
        0x1c, # ANDCC (immediate)
    )
    def instruction_ANDCC(self, opcode, ea=None, operand=None):
        """
        Performs a logical AND between the condition code register and the
        immediate byte specified in the instruction and places the result in the
        condition code register.

        source code forms: ANDCC #xx

        CC bits "HNZVC": ddddd
        """
        raise NotImplementedError("TODO: $%x ANDCC" % opcode)
        # Update CC bits: ddddd

    @opcode( # Arithmetic shift of accumulator or memory right
        0x7, 0x67, 0x77, # ASR (direct, indexed, extended)
        0x47, # ASRA (inherent)
        0x57, # ASRB (inherent)
    )
    def instruction_ASR(self, opcode, ea=None, operand=None):
        """
        Shifts all bits of the operand one place to the right. Bit seven is held
        constant. Bit zero is shifted into the C (carry) bit.

        source code forms: ASR Q; ASRA; ASRB

        CC bits "HNZVC": uaa-s
        """
        raise NotImplementedError("TODO: $%x ASR" % opcode)
        self.cc.update_NZC()

    @opcode( # Branch if equal
        0x27, # BEQ (relative)
        0x1027, # LBEQ (relative)
    )
    def instruction_BEQ(self, opcode, ea=None):
        """
        Tests the state of the Z (zero) bit and causes a branch if it is set.
        When used after a subtract or compare operation, this instruction will
        branch if the compared values, signed or unsigned, were exactly the
        same.

        source code forms: BEQ dd; LBEQ DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BEQ" % opcode)

    @opcode( # Branch if greater than or equal (signed)
        0x2c, # BGE (relative)
        0x102c, # LBGE (relative)
    )
    def instruction_BGE(self, opcode, ea=None):
        """
        Causes a branch if the N (negative) bit and the V (overflow) bit are
        either both set or both clear. That is, branch if the sign of a valid
        twos complement result is, or would be, positive. When used after a
        subtract or compare operation on twos complement values, this
        instruction will branch if the register was greater than or equal to the
        memory operand.

        source code forms: BGE dd; LBGE DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BGE" % opcode)

    @opcode( # Branch if greater (signed)
        0x2e, # BGT (relative)
        0x102e, # LBGT (relative)
    )
    def instruction_BGT(self, opcode, ea=None):
        """
        Causes a branch if the N (negative) bit and V (overflow) bit are either
        both set or both clear and the Z (zero) bit is clear. In other words,
        branch if the sign of a valid twos complement result is, or would be,
        positive and not zero. When used after a subtract or compare operation
        on twos complement values, this instruction will branch if the register
        was greater than the memory operand.

        source code forms: BGT dd; LBGT DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BGT" % opcode)

    @opcode( # Branch if higher (unsigned)
        0x22, # BHI (relative)
        0x1022, # LBHI (relative)
    )
    def instruction_BHI(self, opcode, ea=None):
        """
        Causes a branch if the previous operation caused neither a carry nor a
        zero result. When used after a subtract or compare operation on unsigned
        binary values, this instruction will branch if the register was higher
        than the memory operand.

        Generally not useful after INC/DEC, LD/TST, and TST/CLR/COM
        instructions.

        source code forms: BHI dd; LBHI DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BHI" % opcode)

    @opcode( # Bit test memory with accumulator
        0x85, 0x95, 0xa5, 0xb5, # BITA (immediate, direct, indexed, extended)
        0xc5, 0xd5, 0xe5, 0xf5, # BITB (immediate, direct, indexed, extended)
    )
    def instruction_BIT(self, opcode, ea=None, operand=None):
        """
        Performs the logical AND of the contents of accumulator A or B and the
        contents of memory location M and modifies the condition codes
        accordingly. The contents of accumulator A or B and memory location M
        are not affected.

        source code forms: BITA P; BITB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x BIT" % opcode)
        self.cc.update_NZ0()

    @opcode( # Branch if less than or equal (signed)
        0x2f, # BLE (relative)
        0x102f, # LBLE (relative)
    )
    def instruction_BLE(self, opcode, ea=None):
        """
        Causes a branch if the exclusive OR of the N (negative) and V (overflow)
        bits is 1 or if the Z (zero) bit is set. That is, branch if the sign of
        a valid twos complement result is, or would be, negative. When used
        after a subtract or compare operation on twos complement values, this
        instruction will branch if the register was less than or equal to the
        memory operand.

        source code forms: BLE dd; LBLE DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BLE" % opcode)

    @opcode( # Branch if lower or same (unsigned)
        0x23, # BLS (relative)
        0x1023, # LBLS (relative)
    )
    def instruction_BLS(self, opcode, ea=None):
        """
        Causes a branch if the previous operation caused either a carry or a
        zero result. When used after a subtract or compare operation on unsigned
        binary values, this instruction will branch if the register was lower
        than or the same as the memory operand.

        Generally not useful after INC/DEC, LD/ST, and TST/CLR/COM instructions.

        source code forms: BLS dd; LBLS DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BLS" % opcode)

    @opcode( # Branch if less than (signed)
        0x2d, # BLT (relative)
        0x102d, # LBLT (relative)
    )
    def instruction_BLT(self, opcode, ea=None):
        """
        Causes a branch if either, but not both, of the N (negative) or V
        (overflow) bits is set. That is, branch if the sign of a valid twos
        complement result is, or would be, negative. When used after a subtract
        or compare operation on twos complement binary values, this instruction
        will branch if the register was less than the memory operand.

        source code forms: BLT dd; LBLT DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BLT" % opcode)

    @opcode( # Branch if minus
        0x2b, # BMI (relative)
        0x102b, # LBMI (relative)
    )
    def instruction_BMI(self, opcode, ea=None):
        """
        Tests the state of the N (negative) bit and causes a branch if set. That
        is, branch if the sign of the twos complement result is negative.

        When used after an operation on signed binary values, this instruction
        will branch if the result is minus. It is generally preferred to use the
        LBLT instruction after signed operations.

        source code forms: BMI dd; LBMI DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BMI" % opcode)

    @opcode( # Branch if not equal
        0x26, # BNE (relative)
        0x1026, # LBNE (relative)
    )
    def instruction_BNE(self, opcode, ea=None):
        """
        Tests the state of the Z (zero) bit and causes a branch if it is clear.
        When used after a subtract or compare operation on any binary values,
        this instruction will branch if the register is, or would be, not equal
        to the memory operand.

        source code forms: BNE dd; LBNE DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BNE" % opcode)

    @opcode( # Branch if plus
        0x2a, # BPL (relative)
        0x102a, # LBPL (relative)
    )
    def instruction_BPL(self, opcode, ea=None):
        """
        Tests the state of the N (negative) bit and causes a branch if it is
        clear. That is, branch if the sign of the twos complement result is
        positive.

        When used after an operation on signed binary values, this instruction
        will branch if the result (possibly invalid) is positive. It is
        generally preferred to use the BGE instruction after signed operations.

        source code forms: BPL dd; LBPL DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BPL" % opcode)

    @opcode( # Branch always
        0x20, # BRA (relative)
        0x16, # LBRA (relative)
    )
    def instruction_BRA(self, opcode, ea=None):
        """
        Causes an unconditional branch.

        source code forms: BRA dd; LBRA DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BRA" % opcode)

    @opcode( # Branch never
        0x21, # BRN (relative)
        0x1021, # LBRN (relative)
    )
    def instruction_BRN(self, opcode, ea=None):
        """
        Does not cause a branch. This instruction is essentially a no operation,
        but has a bit pattern logically related to branch always.

        source code forms: BRN dd; LBRN DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BRN" % opcode)

    @opcode( # Branch to subroutine
        0x8d, # BSR (relative)
        0x17, # LBSR (relative)
    )
    def instruction_BSR(self, opcode, ea=None):
        """
        The program counter is pushed onto the stack. The program counter is
        then loaded with the sum of the program counter and the offset.

        A return from subroutine (RTS) instruction is used to reverse this
        process and must be the last instruction executed in a subroutine.

        source code forms: BSR dd; LBSR DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BSR" % opcode)

    @opcode( # Branch if valid twos complement result
        0x28, # BVC (relative)
        0x1028, # LBVC (relative)
    )
    def instruction_BVC(self, opcode, ea=None):
        """
        Tests the state of the V (overflow) bit and causes a branch if it is
        clear. That is, branch if the twos complement result was valid. When
        used after an operation on twos complement binary values, this
        instruction will branch if there was no overflow.

        source code forms: BVC dd; LBVC DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BVC" % opcode)

    @opcode( # Branch if invalid twos complement result
        0x29, # BVS (relative)
        0x1029, # LBVS (relative)
    )
    def instruction_BVS(self, opcode, ea=None):
        """
        Tests the state of the V (overflow) bit and causes a branch if it is
        set. That is, branch if the twos complement result was invalid. When
        used after an operation on twos complement binary values, this
        instruction will branch if there was an overflow.

        source code forms: BVS dd; LBVS DDDD

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x BVS" % opcode)

    @opcode( # Clear accumulator or memory location
        0xf, 0x6f, 0x7f, # CLR (direct, indexed, extended)
        0x4f, # CLRA (inherent)
        0x5f, # CLRB (inherent)
    )
    def instruction_CLR(self, opcode, ea=None, operand=None):
        """
        Accumulator A or B or memory location M is loaded with 00000000 2 . Note
        that the EA is read during this operation.

        source code forms: CLR Q

        CC bits "HNZVC": -0100
        """
        raise NotImplementedError("TODO: $%x CLR" % opcode)
        self.cc.update_0100()

    @opcode( # Compare memory from stack pointer
        0x1083, 0x1093, 0x10a3, 0x10b3, # CMPD (immediate, direct, indexed, extended)
        0x118c, 0x119c, 0x11ac, 0x11bc, # CMPS (immediate, direct, indexed, extended)
        0x1183, 0x1193, 0x11a3, 0x11b3, # CMPU (immediate, direct, indexed, extended)
        0x8c, 0x9c, 0xac, 0xbc, # CMPX (immediate, direct, indexed, extended)
        0x108c, 0x109c, 0x10ac, 0x10bc, # CMPY (immediate, direct, indexed, extended)
    )
    def instruction_CMP16(self, opcode, ea=None, operand=None):
        """
        Compares the 16-bit contents of the concatenated memory locations M:M+1
        to the contents of the specified register and sets the appropriate
        condition codes. Neither the memory locations nor the specified register
        is modified unless autoincrement or autodecrement are used. The carry
        flag represents a borrow and is set to the inverse of the resulting
        binary carry.

        source code forms: CMPD P; CMPX P; CMPY P; CMPU P; CMPS P

        CC bits "HNZVC": -aaaa
        """
        raise NotImplementedError("TODO: $%x CMP16" % opcode)
        self.cc.update_NZVC_16(a, b, r)

    @opcode( # Compare memory from accumulator
        0x81, 0x91, 0xa1, 0xb1, # CMPA (immediate, direct, indexed, extended)
        0xc1, 0xd1, 0xe1, 0xf1, # CMPB (immediate, direct, indexed, extended)
    )
    def instruction_CMP8(self, opcode, ea=None, operand=None):
        """
        Compares the contents of memory location to the contents of the
        specified register and sets the appropriate condition codes. Neither
        memory location M nor the specified register is modified. The carry flag
        represents a borrow and is set to the inverse of the resulting binary
        carry.

        source code forms: CMPA P; CMPB P

        CC bits "HNZVC": uaaaa
        """
        raise NotImplementedError("TODO: $%x CMP8" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # Complement accumulator or memory location
        0x3, 0x63, 0x73, # COM (direct, indexed, extended)
        0x43, # COMA (inherent)
        0x53, # COMB (inherent)
    )
    def instruction_COM(self, opcode, ea=None, operand=None):
        """
        Replaces the contents of memory location M or accumulator A or B with
        its logical complement. When operating on unsigned values, only BEQ and
        BNE branches can be expected to behave properly following a COM
        instruction. When operating on twos complement values, all signed
        branches are available.

        source code forms: COM Q; COMA; COMB

        CC bits "HNZVC": -aa01
        """
        raise NotImplementedError("TODO: $%x COM" % opcode)
        self.cc.update_NZ01()

    @opcode( # AND condition code register, then wait for interrupt
        0x3c, # CWAI (immediate)
    )
    def instruction_CWAI(self, opcode, ea=None):
        """
        This instruction ANDs an immediate byte with the condition code register
        which may clear the interrupt mask bits I and F, stacks the entire
        machine state on the hardware stack and then looks for an interrupt.
        When a non-masked interrupt occurs, no further machine state information
        need be saved before vectoring to the interrupt handling routine. This
        instruction replaced the MC6800 CLI WAI sequence, but does not place the
        buses in a high-impedance state. A FIRQ (fast interrupt request) may
        enter its interrupt handler with its entire machine state saved. The RTI
        (return from interrupt) instruction will automatically return the entire
        machine state after testing the E (entire) bit of the recovered
        condition code register.

        The following immediate values will have the following results: FF =
        enable neither EF = enable IRQ BF = enable FIRQ AF = enable both

        source code forms: CWAI #$XX E F H I N Z V C

        CC bits "HNZVC": ddddd
        """
        raise NotImplementedError("TODO: $%x CWAI" % opcode)
        # Update CC bits: ddddd

    @opcode( # Decimal adjust A accumulator
        0x19, # DAA (inherent)
    )
    def instruction_DAA(self, opcode):
        """
        The sequence of a single-byte add instruction on accumulator A (either
        ADDA or ADCA) and a following decimal addition adjust instruction
        results in a BCD addition with an appropriate carry bit. Both values to
        be added must be in proper BCD form (each nibble such that: 0 <= nibble
        <= 9). Multiple-precision addition must add the carry generated by this
        decimal addition adjust into the next higher digit during the add
        operation (ADCA) immediately prior to the next decimal addition adjust.

        source code forms: DAA

        CC bits "HNZVC": -aa0a
        """
        raise NotImplementedError("TODO: $%x DAA" % opcode)
        # Update CC bits: -aa0a

    @opcode( # Decrement accumulator or memory location
        0xa, 0x6a, 0x7a, # DEC (direct, indexed, extended)
        0x4a, # DECA (inherent)
        0x5a, # DECB (inherent)
    )
    def instruction_DEC(self, opcode, ea=None, operand=None):
        """
        Subtract one from the operand. The carry bit is not affected, thus
        allowing this instruction to be used as a loop counter in multiple-
        precision computations. When operating on unsigned values, only BEQ and
        BNE branches can be expected to behave consistently. When operating on
        twos complement values, all signed branches are available.

        source code forms: DEC Q; DECA; DECB

        CC bits "HNZVC": -aaa-
        """
        raise NotImplementedError("TODO: $%x DEC" % opcode)
        self.cc.update_NZV(a, b, r)

    @opcode( # Exclusive OR memory with accumulator
        0x88, 0x98, 0xa8, 0xb8, # EORA (immediate, direct, indexed, extended)
        0xc8, 0xd8, 0xe8, 0xf8, # EORB (immediate, direct, indexed, extended)
    )
    def instruction_EOR(self, opcode, ea=None, operand=None):
        """
        The contents of memory location M is exclusive ORed into an 8-bit
        register.

        source code forms: EORA P; EORB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x EOR" % opcode)
        self.cc.update_NZ0()

    @opcode( # Exchange Rl with R2
        0x1e, # EXG (immediate)
    )
    def instruction_EXG(self, opcode, ea=None):
        """
        0000 = A:B 1000 = A 0001 = X 1001 = B 0010 = Y 1010 = CCR 0011 = US 1011
        = DPR 0100 = SP 1100 = Undefined 0101 = PC 1101 = Undefined 0110 =
        Undefined 1110 = Undefined 0111 = Undefined 1111 = Undefined

        source code forms: EXG R1,R2

        CC bits "HNZVC": ccccc
        """
        raise NotImplementedError("TODO: $%x EXG" % opcode)
        # Update CC bits: ccccc

    @opcode( # Increment accumulator or memory location
        0xc, 0x6c, 0x7c, # INC (direct, indexed, extended)
        0x4c, # INCA (inherent)
        0x5c, # INCB (inherent)
    )
    def instruction_INC(self, opcode, ea=None, operand=None):
        """
        Adds to the operand. The carry bit is not affected, thus allowing this
        instruction to be used as a loop counter in multiple-precision
        computations. When operating on unsigned values, only the BEQ and BNE
        branches can be expected to behave consistently. When operating on twos
        complement values, all signed branches are correctly available.

        source code forms: INC Q; INCA; INCB

        CC bits "HNZVC": -aaa-
        """
        raise NotImplementedError("TODO: $%x INC" % opcode)
        self.cc.update_NZV(a, b, r)

    @opcode( # Jump
        0xe, 0x6e, 0x7e, # JMP (direct, indexed, extended)
    )
    def instruction_JMP(self, opcode, ea=None):
        """
        Program control is transferred to the effective address.

        source code forms: JMP EA

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x JMP" % opcode)

    @opcode( # Jump to subroutine
        0x9d, 0xad, 0xbd, # JSR (direct, indexed, extended)
    )
    def instruction_JSR(self, opcode, ea=None):
        """
        Program control is transferred to the effective address after storing
        the return address on the hardware stack. A RTS instruction should be
        the last executed instruction of the subroutine.

        source code forms: JSR EA

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x JSR" % opcode)

    @opcode( # Load stack pointer from memory
        0xcc, 0xdc, 0xec, 0xfc, # LDD (immediate, direct, indexed, extended)
        0x10ce, 0x10de, 0x10ee, 0x10fe, # LDS (immediate, direct, indexed, extended)
        0xce, 0xde, 0xee, 0xfe, # LDU (immediate, direct, indexed, extended)
        0x8e, 0x9e, 0xae, 0xbe, # LDX (immediate, direct, indexed, extended)
        0x108e, 0x109e, 0x10ae, 0x10be, # LDY (immediate, direct, indexed, extended)
    )
    def instruction_LD16(self, opcode, ea=None, operand=None):
        """
        Load the contents of the memory location M:M+1 into the designated
        16-bit register.

        source code forms: LDD P; LDX P; LDY P; LDS P; LDU P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x LD16" % opcode)
        self.cc.update_NZ0_16()

    @opcode( # Load accumulator from memory
        0x86, 0x96, 0xa6, 0xb6, # LDA (immediate, direct, indexed, extended)
        0xc6, 0xd6, 0xe6, 0xf6, # LDB (immediate, direct, indexed, extended)
    )
    def instruction_LD8(self, opcode, ea=None, operand=None):
        """
        Loads the contents of memory location M into the designated register.

        source code forms: LDA P; LDB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x LD8" % opcode)
        self.cc.update_NZ0()

    @opcode( # Load effective address into stack pointer
        0x32, # LEAS (indexed)
        0x33, # LEAU (indexed)
    )
    def instruction_LEA_pointer(self, opcode, ea=None, operand=None):
        """
        Calculates the effective address from the indexed addressing mode and
        places the address in an indexable register. LEAX and LEAY affect the Z
        (zero) bit to allow use of these registers as counters and for MC6800
        INX/DEX compatibility. LEAU and LEAS do not affect the Z bit to allow
        cleaning up the stack while returning the Z bit as a parameter to a
        calling routine, and also for MC6800 INS/DES compatibility.

        Instruction Operation Comment Instruction  Operation  Comment LEAX 10,X
        X+10 -> X Adds 5-bit constant 10 to X LEAX 500,X X+500 -> X Adds 16-bit
        constant 500 to X LEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y LEAY D,Y
        Y+D -> Y Adds 16-bit D accumulator to Y LEAU -10,U U-10 -> U Subtracts
        10 from U LEAS -10,S S-10 -> S Used to reserve area on stack LEAS 10,S
        S+10 -> S Used to 'clean up' stack LEAX 5,S S+5 -> X Transfers as well
        as adds

        source code forms: LEAX, LEAY, LEAS, LEAU

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x LEA_pointer" % opcode)

    @opcode( # Load effective address into stack pointer
        0x30, # LEAX (indexed)
        0x31, # LEAY (indexed)
    )
    def instruction_LEA_register(self, opcode, ea=None, operand=None):
        """
        Calculates the effective address from the indexed addressing mode and
        places the address in an indexable register. LEAX and LEAY affect the Z
        (zero) bit to allow use of these registers as counters and for MC6800
        INX/DEX compatibility. LEAU and LEAS do not affect the Z bit to allow
        cleaning up the stack while returning the Z bit as a parameter to a
        calling routine, and also for MC6800 INS/DES compatibility.

        Instruction Operation Comment Instruction  Operation  Comment LEAX 10,X
        X+10 -> X Adds 5-bit constant 10 to X LEAX 500,X X+500 -> X Adds 16-bit
        constant 500 to X LEAY A,Y Y+A -> Y Adds 8-bit accumulator to Y LEAY D,Y
        Y+D -> Y Adds 16-bit D accumulator to Y LEAU -10,U U-10 -> U Subtracts
        10 from U LEAS -10,S S-10 -> S Used to reserve area on stack LEAS 10,S
        S+10 -> S Used to 'clean up' stack LEAX 5,S S+5 -> X Transfers as well
        as adds

        source code forms: LEAX, LEAY, LEAS, LEAU

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x LEA_register" % opcode)

    @opcode( # Logical shift left accumulator or memory location / Arithmetic shift of accumulator or memory left
        0x8, 0x68, 0x78, # LSL/ASL (direct, indexed, extended)
        0x48, # LSLA/ASLA (inherent)
        0x58, # LSLB/ASLB (inherent)
    )
    def instruction_LSL(self, opcode, ea=None, operand=None):
        """
        Shifts all bits of accumulator A or B or memory location M one place to
        the left. Bit zero is loaded with a zero. Bit seven of accumulator A or
        B or memory location M is shifted into the C (carry) bit.

        This is a duplicate assembly-language mnemonic for the single machine
        instruction ASL.

        source code forms: LSL Q; LSLA; LSLB

        CC bits "HNZVC": naaas
        """
        raise NotImplementedError("TODO: $%x LSL" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # Logical shift right accumulator or memory location
        0x4, 0x64, 0x74, # LSR (direct, indexed, extended)
        0x44, # LSRA (inherent)
        0x54, # LSRB (inherent)
    )
    def instruction_LSR(self, opcode, ea=None, operand=None):
        """
        Performs a logical shift right on the operand. Shifts a zero into bit
        seven and bit zero into the C (carry) bit.

        source code forms: LSR Q; LSRA; LSRB

        CC bits "HNZVC": -0a-s
        """
        raise NotImplementedError("TODO: $%x LSR" % opcode)
        self.cc.update_0ZC()

    @opcode( # Unsigned multiply (A * B ? D)
        0x3d, # MUL (inherent)
    )
    def instruction_MUL(self, opcode):
        """
        Multiply the unsigned binary numbers in the accumulators and place the
        result in both accumulators (ACCA contains the most-significant byte of
        the result). Unsigned multiply allows multiple-precision operations.

        The C (carry) bit allows rounding the most-significant byte through the
        sequence: MUL, ADCA #0.

        source code forms: MUL

        CC bits "HNZVC": --a-a
        """
        raise NotImplementedError("TODO: $%x MUL" % opcode)
        # Update CC bits: --a-a

    @opcode( # Negate accumulator or memory
        0x0, 0x60, 0x70, # NEG (direct, indexed, extended)
        0x40, # NEGA (inherent)
        0x50, # NEGB (inherent)
    )
    def instruction_NEG(self, opcode, ea=None, operand=None):
        """
        Replaces the operand with its twos complement. The C (carry) bit
        represents a borrow and is set to the inverse of the resulting binary
        carry. Note that 80 16 is replaced by itself and only in this case is
        the V (overflow) bit set. The value 00 16 is also replaced by itself,
        and only in this case is the C (carry) bit cleared.

        source code forms: NEG Q; NEGA; NEG B

        CC bits "HNZVC": uaaaa
        """
        raise NotImplementedError("TODO: $%x NEG" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # No operation
        0x12, # NOP (inherent)
    )
    def instruction_NOP(self, opcode):
        """
        source code forms: NOP

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x NOP" % opcode)

    @opcode( # OR memory with accumulator
        0x8a, 0x9a, 0xaa, 0xba, # ORA (immediate, direct, indexed, extended)
        0xca, 0xda, 0xea, 0xfa, # ORB (immediate, direct, indexed, extended)
    )
    def instruction_OR(self, opcode, ea=None, operand=None):
        """
        Performs an inclusive OR operation between the contents of accumulator A
        or B and the contents of memory location M and the result is stored in
        accumulator A or B.

        source code forms: ORA P; ORB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x OR" % opcode)
        self.cc.update_NZ0()

    @opcode( # OR condition code register
        0x1a, # ORCC (immediate)
    )
    def instruction_ORCC(self, opcode, ea=None, operand=None):
        """
        Performs an inclusive OR operation between the contents of the condition
        code registers and the immediate value, and the result is placed in the
        condition code register. This instruction may be used to set interrupt
        masks (disable interrupts) or any other bit(s).

        source code forms: ORCC #XX

        CC bits "HNZVC": ddddd
        """
        raise NotImplementedError("TODO: $%x ORCC" % opcode)
        # Update CC bits: ddddd

    @opcode( # Branch if lower (unsigned)
        0x24, # BHS/BCC (relative)
        0x25, # BLO/BCS (relative)
        0x1024, # LBHS/LBCC (relative)
        0x1025, # LBLO/LBCS (relative)
    )
    def instruction_OTHER_INSTRUCTIONS(self, opcode, ea=None):
        """
        source code forms:

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x OTHER_INSTRUCTIONS" % opcode)

    @opcode( # 
        0x10, # PAGE1+ (variant)
        0x11, # PAGE2+ (variant)
    )
    def instruction_PAGE(self, opcode):
        """
        Page 1/2 instructions

        source code forms:

        CC bits "HNZVC": +++++
        """
        raise NotImplementedError("TODO: $%x PAGE" % opcode)
        # Update CC bits: +++++

    @opcode( # Push A, B, CC, DP, D, X, Y, U, or PC onto hardware stack
        0x34, # PSHS (immediate)
    )
    def instruction_PSHS(self, opcode, ea=None, operand=None):
        """
        All, some, or none of the processor registers are pushed onto the
        hardware stack (with the exception of the hardware stack pointer
        itself).

        A single register may be placed on the stack with the condition codes
        set by doing an autodecrement store onto the stack (example: STX ,--S).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC U Y X DP B A CC push order
        ->

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x PSHS" % opcode)

    @opcode( # Push A, B, CC, DP, D, X, Y, S, or PC onto user stack
        0x36, # PSHU (immediate)
    )
    def instruction_PSHU(self, opcode, ea=None, operand=None):
        """
        All, some, or none of the processor registers are pushed onto the user
        stack (with the exception of the user stack pointer itself).

        A single register may be placed on the stack with the condition codes
        set by doing an autodecrement store onto the stack (example: STX ,--U).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC S Y X DP B A CC push order
        ->

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x PSHU" % opcode)

    @opcode( # Pull A, B, CC, DP, D, X, Y, U, or PC from hardware stack
        0x35, # PULS (immediate)
    )
    def instruction_PULS(self, opcode, ea=None, operand=None):
        """
        All, some, or none of the processor registers are pulled from the
        hardware stack (with the exception of the hardware stack pointer
        itself).

        A single register may be pulled from the stack with condition codes set
        by doing an autoincrement load from the stack (example: LDX ,S++).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC U Y X DP B A CC = pull
        order

        CC bits "HNZVC": ccccc
        """
        raise NotImplementedError("TODO: $%x PULS" % opcode)
        # Update CC bits: ccccc

    @opcode( # Pull A, B, CC, DP, D, X, Y, S, or PC from hardware stack
        0x37, # PULU (immediate)
    )
    def instruction_PULU(self, opcode, ea=None, operand=None):
        """
        All, some, or none of the processor registers are pulled from the user
        stack (with the exception of the user stack pointer itself).

        A single register may be pulled from the stack with condition codes set
        by doing an autoincrement load from the stack (example: LDX ,U++).

        source code forms: b7 b6 b5 b4 b3 b2 b1 b0 PC S Y X DP B A CC = pull
        order

        CC bits "HNZVC": ccccc
        """
        raise NotImplementedError("TODO: $%x PULU" % opcode)
        # Update CC bits: ccccc

    @opcode( # 
        0x3e, # RESET* (inherent)
    )
    def instruction_RESET(self, opcode):
        """
         Build the ASSIST09 vector table and setup monitor defaults, then invoke
        the monitor startup routine.

        source code forms:

        CC bits "HNZVC": *****
        """
        raise NotImplementedError("TODO: $%x RESET" % opcode)
        # Update CC bits: *****

    @opcode( # Rotate accumulator or memory left
        0x9, 0x69, 0x79, # ROL (direct, indexed, extended)
        0x49, # ROLA (inherent)
        0x59, # ROLB (inherent)
    )
    def instruction_ROL(self, opcode, ea=None, operand=None):
        """
        Rotates all bits of the operand one place left through the C (carry)
        bit. This is a 9-bit rotation.

        source code forms: ROL Q; ROLA; ROLB

        CC bits "HNZVC": -aaas
        """
        raise NotImplementedError("TODO: $%x ROL" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # Rotate accumulator or memory right
        0x6, 0x66, 0x76, # ROR (direct, indexed, extended)
        0x46, # RORA (inherent)
        0x56, # RORB (inherent)
    )
    def instruction_ROR(self, opcode, ea=None, operand=None):
        """
        Rotates all bits of the operand one place right through the C (carry)
        bit. This is a 9-bit rotation.

        source code forms: ROR Q; RORA; RORB

        CC bits "HNZVC": -aa-s
        """
        raise NotImplementedError("TODO: $%x ROR" % opcode)
        self.cc.update_NZC()

    @opcode( # Return from interrupt
        0x3b, # RTI (inherent)
    )
    def instruction_RTI(self, opcode):
        """
        The saved machine state is recovered from the hardware stack and control
        is returned to the interrupted program. If the recovered E (entire) bit
        is clear, it indicates that only a subset of the machine state was saved
        (return address and condition codes) and only that subset is recovered.

        source code forms: RTI

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x RTI" % opcode)

    @opcode( # Return from subroutine
        0x39, # RTS (inherent)
    )
    def instruction_RTS(self, opcode):
        """
        Program control is returned from the subroutine to the calling program.
        The return address is pulled from the stack.

        source code forms: RTS

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x RTS" % opcode)

    @opcode( # Subtract memory from accumulator with borrow
        0x82, 0x92, 0xa2, 0xb2, # SBCA (immediate, direct, indexed, extended)
        0xc2, 0xd2, 0xe2, 0xf2, # SBCB (immediate, direct, indexed, extended)
    )
    def instruction_SBC(self, opcode, ea=None, operand=None):
        """
        Subtracts the contents of memory location M and the borrow (in the C
        (carry) bit) from the contents of the designated 8-bit register, and
        places the result in that register. The C bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SBCA P; SBCB P

        CC bits "HNZVC": uaaaa
        """
        raise NotImplementedError("TODO: $%x SBC" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # Sign Extend B accumulator into A accumulator
        0x1d, # SEX (inherent)
    )
    def instruction_SEX(self, opcode):
        """
        This instruction transforms a twos complement 8-bit value in accumulator
        B into a twos complement 16-bit value in the D accumulator.

        source code forms: SEX

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x SEX" % opcode)
        self.cc.update_NZ0()

    @opcode( # Store stack pointer to memory
        0xdd, 0xed, 0xfd, # STD (direct, indexed, extended)
        0x10df, 0x10ef, 0x10ff, # STS (direct, indexed, extended)
        0xdf, 0xef, 0xff, # STU (direct, indexed, extended)
        0x9f, 0xaf, 0xbf, # STX (direct, indexed, extended)
        0x109f, 0x10af, 0x10bf, # STY (direct, indexed, extended)
    )
    def instruction_ST16(self, opcode, ea=None, operand=None):
        """
        Writes the contents of a 16-bit register into two consecutive memory
        locations.

        source code forms: STD P; STX P; STY P; STS P; STU P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x ST16" % opcode)
        self.cc.update_NZ0_16()

    @opcode( # Store accumulator to memroy
        0x97, 0xa7, 0xb7, # STA (direct, indexed, extended)
        0xd7, 0xe7, 0xf7, # STB (direct, indexed, extended)
    )
    def instruction_ST8(self, opcode, ea=None, operand=None):
        """
        Writes the contents of an 8-bit register into a memory location.

        source code forms: STA P; STB P

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x ST8" % opcode)
        self.cc.update_NZ0()

    @opcode( # Subtract memory from D accumulator
        0x83, 0x93, 0xa3, 0xb3, # SUBD (immediate, direct, indexed, extended)
    )
    def instruction_SUB16(self, opcode, ea=None, operand=None):
        """
        Subtracts the value in memory location M:M+1 from the contents of a
        designated 16-bit register. The C (carry) bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SUBD P

        CC bits "HNZVC": -aaaa
        """
        raise NotImplementedError("TODO: $%x SUB16" % opcode)
        self.cc.update_NZVC_16(a, b, r)

    @opcode( # Subtract memory from accumulator
        0x80, 0x90, 0xa0, 0xb0, # SUBA (immediate, direct, indexed, extended)
        0xc0, 0xd0, 0xe0, 0xf0, # SUBB (immediate, direct, indexed, extended)
    )
    def instruction_SUB8(self, opcode, ea=None, operand=None):
        """
        Subtracts the value in memory location M from the contents of a
        designated 8-bit register. The C (carry) bit represents a borrow and is
        set to the inverse of the resulting binary carry.

        source code forms: SUBA P; SUBB P

        CC bits "HNZVC": uaaaa
        """
        raise NotImplementedError("TODO: $%x SUB8" % opcode)
        self.cc.update_NZVC(a, b, r)

    @opcode( # Software interrupt (absolute indirect)
        0x3f, # SWI (inherent)
    )
    def instruction_SWI(self, opcode):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt vector. Both the normal and
        fast interrupts are masked (disabled).

        source code forms: SWI

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x SWI" % opcode)

    @opcode( # Software interrupt (absolute indirect)
        0x103f, # SWI2 (inherent)
    )
    def instruction_SWI2(self, opcode, ea=None):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt 2 vector. This interrupt is
        available to the end user and must not be used in packaged software.
        This interrupt does not mask (disable) the normal and fast interrupts.

        source code forms: SWI2

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x SWI2" % opcode)

    @opcode( # Software interrupt (absolute indirect)
        0x113f, # SWI3 (inherent)
    )
    def instruction_SWI3(self, opcode, ea=None):
        """
        All of the processor registers are pushed onto the hardware stack (with
        the exception of the hardware stack pointer itself), and control is
        transferred through the software interrupt 3 vector. This interrupt does
        not mask (disable) the normal and fast interrupts.

        source code forms: SWI3

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x SWI3" % opcode)

    @opcode( # Synchronize with interrupt line
        0x13, # SYNC (inherent)
    )
    def instruction_SYNC(self, opcode):
        """
        FAST SYNC WAIT FOR DATA Interrupt! LDA DISC DATA FROM DISC AND CLEAR
        INTERRUPT STA ,X+ PUT IN BUFFER DECB COUNT IT, DONE? BNE FAST GO AGAIN
        IF NOT.

        source code forms: SYNC

        CC bits "HNZVC": -----
        """
        raise NotImplementedError("TODO: $%x SYNC" % opcode)

    @opcode( # Transfer R1 to R2
        0x1f, # TFR (immediate)
    )
    def instruction_TFR(self, opcode, ea=None):
        """
        0000 = A:B 1000 = A 0001 = X 1001 = B 0010 = Y 1010 = CCR 0011 = US 1011
        = DPR 0100 = SP 1100 = Undefined 0101 = PC 1101 = Undefined 0110 =
        Undefined 1110 = Undefined 0111 = Undefined 1111 = Undefined

        source code forms: TFR R1, R2

        CC bits "HNZVC": ccccc
        """
        raise NotImplementedError("TODO: $%x TFR" % opcode)
        # Update CC bits: ccccc

    @opcode( # Test accumulator or memory location
        0xd, 0x6d, 0x7d, # TST (direct, indexed, extended)
        0x4d, # TSTA (inherent)
        0x5d, # TSTB (inherent)
    )
    def instruction_TST(self, opcode, ea=None, operand=None):
        """
        Set the N (negative) and Z (zero) bits according to the contents of
        memory location M, and clear the V (overflow) bit. The TST instruction
        provides only minimum information when testing unsigned values; since no
        unsigned value is less than zero, BLO and BLS have no utility. While BHI
        could be used after TST, it provides exactly the same control as BNE,
        which is preferred. The signed branches are available.

        The MC6800 processor clears the C (carry) bit.

        source code forms: TST Q; TSTA; TSTB

        CC bits "HNZVC": -aa0-
        """
        raise NotImplementedError("TODO: $%x TST" % opcode)
        self.cc.update_NZ0()

"""
No ops for:
"""
