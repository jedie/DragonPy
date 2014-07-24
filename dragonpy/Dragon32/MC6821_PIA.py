#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#pia0

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

import logging

log = logging.getLogger("DragonPy.components.MC6821_PIA")


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
        log = logging.getLogger("DragonPy.Periphery.PIA")

        self.func_map = {
            0xff00: self.pia_0_A_data,
            0xff01: self.pia_0_A_control,
            0xff02: self.pia_0_B_data,
            0xff03: self.pia_0_B_control,
            0xff20: self.pia_1_A_data,
            0xff21: self.pia_1_A_control,
            0xff22: self.pia_1_B_data,
            0xff23: self.pia_1_B_control,
        }
        self.pia_0_A_registers = PIA_register("PIA0 A")
        self.pia_0_B_registers = PIA_register("PIA0 B")
        self.pia_1_A_registers = PIA_register("PIA1 A")
        self.pia_1_B_registers = PIA_register("PIA1 B")

    def reset(self):
        self.pia_0_A_registers.reset()
        self.pia_0_B_registers.reset()
        self.pia_1_A_registers.reset()
        self.pia_1_B_registers.reset()

    def __call__(self, address):
        func = self.func_map[address]
        value = func()
        log.debug(" PIA call at $%x %s returned $%x \t| %s" % (
            address, func.__name__, value, self.cfg.mem_info.get_shortest(address)
        ))
        return value

    def write_byte(self, address, value):
        log.error(" *** TODO: PIA write byte $%02x to $%x \t| %s" % (
            value, address, self.cfg.mem_info.get_shortest(address)
        ))

    def pia_0_A_data(self):
        log.error(" *** TODO: PIA 0 A side data register")
        return 0x00 # self.kbd
    def pia_0_A_control(self):
        log.error(" *** TODO: PIA 0 A side control register")
        return 0xb3
    def pia_0_B_data(self):
        log.error(" *** TODO: PIA 0 B side data register")
        return 0x00
    def pia_0_B_control(self):
        log.error(" *** TODO: PIA 0 B side control register")
        return 0x35

    def pia_1_A_data(self):
        log.error(" *** TODO: PIA 1 A side data register")
        return 0x01
    def pia_1_A_control(self):
        log.error(" *** TODO: PIA 1 A side control register")
        return 0x34
    def pia_1_B_data(self):
        log.error(" *** TODO: PIA 1 B side data register")
        return 0x00
    def pia_1_B_control(self):
        log.error(" *** TODO: PIA 1 B side control register")
        return 0x37
