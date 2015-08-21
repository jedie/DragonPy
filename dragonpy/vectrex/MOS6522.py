# encoding:utf8

"""
    DragonPy
    ========

    most parts are ported from JSVecX by Chris Smith alias raz0red.
        Copyright (C) 2010 Chris Smith alias raz0red
        http://www.twitchasylum.com/jsvecx/

    The original C version was written by Valavan Manohararajah
        http://www.valavan.net/vectrex.html

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import six
xrange = six.moves.xrange

import logging

log=logging.getLogger(__name__)


VECTREX_MHZ = 1500000
VECTREX_COLORS = 128
VECTREX_PDECAY = 30
VECTOR_HASH = 65521

ALG_MAX_X = 33000
ALG_MAX_Y = 41000
SCREEN_X_DEFAULT = 330 # in pixel
SCREEN_Y_DEFAULT = 410 # in pixel

FCYCLES_INIT = VECTREX_MHZ // VECTREX_PDECAY >> 0
VECTOR_CNT = VECTREX_MHZ // VECTREX_PDECAY >> 0


class MOS6522VIA(object):
    """
    MOS Technology 6522 Versatile Interface Adapter (VIA)

    https://en.wikipedia.org/wiki/MOS_Technology_6522

    $D000 - $D7FF 6522 interface adapter
    $D800 - $DFFF 6522 / RAM ?!?
    """
    def __init__(self, cfg, memory):
        self.cfg = cfg
        self.memory = memory

        self.memory.add_read_byte_callback(
            callback_func=self.read_byte,
            start_addr=0xd000,
            end_addr=0xdfff
        )

        self.memory.add_write_byte_callback(
            callback_func=self.write_byte,
            start_addr=0xd000,
            end_addr=0xdfff
        )

        self.reset()

    def reset(self):
        self.snd_regs = {}
        for i in xrange(16):
            self.snd_regs[i] = 0
        self.snd_regs[14] = 0xff

        self.snd_select = 0
        self.via_ora = 0
        self.via_orb = 0
        self.via_ddra = 0
        self.via_ddrb = 0
        self.via_t1on = 0
        self.via_t1int = 0
        self.via_t1c = 0
        self.via_t1ll = 0
        self.via_t1lh = 0
        self.via_t1pb7 = 0x80
        self.via_t2on = 0
        self.via_t2int = 0
        self.via_t2c = 0
        self.via_t2ll = 0
        self.via_sr = 0
        self.via_srb = 8
        self.via_src = 0
        self.via_srclk = 0
        self.via_acr = 0
        self.via_pcr = 0
        self.via_ifr = 0
        self.via_ier = 0
        self.via_ca2 = 1
        self.via_cb2h = 1
        self.via_cb2s = 0
        self.alg_rsh = 128
        self.alg_xsh = 128
        self.alg_ysh = 128
        self.alg_zsh = 0
        self.alg_jch0 = 128
        self.alg_jch1 = 128
        self.alg_jch2 = 128
        self.alg_jch3 = 128
        self.alg_jsh = 128
        self.alg_compare = 0
        self.alg_dx = 0
        self.alg_dy = 0
        self.alg_curr_x = ALG_MAX_X >> 1
        self.alg_curr_y = ALG_MAX_Y >> 1
        self.alg_vectoring = 0

        self.vector_draw_cnt = 0
        self.vector_erse_cnt = 0
        self.vectors_draw = {}
        self.vectors_erse = {}

        self.fcycles = FCYCLES_INIT
        self.t2shift = 0

    def read_byte(self, cpu_cycles, op_address, address):
        result = self.read8(address)
        log.error("%04x| TODO: 6522 read byte from $%04x - Send $%02x back", op_address, address, result)
        assert result is not None
        return result

    def write_byte(self, cpu_cycles, op_address, address, value):
        self.write8(address, value)
        log.error("%04x| TODO: 6522 write $%02x to $%04x", op_address, value, address)

    def snd_update (self):
        switch_orb = self.via_orb & 0x18
        if switch_orb == 0x10:
            if(self.snd_select != 14):
                self.snd_regs[self.snd_select] = self.via_ora
        elif switch_orb == 0x18:
            if ((self.via_ora & 0xf0) == 0x00):
                self.snd_select = self.via_ora & 0x0f

    def alg_update(self):
        switch_orb = self.via_orb & 0x06
        if switch_orb == 0x00:
            self.alg_jsh = self.alg_jch0
            if ((self.via_orb & 0x01) == 0x00):
                self.alg_ysh = self.alg_xsh
        elif switch_orb == 0x02:
            self.alg_jsh = self.alg_jch1
            if ((self.via_orb & 0x01) == 0x00):
                self.alg_rsh = self.alg_xsh
        elif switch_orb == 0x04:
            self.alg_jsh = self.alg_jch2
            if ((self.via_orb & 0x01) == 0x00):
                if(self.alg_xsh > 0x80):
                    self.alg_zsh = self.alg_xsh - 0x80
                else:
                    self.alg_zsh = 0
        elif switch_orb == 0x06:
            self.alg_jsh = self.alg_jch3

        if(self.alg_jsh > self.alg_xsh):
            self.alg_compare = 0x20
        else:
            self.alg_compare = 0

        self.alg_dx = self.alg_xsh - self.alg_rsh
        self.alg_dy = self.alg_rsh - self.alg_ysh

    def read8(self, address):
        switch_addr = address & 0xf
        if switch_addr == 0x0:
            if(self.via_acr & 0x80):
                data = ((self.via_orb & 0x5f) | self.via_t1pb7 | self.alg_compare)
            else:
                data = ((self.via_orb & 0xdf) | self.alg_compare)
            return data & 0xff
        elif switch_addr == 0x1:
            if ((self.via_pcr & 0x0e) == 0x08):
                self.via_ca2 = 0
        elif switch_addr == 0xf:
            if ((self.via_orb & 0x18) == 0x08):
                data = self.snd_regs[self.snd_select]
            else:
                data = self.via_ora
            return data & 0xff
        elif switch_addr == 0x2:
            return self.via_ddrb & 0xff
        elif switch_addr == 0x3:
            return self.via_ddra & 0xff
        elif switch_addr == 0x4:
            data = self.via_t1c
            self.via_ifr &= 0xbf
            self.via_t1on = 0
            self.via_t1int = 0
            self.via_t1pb7 = 0x80
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
            return data & 0xff
        elif switch_addr == 0x5:
            return (self.via_t1c >> 8) & 0xff
        elif switch_addr == 0x6:
            return self.via_t1ll & 0xff
        elif switch_addr == 0x7:
            return self.via_t1lh & 0xff
        elif switch_addr == 0x8:
            data = self.via_t2c
            self.via_ifr &= 0xdf
            self.via_t2on = 0
            self.via_t2int = 0
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
            return data & 0xff
        elif switch_addr == 0x9:
            return (self.via_t2c >> 8)
        elif switch_addr == 0xa:
            data = self.via_sr
            self.via_ifr &= 0xfb
            self.via_srb = 0
            self.via_srclk = 1
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
            return data & 0xff
        elif switch_addr == 0xb:
            return self.via_acr & 0xff
        elif switch_addr == 0xc:
            return self.via_pcr & 0xff
        elif switch_addr == 0xd:
            return self.via_ifr & 0xff
        elif switch_addr == 0xe:
            return (self.via_ier | 0x80) & 0xff

        return 0xff

    def write8 (self, address, data):
        switch_addr = address & 0xf
        if switch_addr == 0x0:
            self.via_orb = data
            self.snd_update()
            self.alg_update()
            if ((self.via_pcr & 0xe0) == 0x80):
                self.via_cb2h = 0
        elif switch_addr == 0x1:
            if ((self.via_pcr & 0x0e) == 0x08):
                self.via_ca2 = 0
        elif switch_addr == 0xf:
            self.via_ora = data
            self.snd_update()
            self.alg_xsh = data ^ 0x80
            self.alg_update()
        elif switch_addr == 0x2:
            self.via_ddrb = data
        elif switch_addr == 0x3:
            self.via_ddra = data
        elif switch_addr == 0x4:
            self.via_t1ll = data
        elif switch_addr == 0x5:
            self.via_t1lh = data
            self.via_t1c = (self.via_t1lh << 8) | self.via_t1ll
            self.via_ifr &= 0xbf
            self.via_t1on = 1
            self.via_t1int = 1
            self.via_t1pb7 = 0
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
        elif switch_addr == 0x6:
            self.via_t1ll = data
        elif switch_addr == 0x7:
            self.via_t1lh = data
        elif switch_addr == 0x8:
            self.via_t2ll = data
        elif switch_addr == 0x9:
            self.via_t2c = (data << 8) | self.via_t2ll
            self.via_ifr &= 0xdf
            self.via_t2on = 1
            self.via_t2int = 1
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
        elif switch_addr == 0xa:
            self.via_sr = data
            self.via_ifr &= 0xfb
            self.via_srb = 0
            self.via_srclk = 1
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
        elif switch_addr == 0xb:
            self.via_acr = data
        elif switch_addr == 0xc:
            self.via_pcr = data
            if ((self.via_pcr & 0x0e) == 0x0c):
                self.via_ca2 = 0
            else:
                self.via_ca2 = 1
            if ((self.via_pcr & 0xe0) == 0xc0):
                self.via_cb2h = 0
            else:
                self.via_cb2h = 1
        elif switch_addr == 0xd:
            self.via_ifr &= (~(data & 0x7f))
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f
        elif switch_addr == 0xe:
            if(data & 0x80):
                self.via_ier |= data & 0x7f
            else:
                self.via_ier &= (~(data & 0x7f))
            if ((self.via_ifr & 0x7f) & (self.via_ier & 0x7f)):
                self.via_ifr |= 0x80
            else:
                self.via_ifr &= 0x7f


#------------------------------------------------------------------------------


