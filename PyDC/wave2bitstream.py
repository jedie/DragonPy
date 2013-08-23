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
import logging

# own modules
from utils import average, diff_info, print_bitlist, TextLevelMeter, iter_window, \
    human_duration, ProcessInfo
import struct
import time


log = logging.getLogger("PyDC")

LOG_FORMATTER = logging.Formatter("") # %(asctime)s %(message)s")
LOG_LEVEL_DICT = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


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

    def __init__(self, wave_filename,
            bit_nul_hz, # sinus cycle frequency in Hz for one "0" bit
            bit_one_hz, # sinus cycle frequency in Hz for one "1" bit
            hz_variation, # How much Hz can signal scatter to match 1 or 0 bit ?
            min_volume_ratio=1, # Ignore sample frames if lower volume
            mid_volume_ratio=5,
            hysteresis_ratio=0.1
        ):
        self.wave_filename = wave_filename

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
        self.max_value = self.MAX_VALUES[self.samplewidth]
        print "the max volume value is:", self.max_value

        self.min_volume = int(round(self.max_value * min_volume_ratio / 100))
        print "Ignore sample lower than %.f%% = %i" % (min_volume_ratio, self.min_volume)

        self.trigger_value = int(round(self.max_value * mid_volume_ratio / 100))
        print "Use trigger value: %.f%% = %i" % (mid_volume_ratio, self.trigger_value)

#         hysteresis_shift = self.trigger_value * hysteresis_ratio
#         print "Hysteresis shift:", hysteresis_shift
#
#         self.hysteresis_min = self.trigger_value - hysteresis_shift
#         assert self.hysteresis_min > 0, "hysteresis ratio to big! (min: %s)" % self.hysteresis_min
#
#         self.hysteresis_max = self.trigger_value + hysteresis_shift
#         assert self.hysteresis_max < self.max_value, "hysteresis ratio to big! (max: %s)" % self.hysteresis_max
#
#         print "hysteresis trigger valume: %i - %i" % (self.hysteresis_min, self.hysteresis_max)


        # build min/max Hz values
        self.bit_nul_min_hz = bit_nul_hz - hz_variation
        self.bit_nul_max_hz = bit_nul_hz + hz_variation

        self.bit_one_min_hz = bit_one_hz - hz_variation
        self.bit_one_max_hz = bit_one_hz + hz_variation
        print "bit-0 in %sHz - %sHz  |  bit-1 in %sHz - %sHz" % (
            self.bit_nul_min_hz, self.bit_nul_max_hz,
            self.bit_one_min_hz, self.bit_one_max_hz,
        )
        assert self.bit_nul_max_hz < self.bit_one_min_hz, "hz variation %sHz to big!" % (
            ((self.bit_nul_max_hz - self.bit_one_min_hz) / 2) + 1
        )

        self.half_sinus = False # in trigger yield the full cycle


        # create the generator chain:

        # get frame numer + volume value from the WAVE file
        self.wave_values_generator = self.iter_wave_values()

        # triggered frame numbers of a half sinus cycle
        self.iter_trigger_generator = self.iter_trigger(self.wave_values_generator)
#         self.iter_trigger_generator = self.iter_simple_trigger(self.wave_values_generator)

        # duration of a complete sinus cycle
        self.iter_duration_generator = self.iter_duration(self.iter_trigger_generator)

        self.auto_sync_duration_generator = self.auto_sync_duration(self.iter_duration_generator)

        # build from sinus cycle duration the bit stream
        self.iter_bitstream_generator = self.iter_bitstream(self.auto_sync_duration_generator)

    def sync(self, length):
        """
        synchronized weave sync trigger
        """
        return
        # go in wave stream to the first bit
        try:
            first_bit_frame_no, first_bit = self.next()
        except StopIteration:
            print "Error: no bits identified!"
            sys.exit(-1)
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

        if diff1 > diff2:
            print "Sync one step."
            self.iter_trigger_generator.next()
            print "Synced."
        else:
            print "No sync needed."

        self.half_sinus = False
        print "disable half sinus scan"

    def __iter__(self):
        return self

    def next(self):
        return self.iter_bitstream_generator.next()

    def iter_bitstream(self, iter_duration_generator):
        """
        iterate over self.iter_trigger() and
        yield the bits
        """
        assert self.half_sinus == False # Allways trigger full sinus cycle

        process_info = ProcessInfo(self.frame_count, use_last_rates=4)
        start_time = time.time()
        next_status = start_time + 0.25

        def _print_status(frame_no, bit_count):
            ms = float(frame_no) / self.framerate
            rest, eta, rate = process_info.update(frame_no)
            sys.stdout.write(
                "\r%i frames (wav pos:%s) get %iBits - eta: %s (rate: %iFrames/sec)   " % (
                    frame_no, human_duration(ms), bit_count, eta, rate
                )
            )

        one_hz_count = 0
        one_hz_min = sys.maxint
        one_hz_avg = None
        one_hz_max = 0
        nul_hz_count = 0
        nul_hz_min = sys.maxint
        nul_hz_avg = None
        nul_hz_max = 0

        bit_count = 0

        for frame_no, duration in iter_duration_generator:
#             if frame_no > 500:
#                 sys.exit()

            hz = self.framerate / duration
            if hz > self.bit_one_min_hz and hz < self.bit_one_max_hz:
                log.debug(
                    "bit 1 at %s in %sSamples = %sHz" % (frame_no, duration, hz)
                )
                bit_count += 1
                yield (frame_no, 1)
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif hz > self.bit_nul_min_hz and hz < self.bit_nul_max_hz:
                log.debug(
                    "bit 0 at %s in %sSamples = %sHz" % (frame_no, duration, hz)
                )
                bit_count += 1
                yield (frame_no, 0)
                nul_hz_count += 1
                if hz < nul_hz_min:
                    nul_hz_min = hz
                if hz > nul_hz_max:
                    nul_hz_max = hz
                nul_hz_avg = average(nul_hz_avg, hz, nul_hz_count)
            else:
                log.debug(
                    "Skip signal at %s with %sSamples = %sHz" % (frame_no, duration, hz)
                )
                continue

            if time.time() > next_status:
                next_status = time.time() + 1
                _print_status(frame_no, bit_count)

        _print_status(frame_no, bit_count)
        print

        print
        print "%i Bits: %i positive bits and %i negative bits" % (
            bit_count, one_hz_count, nul_hz_count
        )
        print
        if bit_count > 0:
            print "Bit 0: %sHz - %sHz avg: %.1fHz variation: %sHz" % (
                nul_hz_min, nul_hz_max, nul_hz_avg, nul_hz_max - nul_hz_min
            )
            print "Bit 1: %sHz - %sHz avg: %.1fHz variation: %sHz" % (
                one_hz_min, one_hz_max, one_hz_avg, one_hz_max - one_hz_min
            )


    def auto_sync_duration(self, iter_duration):
        """
        yield the duration of two frames in a row.
        """
        for previous, current, next_value in itertools.islice(iter_window(iter_duration, window_size=3), 1, None, 2):
            diff1 = abs(previous[1] - current[1])
            diff2 = abs(current[1] - next_value[1])

            if diff1 < diff2:
                log.debug("EVEN")
                yield (current[0], previous[1] + current[1])
            else:
                log.debug("ODD")
                yield (current[0], current[1] + next_value[1])


#         old_frame = next(iter_duration)
#         print "old frame:", old_frame
#         count = 0
#         while True:
#             count += 1
#             if count > 40:sys.exit()
#             durations = itertools.islice(iter_duration, 3)
#             print list(durations)
#             diff += abs(no1 - no2)
#
#         old_frame_no = next(iter_trigger)
#         for frame_no in iter_trigger:
#             duration = frame_no - old_frame_no
#             yield (frame_no, duration)
#             old_frame_no = frame_no

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
        last_state = True
        for frame_no, value in iter_wave_values:
            if last_state == False and value > self.trigger_value:
                log.debug(" ==== go into positive sinus cycle ===============")
                yield frame_no
                last_state = True
            elif last_state == True and value < -self.trigger_value:
                log.debug(" ---- go into netative sinus cycle ---------------")
#                 if self.half_sinus:
                log.debug(" -**- yield half sinus -**-------------------------")
                yield frame_no
                last_state = False
#
#     def iter_trigger(self, iter_wave_values):
#         """
#         yield only the triggered frame numbers
#         simmilar to a Schmitt trigger
#         """
#         phase = 1
#         for frame_no, value in iter_wave_values:
# #             print "frame no: %s, phase: %s, volume: %s" % (frame_no, phase, value)
# #             if frame_no > 100:
# #                 sys.exit()
#             if phase == 1 and value > self.hysteresis_max:
#                 log.debug(" ==== go into positive sinus cycle ===============")
#                 yield frame_no
#                 phase = 2
#             elif phase == 2 and value < self.hysteresis_min:
#                 log.debug(" ---- leave positive sinus cycle -----------------")
#                 phase = 3
#             elif phase == 3 and value < -self.hysteresis_max:
#                 log.debug(" ---- go into netative sinus cycle ---------------")
#                 if self.half_sinus:
#                     log.debug(" -**- yield half sinus -**-------------------------")
#                     yield frame_no
#                 phase = 4
#             elif phase == 4 and value > -self.hysteresis_min:
#                 log.debug(" ---- leave netative sinus cycle -----------------")
#                 phase = 1

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

        tlm = TextLevelMeter(self.max_value, 79)

        frame_no = 0
        get_wave_block_func = functools.partial(self.wavefile.readframes, self.WAVE_READ_SIZE)
        skipped_values = 0
        for frames in iter(get_wave_block_func, ""):
            for value in array.array(typecode, frames):

                if abs(value) < self.min_volume:
                    # Ignore to lower amplitude
                    skipped_values += 1
                    continue
                elif skipped_values > 0:
                    log.debug(" *** Have %i samples skipped, because to lower amplitude." % skipped_values)
                    skipped_values = 0

                msg = tlm.feed(value)
                log.debug(
                    "%s value: %i (%.1f%%)" % (msg, value, abs(self.max_value / value))
                )

                frame_no += 1
                yield frame_no, value

#     def iter_wave_valuesOLD(self):
#         if self.samplewidth == 1:
#             struct_unpack_str = "<b"
#         elif self.samplewidth == 2:
#             struct_unpack_str = "<h"
#         else:
#             raise NotImplementedError("Only sample width 2 or 1 are supported, yet!")
#         print "struct_unpack_str:", struct_unpack_str
#
#         tlm = TextLevelMeter(self.max_value, 79)
#
#         frame_no = 0
#         while True:
#             frames = self.wavefile.readframes(8096)
#             if not frames:
#                 break
#
#             for frame in frames:
#                 frame_no += 1
#                 if frame_no > 1000: break
#                 value = struct.unpack(struct_unpack_str, frame)[0]
#                 value = -value
#                 msg = tlm.feed(value)
#                 log.debug("%s value: %i" % (msg, value))
#                 yield frame_no, value


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

    log_level = LOG_LEVEL_DICT[3] # args.verbosity
    log.setLevel(log_level)

    logfilename = FILENAME + ".log" # args.logfile
    if logfilename:
        handler = logging.FileHandler(logfilename,
    #         mode='a',
            mode='w',
            encoding="utf8"
        )
        handler.setFormatter(LOG_FORMATTER)
        log.addHandler(handler)

    # if args.stdout_log:
    # handler = logging.StreamHandler()
    # handler.setFormatter(LOG_FORMATTER)
    # log.addHandler(handler)

    st = Wave2Bitstream(FILENAME,
        bit_nul_hz=1200, # "0" is a single cycle at 1200 Hz
        bit_one_hz=2400, # "1" is a single cycle at 2400 Hz
        hz_variation=450, # How much Hz can signal scatter to match 1 or 0 bit ?
#         min_volume_ratio=0.01, # Ignore sample frames if lower volume
#         mid_volume_ratio=0.2, hysteresis_ratio=0.1
    )

    bitstream = iter(st)
    bitstream.sync(16)

    bitstream = itertools.imap(lambda x: x[1], bitstream)
    bit_list = array.array('B', bitstream)

    print "-"*79
    print_bitlist(bit_list)
    print "-"*79


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
