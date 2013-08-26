#!/usr/bin/env python2
# coding: utf-8

"""
    Convert dragon 32 Cassetts WAV files into plain text.
    =====================================================

    Currently ony supported:
        * BASIC programs in tokenised form

    TODO:
        - check BASIC programs in ASCII form: CSAVE "NAME",A
        - detect even_odd startpoint!
        - add cli
        - write .BAS file

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys
import itertools
import logging
from configs import Dragon32Config
from CassetteObjects import Cassette

log = logging.getLogger("PyDC")


# own modules
from basic_tokens import BASIC_TOKENS, FUNCTION_TOKEN
from utils import find_iter_window, iter_steps, MaxPosArraived, \
    print_bitlist, bits2codepoint, list2str, bitstream2codepoints, get_word, \
    print_codepoint_stream, codepoints2string, print_as_hex_list, \
    PatternNotFound, LOG_LEVEL_DICT, LOG_FORMATTER, codepoints2bitstream, \
    pprint_codepoints
from wave2bitstream import Wave2Bitstream


DISPLAY_BLOCK_COUNT = 8 # How many bit block should be printet in one line?

MIN_SAMPLE_VALUE = 5



def pop_bytes_from_bit_list(bit_list, count):
    """
    >>> bit_str = (
    ... "00110011"
    ... "00001111"
    ... "01010101"
    ... "11001100")
    >>> bit_list = [int(i) for i in bit_str]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 1)
    >>> bytes
    [[0, 0, 1, 1, 0, 0, 1, 1]]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 2)
    >>> bytes
    [[0, 0, 0, 0, 1, 1, 1, 1], [0, 1, 0, 1, 0, 1, 0, 1]]
    >>> bit_list, bytes = pop_bytes_from_bit_list(bit_list, 1)
    >>> bytes
    [[1, 1, 0, 0, 1, 1, 0, 0]]
    """
    data_bit_count = count * 8

    data_bit_list = bit_list[:data_bit_count]
    data = list(iter_steps(data_bit_list, steps=8))

    bit_list = bit_list[data_bit_count:]
    return bit_list, data




def print_block_table(block_codepoints):
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        character = chr(byte_no)
        print "%s %4s %3s %s" % (
            list2str(block), hex(byte_no), byte_no, repr(character)
        )


def print_as_hex(block_codepoints):
    line = ""
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        character = chr(byte_no)
        line += hex(byte_no)
    print line



class BitstreamHandler(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.cassette = Cassette(cfg)

    def feed(self, bitstream):
        while True:
            print "_"*79
    #         bitstream = list(bitstream)
    #         print " ***** Bitstream length:", len(bitstream)
    #         bitstream = iter(bitstream)

            block_type, block_length, codepoint_stream = self.get_block_info(bitstream)

            codepoint_stream = list(codepoint_stream)
            print "\n***** codepoint_stream length:", len(codepoint_stream)
            pprint_codepoints(codepoint_stream)
            print " -"*40
            codepoint_stream = iter(codepoint_stream)

            print "*** block length:", block_length

            try:
                block_type_name = self.cfg.BLOCK_TYPE_DICT[block_type]
            except KeyError:
                print "ERROR: Block type %s unknown in BLOCK_TYPE_DICT!" % hex(block_type)
                print "-"*79
                print "Debug bitlist:"
                print_bitlist(bitstream)
                print "-"*79
                sys.exit(-1)


            print "*** block type: 0x%x (%s)" % (block_type, block_type_name)

            if block_type == self.cfg.EOF_BLOCK:
                print "EOF-Block found"
                break

            if block_length == 0:
                print "ERROR: block length == 0 ???"
                print "-"*79
                print "Debug bitlist:"
                print_bitlist(bitstream)
                print "-"*79
                sys.exit(-1)

    #         block_codepoints = bitstream2codepoints(block_bits)

    #         block_codepoints = list(block_codepoints)
    #         print_codepoint_stream(block_codepoints)
    #         block_codepoints = iter(block_codepoints)

            self.cassette.add_block(block_type, block_length, codepoint_stream)
            print "="*79


    def sync_stream(self, bitstream):
        sync_pattern = list(codepoints2bitstream(self.cfg.SYNC_BYTE_CODEPOINT))
        max_pos = (self.cfg.LEAD_BYTE_LEN + 2) * 8

        try:
            sync_pos = find_iter_window(bitstream, sync_pattern, max_pos)
        except MaxPosArraived, err:
            print "\nError: Sync-Byte not found in the first %i Bytes! (%s)" % (
                self.cfg.LEAD_BYTE_LEN, err
            )
            sys.exit(-1)
        except PatternNotFound, err:
            print "\nError: Sync-Byte doesn't exist in bitstream! (%s)" % err
            sys.exit(-1)
        else:
            print "\nSync-Byte '%s' (%x) found at %i Bytes" % (
                list2str(sync_pattern), self.cfg.SYNC_BYTE_CODEPOINT, sync_pos
            )


    def get_block_info(self, bitstream):
#         print "-"*79
#         bitstream = list(bitstream)
#         print_bitlist(bitstream, no_repr=True)
#         bitstream = iter(bitstream)
#         print "-"*79

        lead_in_pattern = list(codepoints2bitstream(self.cfg.LEAD_BYTE_CODEPOINT))
        max_pos = self.cfg.LEAD_BYTE_LEN * 8

        # Searching for lead-in byte
        try:
            leader_pos = find_iter_window(bitstream, lead_in_pattern, max_pos)
        except MaxPosArraived, err:
            print "\nError: Leader-Byte '%s' (%s) not found in the first %i Bytes! (%s)" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT),
                self.cfg.LEAD_BYTE_LEN, err
            )
            sys.exit(-1)
        except PatternNotFound, err:
            print "\nError: Leader-Byte '%s' (%s) doesn't exist in bitstream! (%s)" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT), err
            )
            sys.exit(-1)
        else:
            print "\nLeader-Byte '%s' (%s) found at %i Bytes" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT), leader_pos
            )

    #     print "-"*79
    #     print_bitlist(bitstream, no_repr=True)
    #     print "-"*79
    #     sys.exit()

        self.sync_stream(bitstream) # Sync bitstream with SYNC_BYTE

    #     print "-"*79
    #     bitstream = list(bitstream)
    #     print_bitlist(bitstream)
    #     bitstream = iter(bitstream)
    #     print "-"*79

        codepoint_stream = bitstream2codepoints(bitstream)
    #     print "-"*79
    #     print_codepoint_stream(codepoint_stream)
    #     print "-"*79

        block_type = next(codepoint_stream)
    #     print "raw block type:", repr(block_type), hex(block_type)
        block_length = next(codepoint_stream)
    #     print "raw block length:", repr(block_length)

        codepoint_stream = itertools.islice(codepoint_stream, block_length)

        return block_type, block_length, codepoint_stream







def print_bit_list_stats(bit_list):
    """
    >>> print_bit_list_stats([1,1,1,1,0,0,0,0])
    8 Bits: 4 positive bits and 4 negative bits
    """
    print "%i Bits:" % len(bit_list),
    positive_count = 0
    negative_count = 0
    for bit in bit_list:
        if bit == 1:
            positive_count += 1
        elif bit == 0:
            negative_count += 1
        else:
            raise TypeError("Not a bit: %s" % repr(bit))
    print "%i positive bits and %i negative bits" % (positive_count, negative_count)




if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
#     sys.exit()



    # created by Xroar Emulator
    FILENAME = "HelloWorld1 xroar.wav" # 8Bit 22050Hz
#     Bit 1 min: 1696Hz avg: 2058.3Hz max: 2205Hz variation: 509Hz
#     Bit 0 min: 595Hz avg: 1090.4Hz max: 1160Hz Variation: 565Hz
#     4760 Bits: 2243 positive bits and 2517 negative bits



    # created by origin Dragon 32 machine
#     FILENAME = "HelloWorld1 origin.wav" # 16Bit 44.1KHz mono
    # Bit 1 min: 1764Hz avg: 2013.9Hz max: 2100Hz variation: 336Hz
    # Bit 0 min: 595Hz avg: 1090.2Hz max: 1336Hz Variation: 741Hz
    # 2710 Bits: 1217 positive bits and 1493 negative bits



    """
    The origin BASIC code of the two WAV file is:

    10 FOR I = 1 TO 10
    20 PRINT I;"HELLO WORLD!"
    30 NEXT I

    The WAV files are here:
    https://github.com/jedie/python-code-snippets/raw/master/CodeSnippets/Dragon%2032/HelloWorld1%20origin.wav
    https://github.com/jedie/python-code-snippets/raw/master/CodeSnippets/Dragon%2032/HelloWorld1%20xroar.wav
    """


    # Test files from:
    # http://archive.worldofdragon.org/archive/index.php?dir=Tapes/Dragon/wav/
#     FILENAME = "Quickbeam Software - Duplicas v3.0.wav" # binary!


#     FILENAME = "Dragon Data Ltd - Examples from the Manual - 39~58 [run].wav"
    # Bit 1 min: 1696Hz avg: 2004.0Hz max: 2004Hz variation: 308Hz
    # Bit 0 min: 1025Hz avg: 1025.0Hz max: 1025Hz Variation: 0Hz
    # 155839 Bits: 73776 positive bits and 82063 negative bits

#     FILENAME = "1_MANIA.WAV" # 148579 frames, 4879 bits (raw)
#     FILENAME = "2_DBJ.WAV" # TODO

    # BASIC file with high line numbers:
#     FILENAME = "LineNumber Test 01.wav" # tokenized BASIC - no sync
#     FILENAME = "LineNumber Test 02.wav" # ASCII BASIC - no sync



#     log_level = LOG_LEVEL_DICT[3] # args.verbosity
#     log.setLevel(log_level)
#
#     logfilename = FILENAME + ".log" # args.logfile
#     if logfilename:
#         print "Log into '%s'" % logfilename
#         handler = logging.FileHandler(logfilename, mode='w', encoding="utf8")
#         handler.setFormatter(LOG_FORMATTER)
#         log.addHandler(handler)
#
#     # if args.stdout_log:
#     handler = logging.StreamHandler()
#     handler.setFormatter(LOG_FORMATTER)
#     log.addHandler(handler)

    d32cfg = Dragon32Config()
    c = Cassette(d32cfg)

    # get bitstream from WAVE file:
    st = Wave2Bitstream("test_files/%s" % FILENAME,
        bit_nul_hz=1200, # "0" is a single cycle at 1200 Hz
        bit_one_hz=2400, # "1" is a single cycle at 2400 Hz
        hz_variation=450, # How much Hz can signal scatter to match 1 or 0 bit ?
        min_volume_ratio=5, # percent volume to ignore sample
        mid_volume_ratio=15, # percent volume to trigger the sinus cycle
    )
    bitstream = iter(st)
    bitstream.sync(32)
    bitstream = itertools.imap(lambda x: x[1], bitstream) # remove frame_no


    # Create a bitstream from a existing .bas file:
#     c.add_from_bas("test_files/HelloWorld1.bas")
#     c.add_from_bas("test_files/Dragon Data Ltd - Examples from the Manual - 39~58 [run].bas")
#     c.add_from_bas("test_files/LineNumberTest.bas")
#     c.print_debug_info()
#     bitstream = c.get_as_bitstream()



#     bitstream = list(bitstream)
#     print " ***** Bitstream length:", len(bitstream)
#     print_bitlist(bitstream)
#     bitstream = iter(bitstream)


    bh = BitstreamHandler(d32cfg)
    bh.feed(bitstream)

