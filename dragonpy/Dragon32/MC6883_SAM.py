#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#sam

    $ffc0-ffdf    SAM (Synchronous Address Multiplexer) register bits - use
                      even address to clear, odd address to set
    $ffc0-ffc5    SAM VDG Mode registers V0-V2
    $ffc0/ffc1    SAM VDG Reg V0
    $ffc2/ffc3    SAM VDG Reg V1
    $ffc4/ffc5    SAM VDG Reg V2
    $ffc6-ffd3    SAM Display offset in 512 byte pages F0-F6
    $ffc6/ffc7    SAM Display Offset bit F0
    $ffc8/ffc9    SAM Display Offset bit F1
    $ffca/ffcb    SAM Display Offset bit F2
    $ffcc/ffcd    SAM Display Offset bit F3
    $ffce/ffcf    SAM Display Offset bit F4
    $ffd0/ffc1    SAM Display Offset bit F5
    $ffd2/ffc3    SAM Display Offset bit F6
    $ffd4/ffd5    SAM Page #1 bit - in D64 maps upper 32K Ram to $0000 to $7fff
    $ffd6-ffd9    SAM MPU Rate R0-R1
    $ffd6/ffd7    SAM MPU Rate bit R0
    $ffd8/ffd9    SAM MPU Rate bit R1
    $ffda-ffdd    SAM Memory Size select M0-M1
    $ffda/ffdb    SAM Memory Size select bit M0
    $ffdc/ffdd    SAM Memory Size select bit M1
    $ffde/ffdf    SAM Map Type - in D64 switches in upper 32K RAM $8000-$feff

    from http://archive.worldofdragon.org/index.php?title=Dragon_32_-_64K_Upgrade#APPENDICES. :
    Most well—known of these operations is the so-called 'speed-up poke'
    (POKE&HFFD7,0 and its reverse, POKE&HFFD6,0); however, of more concern to us
    here is the Map Type Bit (TY), set by FFDF, cleared by FFDE; the Page Bit (Pl),
    set by FFD5, cleared by FFD4; and the Memory Size Bits (M0 A Ml) set/cleared by
    FFDB/FFDA & FFDD/FFDC respectively. Of the remaining addresses, FFD6 to FFD9
    control the 2 clockrate bits (R0 & Rl); FFC6 to FFD3 control 7 bits (F0 to F6)
    giving the base address of the current Video-RAM (in units of 512 bytes); and
    FFC0 to FFC5 control 3 VDG Mode bits (V0 to V2).

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

import logging

log=logging.getLogger(__name__)


class SAM(object):
    """
    MC6883 (74LS783) Synchronous Address Multiplexer (SAM)
    """

    # http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4894&p=11730#p11726
    IRQ_CYCLES = 17784

    def __init__(self, cfg, cpu, memory):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory


        self.cpu.add_sync_callback(callback_cycles=self.IRQ_CYCLES, callback=self.irq_trigger)

        #
        # TODO: Collect this information via a decorator similar to op codes in CPU!
        #
        self.memory.add_read_byte_callback(self.read_VDG_mode_register_v1, 0xffc2)

        self.memory.add_write_byte_callback(self.write_VDG_mode_register_v0, 0xffc0)
        self.memory.add_write_byte_callback(self.write_VDG_mode_register_v1, 0xffc2)
        self.memory.add_write_byte_callback(self.write_VDG_mode_register_v2, 0xffc4)
        self.memory.add_write_byte_callback(self.write_display_offset_F0, 0xffc6)
        self.memory.add_write_byte_callback(self.write_display_offset_F1, 0xffc8)
        self.memory.add_write_byte_callback(self.write_display_offset_F2, 0xffca)
        self.memory.add_write_byte_callback(self.write_display_offset_F3, 0xffcc)
        self.memory.add_write_byte_callback(self.write_display_offset_F4, 0xffce)
        self.memory.add_write_byte_callback(self.write_display_offset_F5, 0xffd0)
        self.memory.add_write_byte_callback(self.write_display_offset_F6, 0xffd2)
        self.memory.add_write_byte_callback(self.write_page_bit, 0xffd4)
        self.memory.add_write_byte_callback(self.write_MPU_rate_bit0, 0xffd6)
        self.memory.add_write_byte_callback(self.write_MPU_rate_bit1, 0xffd8)
        self.memory.add_write_byte_callback(self.write_size_select_bit0, 0xffda)
        self.memory.add_write_byte_callback(self.write_size_select_bit1, 0xffdc)
        self.memory.add_write_byte_callback(self.write_map_type, 0xffde)
        self.memory.add_write_byte_callback(self.write_map0, 0xffdd)

        #  Dragon 64 only:
        self.memory.add_write_byte_callback(self.write_D64_dynamic_memory, 0xffc9)

        self.memory.add_read_byte_callback(self.interrupt_vectors, 0xfff0, 0xffff)

    def reset(self):
        log.critical("TODO: VDG reset")

    def irq_trigger(self, call_cycles):
#        log.critical("%04x| SAM irq trigger called %i cycles to late",
#            self.cpu.last_op_address, call_cycles - self.IRQ_CYCLES
#        )
        self.cpu.irq()

    def interrupt_vectors(self, cpu_cycles, op_address, address):
        new_address = address - 0x4000
        value = self.memory.read_byte(new_address)
#         log.critical("read interrupt vector $%04x redirect in SAM to $%04x use value $%02x",
#             address, new_address, value
#         )
        return value

#     def read_VDG_mode_register_v0(self, cpu_cycles, op_address, address):
#         log.debug("TODO: read VDG mode register V0 $%04x", address)
#         return 0x00

    def read_VDG_mode_register_v1(self, cpu_cycles, op_address, address):
        log.debug("TODO: read VDG mode register V1 $%04x", address)
        return 0x00

    #--------------------------------------------------------------------------

    def write_VDG_mode_register_v0(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write VDG mode register V0 $%02x to $%04x", value, address)

    def write_VDG_mode_register_v1(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write VDG mode register V1 $%02x to $%04x", value, address)

    def write_VDG_mode_register_v2(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write VDG mode register V2 $%02x to $%04x", value, address)

    def write_display_offset_F0(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F0 $%02x to $%04x", value, address)

    def write_display_offset_F1(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F1 $%02x to $%04x", value, address)

    def write_display_offset_F2(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F2 $%02x to $%04x", value, address)

    def write_display_offset_F3(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F3 $%02x to $%04x", value, address)

    def write_display_offset_F4(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F4 $%02x to $%04x", value, address)

    def write_display_offset_F5(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F5 $%02x to $%04x", value, address)

    def write_display_offset_F6(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write display_offset_F6 $%02x to $%04x", value, address)

    def write_page_bit(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write page_bit $%02x to $%04x", value, address)

    def write_MPU_rate_bit0(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write MPU_rate_bit0 $%02x to $%04x", value, address)

    def write_MPU_rate_bit1(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write MPU_rate_bit1 $%02x to $%04x", value, address)

    def write_size_select_bit0(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write size_select_bit0 $%02x to $%04x", value, address)

    def write_size_select_bit1(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write size_select_bit1 $%02x to $%04x", value, address)

    def write_map_type(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write map_type $%02x to $%04x", value, address)

    def write_map0(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write map0 $%02x to $%04x", value, address)

    def write_D64_dynamic_memory(self, cpu_cycles, op_address, address, value):
        log.debug("TODO: write D64_dynamic_memory $%02x to $%04x", value, address)


#------------------------------------------------------------------------------


