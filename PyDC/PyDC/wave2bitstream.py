#!/usr/bin/env python2

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import array
import functools
import itertools
import logging
import math
import struct
import time
import wave

from PyDC.PyDC.utils import (
    ProcessInfo,
    TextLevelMeter,
    average,
    bits2codepoint,
    codepoints2bitstream,
    count_sign,
    diff_info,
    duration2hz,
    human_duration,
    hz2duration,
    iter_steps,
    iter_window,
    sinus_values_by_hz,
)


try:
    import audioop
except ImportError as err:
    # e.g. PyPy, see: http://bugs.pypy.org/msg4430
    print("Can't use audioop:", err)
    audioop = None


log = logging.getLogger("PyDC")


WAVE_READ_SIZE = 16 * 1024  # How many frames should be read from WAVE file at once?
WAV_ARRAY_TYPECODE = {
    1: "b",  # 8-bit wave file
    2: "h",  # 16-bit wave file
    4: "l",  # 32-bit wave file TODO: Test it
}

# Maximum volume value in wave files:
MAX_VALUES = {
    1: 255,  # 8-bit wave file
    2: 32768,  # 16-bit wave file
    4: 2147483647,  # 32-bit wave file
}
HUMAN_SAMPLEWIDTH = {
    1: "8-bit",
    2: "16-bit",
    4: "32-bit",
}


class WaveBase:
    def get_typecode(self, samplewidth):
        try:
            typecode = WAV_ARRAY_TYPECODE[samplewidth]
        except KeyError:
            raise NotImplementedError(
                "Only %s wave files are supported, yet!" % (
                    ", ".join(["%sBit" % (i * 8) for i in list(WAV_ARRAY_TYPECODE.keys())])
                )
            )
        return typecode

    def pformat_pos(self):
        sec = float(self.wave_pos) / self.framerate / self.samplewidth
        return f"{human_duration(sec)} (frame no.: {self.wave_pos})"

    def _hz2duration(self, hz):
        return hz2duration(hz, framerate=self.framerate)

    def _duration2hz(self, duration):
        return duration2hz(duration, framerate=self.framerate)

    def set_wave_properties(self):
        self.framerate = self.wavefile.getframerate()  # frames / second
        self.samplewidth = self.wavefile.getsampwidth()  # 1 for 8-bit, 2 for 16-bit, 4 for 32-bit samples
        self.max_value = MAX_VALUES[self.samplewidth]
        self.nchannels = self.wavefile.getnchannels()  # typically 1 for mono, 2 for stereo

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

        self.half_sinus = False  # in trigger yield the full cycle
        self.wave_pos = 0  # Absolute position in the frame stream

        assert cfg.END_COUNT > 0  # Sample count that must be pos/neg at once
        assert cfg.MID_COUNT > 0  # Sample count that can be around null

        print(f"open wave file '{wave_filename}'...")
        try:
            self.wavefile = wave.open(wave_filename, "rb")
        except OSError as err:
            msg = f"Error opening {repr(wave_filename)}: {err}"
            log.error(msg)
            sys.stderr.write(msg)
            sys.exit(-1)

        self.set_wave_properties()

        self.frame_count = self.wavefile.getnframes()
        print("Number of audio frames:", self.frame_count)

        self.min_volume = int(round(self.max_value * cfg.MIN_VOLUME_RATIO / 100))
        print(f"Ignore sample lower than {cfg.MIN_VOLUME_RATIO:.1f}% = {self.min_volume:d}")

        self.half_sinus = False  # in trigger yield the full cycle
        self.frame_no = None

        # create the generator chain:

        # get frame numer + volume value from the WAVE file
        self.wave_values_generator = self.iter_wave_values()

        if cfg.AVG_COUNT > 1:
            # merge samples to a average sample
            log.debug(f"Merge {cfg.AVG_COUNT} audio sample to one average sample")
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
        sys.stdout.write(
            f"\r{percent:.1f}% wav pos:{self.pformat_pos()} - eta: {eta} (rate: {rate:d}Frames/sec)       ")
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

        print()
        print("Found this zeror crossing timings in the wave file:")
        print()

        for duration, count in sorted(list(statistics.items()), reverse=True):
            hz = duration2hz(duration, self.framerate / 2)
            w = int(round(float(width) / max_count * count))
            stars = "*" * w
            print(f"{hz:>5}Hz ({duration:>5} Samples) exist: {count:>4} {stars}")

        print()
        print("Notes:")
        print(" - Hz values are converted to full sinus cycle duration.")
        print(" - Sample cound is from half sinus cycle.")

    def sync(self, length):
        """
        synchronized weave sync trigger
        """

        # go in wave stream to the first bit
        try:
            next(self)
        except StopIteration:
            print("Error: no bits identified!")
            sys.exit(-1)

        log.info(f"First bit is at: {self.pformat_pos()}")
        log.debug("enable half sinus scan")
        self.half_sinus = True

        # Toggle sync test by consuming one half sinus sample
#         self.iter_trigger_generator.next() # Test sync

        # get "half sinus cycle" test data
        test_durations = itertools.islice(self.iter_duration_generator, length)
        # It's a tuple like: [(frame_no, duration)...]

        test_durations = list(test_durations)

        diff1, diff2 = diff_info(test_durations)
        log.debug(f"sync diff info: {diff1:d} vs. {diff2:d}")

        if diff1 > diff2:
            log.info("\nbit-sync one step.")
            next(self.iter_trigger_generator)
            log.debug("Synced.")
        else:
            log.info("\nNo bit-sync needed.")

        self.half_sinus = False
        log.debug("disable half sinus scan")

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iter_bitstream_generator)

    def iter_bitstream(self, iter_duration_generator):
        """
        iterate over self.iter_trigger() and
        yield the bits
        """
        assert self.half_sinus is False  # Allways trigger full sinus cycle

        # build min/max Hz values
        bit_nul_min_hz = self.cfg.BIT_NUL_HZ - self.cfg.HZ_VARIATION
        bit_nul_max_hz = self.cfg.BIT_NUL_HZ + self.cfg.HZ_VARIATION

        bit_one_min_hz = self.cfg.BIT_ONE_HZ - self.cfg.HZ_VARIATION
        bit_one_max_hz = self.cfg.BIT_ONE_HZ + self.cfg.HZ_VARIATION

        bit_nul_max_duration = self._hz2duration(bit_nul_min_hz)
        bit_nul_min_duration = self._hz2duration(bit_nul_max_hz)

        bit_one_max_duration = self._hz2duration(bit_one_min_hz)
        bit_one_min_duration = self._hz2duration(bit_one_max_hz)

        log.info(
            f"bit-0 in {bit_nul_min_hz}Hz - {bit_nul_max_hz}Hz"
            f" (duration: {bit_nul_min_duration}-{bit_nul_max_duration})"
            f"  |  bit-1 in {bit_one_min_hz}Hz - {bit_one_max_hz}Hz"
            f" (duration: {bit_one_min_duration}-{bit_one_max_duration})"
        )
        assert (
            bit_nul_max_hz < bit_one_min_hz
        ), f"HZ_VARIATION value is {(bit_nul_max_hz - bit_one_min_hz) / 2 + 1}Hz too high!"
        assert bit_one_max_duration < bit_nul_min_duration, "HZ_VARIATION value is too high!"

        # for end statistics
        bit_one_count = 0
        one_hz_min = sys.maxsize
        one_hz_avg = None
        one_hz_max = 0
        bit_nul_count = 0
        nul_hz_min = sys.maxsize
        nul_hz_avg = None
        nul_hz_max = 0

        for duration in iter_duration_generator:

            if bit_one_min_duration < duration < bit_one_max_duration:
                hz = self._duration2hz(duration)
                log.log(5,
                        f"bit 1 at {self.pformat_pos()} in {duration}Samples = {hz}Hz"
                        )
                yield 1
                bit_one_count += 1
                if hz < one_hz_min:
                    one_hz_min = hz
                if hz > one_hz_max:
                    one_hz_max = hz
                one_hz_avg = average(one_hz_avg, hz, bit_one_count)
            elif bit_nul_min_duration < duration < bit_nul_max_duration:
                hz = self._duration2hz(duration)
                log.log(5,
                        f"bit 0 at {self.pformat_pos()} in {duration}Samples = {hz}Hz"
                        )
                yield 0
                bit_nul_count += 1
                if hz < nul_hz_min:
                    nul_hz_min = hz
                if hz > nul_hz_max:
                    nul_hz_max = hz
                nul_hz_avg = average(nul_hz_avg, hz, bit_nul_count)
            else:
                hz = self._duration2hz(duration)
                log.log(7,
                        f"Skip signal at {self.pformat_pos()} with {hz}Hz ({duration}Samples) out of frequency range."
                        )
                continue

        bit_count = bit_one_count + bit_nul_count

        if bit_count == 0:
            print("ERROR: No information from wave to generate the bits")
            print("trigger volume to high?")
            sys.exit(-1)

        log.info(f"\n{bit_count:d} Bits: {bit_one_count:d} positive bits and {bit_nul_count:d} negative bits")
        if bit_one_count > 0:
            log.info(
                f"Bit 1: {one_hz_min}Hz - {one_hz_max}Hz avg:"
                f" {one_hz_avg:.1f}Hz variation: {one_hz_max - one_hz_min}Hz"
            )
        if bit_nul_count > 0:
            log.info(
                f"Bit 0: {nul_hz_min}Hz - {nul_hz_max}Hz avg:"
                f" {nul_hz_avg:.1f}Hz variation: {nul_hz_max - nul_hz_min}Hz"
            )

    def iter_duration(self, iter_trigger):
        """
        yield the duration of two frames in a row.
        """
        print()
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
        print()

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
            previous_values = values[:self.cfg.END_COUNT]  # e.g.: 123-----
            mid_values = values[self.cfg.END_COUNT:self.cfg.END_COUNT + self.cfg.MID_COUNT]  # e.g.: ---45---
            next_values = values[-self.cfg.END_COUNT:]  # e.g.: -----678

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
            if in_pos is False and sign_info == pos_null_transit:
                log.log(5, "sinus curve goes from negative into positive")
#                 log.debug(" %s | %s | %s" % (previous_values, mid_values, next_values))
                yield mid_values[mid_index][0]
                in_pos = True
            elif in_pos and sign_info == neg_null_transit:
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
                        f"{msg} average {','.join([str(v) for v in values])} samples to: {avg_value} ({percent:.1f}%)"
                        )
            yield (self.wave_pos, avg_value)

    def iter_wave_values(self):
        """
        yield frame numer + volume value from the WAVE file
        """
        typecode = self.get_typecode(self.samplewidth)

        # if log.level >= 5:
        #     if self.cfg.AVG_COUNT > 1:
        #         # merge samples -> log output in iter_avg_wave_values
        #         tlm = None
        #     else:
        #         tlm = TextLevelMeter(self.max_value, 79)

        # Use only a read size which is a quare divider of the samplewidth
        # Otherwise array.array will raise: ValueError: string length not a multiple of item size
        divider = int(round(float(WAVE_READ_SIZE) / self.samplewidth))
        read_size = self.samplewidth * divider
        if read_size != WAVE_READ_SIZE:
            log.info(f"Real use wave read size: {read_size:d} Bytes")

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
            except ValueError as err:
                # e.g.:
                #     ValueError: string length not a multiple of item size
                # Work-a-round: Skip the last frames of this block
                frame_count = len(frames)
                divider = int(math.floor(float(frame_count) / self.samplewidth))
                new_count = self.samplewidth * divider
                frames = frames[:new_count]  # skip frames
                log.error(
                    "Can't make array from %s frames: Value error: %s (Skip %i and use %i frames)" % (
                        frame_count, err, frame_count - new_count, len(frames)
                    ))
                values = array.array(typecode, frames)

            for value in values:
                self.wave_pos += 1  # Absolute position in the frame stream

                if manually_audioop_bias:
                    # audioop.bias can't be used.
                    # See: http://hg.python.org/cpython/file/482590320549/Modules/audioop.c#l957
                    value = value % 0xff - 128

#                 if abs(value) < self.min_volume:
# #                     log.log(5, "Ignore to lower amplitude")
#                     skip_count += 1
#                     continue

                yield (self.wave_pos, value)

        log.info(f"Skip {skip_count:d} samples that are lower than {self.min_volume:d}")
        log.info(f"Last readed Frame is: {self.pformat_pos()}")


class Bitstream2Wave(WaveBase):
    def __init__(self, destination_filepath, cfg):
        self.destination_filepath = destination_filepath
        self.cfg = cfg

        wave_max_value = MAX_VALUES[self.cfg.SAMPLEWIDTH]
        self.used_max_values = int(round(
            float(wave_max_value) / 100 * self.cfg.VOLUME_RATIO
        ))
        log.info(
            f"Create {HUMAN_SAMPLEWIDTH[self.cfg.SAMPLEWIDTH]} wave file"
            f" with {self.cfg.FRAMERATE}Hz and {self.used_max_values} max volumen ({self.cfg.VOLUME_RATIO}%)"
        )

        self.typecode = self.get_typecode(self.cfg.SAMPLEWIDTH)

        self.bit_nul_samples = self.get_samples(self.cfg.BIT_NUL_HZ)
        self.bit_one_samples = self.get_samples(self.cfg.BIT_ONE_HZ)

        log.info(f"create wave file '{destination_filepath}'...")
        try:
            self.wavefile = wave.open(destination_filepath, "wb")
        except OSError as err:
            log.error(f"Error opening {repr(destination_filepath)}: {err}")
            sys.exit(-1)

        self.wavefile.setnchannels(1)  # Mono
        self.wavefile.setsampwidth(self.cfg.SAMPLEWIDTH)
        self.wavefile.setframerate(self.cfg.FRAMERATE)

        self.set_wave_properties()

    @property
    def wave_pos(self):
        pos = self.wavefile._nframeswritten * self.samplewidth
        return pos

    def pack_values(self, values):
        value_length = len(values)
        pack_format = f"{value_length:d}{self.typecode}"
        packed_samples = struct.pack(pack_format, *values)

        return packed_samples

    def get_samples(self, hz):
        values = tuple(
            sinus_values_by_hz(self.cfg.FRAMERATE, hz, self.used_max_values)
        )
        real_hz = float(self.cfg.FRAMERATE) / len(values)
        log.debug(f"Real frequency: {real_hz:.2f}")
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
        log.debug(f"Written at {self.pformat_pos()}: {','.join([hex(x) for x in written_codepoints])}")

    def write_silence(self, sec):
        start_pos = self.pformat_pos()
        silence = [0x00] * int(round(sec * self.framerate))

        packed_samples = self.pack_values(silence)

        self.wavefile.writeframes(packed_samples)
        log.debug(f"Write {sec}sec. silence {start_pos} - {self.pformat_pos()}")

    def close(self):
        self.wavefile.close()
        log.info(f"Wave file {self.destination_filepath} written ({self.pformat_pos()})")


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
        verbose=False
        # verbose=True
    ))
    # sys.exit()

    # test via CLI:

    import subprocess
    import sys

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
