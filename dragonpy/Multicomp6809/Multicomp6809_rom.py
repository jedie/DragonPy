"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import logging
import os
import zipfile
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    from zipfile import BadZipFile
else:
    from zipfile import BadZipfile as BadZipFile


from dragonpy.components.rom import ROMFile, ARCHIVE_EXT_ZIP
from dragonpy.utils.hex2bin import hex2bin


log = logging.getLogger(__name__)


class Multicomp6809Rom(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://searle.hostei.com/grant/Multicomp/Multicomp.zip"
    DOWNLOAD_SHA1 = "b44c46cf35775b404d9c12b76517817221536f52" # downloaded .zip archive
    FILE_COUNT = 1 # How many files are in the archive?
    SHA1 = "c49a741b6982cb3d27ccceca74eeaf121a3391ec" # extracted ROM
    FILENAME = "EXT_BASIC_NO_USING.bin"

    def extract_zip(self):
        assert self.FILE_COUNT>0
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zip:
                content = zip.read("ROMS/6809/EXT_BASIC_NO_USING.hex")
                out_filename=os.path.join(self.ROM_PATH, "EXT_BASIC_NO_USING.hex")
                with open(out_filename, "wb") as f:
                    f.write(content)

                print("%r extracted" % out_filename)
                self.post_processing(out_filename)

        except BadZipFile as err:
            msg = "Error extracting archive %r: %s" % (self.archive_path, err)
            log.error(msg)
            raise BadZipFile(msg)

    def post_processing(self, out_filename):
        hex2bin(
            src=out_filename,
            dst=self.rom_path,
            verbose=False
        )


