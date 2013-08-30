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
import struct
import time
import math


try:
    import audioop
except ImportError, err:
    # e.g. PyPy, see: http://bugs.pypy.org/msg4430
    print "Can't use audioop:", err
    audioop = None


# own modules
from utils import average, diff_info, TextLevelMeter, iter_window, \
    human_duration, ProcessInfo, pformat_frame_no, \
    count_sign, iter_steps, sinus_values_by_hz


log = logging.getLogger("PyDC")


WAVE_READ_SIZE = 16 * 1024 # How many frames should be read from WAVE file at once?
WAV_ARRAY_TYPECODE = {
    1: "b", #  8-bit wave file
    2: "h", # 16-bit wave file
    4: "l", # 32-bit wave file TODO: Test it
}

# Maximum volume value in wave files:
MAX_VALUES = {
    1: 255, # 8-bit wave file
    2: 32768, # 16-bit wave file
    4: 2147483647, # 32-bit wave file
}
HUMAN_SAMPLEWIDTH = {
    1: "8-bit",
    2: "16-bit",
    4: "32-bit",
}


class WaveBase(object):
    def get_typecode(self, samplewidth):
        try:
            typecode = WAV_ARRAY_TYPECODE[samplewidth]
        except KeyError:
            raise NotImplementedError(
                "Only %s wave files are supported, yet!" % (
                    ", ".join(["%sBit" % (i * 8) for i in WAV_ARRAY_TYPECODE.keys()])
                )
            )
        return typecode


class Wave2Bitstream(WaveBase):

    def __init__(self, wave_filename, cfg):
        self.wave_filename = wave_filename
        self.cfg = cfg

        self.half_sinus = False # in trigger yield the full cycle
        self.wave_pos = 0 # Absolute position in the frame stream

        assert cfg.END_COUNT > 0 # Sample count that must be pos/neg at once
        assert cfg.MID_COUNT > 0 # Sample count that can be around null

        print "open wave file '%s'..." % wave_filename
        try:
            self.wavefile = wave.open(wave_filename, "rb")
        except IOError, err:
            log.error("Error opening %s: %s" % (repr(wave_filename), err))
            sys.exit(-1)

        self.framerate = self.wavefile.getframerate() # frames / second
        print "Framerate:", self.framerate

        self.frame_count = self.wavefile.getnframes()
        print "Number of audio frames:", self.frame_count

        self.nchannels = self.wavefile.getnchannels() # typically 1 for mono, 2 for stereo
        print "channels:", self.nchannels
        assert self.nchannels == 1, "Only MONO files are supported, yet!"

        self.samplewidth = self.wavefile.getsampwidth() # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples
        print "samplewidth: %i (%sBit wave file)" % (self.samplewidth, self.samplewidth * 8)

        self.max_value = MAX_VALUES[self.samplewidth]
        print "the max volume value is:", self.max_value

        self.min_volume = int(round(self.max_value * cfg.MIN_VOLUME_RATIO / 100))
        print "Ignore sample lower than %.1f%% = %i" % (cfg.MIN_VOLUME_RATIO, self.min_volume)

        # build min/max Hz values
        self.bit_nul_min_hz = cfg.BIT_NUL_HZ - cfg.HZ_VARIATION
        self.bit_nul_max_hz = cfg.BIT_NUL_HZ + cfg.HZ_VARIATION

        self.bit_one_min_hz = cfg.BIT_ONE_HZ - cfg.HZ_VARIATION
        self.bit_one_max_hz = cfg.BIT_ONE_HZ + cfg.HZ_VARIATION
        print "bit-0 in %sHz - %sHz  |  bit-1 in %sHz - %sHz" % (
            self.bit_nul_min_hz, self.bit_nul_max_hz,
            self.bit_one_min_hz, self.bit_one_max_hz,
        )
        assert self.bit_nul_max_hz < self.bit_one_min_hz, "hz variation %sHz to big!" % (
            ((self.bit_nul_max_hz - self.bit_one_min_hz) / 2) + 1
        )

        self.half_sinus = False # in trigger yield the full cycle
        self.frame_no = None

        # create the generator chain:

        # get frame numer + volume value from the WAVE file
        self.wave_values_generator = self.iter_wave_values()

        if cfg.AVG_COUNT > 1:
            # merge samples to a average sample
            log.debug("Merge %s audio sample to one average sample" % self.avg_count)
            self.avg_wave_values_generator = self.iter_avg_wave_values(self.wave_values_generator)
            # trigger sinus cycle
            self.iter_trigger_generator = self.iter_trigger(self.avg_wave_values_generator)
        else:
            # trigger sinus cycle
            self.iter_trigger_generator = self.iter_trigger(self.wave_values_generator)

        # duration of a complete sinus cycle
        self.iter_duration_generator = self.iter_duration(self.iter_trigger_generator)

#         self.auto_sync_duration_generator = self.auto_sync_duration(self.iter_duration_generator)

        # build from sinus cycle duration the bit stream
        self.iter_bitstream_generator = self.iter_bitstream(self.iter_duration_generator)

    def sync(self, length):
        """
        synchronized weave sync trigger
        """

        # go in wave stream to the first bit
        try:
            self.next()
        except StopIteration:
            print "Error: no bits identified!"
            sys.exit(-1)

        log.info("First bit is at: %s" % pformat_frame_no(self.wave_pos, self.framerate))
        log.debug("enable half sinus scan")
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
        log.debug("sync diff info: %i vs. %i" % (diff1, diff2))

        if diff1 > diff2:
            log.info("\nbit-sync one step.")
            self.iter_trigger_generator.next()
            log.debug("Synced.")
        else:
            log.info("\nNo bit-sync needed.")

        self.half_sinus = False
        log.debug("disable half sinus scan")

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
            print "%i frames (wav pos:%s) get %iBits - eta: %s (rate: %iFrames/sec)" % (
                frame_no, human_duration(ms), bit_count, eta, rate
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

        frame_no = False
        for frame_no, duration in iter_duration_generator:
#             if frame_no > 500:
#                 sys.exit()

            hz = self.framerate / duration
            if hz > self.bit_one_min_hz and hz < self.bit_one_max_hz:
                log.log(5,
                    "bit 1 at %s in %sSamples = %sHz" % (frame_no, duration, hz)
                )
                bit_count += 1
                yield 1
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif hz > self.bit_nul_min_hz and hz < self.bit_nul_max_hz:
                log.log(5,
                    "bit 0 at %s in %sSamples = %sHz" % (frame_no, duration, hz)
                )
                bit_count += 1
                yield 0
                nul_hz_count += 1
                if hz < nul_hz_min:
                    nul_hz_min = hz
                if hz > nul_hz_max:
                    nul_hz_max = hz
                nul_hz_avg = average(nul_hz_avg, hz, nul_hz_count)
            else:
                log.log(5,
                    "Skip signal at %s with %sSamples = %sHz" % (frame_no, duration, hz)
                )
                continue

            if time.time() > next_status:
                next_status = time.time() + 1
                _print_status(frame_no, bit_count)

        if frame_no == False:
            print "ERROR: No information from wave to generate the bits"
            print "trigger volume to high?"
            sys.exit(-1)

        _print_status(frame_no, bit_count)
        print

        log.info("\n%i Bits: %i positive bits and %i negative bits" % (
            bit_count, one_hz_count, nul_hz_count
        ))
        if bit_count > 0:
            log.info("Bit 0: %sHz - %sHz avg: %.1fHz variation: %sHz" % (
                nul_hz_min, nul_hz_max, nul_hz_avg, nul_hz_max - nul_hz_min
            ))
            log.info("Bit 1: %sHz - %sHz avg: %.1fHz variation: %sHz" % (
                one_hz_min, one_hz_max, one_hz_avg, one_hz_max - one_hz_min
            ))

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
        trigger middle crossing of the wave sinus curve
        """
        window_size = (2 * self.cfg.END_COUNT) + self.cfg.MID_COUNT

        # sinus curve goes from negative into positive:
        pos_null_transit = [(0, self.cfg.END_COUNT), (self.cfg.END_COUNT, 0)]

        # sinus curve goes from positive into negative:
        neg_null_transit = [(self.cfg.END_COUNT, 0), (0, self.cfg.END_COUNT)]

        if self.cfg.MID_COUNT > 3:
            mid_index = int(round(self.cfg.MID_COUNT / 2.0))
        else:
            mid_index = 0

        in_pos = False
        for values in iter_window(iter_wave_values, window_size):

            # Split the window
            previous_values = values[:self.cfg.END_COUNT] # e.g.: 123-----
            mid_values = values[self.cfg.END_COUNT:self.cfg.END_COUNT + self.cfg.MID_COUNT] # e.g.: ---45---
            next_values = values[-self.cfg.END_COUNT:] # e.g.: -----678

            # get only the value and strip the frame_no
            # e.g.: (frame_no, value) tuple -> value list
            previous_values = [i[1] for i in previous_values]
            next_values = [i[1] for i in next_values]

            # Count sign from previous and next values
            sign_info = [
                count_sign(previous_values, 0),
                count_sign(next_values, 0)
            ]
            # yield the mid crossing
            if in_pos == False and sign_info == pos_null_transit:
                log.log(5,"sinus curve goes from negative into positive")
#                 log.debug(" %s | %s | %s" % (previous_values, mid_values, next_values))
                yield mid_values[mid_index][0]
                in_pos = True
            elif  in_pos == True and sign_info == neg_null_transit:
                if self.half_sinus:
                    log.log(5,"sinus curve goes from positive into negative")
#                     log.debug(" %s | %s | %s" % (previous_values, mid_values, next_values))
                    yield mid_values[mid_index][0]
                in_pos = False

    def iter_avg_wave_values(self, wave_values_generator):
        if self.avg_count == 3:
            mid_index = 1
        elif self.avg_count > 3:
            mid_index = int(round(self.avg_count / 2.0))
        else:
            mid_index = 0
        assert mid_index < self.avg_count

        for value_tuples in iter_steps(wave_values_generator, self.avg_count):
            # (frame_no, value) tuple -> value list
            values = sum([i[1] for i in value_tuples]) / self.avg_count
            try:
                frame_no = value_tuples[mid_index][0]
            except IndexError, err:
                print "\nError getting %i from; %s: %s" % (mid_index, repr(value_tuples), err)
                frame_no = value_tuples[0][0]
            result = (frame_no, values)
            if log.level >= 5:
                log.log(5, "average %s samples to: %s" % (repr(value_tuples), repr(result)))
#             print "average %s samples to: %s" % (repr(value_tuples), repr(result))
            yield result

    def iter_wave_values(self):
        """
        yield frame numer + volume value from the WAVE file
        """
        typecode = self.get_typecode(self.samplewidth)

        tlm = TextLevelMeter(self.max_value, 79)

        # Use only a read size which is a quare divider of the samplewidth
        # Otherwise array.array will raise: ValueError: string length not a multiple of item size
        divider = int(round(float(WAVE_READ_SIZE) / self.samplewidth))
        read_size = self.samplewidth * divider
        if read_size != WAVE_READ_SIZE:
            log.info("Real use wave read size: %i Bytes" % read_size)

        self.frame_no = 0
        get_wave_block_func = functools.partial(self.wavefile.readframes, read_size)
        skip_count = 0

        manually_audioop_bias = self.samplewidth == 1 and audioop is None

        for frames in iter(get_wave_block_func, ""):

            if self.samplewidth == 1:
                if audioop is None:
                    log.warning("use audioop.bias() work-a-round for missing audioop.")
                else:
                    # 8 bit samples are unsigned, see:
                    # http://docs.python.org/2/library/audioop.html#audioop.lin2lin
                    frames = audioop.bias(frames, 1, 128)

            try:
                values = array.array(typecode, frames)
            except ValueError, err:
                # e.g.:
                #     ValueError: string length not a multiple of item size
                # Work-a-round: Skip the last frames of this block
                frame_count = len(frames)
                divider = int(math.floor(float(frame_count) / self.samplewidth))
                new_count = self.samplewidth * divider
                frames = frames[:new_count] # skip frames
                log.error(
                    "Can't make array from %s frames: Value error: %s (Skip %i and use %i frames)" % (
                        frame_count, err, frame_count - new_count, len(frames)
                ))
                values = array.array(typecode, frames)

            for value in values:
                self.wave_pos += 1 # Absolute position in the frame stream

                if manually_audioop_bias:
                    # audioop.bias can't be used.
                    # See: http://hg.python.org/cpython/file/482590320549/Modules/audioop.c#l957
                    value = value % 0xff - 128

                if abs(value) < self.min_volume:
                    # Ignore to lower amplitude
                    skip_count += 1
                    continue

                if log.level >= 5:
                    msg = tlm.feed(value)
                    percent = 100.0 / self.max_value * abs(value)
                    log.log(5,
                        "%s value: %i (%.1f%%)" % (msg, value, percent)
                    )

                yield self.wave_pos, value

        log.info("Skip %i samples that are lower than %i" % (
            skip_count, self.min_volume
        ))
        log.info("Last readed Frame is: %s" % pformat_frame_no(self.wave_pos, self.framerate))


class Bitstream2Wave(WaveBase):
    def __init__(self, bitstream, cfg):
        self.bitstream = bitstream
        self.cfg = cfg

        wave_max_value = MAX_VALUES[self.cfg.SAMPLEWIDTH]
        self.used_max_values = int(round(
            float(wave_max_value) / 100 * self.cfg.VOLUME_RATIO
        ))
        log.info("Create %s wave file with %sHz and %s max volumen (%s%%)" % (
            HUMAN_SAMPLEWIDTH[self.cfg.SAMPLEWIDTH],
            self.cfg.FRAMERATE,
            self.used_max_values, self.cfg.VOLUME_RATIO
        ))

        typecode = self.get_typecode(self.cfg.SAMPLEWIDTH)

        self.bit_nul_samples = self.get_samples(typecode, self.cfg.BIT_NUL_HZ)
        self.bit_one_samples = self.get_samples(typecode, self.cfg.BIT_ONE_HZ)

    def get_samples(self, typecode, hz):
        values = tuple(
            sinus_values_by_hz(self.cfg.FRAMERATE, hz, self.used_max_values)
        )
        real_hz = float(self.cfg.FRAMERATE) / len(values)
        log.debug("Real frequency: %.2f" % real_hz)
        return array.array(typecode, values)

    def write_wave(self, destination_filepath):
        log.info("create wave file '%s'..." % destination_filepath)
        try:
            wavefile = wave.open(destination_filepath, "wb")
        except IOError, err:
            log.error("Error opening %s: %s" % (repr(destination_filepath), err))
            sys.exit(-1)

        wavefile.setnchannels(1) # Mono
        wavefile.setsampwidth(self.cfg.SAMPLEWIDTH)
        wavefile.setframerate(self.cfg.FRAMERATE)

        for bit in self.bitstream:
            if bit == 0:
#                 wavefile.writeframes(self.bit_nul_samples)
                wavefile.writeframesraw(self.bit_nul_samples)
            elif bit == 1:
#                 wavefile.writeframes(self.bit_one_samples)
                wavefile.writeframesraw(self.bit_one_samples)
            else:
                raise TypeError

        wavefile.close()
        log.info("Wave file %s written." % destination_filepath)


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )

    # test via CLI:

    import sys, subprocess

    # bas -> wav
    subprocess.Popen([sys.executable, "../PyDC_cli.py", "--verbosity=10",
#         "--log_format=%(module)s %(lineno)d: %(message)s",
        "../test_files/HelloWorld1.bas", "../test.wav"
    ]).wait()

    # wav -> bas
    subprocess.Popen([sys.executable, "../PyDC_cli.py", "--verbosity=10",
#         "--log_format=%(module)s %(lineno)d: %(message)s",
#         "../test.wav", "../test.bas",
        "../test_files/HelloWorld1 origin.wav", "../test_files/HelloWorld1.bas",
    ]).wait()

    print "-- END --"
