#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License
"""

import logging
try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

from dragonpy.Dragon32.display import Display
from dragonpy.Dragon32.MC6883_SAM import SAM
from dragonpy.Dragon32.MC6821_PIA import PIA
from dragonpy.components.periphery import PeripheryBase

log = logging.getLogger("DragonPy.perophery.dragon")



class Dragon32Periphery(PeripheryBase):

    def __init__(self, cfg):
        super(Dragon32Periphery, self).__init__(cfg)

        self.kbd = 0xBF
        self.display = Display()
        self.speaker = None # Speaker()
        self.cassette = None # Cassette()

        self.sam = SAM(cfg)
        self.pia = PIA(cfg)

        self.address2func_map = {
            0xfffe: self.reset_vector,
        }

    def read_byte(self, cpu_cycles, op_address, address):
        self.cfg.mem_info(address, "Periphery.read_byte (cpu_cycles: %s) from" % hex(cpu_cycles))
        assert self.cfg.RAM_END <= address <= 0xFFFF, \
            "cycles: %s - address: %s" % (cpu_cycles, hex(address))

        if address == 0xfffe:
            raise NotImplementedError("$fffe:ffff    RESET     ($b3b4; D64 64K mode $c000 - never accessed)")

        if 0xc000 <= address <= 0xfeff:
            # $c000-dfff = DOS ROM area
            # Available address range to cartridge expansion port 32K mode
            log.debug("TODO: cartridge expansion ROM")
            return 0x7E

        if 0xff00 <= address <= 0xff23:
            # read/write to PIA 0 or PIA 1 - MC6821 Peripheral Interface Adaptor
            return self.pia(address)

        if 0xffc0 <= address <= 0xffdf:
            # read/write to SAM (Synchronous Address Multiplexer)
            return self.sam(address)


#         if 0xffc0 <= address <= 0xffdf:
#             log.debug(" *** TODO: SAM (Synchronous Address Multiplexer) register bits")
#             return 0x7E

#         if 0xffc0 <= address <= 0xffc5:
#             # $ffc0/ffc1    SAM VDG Reg V0
#             # $ffc2/ffc3    SAM VDG Reg V1
#             # $ffc3/ffc5    SAM VDG Reg V2
#             return 0x7E

#         if 0xffc6 <= address <= 0xffd3:
#             log.debug(" *** TODO: SAM Display offset in 512 byte pages F0-F6")
#             return 0x7E

#         if 0xffdc <= address <= 0xffdd:
#             log.debug(" *** TODO: SAM Memory Size select bit M1")
#             return 0x7E

#         if address == 0xC000:
#             return self.kbd
#         elif address == 0xC010:
#             self.kbd = self.kbd & 0x7F
#         elif address == 0xC030:
#             if self.speaker:
#                 self.speaker.toggle(cpu_cycles)
#         elif address == 0xC050:
#             self.display.txtclr()
#         elif address == 0xC051:
#             self.display.txtset()
#         elif address == 0xC052:
#             self.display.mixclr()
#         elif address == 0xC053:
#             self.display.mixset()
#         elif address == 0xC054:
#             self.display.lowscr()
#         elif address == 0xC055:
#             self.display.hiscr()
#         elif address == 0xC056:
#             self.display.lores()
#         elif address == 0xC057:
#             self.display.hires()
#         elif address == 0xC060:
#             if self.cassette:
#                 return self.cassette.read_byte(cpu_cycles)
#         else:
#             pass # print "%04X" % address

        msg = "ERROR: no periphery handler at $%x (cpu_cycles: %s) \t| %s" % (
            address, cpu_cycles,
            self.cfg.mem_info.get_shortest(address)
        )
        log.error(msg)
#         raise NotImplementedError(msg)
        return 0x00

    def read_word(self, cpu_cycles, op_address, address):
        log.debug(
            "Periphery.read_word from $%x (cpu_cycles: %i)" % (
            address, cpu_cycles
        ))
        try:
            func = self.address2func_map[address]
        except KeyError, err:
            log.debug("TODO: $%x" % address)
        else:
            return func(address)

        raise NotImplementedError(
            "TODO: Periphery.read_word from $%x (cpu_cycles: %i)" % (
            address, cpu_cycles
        ))

    def write_byte(self, cpu_cycles, op_address, address, value):
        log.debug(" *** write to periphery at $%x the value $%x" % (address, value))
        if 0xff00 <= address <= 0xff23:
            # read/write to PIA 0 or PIA 1 - MC6821 Peripheral Interface Adaptor
            return self.pia.write_byte(address, value)

        if 0xffc0 <= address <= 0xffdf:
            # read/write to SAM (Synchronous Address Multiplexer)
            return self.sam.write_byte(address, value)

        msg = "ERROR: no periphery handler at $%x (cpu_cycles: %s) \t| %s" % (
            address, cpu_cycles,
            self.cfg.mem_info.get_shortest(address)
        )
        log.debug(msg)
#         raise NotImplementedError(msg)
        return 0x00

    write_word = write_byte # TODO: implement

    def update(self, cpu_cycles):
        super(Dragon32Periphery, self).update(cpu_cycles)
        self.display.flash()
        pygame.display.flip()
        if self.speaker:
            self.speaker.update(cpu_cycles)

    def cycle(self, cpu_cycles, op_address):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log.critical("pygame.QUIT: shutdown")
                self.exit()
                return False # Quit

            if event.type == pygame.KEYDOWN:
                key = ord(event.unicode) if event.unicode else 0
                if event.key == pygame.K_LEFT:
                    key = 0x08
                if event.key == pygame.K_RIGHT:
                    key = 0x15
                if key:
                    if key == 0x7F:
                        key = 0x08
                    self.periphery.kbd = 0x80 + (key & 0x7F)

        return super(Dragon32Periphery, self).cycle(cpu_cycles, op_address)

    def reset_vector(self, address):
        ea = 0xb3b4
        log.info("%x| %x        [RESET]" % (address, ea))
        return ea # FIXME: RESET interrupt service routine ???


def test_run():
    import sys, subprocess
    cmd_args = [sys.executable,
        "DragonPy_CLI.py",
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
        "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
#         "--verbosity=50", # CRITICAL/FATAL
#
#         '--log_formatter=%(filename)s %(funcName)s %(lineno)d %(message)s',
#
#         "--area_debug_active=5:bb79-ffff",
#         "--area_debug_cycles=1587101",
#
        "--cfg=Dragon32",
#
        "--display_cycle", # print CPU cycle/sec while running.
#         "--compare_trace=2", # PC differ
#
#         "--max=15000",
#         "--max=46041",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
