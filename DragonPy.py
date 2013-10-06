#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    Based on:
        ApplePy - an Apple ][ emulator in Python:
        James Tauber / http://jtauber.com/ / https://github.com/jtauber/applepy
        originally written 2001, updated 2011
        origin source code licensed under MIT License
"""


import numpy
import pygame
import select
import socket
import struct
import subprocess
import sys
import time
import wave
import logging

from configs import Dragon32Cfg

log = logging.getLogger("DragonPy")


class Display(object):

    characters = [
        [0b00000, 0b01110, 0b10001, 0b10101, 0b10111, 0b10110, 0b10000, 0b01111],
        [0b00000, 0b00100, 0b01010, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01111, 0b10000, 0b10000, 0b10000, 0b10011, 0b10001, 0b01111],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11111],
        [0b00000, 0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000],
        [0b00000, 0b11111, 0b00011, 0b00011, 0b00011, 0b00011, 0b00011, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
        [0b00000, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010],
        [0b00000, 0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
        [0b00000, 0b11000, 0b11001, 0b00010, 0b00100, 0b01000, 0b10011, 0b00011],
        [0b00000, 0b01000, 0b10100, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b01000, 0b10000, 0b10000, 0b10000, 0b01000, 0b00100],
        [0b00000, 0b00100, 0b00010, 0b00001, 0b00001, 0b00001, 0b00010, 0b00100],
        [0b00000, 0b00100, 0b10101, 0b01110, 0b00100, 0b01110, 0b10101, 0b00100],
        [0b00000, 0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
        [0b00000, 0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        [0b00000, 0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
        [0b00000, 0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
        [0b00000, 0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00111, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b11100],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
        [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
        [0b00000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b00010, 0b00100, 0b00100, 0b00000, 0b00100]
    ]

    lores_colours = [
        (0, 0, 0), # black
        (208, 0, 48), # magenta / dark red
        (0, 0, 128), # dark blue
        (255, 0, 255), # purple / violet
        (0, 128, 0), # dark green
        (128, 128, 128), # gray 1
        (0, 0, 255), # medium blue / blue
        (96, 160, 255), # light blue
        (128, 80, 0), # brown / dark orange
        (255, 128 , 0), # orange
        (192, 192, 192), # gray 2
        (255, 144, 128), # pink / light red
        (0, 255, 0), # light green / green
        (255, 255, 0), # yellow / light orange
        (64, 255, 144), # aquamarine / light green
        (255, 255, 255), # white
    ]

    def __init__(self):
        self.screen = pygame.display.set_mode((560, 384))
        pygame.display.set_caption("DragonPy")
        self.mix = False
        self.flash_time = time.time()
        self.flash_on = False
        self.flash_chars = [[0] * 0x400] * 2

        self.page = 1
        self.text = True
        self.colour = False

        self.chargen = []
        for c in self.characters:
            chars = [[pygame.Surface((14, 16)), pygame.Surface((14, 16))],
                     [pygame.Surface((14, 16)), pygame.Surface((14, 16))]]
            for colour in (0, 1):
                hue = (255, 255, 255) if colour else (0, 200, 0)
                for inv in (0, 1):
                    pixels = pygame.PixelArray(chars[colour][inv])
                    off = hue if inv else (0, 0, 0)
                    on = (0, 0, 0) if inv else hue
                    for row in range(8):
                        b = c[row] << 1
                        for col in range(7):
                            bit = (b >> (6 - col)) & 1
                            pixels[2 * col][2 * row] = on if bit else off
                            pixels[2 * col + 1][2 * row] = on if bit else off
                    del pixels
            self.chargen.append(chars)

    def txtclr(self):
        self.text = False

    def txtset(self):
        self.text = True
        self.colour = False

    def mixclr(self):
        self.mix = False

    def mixset(self):
        self.mix = True
        self.colour = True

    def lowscr(self):
        self.page = 1

    def hiscr(self):
        self.page = 2

    def lores(self):
        self.high_res = False

    def hires(self):
        self.high_res = True

    def update(self, address, value):
        if self.page == 1:
            start_text = 0x400
            start_hires = 0x2000
        elif self.page == 2:
            start_text = 0x800
            start_hires = 0x4000
        else:
            return

        if start_text <= address <= start_text + 0x3FF:
            base = address - start_text
            self.flash_chars[self.page - 1][base] = value
            hi, lo = divmod(base, 0x80)
            row_group, column = divmod(lo, 0x28)
            row = hi + 8 * row_group

            if row_group == 3:
                return

            if self.text or not self.mix or not row < 20:
                mode, ch = divmod(value, 0x40)

                if mode == 0:
                    inv = True
                elif mode == 1:
                    inv = self.flash_on
                else:
                    inv = False

                self.screen.blit(self.chargen[ch][self.colour][inv], (2 * (column * 7), 2 * (row * 8)))
            else:
                pixels = pygame.PixelArray(self.screen)
                if not self.high_res:
                    lower, upper = divmod(value, 0x10)

                    for dx in range(14):
                        for dy in range(8):
                            x = column * 14 + dx
                            y = row * 16 + dy
                            pixels[x][y] = self.lores_colours[upper]
                        for dy in range(8, 16):
                            x = column * 14 + dx
                            y = row * 16 + dy
                            pixels[x][y] = self.lores_colours[lower]
                del pixels

        elif start_hires <= address <= start_hires + 0x1FFF:
            if self.high_res:
                base = address - start_hires
                row8, b = divmod(base, 0x400)
                hi, lo = divmod(b, 0x80)
                row_group, column = divmod(lo, 0x28)
                row = 8 * (hi + 8 * row_group) + row8

                if self.mix and row >= 160:
                    return

                if row < 192 and column < 40:

                    pixels = pygame.PixelArray(self.screen)
                    msb = value // 0x80

                    for b in range(7):
                        c = value & (1 << b)
                        xx = (column * 7 + b)
                        x = 2 * xx
                        y = 2 * row

                        if msb:
                            if xx % 2:
                                pixels[x][y] = (0, 0, 0)
                                # orange
                                pixels[x][y] = (255, 192, 0) if c else (0, 0, 0) # @@@
                                pixels[x + 1][y] = (255, 192, 0) if c else (0, 0, 0)
                            else:
                                # blue
                                pixels[x][y] = (0, 192, 255) if c else (0, 0, 0)
                                pixels[x + 1][y] = (0, 0, 0)
                                pixels[x + 1][y] = (0, 192, 255) if c else (0, 0, 0) # @@@
                        else:
                            if xx % 2:
                                pixels[x][y] = (0, 0, 0)
                                # green
                                pixels[x][y] = (0, 255, 0) if c else (0, 0, 0) # @@@
                                pixels[x + 1][y] = (0, 255, 0) if c else (0, 0, 0)
                            else:
                                # violet
                                pixels[x][y] = (255, 0, 255) if c else (0, 0, 0)
                                pixels[x + 1][y] = (0, 0, 0)
                                pixels[x + 1][y] = (255, 0, 255) if c else (0, 0, 0) # @@@

                        pixels[x][y + 1] = (0, 0, 0)
                        pixels[x + 1][y + 1] = (0, 0, 0)

                    del pixels

    def flash(self):
        if time.time() - self.flash_time >= 0.5:
            self.flash_on = not self.flash_on
            for offset, char in enumerate(self.flash_chars[self.page - 1]):
                if (char & 0xC0) == 0x40:
                    self.update(0x400 + offset, char)
            self.flash_time = time.time()


class Speaker:

    CPU_CYCLES_PER_SAMPLE = 60
    CHECK_INTERVAL = 1000

    def __init__(self):
        pygame.mixer.pre_init(11025, -16, 1)
        pygame.init()
        self.reset()

    def toggle(self, cycle):
        if self.last_toggle is not None:
            l = (cycle - self.last_toggle) / Speaker.CPU_CYCLES_PER_SAMPLE
            self.buffer.extend([0, 26000] if self.polarity else [0, -2600])
            self.buffer.extend((l - 2) * [16384] if self.polarity else [-16384])
            self.polarity = not self.polarity
        self.last_toggle = cycle

    def reset(self):
        self.last_toggle = None
        self.buffer = []
        self.polarity = False

    def play(self):
        sample_array = numpy.int16(self.buffer)
        sound = pygame.sndarray.make_sound(sample_array)
        sound.play()
        self.reset()

    def update(self, cycle):
        if self.buffer and (cycle - self.last_toggle) > self.CHECK_INTERVAL:
            self.play()


class Cassette:

    def __init__(self, fn):
        wav = wave.open(fn, "r")
        self.raw = wav.readframes(wav.getnframes())
        self.start_cycle = 0
        self.start_offset = 0

        for i, b in enumerate(self.raw):
            if ord(b) > 0xA0:
                self.start_offset = i
                break

    def read_byte(self, cycle):
        if self.start_cycle == 0:
            self.start_cycle = cycle
        offset = self.start_offset + (cycle - self.start_cycle) * 22000 / 1000000
        return ord(self.raw[offset]) if offset < len(self.raw) else 0x80


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

    http://www.6809.org.uk/dragon/hardware.shtml#pia0
    """
    def __init__(self, cfg):
        self.cfg = cfg

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
        log.debug(" PIA call at $%x %s returned $%x" % (address, func.__name__, value))
        return value

    def pia_0_A_data(self):
        log.debug(" *** TODO: PIA 0 A side data register")
        return 0x00 # self.kbd
    def pia_0_A_control(self):
        log.debug(" *** TODO: PIA 0 A side control register")
        return 0xb3
    def pia_0_B_data(self):
        log.debug(" *** TODO: PIA 0 B side data register")
        return 0x00
    def pia_0_B_control(self):
        log.debug(" *** TODO: PIA 0 B side control register")
        return 0x35

    def pia_1_A_data(self):
        log.debug(" *** TODO: PIA 1 A side data register")
        return 0x01
    def pia_1_A_control(self):
        log.debug(" *** TODO: PIA 1 A side control register")
        return 0x34
    def pia_1_B_data(self):
        log.debug(" *** TODO: PIA 1 B side data register")
        return 0x34
    def pia_1_B_control(self):
        log.debug(" *** TODO: PIA 1 B side control register")
        return 0x37


class SoftSwitches(object):

    def __init__(self, cfg, display, speaker, cassette):
        self.cfg = cfg
        self.kbd = 0xBF
        self.display = display
        self.speaker = speaker
        self.cassette = cassette

        self.pia = PIA(cfg)

    def read_byte(self, cycle, address):
        self.cfg.mem_info(address, "SoftSwitches.read_byte (cycle: %s) from" % hex(cycle))

        assert self.cfg.RAM_END <= address <= 0xFFFF, \
            "cycles: %s - address: %s" % (cycle, hex(address))

        if 0xc000 <= address <= 0xfeff:
            # $c000-dfff = DOS ROM area
            # Available address range to cartridge expansion port 32K mode
            log.debug("TODO: cartridge expansion ROM")
            return 0x7E

        if 0xff00 <= address <= 0xff23:
            # read/write to PIA 0 or PIA 1 - MC6821 Peripheral Interface Adaptor
            return self.pia(address)


        if 0xffc0 <= address <= 0xffdf:
            log.debug(" *** TODO: SAM (Synchronous Address Multiplexer) register bits")
            return 0x7E

        if 0xffc0 <= address <= 0xffc5:
            # $ffc0/ffc1    SAM VDG Reg V0
            # $ffc2/ffc3    SAM VDG Reg V1
            # $ffc3/ffc5    SAM VDG Reg V2
            return 0x7E

        if 0xffc6 <= address <= 0xffd3:
            log.debug(" *** TODO: SAM Display offset in 512 byte pages F0-F6")
            return 0x7E

        if 0xffdc <= address <= 0xffdd:
            log.debug(" *** TODO: SAM Memory Size select bit M1")
            return 0x7E

#         if address == 0xC000:
#             return self.kbd
#         elif address == 0xC010:
#             self.kbd = self.kbd & 0x7F
#         elif address == 0xC030:
#             if self.speaker:
#                 self.speaker.toggle(cycle)
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
#                 return self.cassette.read_byte(cycle)
#         else:
#             pass # print "%04X" % address

        msg = "ERROR: no soft switch at $%x (cycle: %s) \t| %s" % (
            address, cycle,
            self.cfg.mem_info.get_shortest(address)
        )
        log.debug(msg)
        raise NotImplementedError(msg)
        return 0x00


class Dragon(object):

    def __init__(self, cfg, display, speaker, cassette):
        self.display = display
        self.speaker = speaker
        self.softswitches = SoftSwitches(cfg, display, speaker, cassette)

        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(0)

        args = [
            sys.executable,
            "cpu6809.py",
            "--bus", str(listener.getsockname()[1]),
            "--rom", cfg.rom,
            "--verbosity=%s" % cfg.verbosity,
        ]
        if cfg.ram:
            args.extend([
                "--ram", cfg.ram,
            ])
        if cfg.pc is not None:
            args.extend([
                "--pc", str(cfg.pc),
            ])
        self.core = subprocess.Popen(args)

        rs, _, _ = select.select([listener], [], [], 2)
        if not rs:
            print >> sys.stderr, "CPU module did not start"
            sys.exit(1)
        self.cpu, _ = listener.accept()

    def run(self):
        update_cycle = 0
        quit = False
        while not quit:
            op = self.cpu.recv(8)
            if len(op) == 0:
                break
            cycle, rw, addr, val = struct.unpack("<IBHB", op)
            if rw == 0:
                self.cpu.send(chr(self.softswitches.read_byte(cycle, addr)))
            elif rw == 1:
                self.display.update(addr, val)
            else:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True

                if event.type == pygame.KEYDOWN:
                    key = ord(event.unicode) if event.unicode else 0
                    if event.key == pygame.K_LEFT:
                        key = 0x08
                    if event.key == pygame.K_RIGHT:
                        key = 0x15
                    if key:
                        if key == 0x7F:
                            key = 0x08
                        self.softswitches.kbd = 0x80 + (key & 0x7F)

            update_cycle += 1
            if update_cycle >= 1024:
                self.display.flash()
                pygame.display.flip()
                if self.speaker:
                    self.speaker.update(cycle)
                update_cycle = 0



if __name__ == "__main__":
    print "Run DragonPy_CLI.py instead"
    sys.exit(0)
