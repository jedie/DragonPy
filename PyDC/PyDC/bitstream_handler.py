#!/usr/bin/env python2
# coding: utf-8

"""
    Convert dragon 32 Cassetts WAV files
    ====================================

    TODO:
        - write .BAS file
        - create GUI

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import itertools
import logging
import os

# own modules
from configs import Dragon32Config
from CassetteObjects import Cassette


log = logging.getLogger("PyDC")


# own modules
from utils import find_iter_window, iter_steps, MaxPosArraived, \
    print_bitlist, bits2codepoint, list2str, bitstream2codepoints, \
    PatternNotFound, LOG_FORMATTER, codepoints2bitstream, pformat_codepoints
from wave2bitstream import Wave2Bitstream


DISPLAY_BLOCK_COUNT = 8 # How many bit block should be printet in one line?

MIN_SAMPLE_VALUE = 5



class SyncByteNotFoundError(Exception):
    pass


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

            try:
                block_type, block_length, codepoints = self.get_block_info(bitstream)
            except SyncByteNotFoundError, err:
                log.error(err)
                break

            try:
                block_type_name = self.cfg.BLOCK_TYPE_DICT[block_type]
            except KeyError:
                print "ERROR: Block type %s unknown in BLOCK_TYPE_DICT!" % hex(block_type)
                print "-"*79
                print "Debug bitlist:"
                print_bitlist(bitstream)
                print "-"*79
                break


            print "*** block type: 0x%x (%s)" % (block_type, block_type_name)

            if block_type == self.cfg.EOF_BLOCK:
                log.info("EOF-Block found")
                break

            if block_length == 0:
                print "ERROR: block length == 0 ???"
                print "-"*79
                print "Debug bitlist:"
                print_bitlist(bitstream)
                print "-"*79
                break

            self.cassette.add_block(block_type, block_length, codepoints)
            print "="*79

    def sync_bitstream(self, bitstream):
        bitstream.sync(32) # Sync bitstream to wave sinus cycle

#         test_bitstream = list(itertools.islice(bitstream, 258 * 8))
#         print_bitlist(test_bitstream)

        # Searching for lead-in byte
        lead_in_pattern = list(codepoints2bitstream(self.cfg.LEAD_BYTE_CODEPOINT))
        max_pos = self.cfg.LEAD_BYTE_LEN * 8
        try:
            leader_pos = find_iter_window(bitstream, lead_in_pattern, max_pos)
        except MaxPosArraived, err:
            log.error("Error: Leader-Byte '%s' (%s) not found in the first %i Bytes! (%s)" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT),
                self.cfg.LEAD_BYTE_LEN, err
            ))
        except PatternNotFound, err:
            log.error("Error: Leader-Byte '%s' (%s) doesn't exist in bitstream! (%s)" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT), err
            ))
        else:
            log.info("Leader-Byte '%s' (%s) found at %i Bytes" % (
                list2str(lead_in_pattern), hex(self.cfg.LEAD_BYTE_CODEPOINT), leader_pos
            ))

        # Search for sync-byte
        sync_pattern = list(codepoints2bitstream(self.cfg.SYNC_BYTE_CODEPOINT))
        max_search_bits = self.cfg.MAX_SYNC_BYTE_SEARCH * 8
        try:
            sync_pos = find_iter_window(bitstream, sync_pattern, max_search_bits)
        except MaxPosArraived, err:
            raise SyncByteNotFoundError(
                "Error: Sync-Byte '%s' (%s) not found in the first %i Bytes! (%s)" % (
                    list2str(sync_pattern), hex(self.cfg.SYNC_BYTE_CODEPOINT),
                    self.cfg.MAX_SYNC_BYTE_SEARCH, err
                )
            )
        except PatternNotFound, err:
            raise SyncByteNotFoundError(
                "Error: Sync-Byte '%s' (%s) doesn't exist in bitstream! (%s)" % (
                    list2str(sync_pattern), hex(self.cfg.SYNC_BYTE_CODEPOINT),
                    err
                )
            )
        else:
            log.info("Sync-Byte '%s' (%s) found at %i Bytes" % (
                list2str(sync_pattern), hex(self.cfg.SYNC_BYTE_CODEPOINT),
                sync_pos
            ))


    def get_block_info(self, bitstream):
        self.sync_bitstream(bitstream) # Sync bitstream with SYNC_BYTE

        # convert the raw bitstream to codepoint stream
        codepoint_stream = bitstream2codepoints(bitstream)

        block_type = next(codepoint_stream)
        log.info("raw block type: %s (%s)" % (hex(block_type), repr(block_type)))

        block_length = next(codepoint_stream)

        # Get the complete block content
        codepoints = list(itertools.islice(codepoint_stream, block_length))

        real_block_len = len(codepoints)
        if real_block_len == block_length:
            log.info("Block length: %sBytes, ok." % block_length)
        else:
            log.error("Block should be %sBytes but are: %sBytes!" % (block_length, real_block_len))

        # Check block checksum

        origin_checksum = next(codepoint_stream)

        calc_checksum = sum([codepoint for codepoint in codepoints])
        calc_checksum += block_type
        calc_checksum += block_length
        calc_checksum = calc_checksum & 0xFF

        if calc_checksum == origin_checksum:
            log.info("Block checksum %s is ok." % hex(origin_checksum))
        else:
            log.error("Block checksum %s is not equal with calculated checksum: %s" % (
                hex(origin_checksum), hex(calc_checksum)
            ))

        # Check if the magic byte exists

        magic_byte = next(codepoint_stream)
        if magic_byte != self.cfg.MAGIC_BYTE:
            log.error("Magic Byte %s is not %s" % (hex(magic_byte), hex(self.cfg.MAGIC_BYTE)))
        else:
            log.info("Magic Byte %s, ok." % hex(magic_byte))

        return block_type, block_length, codepoints







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
#     import doctest
#     print doctest.testmod(
#         verbose=False
#         # verbose=True
#     )

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
