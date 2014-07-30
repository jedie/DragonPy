#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#pia0
    http://www.onastick.clara.net/sys4.htm

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

from dragonpy.utils.logging_utils import log
from dragonpy.Dragon32.keyboard_map import get_dragon_col_row_values
from dragonpy.utils.humanize import byte2bit_string
from dragonpy.utils.bits import is_bit_set


class PIA_register(object):
    def __init__(self, name):
        self.name = name
        self.reset()

    def reset(self):
        self._pdr_selected = False # pdr = Peripheral Data Register
        self.control_register = 0x0
        self.direction_register = 0x0
        self.output_register = 0x0
        self.interrupt_received = 0x0
        self.irq = 0x0

    def is_pdr_selected(self):
        return self._pdr_selected

    def select_pdr(self):
        log.critical("\t Select 'Peripheral Data Register' in %s", self.name)
        self._pdr_selected = True

    def deselect_pdr(self):
        log.critical("\t Deselect 'Peripheral Data Register' in %s", self.name)
        self._pdr_selected = False


class PIA(object):
    """
    PIA - MC6821 - Peripheral Interface Adaptor

    PIA0 - Keyboard, Joystick
    PIA1 - Printer, Cassette, 6-Bit DAC, Sound Mux

    """
    def __init__(self, cfg):
        self.cfg = cfg

        self.pia_0_A_register = PIA_register("PIA0 A")
        self.pia_0_B_register = PIA_register("PIA0 B")
        self.pia_1_A_register = PIA_register("PIA1 A")
        self.pia_1_B_register = PIA_register("PIA1 B")

        self.keyboard_col = 0xff
        self.keyboard_row = 0xff
        self.keyboard_col_send = True
        self.keyboard_row_send = True

    def get_write_func_map(self):
        #
        # TODO: Collect this information via a decorator simmilar to op codes in CPU!
        #
        write_func_map = {
            0xff00: self.write_PIA0_A_data, #    PIA 0 A side Data reg.
            0xff01: self.write_PIA0_A_control, # PIA 0 A side Control reg.
            0xff02: self.write_PIA0_B_data, #    PIA 0 B side Data reg.
            0xff03: self.write_PIA0_B_control, # PIA 0 B side Control reg.

            0xff06: self.write_serial_interface, # Only Dragon 64

            0xff20: self.write_PIA1_A_data, #    PIA 1 A side Data reg.
            0xff21: self.write_PIA1_A_control, # PIA 1 A side Control reg.
            0xff22: self.write_PIA1_B_data, #    PIA 1 B side Data reg.
            0xff23: self.write_PIA1_B_control, # PIA 1 B side Control reg.
        }
        return write_func_map

    def get_read_func_map(self):
        read_func_map = {
            0xff00: self.read_PIA0_A_data, #    PIA 0 A side Data reg.
            0xff01: self.read_PIA0_A_control, # PIA 0 A side Control reg.
            0xff02: self.read_PIA0_B_data, #    PIA 0 B side Data reg.
            0xff03: self.read_PIA0_B_control, # PIA 0 B side Control reg.

            0xff04: self.read_serial_interface, # Only Dragon 64

            0xff20: self.read_PIA1_A_data, #    PIA 1 A side Data reg.
            0xff21: self.read_PIA1_A_control, # PIA 1 A side Control reg.
            0xff22: self.read_PIA1_B_data, #    PIA 1 B side Data reg.
            0xff23: self.read_PIA1_B_control, # PIA 1 B side Control reg.
        }
        return read_func_map

    def reset(self):
        self.pia_0_A_register.reset()
        self.pia_0_B_register.reset()
        self.pia_1_A_register.reset()
        self.pia_1_B_register.reset()

    #--------------------------------------------------------------------------

    def key_down(self, value):
        log.critical("Add user key down %r %r to PIA input queue.", repr(value), chr(value))
        col, row = get_dragon_col_row_values(value)
        self.keyboard_col = col #& self.keyboard_col
        self.keyboard_row = row #& self.keyboard_row
        self.keyboard_col_send = False
        self.keyboard_row_send = False
        log.critical("Set col: $%02x - row: $%02x", self.keyboard_col, self.keyboard_row)

    #--------------------------------------------------------------------------

    def read_PIA1_A_data(self, cpu_cycles, op_address, address):
        """ read from 0xff20 -> PIA 1 A side Data reg. """
        log.error("TODO: read from 0xff20 -> PIA 1 A side Data reg.")
        return 0x01

    def read_PIA1_A_control(self, cpu_cycles, op_address, address):
        """ read from 0xff21 -> PIA 1 A side Control reg. """
        log.error("TODO: read from 0xff21 -> PIA 1 A side Control reg.")
        return 0x34

    def read_PIA1_B_data(self, cpu_cycles, op_address, address):
        """ read from 0xff22 -> PIA 1 B side Data reg. """
        log.error("TODO: read from 0xff22 -> PIA 1 B side Data reg.")
        return 0x00

    def read_PIA1_B_control(self, cpu_cycles, op_address, address):
        """ read from 0xff23 -> PIA 1 B side Control reg. """
        log.error("TODO: read from 0xff23 -> PIA 1 B side Control reg.")
        return 0x37

    #--------------------------------------------------------------------------

    def write_PIA1_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff20 -> PIA 1 A side Data reg. """
        log.error("TODO: write $%02x to 0xff20 -> PIA 1 A side Data reg.", value)

    def write_PIA1_A_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff21 -> PIA 1 A side Control reg. """
        log.error("TODO: write $%02x to 0xff21 -> PIA 1 A side Control reg.", value)

    def write_PIA1_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff22 -> PIA 1 B side Data reg. """
        log.error("TODO: write $%02x to 0xff22 -> PIA 1 B side Data reg.", value)

    def write_PIA1_B_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff23 -> PIA 1 B side Control reg. """
        log.error("TODO: write $%02x to 0xff23 -> PIA 1 B side Control reg.", value)

    #--------------------------------------------------------------------------

    def read_serial_interface(self, cpu_cycles, op_address, address):
        log.error("TODO: read from $%04x (D64 serial interface", address)
        return 0x00

    def write_serial_interface(self, cpu_cycles, op_address, address, value):
        log.error("TODO: write $%02x to $%04x (D64 serial interface", value, address)

    #--------------------------------------------------------------------------
    # Keyboard matrix on PIA0

    def read_PIA0_A_data(self, cpu_cycles, op_address, address):
        """
        read from 0xff00 -> PIA 0 A side Data reg.

        bit 7 | PA7 | joystick comparison input
        bit 6 | PA6 | keyboard matrix row 7
        bit 5 | PA5 | keyboard matrix row 6
        bit 4 | PA4 | keyboard matrix row 5
        bit 3 | PA3 | keyboard matrix row 4 & left  joystick switch 2
        bit 2 | PA2 | keyboard matrix row 3 & right joystick switch 2
        bit 1 | PA1 | keyboard matrix row 2 & left  joystick switch 1
        bit 0 | PA0 | keyboard matrix row 1 & right joystick switch 1
        """
        result = 0x00
        log.critical(
            "%04x| read $%04x (PIA 0 A side Data reg.) send $%02x back.\t|%s",
            op_address, address, result, self.cfg.mem_info.get_shortest(op_address)
        )
        return result

    def write_PIA0_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff00 -> PIA 0 A side Data reg. """
        log.critical("%04x| write $%02x to $%04x -> PIA 0 A side Data reg.\t|%s",
            op_address, value, address, self.cfg.mem_info.get_shortest(op_address)
        )

    def read_PIA0_A_control(self, cpu_cycles, op_address, address):
        """
        read from 0xff01 -> PIA 0 A side control register
        """
        result = 0xb3
        log.critical(
            "%04x| read $%04x (PIA 0 A side Control reg.) send $%02x back.\t|%s",
            op_address, address, result, self.cfg.mem_info.get_shortest(op_address)
        )
        return result

    def write_PIA0_A_control(self, cpu_cycles, op_address, address, value):
        """
        write to 0xff01 -> PIA 0 A side control register

        TODO: Handle IRQ

        bit 7 | IRQ 1 (HSYNC) flag
        bit 6 | IRQ 2 flag(not used)
        bit 5 | Control line 2 (CA2) is an output = 1
        bit 4 | Control line 2 (CA2) set by bit 3 = 1
        bit 3 | select line LSB of analog multiplexor (MUX): 0 = control line 2 LO / 1 = control line 2 HI
        bit 2 | set data direction: 0 = $FF00 is DDR / 1 = $FF00 is normal data lines
        bit 1 | control line 1 (CA1): IRQ polarity 0 = IRQ on HI to LO / 1 = IRQ on LO to HI
        bit 0 | HSYNC IRQ: 0 = disabled IRQ / 1 = enabled IRQ
        """
        log.critical(
            "%04x| write $%02x to $%04x -> PIA 0 A side Control reg.\t|%s",
            op_address, value, address, self.cfg.mem_info.get_shortest(op_address)
        )
        if not is_bit_set(value, bit=2):
            self.pia_0_A_register.select_pdr()
        else:
            self.pia_0_A_register.deselect_pdr()

    def read_PIA0_B_data(self, cpu_cycles, op_address, address):
        """
        read from 0xff02 -> PIA 0 B side Data reg.

        bit 7 | PB7 | keyboard matrix column 8
        bit 6 | PB6 | keyboard matrix column 7 / ram size output
        bit 5 | PB5 | keyboard matrix column 6
        bit 4 | PB4 | keyboard matrix column 5
        bit 3 | PB3 | keyboard matrix column 4
        bit 2 | PB2 | keyboard matrix column 3
        bit 1 | PB1 | keyboard matrix column 2
        bit 0 | PB0 | keyboard matrix column 1

        bits 0-7 also printer data lines
        """
        self.keyboard_col_send = True
        result = self.keyboard_col
        #self.keyboard_col = 0xff
        log.critical(
            "%04x| read $%04x (PIA 0 B side Data reg.) send $%02x back.\t|%s",
            op_address, address, result, self.cfg.mem_info.get_shortest(op_address)
        )
        return result

    def write_PIA0_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff02 -> PIA 0 B side Data reg. """
        log.critical(
            "%04x| write $%02x to $%04x -> PIA 0 B side Data reg.\t|%s",
            op_address, value, address, self.cfg.mem_info.get_shortest(op_address)
        )
        if self.keyboard_col_send:
#            self.keyboard_col = value
#            self.keyboard_col &= value
#            self.keyboard_col &= ~value
            self.keyboard_col = ~value & 0xff

    def read_PIA0_B_control(self, cpu_cycles, op_address, address):
        """
        read from 0xff03 -> PIA 0 B side Control reg.
        """
        self.keyboard_row_send = True
        result = self.keyboard_row
        #self.keyboard_row = 0xff
        log.critical(
            "%04x| read $%04x (PIA 0 B side Control reg.) send $%02x back.\t|%s",
            op_address, address, result, self.cfg.mem_info.get_shortest(op_address)
        )
        return result

    def write_PIA0_B_control(self, cpu_cycles, op_address, address, value):
        """
        write to 0xff03 -> PIA 0 B side Control reg.

        TODO: Handle IRQ

        bit 7 | IRQ 1 (VSYNC) flag
        bit 6 | IRQ 2 flag(not used)
        bit 5 | Control line 2 (CB2) is an output = 1
        bit 4 | Control line 2 (CB2) set by bit 3 = 1
        bit 3 | select line MSB of analog multiplexor (MUX): 0 = control line 2 LO / 1 = control line 2 HI
        bit 2 | set data direction: 0 = $FF02 is DDR / 1 = $FF02 is normal data lines
        bit 1 | control line 1 (CB1): IRQ polarity 0 = IRQ on HI to LO / 1 = IRQ on LO to HI
        bit 0 | VSYNC IRQ: 0 = disable IRQ / 1 = enable IRQ
        """
        log.critical(
            "%04x| write $%02x (%s) to $%04x -> PIA 0 B side Control reg.\t|%s",
            op_address, value, byte2bit_string(value), address, self.cfg.mem_info.get_shortest(op_address)
        )

        if not is_bit_set(value, bit=2):
            self.pia_0_B_register.select_pdr()
        else:
            self.pia_0_B_register.deselect_pdr()



def test_run():
    import sys, os, subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "Dragon64_test.py"),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
