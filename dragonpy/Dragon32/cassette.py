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

import wave


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

    def read_byte(self, cpu_cycles):
        if self.start_cycle == 0:
            self.start_cycle = cpu_cycles
        offset = self.start_offset + (cpu_cycles - self.start_cycle) * 22000 / 1000000
        return ord(self.raw[offset]) if offset < len(self.raw) else 0x80
