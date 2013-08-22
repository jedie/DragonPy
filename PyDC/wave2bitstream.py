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

        self.half_sinus = False

        # create the generator chain:

        # get frame numer + volume value from the WAVE file
        self.wave_values_generator = self.iter_wave_values()

        # triggered frame numbers of a half sinus cycle
        self.iter_trigger_generator = self.iter_trigger(self.wave_values_generator)

        # duration of a complete sinus cycle
        self.iter_duration_generator = self.iter_duration(self.iter_trigger_generator)

        # build from sinus cycle duration the bit stream
        self.iter_bitstream_generator = self.iter_bitstream(self.iter_duration_generator)

    def sync(self, length):
        """
        synchronized weave sync trigger
        """
        # go in wave stream to the first bit
        first_bit_frame_no, first_bit = self.next()
        print "First bit is at:", first_bit_frame_no

        print "enable half sinus scan"
        self.half_sinus = True

        # Toggle sync test by consuming one half sinus sample
#         self.iter_trigger_generator.next() # Test sync

        # get "half sinus cycle" test data
        test_durations = itertools.islice(self.iter_duration_generator, length)
        # It's a tuple like: [(frame_no, duration)...]

        test_durations = list(test_durations)

        # Create only a duration list:
        test_durations = [i[1] for i in test_durations]
#         test_durations = itertools.imap(lambda x: x[1], test_durations)

        diff1, diff2 = diff_info(test_durations)
        print "sync diff info: %i vs. %i" % (diff1, diff2)

        if diff1 < diff2:
            print "Sync one step."
            self.iter_trigger_generator.next()
        else:
            print "No sync needed."

        self.half_sinus = False
        print "disable half sinus scan"

    def __iter__(self):
        return self

    def next(self):
        return self.iter_bitstream_generator.next()

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
                yield (frame_no, 1)
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif hz > bit_nul_min_hz and hz < bit_nul_max_hz:
#                 print "bit 0"
                bit_count += 1
                yield (frame_no, 0)
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

    def iter_trigger(self, iter_wave_values):
        """
        yield only the triggered frame numbers
        simmilar to a Schmitt trigger
        """
        last_state = False
        for frame_no, value in iter_wave_values:
            if last_state == False and value > self.trigger_value:
#                 print "half:", self.half_sinus
                yield frame_no
                last_state = True
            elif last_state == True and value < -self.trigger_value:
                if self.half_sinus:
#                     print "half sinus!"
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

#     FILENAME = "HelloWorld1 xroar.wav" # 8Bit 22050Hz
    FILENAME = "HelloWorld1 origin.wav" # 109922 frames, 16Bit wave, 44100Hz
#     FILENAME = "LineNumber Test 01.wav" # tokenized BASIC


    st = Wave2Bitstream(FILENAME, LEAD_IN_PATTERN)

    bitstream = iter(st)

    bitstream.sync(16)

    bitstream = itertools.imap(lambda x: x[1], bitstream)
    print_bitlist(bitstream)

    print "-- END --"

"""
open wave file 'HelloWorld1 xroar.wav'...
Framerate: 22050
Number of audio frames: 75025
channels: 1
samplewidth: 1 (8Bit wave file)
Use trigger value: 51.0
First bit is at: 15
enable half sinus scan
sync diff info: 32 vs. 5
No sync needed.
disable half sinus scan
   0 - 10101100 10110100 11010110 01011010 01101010 01101100 10101100 10110100
   8 - 11010110 01011010 01101010 01101100 10101100 10110100 11010110 01011010
  16 - 01101010 01101100 10101100 10110100 11010110 01011010 01101010 01101100
  24 - 10101100 10110100 11010110 01011010 01101010 01101100 10101100 10110100
  32 - 11010110 01011010 01101010 01101100 10101100 10110100 11010110 01011010
  40 - 01101010 01101100 10101100 10110100 11010110 01011010 01101010 01101100
  48 - 10101100 10110100 11010110 01011010 01101010 01101100 10101100 10110100
  56 - 11010110 11011010 01101010 01101100 10101100 10110100 11010110 11011010
  64 - 01101010 01101100 10101100 10110100 11010110 11011010 01101010 01101100
  72 - 10101100 10110100 11010110 11011010 01101010 01101100 10101100 10110100
  80 - 11010110 11011010 01101010 01101100 10101100 10110100 11010110 11011010
  88 - 01101010 01101100 10101100 10110100 11010110 11011010 01101010 01101100
  96 - 10101100 10110100 11010110 11011010 01101010 01101100 10101100 10110100
 104 - 11010110 11011010 01101010 01101100 10101100 10110100 11010110 11011010
 112 - 01101010 01101100 10101100 10110100 11010110 11011010 01011010 01101100
 120 - 10101100 10110100 11010110 11011010 01011010 01101100 10101100 10110100
 128 - 11010110 11011010 01011010 01101100 10101100 10110100 11010110 11011010
 136 - 01011010 01101100 10101100 10110100 11010110 11011010 01011010 01101100
 144 - 10101100 10110100 11010110 11011010 01011010 01101100 10101100 10110100
 152 - 11010110 11011010 01011010 01101100 10101100 10110100 11010110 11011010
 160 - 01011010 01101100 10101100 10110100 11010110 11011010 01011010 01101100
 168 - 10101100 10110100 11010110 11011010 01011010 01101100 10101100 10110100
 176 - 11010110 11011010 01011010 01101010 10101100 10110100 11010110 11011010
 184 - 01011010 01101010 10101100 10110100 11010110 11011010 01011010 01101010
 192 - 10101100 10110100 11010110 11011010 01011010 01101010 10101100 10110100
 200 - 11010110 11011010 01011010 01101010 10101100 10110100 11010110 11011010
 208 - 01011010 01101010 10101100 10110100 11010110 11011010 01011010 01101010
 216 - 10101100 10110100 11010110 11011010 01011010 01101010 10101100 10110100
 224 - 11010110 11011010 01011010 01101010 10101100 10110100 11010110 11011010
 232 - 01011010 01101010 10101100 10110100 11010110 11011010 01011010 01101010
 240 - 10101100 10110100 11010110 11011010 01011010 01101010 10101100 10110100
 248 - 11010110 11011010 01011010 01101010 10101100 10110100 11010110 01101100
 256 - 01111000 00000000 11100000 00000100 00000100 00000100 00001100 00001000
 264 - 00001000 00000100 00000100 00000000 00000000 00000000 00000000 00000000
 272 - 00000000 00000000 11110000 11010110 10110100 10110110 11010110 01011010
 280 - 01101010 10101100 10110100 10110110 11010110 01011010 01101010 10101100
 288 - 10110100 10110110 11010110 01011010 01101010 10101100 10110100 10110110
 296 - 11010110 01011010 01101010 10101100 10110100 10110110 11010110 01011010
 304 - 01101010 10101100 10110100 10110110 11010110 01011010 01101010 10101100
 312 - 10110100 10110110 11010110 01011010 01101010 10101100 10110100 10110110
 320 - 11010110 01011010 01101010 10101100 10110100 10110110 11010110 01011010
 328 - 01101010 10101100 10110100 10110110 11010110 01011010 01101010 10101100
 336 - 10110100 10110110 11010110 01011010 01101010 10101100 10110100 10110110
 344 - 11010110 01011010 01101010 10101100 10110100 10110110 11010110 01011010
 352 - 01101010 10101100 10110100 10110110 11010110 01011010 01101010 10101100
 360 - 10110100 10110110 11010110 01011010 01101010 10101100 10110100 10110110
 368 - 11010110 01011010 01101010 10101100 10110100 10110110 11010110 01011010
 376 - 01101010 01101100 10110100 10110110 11010110 01011010 01101010 01101100
 384 - 10110100 10110110 11010110 01011010 01101010 01101100 10110100 10110110
 392 - 11010110 01011010 01101010 01101100 10110100 10110110 11010110 01011010
 400 - 01101010 01101100 10110100 10110110 11010110 01011010 01101010 01101100
 408 - 10110100 10110110 11010110 01011010 01101010 01101100 10110100 10110110
 416 - 11010110 01011010 01101010 01101100 10110100 10110110 11010110 01011010
 424 - 01101010 01101100 10110100 10110110 11010110 01011010 01101010 01101100
 432 - 10110100 10110110 11010110 01011010 01101010 01101100 10101100 10110110
 440 - 11010110 01011010 01101010 01101100 10101100 10110110 11010110 01011010
 448 - 01101010 01101100 10101100 10110110 11010110 01011010 01101010 01101100
 456 - 10101100 10110110 11010110 01011010 01101010 01101100 10101100 10110110
 464 - 11010110 01011010 01101010 01101100 10101100 10110110 11010110 01011010
 472 - 01101010 01101100 10101100 10110110 11010110 01011010 01101010 01101100
 480 - 10101100 10110110 11010110 01011010 01101010 01101100 10101100 10110110
 488 - 11010110 01011010 01101010 01101100 10101100 10110110 11010110 01011010
 496 - 01101010 01101100 10101100 10110100 11010110 01011010 01101010 01101100
 504 - 10101100 10110100 11010110 01011010 01101010 01101100 10101100 10110100
 512 - 11010110 01011010 01101010 01101100 10101100 10110100 11010110 01011010
 520 - 01101010 01101100 10101100 10110100 11010110 01011010 01101010 01101100
 528 - 10101100 10110100 11010110 01011010 01011010 01111100 00000000 10011100
 536 - 01111000 11001000 00000000 10110000 00000010 00001000 00100110 00001100
 544 - 11010110 00001000 10011100 00000100 00111100 00000100 10001000 00011000
 552 - 00000000 01111000 10011000 00000000 01101000 11000010 00001100 10010010
 560 - 10111100 10001000 00100100 01100010 00100100 01110010 11110010 00000100
 568 - 11011010 11110010 01010100 01110010 00100100 00001000 10001000 00000000
 576 - 01111000 10001000 00000000 01111000 11100010 00001000 00100110 00000000
 584 - 00000000 00000000 11110100 11010110 11011010 00111100 11111110 00000000

4752 Bits: 2401 positive bits and 2351 negative bits

Bit 1: 1470-2205Hz avg: 1487.6Hz variation: 735Hz
Bit 0: 689-1378Hz avg: 1332.3Hz variation: 689Hz
"""
