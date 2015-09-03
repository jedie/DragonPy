#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#pia0
    http://www.onastick.clara.net/sys4.htm

    http://mamedev.org/source/src/emu/machine/6821pia.c.html
    http://mamedev.org/source/src/emu/machine/6821pia.h.html

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

from __future__ import absolute_import, division, print_function

import os

try:
    import queue # Python 3
except ImportError:
    import Queue as queue # Python 2

import logging

log=logging.getLogger(__name__)
from dragonpy.core.configs import COCO2B
from dragonpy.utils.bits import is_bit_set, invert_byte, clear_bit, set_bit
from dragonpy.utils.humanize import byte2bit_string


class PIA_register(object):

    def __init__(self, name):
        self.name = name
        self.reset()
        self.value = 0x00

    def reset(self):
        self._pdr_selected = False  # pdr = Peripheral Data Register
        self.control_register = 0x00
        self.direction_register = 0x00
        self.output_register = 0x00
        self.interrupt_received = 0x00
        self.irq = 0x00

    def set(self, value):
        log.debug("\t set %s to $%02x %s", self.name, value, '{0:08b}'.format(value))
        self.value = value

    def get(self):
        return self.value

    def is_pdr_selected(self):
        return self._pdr_selected

    def select_pdr(self):
        log.error("\t Select 'Peripheral Data Register' in %s", self.name)
        self._pdr_selected = True

    def deselect_pdr(self):
        log.error("\t Deselect 'Peripheral Data Register' in %s", self.name)
        self._pdr_selected = False


class PIA(object):
    """
    PIA - MC6821 - Peripheral Interface Adaptor

    PIA 0 - Keyboard, Joystick
    PIA 1 - Printer, Cassette, 6-Bit DAC, Sound Mux

    $ff00 PIA 0 A side Data register        PA7
    $ff01 PIA 0 A side Control register     CA1
    $ff02 PIA 0 B side Data register        PB7
    $ff03 PIA 0 B side Control register     CB1

    $ff04 D64 - ACIA serial port read/write data register
    $ff05 D64 - ACIA serial port status (R)/ reset (W) register
    $ff06 D64 - ACIA serial port command register
    $ff07 D64 - ACIA serial port control register

    $ff20 PIA 1 A side Data register         PA7
    $ff21 PIA 1 A side Control register      CA1
    $ff22 PIA 1 B side Data register         PB7
    $ff23 PIA 1 B side Control register      CB1
    """
    def __init__(self, cfg, cpu, memory, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory
        self.user_input_queue = user_input_queue

        self.pia_0_A_register = PIA_register("PIA0 A")
        self.pia_0_B_data = PIA_register("PIA0 B data register $ff02")
        self.pia_0_B_control = PIA_register("PIA0 B control register $ff03")

        self.pia_1_A_register = PIA_register("PIA1 A")
        self.pia_1_B_register = PIA_register("PIA1 B")

        self.internal_reset()

        #
        # TODO: Collect this information via a decorator similar to op codes in CPU!
        #
        # Register memory read/write Byte callbacks:
        # PIA 0 A side Data reg.
        self.memory.add_read_byte_callback(self.read_PIA0_A_data, 0xff00)
        self.memory.add_write_byte_callback(self.write_PIA0_A_data, 0xff00)
        # PIA 0 A side Control reg.
        self.memory.add_read_byte_callback(self.read_PIA0_A_control, 0xff01)
        self.memory.add_write_byte_callback(self.write_PIA0_A_control, 0xff01)
        # PIA 0 B side Data reg.
        self.memory.add_read_byte_callback(self.read_PIA0_B_data, 0xff02)
        self.memory.add_write_byte_callback(self.write_PIA0_B_data, 0xff02)
        # PIA 0 B side Control reg.
        self.memory.add_read_byte_callback(self.read_PIA0_B_control, 0xff03)
        self.memory.add_write_byte_callback(self.write_PIA0_B_control, 0xff03)

        # PIA 1 A side Data reg.
        self.memory.add_read_byte_callback(self.read_PIA1_A_data, 0xff20)
        self.memory.add_write_byte_callback(self.write_PIA1_A_data, 0xff20)
        # PIA 1 A side Control reg.
        self.memory.add_read_byte_callback(self.read_PIA1_A_control, 0xff21)
        self.memory.add_write_byte_callback(self.write_PIA1_A_control, 0xff21)
        # PIA 1 B side Data reg.
        self.memory.add_read_byte_callback(self.read_PIA1_B_data, 0xff22)
        self.memory.add_write_byte_callback(self.write_PIA1_B_data, 0xff22)
        # PIA 1 B side Control reg.
        self.memory.add_read_byte_callback(self.read_PIA1_B_control, 0xff23)
        self.memory.add_write_byte_callback(self.write_PIA1_B_control, 0xff23)

        # Only Dragon 64:
        self.memory.add_read_byte_callback(self.read_serial_interface, 0xff04)
        self.memory.add_write_word_callback(
            self.write_serial_interface, 0xff06)

    def reset(self):
        log.critical("PIA reset()")
        self.pia_0_A_register.reset()
        self.pia_0_B_data.reset()
        self.pia_0_B_control.reset()
        self.pia_1_A_register.reset()
        self.pia_1_B_register.reset()

    def internal_reset(self):
        """
        internal state reset.
        used e.g. in unittests
        """
        log.critical("PIA internal_reset()")
        self.empty_key_toggle = True
        self.current_input_char = None
        self.input_repead = 0

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
        log.debug("TODO: read from 0xff22 -> PIA 1 B side Data reg.")
        return 0x00

    def read_PIA1_B_control(self, cpu_cycles, op_address, address):
        """ read from 0xff23 -> PIA 1 B side Control reg. """
        log.error("TODO: read from 0xff23 -> PIA 1 B side Control reg.")
        return 0x37

    #--------------------------------------------------------------------------

    def write_PIA1_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff20 -> PIA 1 A side Data reg. """
        log.error(
            "TODO: write $%02x to 0xff20 -> PIA 1 A side Data reg.", value)

    def write_PIA1_A_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff21 -> PIA 1 A side Control reg. """
        log.error(
            "TODO: write $%02x to 0xff21 -> PIA 1 A side Control reg.", value)

    def write_PIA1_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff22 -> PIA 1 B side Data reg. """
        log.debug(
            "TODO: write $%02x to 0xff22 -> PIA 1 B side Data reg.", value
        )

    def write_PIA1_B_control(self, cpu_cycles, op_address, address, value):
        """ write to 0xff23 -> PIA 1 B side Control reg. """
        log.error(
            "TODO: write $%02x to 0xff23 -> PIA 1 B side Control reg.", value)

    #--------------------------------------------------------------------------

    def read_serial_interface(self, cpu_cycles, op_address, address):
        log.error("TODO: read from $%04x (D64 serial interface", address)
        return 0x00

    def write_serial_interface(self, cpu_cycles, op_address, address, value):
        log.error(
            "TODO: write $%02x to $%04x (D64 serial interface", value, address)

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
        pia0b = self.pia_0_B_data.value  # $ff02

        # FIXME: Find a way to handle CoCo and Dragon in the same way!
        if self.cfg.CONFIG_NAME == COCO2B:
#            log.critical("\t count: %i", self.input_repead)
            if self.input_repead == 7:
                try:
                    self.current_input_char = self.user_input_queue.get_nowait()
                except queue.Empty:
                    self.current_input_char = None
                else:
                    log.critical(
                        "\tget new key from queue: %s", repr(self.current_input_char))
            elif self.input_repead == 18:
#                log.critical("\tForce send 'no key pressed'")
                self.current_input_char = None
            elif self.input_repead > 20:
                self.input_repead = 0

            self.input_repead += 1
        else:  # Dragon
            if pia0b == self.cfg.PIA0B_KEYBOARD_START:  # FIXME
                if self.empty_key_toggle:
                    # Work-a-round for "poor" dragon keyboard scan routine:
                    # The scan routine in ROM ignores key pressed directly behind
                    # one another if they are in the same row!
                    # See "Inside the Dragon" book, page 203 ;)
                    #
                    # Here with the empty_key_toggle, we always send a "no key pressed"
                    # after every key press back and then we send the next key from
                    # the self.user_input_queue
                    #
                    # TODO: We can check the row of the previous key press and only
                    # force a 'no key pressed' if the row is the same
                    self.empty_key_toggle = False
                    self.current_input_char = None
#                     log.critical("\tForce send 'no key pressed'")
                else:
                    try:
                        self.current_input_char = self.user_input_queue.get_nowait()
                    except queue.Empty:
#                        log.critical("\tinput_queue is empty"))
                        self.current_input_char = None
                    else:
#                        log.critical("\tget new key from queue: %s", repr(self.current_input_char))
                        self.empty_key_toggle = True

        if self.current_input_char is None:
#            log.critical("\tno key pressed")
            result = 0xff
            self.empty_key_toggle = False
        else:
#            log.critical("\tsend %s", repr(self.current_input_char))
            result = self.cfg.pia_keymatrix_result(
                self.current_input_char, pia0b)

#         if not is_bit_set(pia0b, bit=7):
# bit 7 | PA7 | joystick comparison input
#             result = clear_bit(result, bit=7)

#         if self.current_input_char is not None:
#             log.critical(
#                 "%04x| read $%04x ($ff02 is $%02x %s) send $%02x %s back\t|%s",
#                 op_address, address,
#                 pia0b, '{0:08b}'.format(pia0b),
#                 result, '{0:08b}'.format(result),
#                 self.cfg.mem_info.get_shortest(op_address)
#             )
        return result

    def write_PIA0_A_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff00 -> PIA 0 A side Data reg. """
        log.error("%04x| write $%02x (%s) to $%04x -> PIA 0 A side Data reg.\t|%s",
            op_address, value, byte2bit_string(value), address,
            self.cfg.mem_info.get_shortest(op_address)
        )
        self.pia_0_A_register.set(value)

    def read_PIA0_A_control(self, cpu_cycles, op_address, address):
        """
        read from 0xff01 -> PIA 0 A side control register
        """
        value = 0xb3
        log.error(
            "%04x| read $%04x (PIA 0 A side Control reg.) send $%02x (%s) back.\t|%s",
            op_address, address, value, byte2bit_string(value),
            self.cfg.mem_info.get_shortest(op_address)
        )
        return value

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
        log.error(
            "%04x| write $%02x (%s) to $%04x -> PIA 0 A side Control reg.\t|%s",
            op_address, value, byte2bit_string(value), address,
            self.cfg.mem_info.get_shortest(op_address)
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
        value = self.pia_0_B_data.value  # $ff02
        log.debug(
            "%04x| read $%04x (PIA 0 B side Data reg.) send $%02x (%s) back.\t|%s",
            op_address, address, value, byte2bit_string(value),
            self.cfg.mem_info.get_shortest(op_address)
        )
        return value

    def write_PIA0_B_data(self, cpu_cycles, op_address, address, value):
        """ write to 0xff02 -> PIA 0 B side Data reg. """
        log.debug(
#        log.info(
            "%04x| write $%02x (%s) to $%04x -> PIA 0 B side Data reg.\t|%s",
            op_address, value, byte2bit_string(value),
            address, self.cfg.mem_info.get_shortest(op_address)
        )
        self.pia_0_B_data.set(value)

    def read_PIA0_B_control(self, cpu_cycles, op_address, address):
        """
        read from 0xff03 -> PIA 0 B side Control reg.
        """
        value = self.pia_0_B_control.value
        log.error(
            "%04x| read $%04x (PIA 0 B side Control reg.) send $%02x (%s) back.\t|%s",
            op_address, address, value, byte2bit_string(value),
            self.cfg.mem_info.get_shortest(op_address)
        )
        return value

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
            op_address, value, byte2bit_string(value),
            address, self.cfg.mem_info.get_shortest(op_address)
        )

        if is_bit_set(value, bit=0):
            log.critical(
                "%04x| write $%02x (%s) to $%04x -> VSYNC IRQ: enable\t|%s",
                op_address, value, byte2bit_string(value),
                address, self.cfg.mem_info.get_shortest(op_address)
            )
            self.cpu.irq_enabled = True
            value = set_bit(value, bit=7)
        else:
            log.critical(
                "%04x| write $%02x (%s) to $%04x -> VSYNC IRQ: disable\t|%s",
                op_address, value, byte2bit_string(value),
                address, self.cfg.mem_info.get_shortest(op_address)
            )
            self.cpu.irq_enabled = False

        if not is_bit_set(value, bit=2):
            self.pia_0_B_control.select_pdr()
        else:
            self.pia_0_B_control.deselect_pdr()

        self.pia_0_B_control.set(value)

#------------------------------------------------------------------------------


