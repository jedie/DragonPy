#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
import Tkinter
import os

log = logging.getLogger("DragonPy.Periphery")


class SBC09PeripheryBase(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.read_address2func_map = None
        self.write_address2func_map = None

    def read_byte(self, cpu_cycles, op_address, address):
#        log.debug(
#            "%04x| Periphery.read_byte from $%x (cpu_cycles: %i)",
#            op_address, address, cpu_cycles
#        )
        try:
            func = self.read_address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
#            log.debug("func: %s", func.__name__)
            byte = func(cpu_cycles, op_address, address)
#            log.debug("\tsend byte $%x back" % byte)
            return byte
    read_word = read_byte

    def write_byte(self, cpu_cycles, op_address, address, value):
#        log.debug(
#            "%04x| Periphery.write_byte $%x to $%x (cpu_cycles: %i)",
#            op_address, value, address, cpu_cycles
#        )
        try:
            func = self.write_address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
#            log.debug("func: %s", func.__name__)
            func(cpu_cycles, op_address, address, value)

    write_word = write_byte

    def cycle(self, cpu_cycles, op_address):
        log.debug("TODO: SBC09Periphery.cycle")



class SBC09PeripheryTk(SBC09PeripheryBase):
    def __init__(self, cfg):
        super(SBC09PeripheryTk, self).__init__(cfg)
        self.root = Tkinter.Tk()
        self.root.title("DragonPy - Buggy machine language monitor and rudimentary O.S. version 1.0")
#         self.root.geometry() # '640x480+500+300') # X*Y + x/y-offset
        self.root.geometry("+500+300") # Chnage inital position

        # http://www.tutorialspoint.com/python/tk_text.htm
        self.text = Tkinter.Text(
            self.root,
            height=20, width=80,
            state=Tkinter.DISABLED # FIXME: make textbox "read-only"
        )
        scollbar = Tkinter.Scrollbar(self.root)
        scollbar.config(command=self.text.yview)

        self.text.config(
            background="#08ff08", # nearly green
            foreground="#004100", # nearly black
            font=('courier', 11, 'bold'),
            yscrollcommand=scollbar.set,
        )

        scollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.text.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

        self.root.bind("<Return>", self.event_return)
        self.root.bind("<Escape>", self.from_console_break)
        self.root.bind('<Control-c>', self.copy_to_clipboard)
        self.root.bind("<Key>", self.event_key_pressed)

        self.root.update()

        self.line_buffer = []
        self.read_address2func_map = {
            0xe000: self.read_acia_status, # Control/status port of ACIA
            0xe001: self.read_acia_data, # Data port of ACIA
            0xfffe: self.reset_vector,
        }
        self.write_address2func_map = {
            0xe000: self.write_acia_status, # Control/status port of ACIA
            0xe001: self.write_acia_data, # Data port of ACIA
        }

    def reset_vector(self, cpu_cycles, op_address, address):
        return 0xe400

    def event_return(self, event):
#        log.critical("ENTER: add \\n")
        self.line_buffer.append("\n")

    def from_console_break(self, event):
#        log.critical("BREAK: add 0x03")
        # dc61 81 03              LA3C2     CMPA #3             BREAK KEY?
        self.line_buffer.append("\x03")

    def copy_to_clipboard(self, event):
        log.critical("Copy to clipboard")
        text = self.text.get("1.0", Tkinter.END)
        print text
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def event_key_pressed(self, event):
        log.critical("keycode %s", repr(event.keycode))
        char = event.char
        log.error("char %s", repr(char))
        if char:
            char = char.upper()
            log.error("Send %s", repr(char))
            self.line_buffer.append(char)

    def cycle(self, cpu_cycles, op_address):
        self.root.update()

    def read_acia_status(self, cpu_cycles, op_address, address):
#         return 0xff
        return 0x03
        if self.line_buffer:
            # There is text to send via virtual serial
            value = 0xff
        else:
            # No chars to send.
            value = 0x03 # XXX

#        log.error("read from ACIA status, send $%x", value)
        return value

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        value = 0xff
#        log.error("FIXME: write to ACIA status (send $%x back)", value)
        return value

    def read_acia_data(self, cpu_cycles, op_address, address):
        """
                                *
                                * THIS ROUTINE GETS A KEYSTROKE FROM THE KEYBOARD IF A KEY
                                * IS DOWN. IT RETURNS ZERO TRUE IF THERE WAS NO KEY DOWN.
                                *
                                *
                                LA1C1
        db05 b6 a0 00           KEYIN     LDA  a000(USTAT)
        db08 85 01                        BITA #1
        db0a 27 06                        BEQ  NOCHAR
        db0c b6 a0 01                     LDA  a001(RECEV)
        db0f 84 7f                        ANDA #$7F
        db11 39                           RTS
        db12 4f                 NOCHAR    CLRA
        db13 39                           RTS
        """
#        log.debug(
#         log.error(
#            "%04x| (%i) read from RS232 address: $%x",
#            op_address, cpu_cycles, address,
#        )
        if self.line_buffer:
            char = self.line_buffer.pop(0)
            value = ord(char)
#            log.error("%04x| (%i) read from ACIA-data, send back %r $%x",
#                op_address, cpu_cycles, char, value
#            )
            return value

        return 0x0

    STATE = 0
    LAST_INPUT = ""
    def write_acia_data(self, cpu_cycles, op_address, address, value):
#        log.error("%04x| (%i) write to ACIA-data value: $%x (dez.: %i) ASCII: %r" % (
#            op_address, cpu_cycles, value, value, chr(value)
#        ))
        """
        * ASCII control characters.
        SOH             equ 1
        EOT             equ 4
        ACK             equ 6
        BS              equ 8
        TAB             equ 9
        LF              equ 10
        CR              equ 13
        NAK             equ 21
        CAN             equ 24
        DEL             equ 127

        $01   1  SOH (Start of heading)
        $04   4  EOT (End of transmission)
        $06   6  ACK (Acknowledge)
        $08   8  BS  (Backspace)
        $09   9  HT  (Horizontal Tab)
        $0a  10  LF  (LineFeed)
        $0d  13  CR  (Carriage Return)
        $15  21  NAK (No Acknowledge)
        $18  24  CAN (Cancel)
        """
#         if value == 0xd: # == \n
#             log.error("ignore insert \\n")
#             return
        if value == 0x8: # Backspace
            self.text.config(state=Tkinter.NORMAL)
            # delete last character
            self.text.delete("%s - 1 chars" % Tkinter.INSERT, Tkinter.INSERT)
            self.text.config(state=Tkinter.DISABLED) # FIXME: make textbox "read-only"
            return

        char = chr(value)
#        log.error("*"*79)
#        log.error("Write to screen: %s ($%x)" , repr(char), value)
#        log.error("*"*79)

        if value >= 0x90: # FIXME: Why?
            value -= 0x60
            char = chr(value)
#            log.error("convert value -= 0x30 to %s ($%x)" , repr(char), value)

        if value <= 9: # FIXME: Why?
            value += 0x41
            char = chr(value)
#            log.error("convert value += 0x41 to %s ($%x)" , repr(char), value)

        """
        $ python create_trace.py
        Welcome to BUGGY version 1.0
        r
        X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00
        P=0400 NEG   $00
        r
        X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00
        P=0400 NEG   $00
        ss
        S11300007EE45A7EE4717EE4807EE4E47EE4F57E60
        S1130010E4657EED447EED677EED8C7EEDCF7EED76
        S1130020AC7EE5180C660000000000000000000033
        S113003000000000000000000000000000000000BC
        S113004000000000000000000000000000000000AC
        S1130050000000000000000000000000000000009C
        S1130060000000000000000000000000000000008C
        S1130070000000000000000000000000000000007C
        S1130080000000000000000000000000000000006C
        S1130090000000000000000000000000000000005C
        S11300A0000000000000000000000000000000004C
        S11300B0000000000000000000000000000000003C
        S11300C0000000000000000000000000000000002C
        S11300D0000000000000000000000000000000001C
        S11300E0000000000000000000000000000000000C
        S11300F000000000000000000000000000000000FC
        S9030000FC
        x
        Unknown command
        """

#         self.LAST_INPUT += char
#         if self.STATE == 0 and self.LAST_INPUT.endswith("1.0\r\n"):
#             self.STATE += 1
#             self.line_buffer = list('r\n')
#             self.LAST_INPUT = ""
#         elif self.STATE == 1 and self.LAST_INPUT.endswith("$00\r\n"):
#             self.STATE += 1
#             self.line_buffer = list('r\n')
#             self.LAST_INPUT = ""
#         elif self.STATE == 2 and self.LAST_INPUT.endswith("$00\r\n"):
#             self.STATE += 1
#             self.line_buffer = list('ss\n')
#             self.LAST_INPUT = ""

#         self.LAST_INPUT += char
#         if self.STATE == 0 and self.LAST_INPUT.endswith("1.0\r\n"):
#             print self.LAST_INPUT
#             self.STATE += 1
#             self.line_buffer = list('ss\n')
#             self.LAST_INPUT = ""
#         elif self.STATE == 1 and self.LAST_INPUT.endswith("447"):
#             print self.LAST_INPUT
#             sys.exit()

        #~ self.LAST_INPUT += char
        #~ if self.STATE == 0 and self.LAST_INPUT.endswith("1.0\r\n"):
            #~ print self.LAST_INPUT
            #~ self.STATE += 1

            # SSaddr,len    Dump memory region as Motorola S records.
            #~ self.line_buffer = list('ss\n')

            # Daddr,len     Dump memory region
            #~ self.line_buffer = list('DE5E2\n')

            # Iaddr     Display the contents of the given address.
            #~ self.line_buffer = list('IE001\n') # e.g.: Show the ACIA status

            # Uaddr,len     Diassemble memory region
            #~ self.line_buffer = list('UE400\n')

            # Calculate simple expression in hex with + and -
            #~ self.line_buffer = list('H4444+A5\n')
            #~ self.LAST_INPUT = ""

        self.text.config(state=Tkinter.NORMAL)
        self.text.insert("end", char)
        self.text.see("end")
        self.text.config(state=Tkinter.DISABLED) # FIXME: make textbox "read-only"



# SBC09Periphery = SBC09PeripherySerial
SBC09Periphery = SBC09PeripheryTk


def test_run():
    import subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
        "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL

#         "--area_debug_cycles=6355",
#         "--area_debug_cycles=20241",
#         "--area_debug_cycles=44983",

        "--cfg=SBC09Cfg",
#         "--max=500000",
#         "--max=30000",
#         "--max=20000",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
