#!/usr/bin/env python2
# coding: utf-8

"""
    PyDC - configs
    ==============

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import inspect


class BaseConfig(object):
    def print_debug_info(self):
        from utils import byte2bit_string

        print "Config: '%s'" % self.__class__.__name__

        for name, value in inspect.getmembers(self): # , inspect.isdatadescriptor):
            if name.startswith("_"):
                continue
#             print name, type(value)
            if not isinstance(value, (int, basestring, list, tuple, dict)):
                continue
            if isinstance(value, (int,)):
                bit_string = byte2bit_string(value)
                print "%20s = %-4s (in hex: %7s - binary: %s)" % (
                    name, value, repr(hex(value)), bit_string
                )
            else:
                print "%20s = %s" % (name, value)


class Dragon32Config(BaseConfig):
    """
    >>> d32cfg = Dragon32Config()
    >>> d32cfg.print_debug_info() # doctest: +NORMALIZE_WHITESPACE
    Config: 'Dragon32Config'
              BIT_NUL_HZ = 1200 (in hex: '0x4b0' - binary: 00001101001)
              BIT_ONE_HZ = 2400 (in hex: '0x960' - binary: 000001101001)
         BLOCK_TYPE_DICT = {0: 'filename block (0x00)', 1: 'data block (0x01)', 255: 'end-of-file block (0xff)'}
              DATA_BLOCK = 1    (in hex:   '0x1' - binary: 10000000)
               EOF_BLOCK = 255  (in hex:  '0xff' - binary: 11111111)
          FILENAME_BLOCK = 0    (in hex:   '0x0' - binary: 00000000)
           FILETYPE_DICT = {0: 'BASIC programm (0x00)', 1: 'Data file (0x01)', 255: 'Binary file (0xFF)'}
             FTYPE_BASIC = 0    (in hex:   '0x0' - binary: 00000000)
               FTYPE_BIN = 255  (in hex:  '0xff' - binary: 11111111)
              FTYPE_DATA = 1    (in hex:   '0x1' - binary: 10000000)
            HZ_VARIATION = 450  (in hex: '0x1c2' - binary: 010000111)
     LEAD_BYTE_CODEPOINT = 85   (in hex:  '0x55' - binary: 10101010)
           LEAD_BYTE_LEN = 255  (in hex:  '0xff' - binary: 11111111)
     SYNC_BYTE_CODEPOINT = 60   (in hex:  '0x3c' - binary: 00111100)

    >>> ",".join([hex(c) for c in d32cfg.get_header_codepoint_stream()])
    ... # doctest: +ELLIPSIS
    '0x55,0x55,0x55,...,0x55,0x55,0x55,0x3c'
    """
    BIT_NUL_HZ = 1200 # "0" is a single cycle at 1200 Hz
    BIT_ONE_HZ = 2400 # "1" is a single cycle at 2400 Hz
    HZ_VARIATION = 450 # How much Hz can signal scatter to match 1 or 0 bit ?

    LEAD_BYTE_CODEPOINT = 0x55 # 10101010
    LEAD_BYTE_LEN = 255
    SYNC_BYTE_CODEPOINT = 0x3C # 00111100
    MAX_SYNC_BYTE_SEARCH = 600 # search size in **Bytes**

    # Block types:
    FILENAME_BLOCK = 0x00
    DATA_BLOCK = 0x01
    EOF_BLOCK = 0xff

    BLOCK_TYPE_DICT = {
        FILENAME_BLOCK: "filename block (0x00)",
        DATA_BLOCK: "data block (0x01)",
        EOF_BLOCK: "end-of-file block (0xff)",
    }

    FTYPE_BASIC = 0x00
    FTYPE_DATA = 0x01
    FTYPE_BIN = 0xff
    FILETYPE_DICT = {
        FTYPE_BASIC:"BASIC programm (0x00)",
        FTYPE_DATA:"Data file (0x01)",
        FTYPE_BIN:"Binary file (0xFF)",
    }

    BASIC_TOKENIZED = 0x00
    BASIC_ASCII = 0xff
    BASIC_TYPE_DICT = {
        BASIC_TOKENIZED:"tokenized BASIC (0x00)",
        BASIC_ASCII:"ASCII BASIC (0xff)",
    }

    BASIC_CODE_END = [0x00, 0x00] # Mark the end of the code




if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
