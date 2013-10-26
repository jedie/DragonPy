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
        self.address2func_map = {
            0xfffe: self.reset_vector,
        }

    def read_byte(self, cpu_cycles, op_address, address):
        log.debug(
            "%04x| Periphery.read_byte from $%x (cpu_cycles: %i)" % (
            op_address, address, cpu_cycles
        ))
        if 0xe000 <= address <= 0xe1ff:
            return self.read_rs232_interface(cpu_cycles, op_address, address)

        try:
            func = self.address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
            return func(address)

        raise NotImplementedError

    read_word = read_byte

    def write_byte(self, cpu_cycles, op_address, address, value):
        if 0xe000 <= address <= 0xe1ff:
            return self.write_rs232_interface(cpu_cycles, op_address, address, value)

        msg = "%04x| TODO: write byte $%x to $%x" % (op_address, value, address)
        log.error(msg)
        raise NotImplementedError(msg)
    write_word = write_byte

    def cycle(self, cpu_cycles, op_address):
        log.debug("TODO: SBC09Periphery.cycle")


    def read_rs232_interface(self, cpu_cycles, op_address, address):
        raise NotImplementedError

    def write_rs232_interface(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError

    def reset_vector(self, address):
        return 0xe400


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

    def event_return(self, event):
        log.critical("ENTER: add \\n")
        self.line_buffer.append("\n")

    def from_console_break(self, event):
        log.critical("BREAK: add 0x03")
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

    def read_rs232_interface(self, cpu_cycles, op_address, address):
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
        log.debug(
#         log.error(
            "%04x| (%i) read from RS232 address: $%x",
            op_address, cpu_cycles, address,
        )

        if address == 0xe000:
            return 0xff
#             if self.line_buffer:
#                 # There is text to send via virtual serial
#                 value = 0xff
#             else:
#                 # No chars to send.
#                 value = 0x02 # XXX
#
#             log.error("read 0xe000, send $%x", value)
#             return value

        if self.line_buffer:
            char = self.line_buffer.pop(0)
            value = ord(char)
            log.error("%04x| (%i) read from RS232 address: $%x, send back %r $%x",
                op_address, cpu_cycles, address, char, value
            )
            return value

        return 0x0

    STATE = 0
    LAST_INPUT = ""
    def write_rs232_interface(self, cpu_cycles, op_address, address, value):
        log.error("%04x| (%i) write to RS232 address: $%x value: $%x (dez.: %i) ASCII: %r" % (
            op_address, cpu_cycles, address, value, value, chr(value)
        ))
        if address == 0xe000:
            value = 0xff
            log.error("write 0xe000, send $%x", value)
            return value

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
        log.error("*"*79)
        log.error("Write to screen: %s ($%x)" % (repr(char), value))
        log.error("*"*79)

        # write some simple BASIC test code:
        self.LAST_INPUT += char
        if self.STATE == 0 and self.LAST_INPUT.endswith("1.0\r\n"):
            self.STATE += 1
            self.line_buffer = list('R\r\n')
            self.LAST_INPUT = ""
        elif self.STATE == 1 and "\x94" in self.LAST_INPUT:
            sys.exit()
#         elif self.STATE == 1 and self.LAST_INPUT.endswith("OK\n"):
# #             sys.exit()
#             self.line_buffer = list('PRINT 123\n')
#             self.STATE += 1
#         elif self.STATE == 2 and self.LAST_INPUT.endswith("OK\n"):
#             self.line_buffer = list('10 PRINT 123\nLIST\n')
#             self.STATE += 1
#         elif self.STATE == 3 and self.LAST_INPUT.endswith("OK\n"):
#             self.line_buffer = list('RUN\n')
#             self.STATE += 1
#         elif self.STATE == 4 and self.LAST_INPUT.endswith("OK\n"):
#             self.line_buffer = list('FOR I=1 to 3:PRINT I:NEXT I\n')
#             self.STATE += 1

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
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
        "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL

#         "--area_debug_cycles=5805",

        "--cfg=SBC09Cfg",
#         "--max=500000",
#         "--max=30000",
#         "--max=20000",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
