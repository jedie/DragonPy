#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

log = logging.getLogger(__name__)

class Simple6809Periphery(object):

    def __init__(self, cfg):
        self.cfg = cfg


def get_simple6809_periphery(cfg):
    return Simple6809Periphery(cfg)
