
"""
    This file was generated with: "Instruction_generator.py"
    Please doen't change it directly ;)
    

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

"""


from dragonpy.components.cpu_utils.instruction_base import InstructionBase

class PrepagedInstructions(InstructionBase):

    def direct_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct(),
        )

    def direct_A_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct(),
            register = self.cpu.accu_a,
        )

    def direct_B_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct(),
            register = self.cpu.accu_b,
        )

    def direct_ea(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
        )

    def direct_ea_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
        )
        self.memory.write_byte(ea, value)

    def direct_ea_read8_write8(self, opcode):
        ea, m = self.cpu.get_ea_m_direct()
        ea, value = self.instr_func(
            opcode = opcode,
            ea = ea,
            m = m,
        )
        self.memory.write_byte(ea, value)

    def direct_ea_A_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.accu_a,
        )
        self.memory.write_byte(ea, value)

    def direct_ea_B_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.accu_b,
        )
        self.memory.write_byte(ea, value)

    def direct_ea_D_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.accu_d,
        )
        self.memory.write_word(ea, value)

    def direct_ea_S_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.system_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def direct_ea_U_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.user_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def direct_ea_X_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.index_x,
        )
        self.memory.write_word(ea, value)

    def direct_ea_Y_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_direct(),
            register = self.cpu.index_y,
        )
        self.memory.write_word(ea, value)

    def direct_word_D_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct_word(),
            register = self.cpu.accu_d,
        )

    def direct_word_S_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct_word(),
            register = self.cpu.system_stack_pointer,
        )

    def direct_word_U_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct_word(),
            register = self.cpu.user_stack_pointer,
        )

    def direct_word_X_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct_word(),
            register = self.cpu.index_x,
        )

    def direct_word_Y_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_direct_word(),
            register = self.cpu.index_y,
        )

    def extended_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended(),
        )

    def extended_A_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended(),
            register = self.cpu.accu_a,
        )

    def extended_B_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended(),
            register = self.cpu.accu_b,
        )

    def extended_ea(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
        )

    def extended_ea_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
        )
        self.memory.write_byte(ea, value)

    def extended_ea_read8_write8(self, opcode):
        ea, m = self.cpu.get_ea_m_extended()
        ea, value = self.instr_func(
            opcode = opcode,
            ea = ea,
            m = m,
        )
        self.memory.write_byte(ea, value)

    def extended_ea_A_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.accu_a,
        )
        self.memory.write_byte(ea, value)

    def extended_ea_B_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.accu_b,
        )
        self.memory.write_byte(ea, value)

    def extended_ea_D_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.accu_d,
        )
        self.memory.write_word(ea, value)

    def extended_ea_S_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.system_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def extended_ea_U_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.user_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def extended_ea_X_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.index_x,
        )
        self.memory.write_word(ea, value)

    def extended_ea_Y_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_extended(),
            register = self.cpu.index_y,
        )
        self.memory.write_word(ea, value)

    def extended_word_D_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended_word(),
            register = self.cpu.accu_d,
        )

    def extended_word_S_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended_word(),
            register = self.cpu.system_stack_pointer,
        )

    def extended_word_U_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended_word(),
            register = self.cpu.user_stack_pointer,
        )

    def extended_word_X_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended_word(),
            register = self.cpu.index_x,
        )

    def extended_word_Y_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_extended_word(),
            register = self.cpu.index_y,
        )

    def immediate_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
        )

    def immediate_A_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
            register = self.cpu.accu_a,
        )

    def immediate_B_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
            register = self.cpu.accu_b,
        )

    def immediate_CC_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
            register = self.cpu.cc,
        )

    def immediate_S_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
            register = self.cpu.system_stack_pointer,
        )

    def immediate_U_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate(),
            register = self.cpu.user_stack_pointer,
        )

    def immediate_word_D_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate_word(),
            register = self.cpu.accu_d,
        )

    def immediate_word_S_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate_word(),
            register = self.cpu.system_stack_pointer,
        )

    def immediate_word_U_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate_word(),
            register = self.cpu.user_stack_pointer,
        )

    def immediate_word_X_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate_word(),
            register = self.cpu.index_x,
        )

    def immediate_word_Y_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_immediate_word(),
            register = self.cpu.index_y,
        )

    def indexed_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed(),
        )

    def indexed_A_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed(),
            register = self.cpu.accu_a,
        )

    def indexed_B_read8(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed(),
            register = self.cpu.accu_b,
        )

    def indexed_ea(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
        )

    def indexed_ea_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
        )
        self.memory.write_byte(ea, value)

    def indexed_ea_read8_write8(self, opcode):
        ea, m = self.cpu.get_ea_m_indexed()
        ea, value = self.instr_func(
            opcode = opcode,
            ea = ea,
            m = m,
        )
        self.memory.write_byte(ea, value)

    def indexed_ea_A_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.accu_a,
        )
        self.memory.write_byte(ea, value)

    def indexed_ea_B_write8(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.accu_b,
        )
        self.memory.write_byte(ea, value)

    def indexed_ea_D_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.accu_d,
        )
        self.memory.write_word(ea, value)

    def indexed_ea_S(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.system_stack_pointer,
        )

    def indexed_ea_S_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.system_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def indexed_ea_U(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.user_stack_pointer,
        )

    def indexed_ea_U_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.user_stack_pointer,
        )
        self.memory.write_word(ea, value)

    def indexed_ea_X(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.index_x,
        )

    def indexed_ea_X_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.index_x,
        )
        self.memory.write_word(ea, value)

    def indexed_ea_Y(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.index_y,
        )

    def indexed_ea_Y_write16(self, opcode):
        ea, value = self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_indexed(),
            register = self.cpu.index_y,
        )
        self.memory.write_word(ea, value)

    def indexed_word_D_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed_word(),
            register = self.cpu.accu_d,
        )

    def indexed_word_S_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed_word(),
            register = self.cpu.system_stack_pointer,
        )

    def indexed_word_U_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed_word(),
            register = self.cpu.user_stack_pointer,
        )

    def indexed_word_X_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed_word(),
            register = self.cpu.index_x,
        )

    def indexed_word_Y_read16(self, opcode):
        self.instr_func(
            opcode = opcode,
            m = self.cpu.get_m_indexed_word(),
            register = self.cpu.index_y,
        )

    def inherent(self, opcode):
        self.instr_func(
            opcode = opcode,
        )

    def inherent_A(self, opcode):
        self.instr_func(
            opcode = opcode,
            register = self.cpu.accu_a,
        )

    def inherent_B(self, opcode):
        self.instr_func(
            opcode = opcode,
            register = self.cpu.accu_b,
        )

    def relative_ea(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_relative(),
        )

    def relative_word_ea(self, opcode):
        self.instr_func(
            opcode = opcode,
            ea = self.cpu.get_ea_relative_word(),
        )

