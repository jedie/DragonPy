#!/usr/bin/env python2
# coding: utf-8

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
import wave
import functools
import array
import itertools

# own modules
from utils import average, diff_info, print_bitlist


BIT_ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
BIT_NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz
MAX_HZ_VARIATION = 1000 # How much Hz can signal scatter to match 1 or 0 bit ?

LEAD_IN_PATTERN = "10101010" # 0x55



class Wave2Bitstream(object):

    WAVE_READ_SIZE = 16 * 1024 # How many frames should be read from WAVE file at once?
    WAV_ARRAY_TYPECODE = {
        1: "b", #  8-bit wave file
        2: "h", # 16-bit wave file
        4: "l", # 32-bit wave file TODO: Test it
    }

    # Maximum volume value in wave files:
    MAX_VALUES = {
        1: 255, #  8-bit wave file
        2: 32768, # 16-bit wave file
        4: 2147483647, # 32-bit wave file
    }

    def __init__(self, wave_filename, lead_in_pattern, mid_volume_ratio=0.2, hysteresis_ratio=0.9):
        self.wave_filename = wave_filename
        self.lead_in_pattern = lead_in_pattern
        self.mid_volume_ratio = mid_volume_ratio
        self.hysteresis_ratio = hysteresis_ratio


        print "open wave file '%s'..." % wave_filename
        self.wavefile = wave.open(wave_filename, "rb")

        self.framerate = self.wavefile.getframerate() # frames / second
        print "Framerate:", self.framerate

        self.frame_count = self.wavefile.getnframes()
        print "Number of audio frames:", self.frame_count

        self.nchannels = self.wavefile.getnchannels() # typically 1 for mono, 2 for stereo
        print "channels:", self.nchannels
        assert self.nchannels == 1, "Only MONO files are supported, yet!"

        self.samplewidth = self.wavefile.getsampwidth() # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples
        print "samplewidth: %i (%sBit wave file)" % (self.samplewidth, self.samplewidth * 8)

        # build hysteresis min/max values:
        self.trigger_value = self.MAX_VALUES[self.samplewidth] * self.mid_volume_ratio
        print "Use trigger value:", self.trigger_value

        # get frame numer + volume value from the WAVE file
        self.wave_values = self.iter_wave_values()

    def sync(self, length):
        """
        synchronized weave sync trigger
        """
        iter_trigger = self.iter_trigger(self.wave_values, half_sinus=True)

        # duration of half sinus cycles
        iter_duration = self.iter_duration(iter_trigger)

        test_data = itertools.islice(iter_duration, length)
        test_durations = [i[1] for i in test_data]

        diff1, diff2 = diff_info(test_durations)

        if diff1 < diff2:
            print "Sync one step."
            self.wave_values.next() # FIXME
        else:
            print "No sync needed."

    def __iter__(self):
        # triggered frame numbers of a half sinus cycle
        iter_trigger = self.iter_trigger(self.wave_values, half_sinus=False)

        # duration of a complete sinus cycle
        iter_duration = self.iter_duration(iter_trigger)

        # build from sinus cycle duration the bit stream
        iter_bitstream = self.iter_bitstream(iter_duration)

        return iter_bitstream


    def iter_bitstream(self, iter_func):
        """
        iterate over self.iter_trigger() and
        yield the bits
        """
        bit_one_min_hz = BIT_ONE_HZ - MAX_HZ_VARIATION
        bit_one_max_hz = BIT_ONE_HZ + MAX_HZ_VARIATION

        bit_nul_min_hz = BIT_NUL_HZ - MAX_HZ_VARIATION
        bit_nul_max_hz = BIT_NUL_HZ + MAX_HZ_VARIATION

        one_hz_count = 0
        one_hz_min = sys.maxint
        one_hz_avg = None
        one_hz_max = 0
        nul_hz_count = 0
        nul_hz_min = sys.maxint
        nul_hz_avg = None
        nul_hz_max = 0

        bit_count = 0

        for frame_no, duration in iter_func:
            hz = self.framerate / duration
#             print "%sHz" % hz

            if hz > bit_one_min_hz and hz < bit_one_max_hz:
#                 print "bit 1"
                bit_count += 1
                yield 1
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif hz > bit_nul_min_hz and hz < bit_nul_max_hz:
#                 print "bit 0"
                bit_count += 1
                yield 0
                nul_hz_count += 1
                if hz < nul_hz_min:
                    nul_hz_min = hz
                if hz > nul_hz_max:
                    nul_hz_max = hz
                nul_hz_avg = average(nul_hz_avg, hz, nul_hz_count)
            else:
                print "Skip signal with %sHz." % hz
                continue

        print
        print "%i Bits: %i positive bits and %i negative bits" % (
            bit_count, one_hz_count, nul_hz_count
        )
        print
        print "Bit 1: %s-%sHz avg: %.1fHz variation: %sHz" % (
            one_hz_min, one_hz_max, one_hz_avg, one_hz_max - one_hz_min
        )
        print "Bit 0: %s-%sHz avg: %.1fHz variation: %sHz" % (
            nul_hz_min, nul_hz_max, nul_hz_avg, nul_hz_max - nul_hz_min
        )


    def iter_duration(self, iter_trigger):
        """
        yield the duration of two frames in a row.
        """
        old_frame_no = next(iter_trigger)
        for frame_no in iter_trigger:
            duration = frame_no - old_frame_no
            yield (frame_no, duration)
            old_frame_no = frame_no

    def iter_trigger(self, iter_wave_values, half_sinus):
        """
        yield only the triggered frame numbers
        simmilar to a Schmitt trigger
        """
        last_state = False
        for frame_no, value in iter_wave_values:
            if last_state == False and value > self.trigger_value:
                yield frame_no
                last_state = True
            elif last_state == True and value < -self.trigger_value:
                if half_sinus:
                    yield frame_no
                last_state = False

    def iter_wave_values(self):
        """
        yield frame numer + volume value from the WAVE file
        """
        try:
            typecode = self.WAV_ARRAY_TYPECODE[self.samplewidth]
        except KeyError:
            raise NotImplementedError(
                "Only %s wave files are supported, yet!" % (
                    ", ".join(["%sBit" % (i * 8) for i in self.WAV_ARRAY_TYPECODE.keys()])
                )
            )

        frame_no = 0
        get_wave_block_func = functools.partial(self.wavefile.readframes, self.WAVE_READ_SIZE)
        for frames in iter(get_wave_block_func, ""):
            for value in array.array(typecode, frames):
                frame_no += 1
                yield frame_no, value


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
#     sys.exit()

    # BASIC file with high line numbers:
    FILENAME = "LineNumber Test 01.wav" # tokenized BASIC

    st = Wave2Bitstream(FILENAME, LEAD_IN_PATTERN)

    st.sync(16)

    print_bitlist(st)

#     for no, i in enumerate(st):
        # print no, i
#         print i,
#         if no > 10:
#             print "-- BREAK --"
#             break

    print "-- END --"

"""
132096 frames (wav pos:3.0 sec) eta: 0.0 ms (rate: 67678Frames/sec)
3099 bits decoded from 132096 audio samples in 1.7 sec (0.2KBytes/s)

Bit 1: 1696-2100Hz avg: 2017.9Hz variation: 404Hz
Bit 0: 432-1191Hz avg: 1088.6Hz variation: 759Hz
3099 Bits: 1374 positive bits and 1725 negative bits
   0 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
   8 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  16 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  24 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  32 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  40 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  48 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  56 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  64 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  72 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  80 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  88 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
  96 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 104 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 112 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 120 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 128 - 10101000 11110000 00000011 11000000 11001010 01001001 11001010 10001001
 136 - 11001011 11001000 00110010 00110000 00000000 00000000 00000000 00000000
 144 - 00000000 00000000 00000010 10110010 10101010 10101010 10101010 10101010
 152 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 160 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 168 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 176 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 184 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 192 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 200 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 208 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 216 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 224 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 232 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 240 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 248 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 256 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 264 - 10101010 10101010 10101010 10101010 10101010 10101010 10101010 10101010
 272 - 10101010 10101010 10101010 10101010 10101010 10100011 11001000 00001100
 280 - 01100111 10000101 10000000 00001000 00001110 00010000 01000100 01000011
 288 - 00101001 00100111 00101010 00100000 01000111 00101010 10101011 00100100
 296 - 00101010 00100100 10100000 01000010 10101010 00101100 10100010 10100100
 304 - 01000000 00000111 10001100 01000000 00000101 00001110 00010000 01001000
 312 - 11000000 11000000 00000111 10001011 01000000 00000010 01101110 00010000
 320 - 01001000 11000000 11000000 11000000 00000111 10000001 11001100 00000001
 328 - 01111110 00010000 01001000 11000000 11000000 11000000 11000000 00000111
 336 - 10000010 00101110 01000000 10001110 00010000 01001000 11000000 11000000
 344 - 11000000 11000000 11000000 00000111 10000000 10100000 00010000 00001110
 352 - 00010000 01001100 11000100 11001110 11000110 11000001 11000000 00000111
 360 - 10000100 01101001 11111111 11111110 00010000 01000100 01001010 00100111
 368 - 00100010 00100100 01001101 11000110 11001100 11001001 11001001 11001001
 376 - 11000000 00000000 00000000 00001010 11001010 10101010 10100011 11001111
"""
