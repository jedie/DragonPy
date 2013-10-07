#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    http://www.6809.org.uk/dragon/hardware.shtml#sam

    $ffc0-ffdf    SAM (Synchronous Address Multiplexer) register bits - use
                      even address to clear, odd address to set
    $ffc0-ffc5    SAM VDG Mode registers V0-V2
    $ffc0/ffc1    SAM VDG Reg V0
    $ffc2/ffc3    SAM VDG Reg V1
    $ffc3/ffc5    SAM VDG Reg V2
    $ffc6-ffd3    SAM Display offset in 512 byte pages F0-F6
    $ffc6/ffc7    SAM Display Offset bit F0
    $ffc8/ffc9    SAM Display Offset bit F1
    $ffca/ffcb    SAM Display Offset bit F2
    $ffcc/ffcd    SAM Display Offset bit F3
    $ffce/ffcf    SAM Display Offset bit F4
    $ffd0/ffc1    SAM Display Offset bit F5
    $ffd2/ffc3    SAM Display Offset bit F6
    $ffd4/ffd5    SAM Page #1 bit - in D64 maps upper 32K Ram to $0000 to $7fff
    $ffd6-ffd9    SAM MPU Rate R0-R1
    $ffd6/ffd7    SAM MPU Rate bit R0
    $ffd8/ffd9    SAM MPU Rate bit R1
    $ffda-ffdd    SAM Memory Size select M0-M1
    $ffda/ffdb    SAM Memory Size select bit M0
    $ffdc/ffdd    SAM Memory Size select bit M1
    $ffde/ffdf    SAM Map Type - in D64 switches in upper 32K RAM $8000-$feff

    from http://archive.worldofdragon.org/index.php?title=Dragon_32_-_64K_Upgrade#APPENDICES. :
    Most well—known of these operations is the so-called 'speed-up poke'
    (POKE&HFFD7,0 and its reverse, POKE&HFFD6,0); however, of more concern to us
    here is the Map Type Bit (TY), set by FFDF, cleared by FFDE; the Page Bit (Pl),
    set by FFD5, cleared by FFD4; and the Memory Size Bits (M0 A Ml) set/cleared by
    FFDB/FFDA & FFDD/FFDC respectively. Of the remaining addresses, FFD6 to FFD9
    control the 2 clockrate bits (R0 & Rl); FFC6 to FFD3 control 7 bits (F0 to F6)
    giving the base address of the current Video-RAM (in units of 512 bytes); and
    FFC0 to FFC5 control 3 VDG Mode bits (V0 to V2).

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on: XRoar emulator by Ciaran Anscomb (GPL license) more info, see README
"""

import logging

log = logging.getLogger(__name__)


class SAM(object):
    """
    MC6883 (74LS783) Synchronous Address Multiplexer (SAM)
    """
    def __init__(self, cfg):
        self.cfg = cfg

    def __call__(self, address):
        msg = "TODO: SAM call at $%x" % address
        log.debug(msg)
        value = 0x7e
        log.debug(" SAM call at $%x returned $%x \t| %s" % (
            address, value, self.cfg.mem_info.get_shortest(address)
        ))
        return value
#         raise NotImplementedError

    def write_byte(self, address, value):
        log.debug(" *** TODO: SAM write byte $%x to $%x \t| %s" % (
            value, address, self.cfg.mem_info.get_shortest(address)
        ))
