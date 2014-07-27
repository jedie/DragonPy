#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#pia0

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

from dragonpy.utils.logging_utils import log


class PIA_register(object):
    def __init__(self, name):
        self.name = name
        self.reset()

    def reset(self):
        self.control_register = 0x0
        self.direction_register = 0x0
        self.output_register = 0x0
        self.interrupt_received = 0x0
        self.irq = 0x0


class PIA(object):
    """
    PIA - MC6821 - Peripheral Interface Adaptor
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.pia_0_A_registers = PIA_register("PIA0 A")
        self.pia_0_B_registers = PIA_register("PIA0 B")
        self.pia_1_A_registers = PIA_register("PIA1 A")
        self.pia_1_B_registers = PIA_register("PIA1 B")

    def get_write_func_map(self):
        #
        # TODO: Collect this information via a decorator simmilar to op codes in CPU!
        #
        write_func_map = {
            0xff00: self.write_PIA0_A_data, #    PIA 0 A side Data reg. PA7
            0xff01: self.write_PIA0_A_control, # PIA 0 A side Control reg. CA1
            0xff02: self.write_PIA0_B_data, #    PIA 0 B side Data reg. PB7
            0xff03: self.write_PIA0_B_control, # PIA 0 B side Control reg. CB1

            0xff06: self.write_serial_interface, # Only Dragon 64

            0xff20: self.write_PIA1_A_data, #    PIA 1 A side Data reg. PA7
            0xff21: self.write_PIA1_A_control, # PIA 1 A side Control reg. CA1
            0xff22: self.write_PIA1_B_data, #    PIA 1 B side Data reg. PB7
            0xff23: self.write_PIA1_B_control, # PIA 1 B side Control reg. CB1
        }
        return write_func_map

    def get_read_func_map(self):
        read_func_map = {
            0xff00: self.read_PIA0_A_data, #    PIA 0 A side Data reg. PA7
            0xff01: self.read_PIA0_A_control, # PIA 0 A side Control reg. CA1
            0xff02: self.read_PIA0_B_data, #    PIA 0 B side Data reg. PB7
            0xff03: self.read_PIA0_B_control, # PIA 0 B side Control reg. CB1

            0xff04: self.read_serial_interface, # Only Dragon 64

            0xff20: self.read_PIA1_A_data, #    PIA 1 A side Data reg. PA7
            0xff21: self.read_PIA1_A_control, # PIA 1 A side Control reg. CA1
            0xff22: self.read_PIA1_B_data, #    PIA 1 B side Data reg. PB7
            0xff23: self.read_PIA1_B_control, # PIA 1 B side Control reg. CB1
        }
        return read_func_map

    def reset(self):
        self.pia_0_A_registers.reset()
        self.pia_0_B_registers.reset()
        self.pia_1_A_registers.reset()
        self.pia_1_B_registers.reset()

    #--------------------------------------------------------------------------

    def read_PIA0_A_data(self, cpu_cycles, op_address, address):
        """ read to 0xff00 -> PIA 0 A side Data reg. PA7 """
        log.error("TODO: read to 0xff00 -> PIA 0 A side Data reg. PA7")
        return 0x00

    def read_PIA0_A_control(self, cpu_cycles, op_address, address):
        """ read to 0xff01 -> PIA 0 A side Control reg. CA1 """
        log.error("TODO: read to 0xff01 -> PIA 0 A side Control reg. CA1")
        return 0xb3

    def read_PIA0_B_data(self, cpu_cycles, op_address, address):
        """ read to 0xff02 -> PIA 0 B side Data reg. PB7 """
        log.error("TODO: read to 0xff02 -> PIA 0 B side Data reg. PB7")
        return 0x00

    def read_PIA0_B_control(self, cpu_cycles, op_address, address):
        """ read to 0xff03 -> PIA 0 B side Control reg. CB1 """
        log.error("TODO: read to 0xff03 -> PIA 0 B side Control reg. CB1")
        return 0x35

    def read_PIA1_A_data(self, cpu_cycles, op_address, address):
        """ read to 0xff20 -> PIA 1 A side Data reg. PA7 """
        log.error("TODO: read to 0xff20 -> PIA 1 A side Data reg. PA7")
        return 0x01

    def read_PIA1_A_control(self, cpu_cycles, op_address, address):
        """ read to 0xff21 -> PIA 1 A side Control reg. CA1 """
        log.error("TODO: read to 0xff21 -> PIA 1 A side Control reg. CA1")
        return 0x34

    def read_PIA1_B_data(self, cpu_cycles, op_address, address):
        """ read to 0xff22 -> PIA 1 B side Data reg. PB7 """
        log.error("TODO: read to 0xff22 -> PIA 1 B side Data reg. PB7")
        return 0x00

    def read_PIA1_B_control(self, cpu_cycles, op_address, address):
        """ read to 0xff23 -> PIA 1 B side Control reg. CB1 """
        log.error("TODO: read to 0xff23 -> PIA 1 B side Control reg. CB1")
        return 0x37

    #--------------------------------------------------------------------------

    def write_PIA0_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff00 -> PIA 0 A side Data reg. PA7 """
        log.error("TODO: write $%02x to 0xff00 -> PIA 0 A side Data reg. PA7", value)

    def write_PIA0_A_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff01 -> PIA 0 A side Control reg. CA1 """
        log.error("TODO: write $%02x to 0xff01 -> PIA 0 A side Control reg. CA1", value)

    def write_PIA0_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff02 -> PIA 0 B side Data reg. PB7 """
        log.error("TODO: write $%02x to 0xff02 -> PIA 0 B side Data reg. PB7", value)

    def write_PIA0_B_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff03 -> PIA 0 B side Control reg. CB1 """
        log.error("TODO: write $%02x to 0xff03 -> PIA 0 B side Control reg. CB1", value)

    def write_PIA1_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff20 -> PIA 1 A side Data reg. PA7 """
        log.error("TODO: write $%02x to 0xff20 -> PIA 1 A side Data reg. PA7", value)

    def write_PIA1_A_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff21 -> PIA 1 A side Control reg. CA1 """
        log.error("TODO: write $%02x to 0xff21 -> PIA 1 A side Control reg. CA1", value)

    def write_PIA1_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff22 -> PIA 1 B side Data reg. PB7 """
        log.error("TODO: write $%02x to 0xff22 -> PIA 1 B side Data reg. PB7", value)

    def write_PIA1_B_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff23 -> PIA 1 B side Control reg. CB1 """
        log.error("TODO: write $%02x to 0xff23 -> PIA 1 B side Control reg. CB1", value)

    #--------------------------------------------------------------------------

    def read_serial_interface(self, cpu_cycles, op_address, address):
        log.error("TODO: read from $%04x (D64 serial interface", address)
        return 0x00

    def write_serial_interface(self, cpu_cycles, op_address, address, value):
        log.error("TODO: write $%02x to $%04x (D64 serial interface", value, address)


