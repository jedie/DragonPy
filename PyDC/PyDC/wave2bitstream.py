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
    human_duration, ProcessInfo, count_sign, iter_steps, sinus_values_by_hz, \
    hz2duration, duration2hz, codepoints2bitstream, bits2codepoint


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

    def pformat_pos(self):
        sec = float(self.wave_pos) / self.framerate / self.samplewidth
        return "%s (frame no.: %s)" % (human_duration(sec), self.wave_pos)

    def _hz2duration(self, hz):
        return hz2duration(hz, framerate=self.framerate)

    def _duration2hz(self, duration):
        return duration2hz(duration, framerate=self.framerate)

    def set_wave_properties(self):
        self.framerate = self.wavefile.getframerate() # frames / second
        self.samplewidth = self.wavefile.getsampwidth() # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples
        self.max_value = MAX_VALUES[self.samplewidth]
        self.nchannels = self.wavefile.getnchannels() # typically 1 for mono, 2 for stereo

        log.info("Framerate: %sHz samplewidth: %i (%sBit, max volume value: %s) channels: %s" % (
            self.framerate,
            self.samplewidth, self.samplewidth * 8, self.max_value,
            self.nchannels,
        ))

        assert self.nchannels == 1, "Only MONO files are supported, yet!"


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
            msg = "Error opening %s: %s" % (repr(wave_filename), err)
            log.error(msg)
            sys.stderr.write(msg)
            sys.exit(-1)

        self.set_wave_properties()

        self.frame_count = self.wavefile.getnframes()
        print "Number of audio frames:", self.frame_count

        self.min_volume = int(round(self.max_value * cfg.MIN_VOLUME_RATIO / 100))
        print "Ignore sample lower than %.1f%% = %i" % (cfg.MIN_VOLUME_RATIO, self.min_volume)

        self.half_sinus = False # in trigger yield the full cycle
        self.frame_no = None

        # create the generator chain:

        # get frame numer + volume value from the WAVE file
        self.wave_values_generator = self.iter_wave_values()

        if cfg.AVG_COUNT > 1:
            # merge samples to a average sample
            log.debug("Merge %s audio sample to one average sample" % cfg.AVG_COUNT)
            self.avg_wave_values_generator = self.iter_avg_wave_values(
                self.wave_values_generator, cfg.AVG_COUNT
            )
            # trigger sinus cycle
            self.iter_trigger_generator = self.iter_trigger(self.avg_wave_values_generator)
        else:
            # trigger sinus cycle
            self.iter_trigger_generator = self.iter_trigger(self.wave_values_generator)

        # duration of a complete sinus cycle
        self.iter_duration_generator = self.iter_duration(self.iter_trigger_generator)

        # build from sinus cycle duration the bit stream
        self.iter_bitstream_generator = self.iter_bitstream(self.iter_duration_generator)

    def _print_status(self, process_info):
        percent = float(self.wave_pos) / self.frame_count * 100
        rest, eta, rate = process_info.update(self.wave_pos)
        sys.stdout.write("\r%.1f%% wav pos:%s - eta: %s (rate: %iFrames/sec)       " % (
            percent, self.pformat_pos(), eta, rate
        ))
        sys.stdout.flush()

    def _get_statistics(self, max=None):
        statistics = {}
        iter_duration_generator = self.iter_duration(self.iter_trigger_generator)
        for count, duration in enumerate(iter_duration_generator):
            try:
                statistics[duration] += 1
            except KeyError:
                statistics[duration] = 1
            if max is not None and count >= max:
                break
        return statistics

    def analyze(self):
        """
        Example output:

          394Hz (   28 Samples) exist:    1
          613Hz (   18 Samples) exist:    1
          788Hz (   14 Samples) exist:    1
          919Hz (   12 Samples) exist:  329 *********
         1002Hz (   11 Samples) exist: 1704 **********************************************
         1103Hz (   10 Samples) exist: 1256 **********************************
         1225Hz (    9 Samples) exist: 1743 ***********************************************
         1378Hz (    8 Samples) exist:    1
         1575Hz (    7 Samples) exist:  322 *********
         1838Hz (    6 Samples) exist: 1851 **************************************************
         2205Hz (    5 Samples) exist: 1397 **************************************
         2756Hz (    4 Samples) exist:  913 *************************
        """
        log.debug("enable half sinus scan")
        self.half_sinus = True
        statistics = self._get_statistics()

        width = 50
        max_count = max(statistics.values())

        print
        print "Found this zeror crossing timings in the wave file:"
        print

        for duration, count in sorted(statistics.items(), reverse=True):
            hz = duration2hz(duration, self.framerate / 2)
            w = int(round(float(width) / max_count * count))
            stars = "*"*w
            print "%5sHz (%5s Samples) exist: %4s %s" % (hz, duration, count, stars)

        print
        print "Notes:"
        print " - Hz values are converted to full sinus cycle duration."
        print " - Sample cound is from half sinus cycle."

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

        log.info("First bit is at: %s" % self.pformat_pos())
        log.debug("enable half sinus scan")
        self.half_sinus = True

        # Toggle sync test by consuming one half sinus sample
#         self.iter_trigger_generator.next() # Test sync

        # get "half sinus cycle" test data
        test_durations = itertools.islice(self.iter_duration_generator, length)
        # It's a tuple like: [(frame_no, duration)...]

        test_durations = list(test_durations)

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

        # build min/max Hz values
        bit_nul_min_hz = self.cfg.BIT_NUL_HZ - self.cfg.HZ_VARIATION
        bit_nul_max_hz = self.cfg.BIT_NUL_HZ + self.cfg.HZ_VARIATION

        bit_one_min_hz = self.cfg.BIT_ONE_HZ - self.cfg.HZ_VARIATION
        bit_one_max_hz = self.cfg.BIT_ONE_HZ + self.cfg.HZ_VARIATION

        bit_nul_max_duration = self._hz2duration(bit_nul_min_hz)
        bit_nul_min_duration = self._hz2duration(bit_nul_max_hz)

        bit_one_max_duration = self._hz2duration(bit_one_min_hz)
        bit_one_min_duration = self._hz2duration(bit_one_max_hz)

        log.info("bit-0 in %sHz - %sHz (duration: %s-%s)  |  bit-1 in %sHz - %sHz (duration: %s-%s)" % (
            bit_nul_min_hz, bit_nul_max_hz, bit_nul_min_duration, bit_nul_max_duration,
            bit_one_min_hz, bit_one_max_hz, bit_one_min_duration, bit_one_max_duration,
        ))
        assert bit_nul_max_hz < bit_one_min_hz, "HZ_VARIATION value is %sHz too high!" % (
            ((bit_nul_max_hz - bit_one_min_hz) / 2) + 1
        )
        assert bit_one_max_duration < bit_nul_min_duration, "HZ_VARIATION value is too high!"

        # for end statistics
        one_hz_count = 0
        one_hz_min = sys.maxint
        one_hz_avg = None
        one_hz_max = 0
        nul_hz_count = 0
        nul_hz_min = sys.maxint
        nul_hz_avg = None
        nul_hz_max = 0

        bit_count = 0

        for duration in iter_duration_generator:

            if bit_one_min_duration < duration < bit_one_max_duration:
                hz = self._duration2hz(duration)
                log.log(5,
                    "bit 1 at %s in %sSamples = %sHz" % (
                        self.pformat_pos(), duration, hz
                    )
                )
                bit_count += 1
                yield 1
                one_hz_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, one_hz_count)
            elif bit_nul_min_duration < duration < bit_nul_max_duration:
                hz = self._duration2hz(duration)
                log.log(5,
                    "bit 0 at %s in %sSamples = %sHz" % (
                        self.pformat_pos(), duration, hz
                    )
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
                hz = self._duration2hz(duration)
                log.log(7,
                    "Skip signal at %s with %sHz (%sSamples) out of frequency range." % (
                        self.pformat_pos(), hz, duration
                    )
                )
                continue

        if bit_count == 0:
            print "ERROR: No information from wave to generate the bits"
            print "trigger volume to high?"
            sys.exit(-1)

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
        print
        process_info = ProcessInfo(self.frame_count, use_last_rates=4)
        start_time = time.time()
        next_status = start_time + 0.25

        old_pos = next(iter_trigger)
        for pos in iter_trigger:
            duration = pos - old_pos
#             log.log(5, "Duration: %s" % duration)
            yield duration
            old_pos = pos

            if time.time() > next_status:
                next_status = time.time() + 1
                self._print_status(process_info)

        self._print_status(process_info)
        print

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
#             log.log(5, "sign info: %s" % repr(sign_info))
            # yield the mid crossing
            if in_pos == False and sign_info == pos_null_transit:
                log.log(5, "sinus curve goes from negative into positive")
#                 log.debug(" %s | %s | %s" % (previous_values, mid_values, next_values))
                yield mid_values[mid_index][0]
                in_pos = True
            elif  in_pos == True and sign_info == neg_null_transit:
                if self.half_sinus:
                    log.log(5, "sinus curve goes from positive into negative")
#                     log.debug(" %s | %s | %s" % (previous_values, mid_values, next_values))
                    yield mid_values[mid_index][0]
                in_pos = False


    def iter_avg_wave_values(self, wave_values_generator, avg_count):
        if log.level >= 5:
            tlm = TextLevelMeter(self.max_value, 79)

        for value_tuples in iter_steps(wave_values_generator, avg_count):
            values = [i[1] for i in value_tuples]
            avg_value = int(round(
                float(sum(values)) / avg_count
            ))
            if tlm:
                msg = tlm.feed(avg_value)
                percent = 100.0 / self.max_value * abs(avg_value)
                log.log(5,
                    "%s average %s samples to: %s (%.1f%%)" % (
                        msg,
                        ",".join([str(v) for v in values]),
                        avg_value, percent
                    )
                )
            yield (self.wave_pos, avg_value)

    def iter_wave_values(self):
        """
        yield frame numer + volume value from the WAVE file
        """
        typecode = self.get_typecode(self.samplewidth)

        if log.level >= 5:
            if self.cfg.AVG_COUNT > 1:
                # merge samples -> log output in iter_avg_wave_values
                tlm = None
            else:
                tlm = TextLevelMeter(self.max_value, 79)

        # Use only a read size which is a quare divider of the samplewidth
        # Otherwise array.array will raise: ValueError: string length not a multiple of item size
        divider = int(round(float(WAVE_READ_SIZE) / self.samplewidth))
        read_size = self.samplewidth * divider
        if read_size != WAVE_READ_SIZE:
            log.info("Real use wave read size: %i Bytes" % read_size)

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

#                 if abs(value) < self.min_volume:
# #                     log.log(5, "Ignore to lower amplitude")
#                     skip_count += 1
#                     continue

                yield (self.wave_pos, value)

        log.info("Skip %i samples that are lower than %i" % (
            skip_count, self.min_volume
        ))
        log.info("Last readed Frame is: %s" % self.pformat_pos())


class Bitstream2Wave(WaveBase):
    def __init__(self, destination_filepath, cfg):
        self.destination_filepath = destination_filepath
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

        self.typecode = self.get_typecode(self.cfg.SAMPLEWIDTH)

        self.bit_nul_samples = self.get_samples(self.cfg.BIT_NUL_HZ)
        self.bit_one_samples = self.get_samples(self.cfg.BIT_ONE_HZ)

        log.info("create wave file '%s'..." % destination_filepath)
        try:
            self.wavefile = wave.open(destination_filepath, "wb")
        except IOError, err:
            log.error("Error opening %s: %s" % (repr(destination_filepath), err))
            sys.exit(-1)

        self.wavefile.setnchannels(1) # Mono
        self.wavefile.setsampwidth(self.cfg.SAMPLEWIDTH)
        self.wavefile.setframerate(self.cfg.FRAMERATE)

        self.set_wave_properties()

    @property
    def wave_pos(self):
        pos = self.wavefile._nframeswritten * self.samplewidth
        return pos

    def pack_values(self, values):
        value_length = len(values)
        pack_format = "%i%s" % (value_length, self.typecode)
        packed_samples = struct.pack(pack_format, *values)

        return packed_samples

    def get_samples(self, hz):
        values = tuple(
            sinus_values_by_hz(self.cfg.FRAMERATE, hz, self.used_max_values)
        )
        real_hz = float(self.cfg.FRAMERATE) / len(values)
        log.debug("Real frequency: %.2f" % real_hz)
        return self.pack_values(values)


    def write_codepoint(self, codepoints):
        written_codepoints = []
        bits = []
        for bit in codepoints2bitstream(codepoints):
            bits.append(bit)
            if len(bits) == 8:
                written_codepoints.append(bits2codepoint(bits))
                bits = []
                
            if bit == 0:
#                 wavefile.writeframes(self.bit_nul_samples)
                self.wavefile.writeframes(self.bit_nul_samples)
            elif bit == 1:
#                 wavefile.writeframes(self.bit_one_samples)
                self.wavefile.writeframes(self.bit_one_samples)
            else:
                raise TypeError
        log.debug("Written at %s: %s" % (
            self.pformat_pos(), ",".join([hex(x) for x in written_codepoints])
        ))

    def write_silence(self, sec):
        start_pos = self.pformat_pos()
        silence = [0x00] * int(round((sec * self.framerate)))

        packed_samples = self.pack_values(silence)

        self.wavefile.writeframes(packed_samples)
        log.debug("Write %ssec. silence %s - %s" % (
            sec, start_pos, self.pformat_pos()
        ))

    def close(self):
        self.wavefile.close()
        log.info("Wave file %s written (%s)" % (
            self.destination_filepath, self.pformat_pos()
        ))


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
    # sys.exit()

    # test via CLI:

    import sys, subprocess

#     subprocess.Popen([sys.executable, "../PyDC_cli.py", "--help"])
#     sys.exit()

#     subprocess.Popen([sys.executable, "../PyDC_cli.py", "--verbosity=10",
# #         "--log_format=%(module)s %(lineno)d: %(message)s",
#         "--analyze",
#         "../test_files/HelloWorld1 xroar.wav"
# #         "../test_files/HelloWorld1 origin.wav"
#     ])

#     print "\n"*3
#     print "="*79
#     print "\n"*3

    # bas -> wav
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
        "--verbosity=10",
#         "--verbosity=5",
#         "--logfile=5",
#         "--log_format=%(module)s %(lineno)d: %(message)s",
        "../test_files/HelloWorld1.bas", "--dst=../test.wav"
    ]).wait()

#     print "\n"*3
#     print "="*79
#     print "\n"*3
#
#     # wav -> bas
#     subprocess.Popen([sys.executable, "../PyDC_cli.py",
#         "--verbosity=10",
# #         "--verbosity=5",
# #         "--logfile=5",
# #         "--log_format=%(module)s %(lineno)d: %(message)s",
#         "../test.wav", "--dst=../test.bas",
# #         "../test_files/HelloWorld1 origin.wav", "--dst=../test_files/HelloWorld1.bas",
#     ]).wait()
#
#     print "-- END --"
