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

try:
    import pygame
except ImportError:
    # Maybe Dragon would not be emulated ;)
    pygame = None

try:
    import numpy
except ImportError:
    numpy = None


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
