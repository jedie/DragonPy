#!/usr/bin/env python2

"""
    Convert dragon 32 Cassetts WAV files into plain text.
    =====================================================
    
    In current state only the bits would be decoded, yet!
    
    TODO:
        detect even_odd startpoint!

    Interesting links:
        http://www.onastick.clara.net/cosio.htm
        http://www.cs.unc.edu/~yakowenk/coco/text/tapeformat.html

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import collections
import itertools
import wave
import sys
import struct
import audioop


ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz
MIN_TOGGLE_COUNT = 3 # How many samples must be in pos/neg to count a cycle?


def iter_wave_values(wavefile):
    samplewidth = wavefile.getsampwidth() # i.e 1 for 8-bit samples, 2 for 16-bit samples
    print "samplewidth:", samplewidth
    nchannels = wavefile.getnchannels() # typically 1 for mono, 2 for stereo
    print "channels:", nchannels

    assert nchannels == 1, "Only MONO files are supported, yet!"

    frame_count = wavefile.getnframes() # number of audio frames

    # FIXME
    if samplewidth==1:
        struct_unpack_str = "b"
    elif samplewidth == 2:
        struct_unpack_str = "<h"
    else:
        raise NotImplementedError("Only sample width 2 or 1 are supported, yet!")
    print "struct_unpack_str:", struct_unpack_str

    for frame_no in xrange(frame_count):
        frame = wavefile.readframes(1)
        if not frame:
            break

        frame = struct.unpack(struct_unpack_str, frame)[0]

        yield frame_no, frame


def count_sign(values):
    """
    >>> count_sign([3,-1,-2])
    (1, 2)
    >>> count_sign([0,-1])
    (0, 1)
    """
    positive_count = 0
    negative_count = 0
    for value in values:
        if value>0:
            positive_count += 1
        elif value<0:
            negative_count += 1
    return positive_count, negative_count


def iter_bits(wavefile, even_odd):
    framerate = wavefile.getframerate() # frames / second
    print "Framerate:", framerate

    in_positive = even_odd
    in_negative = not even_odd
    toggle_count = 0 # Counter for detect a complete cycle
    previous_frame_no = 0

    window_values = collections.deque(maxlen=MIN_TOGGLE_COUNT)
    for frame_no, value in iter_wave_values(wavefile):
        #~ ms=float(frame_no)/framerate
        #~ print "%i %0.5fms %i" % (frame_no, ms, value)

        window_values.append(value)
        if len(window_values)>=MIN_TOGGLE_COUNT:
            positive_count, negative_count = count_sign(window_values)

            #~ print window_values, positive_count, negative_count
            if not in_positive and positive_count==MIN_TOGGLE_COUNT and negative_count==0:
                # go into a positive sinus area
                in_positive = True
                in_negative = False
                toggle_count += 1
            elif not in_negative and negative_count==MIN_TOGGLE_COUNT and positive_count==0:
                # go into a negative sinus area
                in_negative = True
                in_positive = False
                toggle_count += 1

            if toggle_count>=2:
                # a single sinus cycle complete
                toggle_count = 0

                frame_count = frame_no-previous_frame_no
                hz=framerate/frame_count
                ms=float(frame_no)/framerate

                dst_one = abs(ONE_HZ-hz)
                dst_nul = abs(NUL_HZ-hz)
                if dst_one<dst_nul:
                    yield 1
                else:
                    yield 0

                #~ print "***", bit, hz, "Hz", "%0.5fms" % ms
                previous_frame_no = frame_no


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        #~ verbose=True
    )


    # created by Xroar Emulator
#     FILENAME = "HelloWorld1 xroar.wav"
#     even_odd = False


    # created by origin Dragon 32 machine
    FILENAME = "HelloWorld1 origin.wav"
    even_odd = True


    print "Read '%s'..." % FILENAME
    wavefile = wave.open(FILENAME, "r")

    frame_count = wavefile.getnframes()
    print "Numer of audio frames:", frame_count

    line = ""
    for bit_count, bit in enumerate(iter_bits(wavefile, even_odd)):
        #~ if frame_no>100:
            #~ break
        line += str(bit)
        if len(line)>70:
            print line
            line = ""

    print "%i bits decoded." % bit_count
