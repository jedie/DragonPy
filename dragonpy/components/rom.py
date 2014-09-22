# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import os
import logging


log = logging.getLogger(__name__)


class ROMFileNotFound(Exception):
    pass


class ROMFile(object):
    def __init__(self, filepath, address, max_size=None):
        self.filepath = filepath
        self.address = address
        self.max_size = max_size

    def get_data(self):
        if not os.path.isfile(self.filepath):
            raise ROMFileNotFound("Error ROM file not found: '%s'" % self.filepath)

        with open(self.filepath, "rb") as f:
            if not self.max_size:
                data = f.read()
            else:
                filesize = os.stat(self.filepath).st_size
                if filesize > self.max_size:
                    log.critical("Load only $%04x (dez.: %i) Bytes - file size is $%04x (dez.: %i) Bytes",
                        self.max_size, self.max_size, filesize, filesize
                    )
                data = f.read(self.max_size)

        return data






