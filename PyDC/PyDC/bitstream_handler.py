#!/usr/bin/env python2

"""
    Convert dragon 32 Cassetts WAV files
    ====================================

    TODO:
        - write .BAS file
        - create GUI

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import functools
import itertools
import logging
import os

from PyDC.PyDC.utils import (
    MaxPosArraived,
    PatternNotFound,
    bits2codepoint,
    bitstream2codepoints,
    codepoints2bitstream,
    count_the_same,
    find_iter_window,
    iter_steps,
    list2str,
    pformat_codepoints,
    print_bitlist,
)


log = logging.getLogger("PyDC")


DISPLAY_BLOCK_COUNT = 8  # How many bit block should be printet in one line?

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
        print(f"{list2str(block)} {hex(byte_no):>4} {byte_no:>3} {repr(character)}")


def print_as_hex(block_codepoints):
    line = ""
    for block in block_codepoints:
        byte_no = bits2codepoint(block)
        # character = chr(byte_no)
        line += hex(byte_no)
    print(line)


class BitstreamHandlerBase:
    def __init__(self, cassette, cfg):
        self.cassette = cassette
        self.cfg = cfg

    def feed(self, bitstream):
        while True:
            print("_" * 79)
    #         bitstream = list(bitstream)
    #         print " ***** Bitstream length:", len(bitstream)
    #         bitstream = iter(bitstream)

            try:
                self.sync_bitstream(bitstream)  # Sync bitstream with SYNC_BYTE
            except SyncByteNotFoundError as err:
                log.error(err)
                log.info(f"Last wave pos: {bitstream.pformat_pos()}")
                break

            block_type, block_length, codepoints = self.get_block_info(bitstream)

            try:
                block_type_name = self.cfg.BLOCK_TYPE_DICT[block_type]
            except KeyError:
                print(f"ERROR: Block type {hex(block_type)} unknown in BLOCK_TYPE_DICT!")
                print("-" * 79)
                print("Debug bitlist:")
                print_bitlist(bitstream)
                print("-" * 79)
                break

            log.debug(
                f"block type: 0x{block_type:x} ({block_type_name})"
            )

            self.cassette.buffer_block(block_type, block_length, codepoints)

            if block_type == self.cfg.EOF_BLOCK:
                log.info("EOF-Block found")
                break

            if block_length == 0:
                print("ERROR: block length == 0 ???")
                print("-" * 79)
                print("Debug bitlist:")
                print_bitlist(bitstream)
                print("-" * 79)
                break

            print("=" * 79)

        self.cassette.buffer2file()

    def get_block_info(self, codepoint_stream):
        block_type = next(codepoint_stream)
        log.info(f"raw block type: {hex(block_type)} ({repr(block_type)})")

        block_length = next(codepoint_stream)

        # Get the complete block content
        codepoints = tuple(itertools.islice(codepoint_stream, block_length))

        try:
            verbose_block_type = self.cfg.BLOCK_TYPE_DICT[block_type]  # noqa
        except KeyError:
            log.error("Blocktype unknown!")
            print(pformat_codepoints(codepoints))
            sys.exit()
            # verbose_block_type = hex(block_type)

#         log.debug("content of '%s':" % verbose_block_type)
#         log.debug("-"*79)
#         log.debug(pformat_codepoints(codepoints))
#         log.debug("-"*79)

        real_block_len = len(codepoints)
        if real_block_len == block_length:
            log.info(f"Block length: {block_length}Bytes, ok.")
        else:
            log.error(f"Block should be {block_length}Bytes but are: {real_block_len}Bytes!")

        # Check block checksum

        origin_checksum = next(codepoint_stream)

        calc_checksum = sum(codepoint for codepoint in codepoints)
        calc_checksum += block_type
        calc_checksum += block_length
        calc_checksum = calc_checksum & 0xFF

        if calc_checksum == origin_checksum:
            log.info(f"Block checksum {hex(origin_checksum)} is ok.")
        else:
            log.error(
                f"Block checksum {hex(origin_checksum)} is not equal with calculated checksum: {hex(calc_checksum)}")

        # Check if the magic byte exists

#         magic_byte = next(codepoint_stream)
#         if magic_byte != self.cfg.MAGIC_BYTE:
#             log.error("Magic Byte %s is not %s" % (hex(magic_byte), hex(self.cfg.MAGIC_BYTE)))
#         else:
#             log.info("Magic Byte %s, ok." % hex(magic_byte))

        return block_type, block_length, codepoints


class BitstreamHandler(BitstreamHandlerBase):
    """
    feed with wave bitstream
    """

    def get_block_info(self, bitstream):
        # convert the raw bitstream to codepoint stream
        codepoint_stream = bitstream2codepoints(bitstream)

        return super().get_block_info(codepoint_stream)

    def sync_bitstream(self, bitstream):
        log.debug(f"start sync bitstream at wave pos: {bitstream.pformat_pos()}")
        bitstream.sync(32)  # Sync bitstream to wave sinus cycle

#         test_bitstream = list(itertools.islice(bitstream, 258 * 8))
#         print_bitlist(test_bitstream)

        log.debug(f"Searching for lead-in byte at wave pos: {bitstream.pformat_pos()}")

        # Searching for lead-in byte
        lead_in_pattern = list(codepoints2bitstream(self.cfg.LEAD_BYTE_CODEPOINT))
        max_pos = self.cfg.LEAD_BYTE_LEN * 8
        try:
            leader_pos = find_iter_window(bitstream, lead_in_pattern, max_pos)
        except MaxPosArraived as err:
            log.error(
                f"Error: Leader-Byte '{list2str(lead_in_pattern)}'"
                f" ({hex(self.cfg.LEAD_BYTE_CODEPOINT)}) not found in the first {self.cfg.LEAD_BYTE_LEN:d} Bytes!"
                f" ({err})"
            )
        except PatternNotFound as err:
            log.error(
                f"Error: Leader-Byte '{list2str(lead_in_pattern)}'"
                f" ({hex(self.cfg.LEAD_BYTE_CODEPOINT)}) doesn't exist in bitstream! ({err})"
            )
        else:
            log.info(
                f"Leader-Byte '{list2str(lead_in_pattern)}'"
                f" ({hex(self.cfg.LEAD_BYTE_CODEPOINT)}) found at {leader_pos:d} Bytes"
                f" (wave pos: {bitstream.pformat_pos()})"
            )

        log.debug(f"Search for sync-byte at wave pos: {bitstream.pformat_pos()}")

        # Search for sync-byte
        sync_pattern = list(codepoints2bitstream(self.cfg.SYNC_BYTE_CODEPOINT))
        max_search_bits = self.cfg.MAX_SYNC_BYTE_SEARCH * 8
        try:
            sync_pos = find_iter_window(bitstream, sync_pattern, max_search_bits)
        except MaxPosArraived as err:
            raise SyncByteNotFoundError(
                f"Error: Sync-Byte '{list2str(sync_pattern)}'"
                f" ({hex(self.cfg.SYNC_BYTE_CODEPOINT)}) not found in the"
                f" first {self.cfg.MAX_SYNC_BYTE_SEARCH:d} Bytes! ({err})"
            )
        except PatternNotFound as err:
            raise SyncByteNotFoundError(
                f"Error: Sync-Byte '{list2str(sync_pattern)}'"
                f" ({hex(self.cfg.SYNC_BYTE_CODEPOINT)}) doesn't exist in bitstream! ({err})"
            )
        else:
            log.info(
                f"Sync-Byte '{list2str(sync_pattern)}'"
                f" ({hex(self.cfg.SYNC_BYTE_CODEPOINT)}) found at {sync_pos:d} Bytes"
                f" (wave pos: {bitstream.pformat_pos()})"
            )


class CasStream:
    def __init__(self, source_filepath):
        self.source_filepath = source_filepath
        self.stat = os.stat(source_filepath)
        self.file_size = self.stat.st_size
        log.debug(f"file sizes: {self.file_size} Bytes")
        self.pos = 0
        self.file_generator = self.__file_generator()

        self.yield_ord = True

    def __iter__(self):
        return self

    def __next__(self):
        byte = next(self.file_generator)
        if self.yield_ord:
            return ord(byte)
        else:
            return byte

    def __file_generator(self):
        max = self.file_size + 1
        with open(self.source_filepath, "rb") as f:
            for chunk in iter(functools.partial(f.read, 1024), ""):
                for byte in chunk:
                    self.pos += 1
                    assert self.pos < max
                    yield byte

    def get_ord(self):
        byte = next(self)
        codepoint = ord(byte)
        return codepoint


class BytestreamHandler(BitstreamHandlerBase):
    """
    feed with byte stream e.g.: from cas file
    """

    def sync_bitstream(self, bitstream):
        leadin_bytes_count, sync_byte = count_the_same(bitstream, self.cfg.LEAD_BYTE_CODEPOINT)
        if leadin_bytes_count == 0:
            log.error("Leadin byte not found in file!")
        else:
            log.info(f"{leadin_bytes_count} x leadin bytes ({hex(self.cfg.LEAD_BYTE_CODEPOINT)}) found.")

        if sync_byte != self.cfg.SYNC_BYTE_CODEPOINT:
            log.error(f"Sync byte wrong. Get {hex(sync_byte)} but excepted {hex(self.cfg.SYNC_BYTE_CODEPOINT)}")
        else:
            log.debug(f"Sync {hex(self.cfg.SYNC_BYTE_CODEPOINT)} byte, ok.")


def print_bit_list_stats(bit_list):
    """
    >>> print_bit_list_stats([1,1,1,1,0,0,0,0])
    8 Bits: 4 positive bits and 4 negative bits
    """
    print(f"{len(bit_list)} Bits:", end=' ')
    positive_count = 0
    negative_count = 0
    for bit in bit_list:
        if bit == 1:
            positive_count += 1
        elif bit == 0:
            negative_count += 1
        else:
            raise TypeError(f"Not a bit: {repr(bit)}")
    print(f"{positive_count:d} positive bits and {negative_count:d} negative bits")


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
        verbose=False
        # verbose=True
    ))
#     sys.exit()

    # test via CLI:

    import subprocess
    import sys

    # bas -> wav
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
                      "--verbosity=10",
                      #         "--verbosity=5",
                      #         "--logfile=5",
                      #         "--log_format=%(module)s %(lineno)d: %(message)s",
                      #         "../test_files/HelloWorld1.bas", "--dst=../test.wav"
                      "../test_files/HelloWorld1.bas", "--dst=../test.cas"
                      ]).wait()

    print("\n" * 3)
    print("=" * 79)
    print("\n" * 3)

#     # wav -> bas
    subprocess.Popen([sys.executable, "../PyDC_cli.py",
                      #         "--verbosity=10",
                      "--verbosity=7",
                      #         "../test.wav", "--dst=../test.bas",
                      "../test.cas", "--dst=../test.bas",
                      #         "../test_files/HelloWorld1 origin.wav", "--dst=../test_files/HelloWorld1.bas",
                      ]).wait()

    print("-- END --")
