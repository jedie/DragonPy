"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015-2020 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
import os
import zipfile
from zipfile import BadZipFile

from dragonpy.components.rom import ARCHIVE_EXT_ZIP, ROMFile
from dragonpy.utils.hex2bin import hex2bin


log = logging.getLogger(__name__)


class Multicomp6809Rom(ROMFile):
    """
    Grant Searle's Multicomp 6809 ROM
    http://searle.x10host.com/
    https://twitter.com/zx80nut
    http://searle.x10host.com/Multicomp/index.html
    """
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://searle.x10host.com/Multicomp/Multicomp.zip"
    DOWNLOAD_SHA1 = "b44c46cf35775b404d9c12b76517817221536f52"  # downloaded .zip archive
    FILE_COUNT = 1  # How many files are in the archive?
    SHA1 = "c49a741b6982cb3d27ccceca74eeaf121a3391ec"  # extracted ROM
    FILENAME = "EXT_BASIC_NO_USING.bin"

    def extract_zip(self):
        assert self.FILE_COUNT > 0
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zip:
                content = zip.read("ROMS/6809/EXT_BASIC_NO_USING.hex")
                out_filename = os.path.join(self.ROM_PATH, "EXT_BASIC_NO_USING.hex")
                with open(out_filename, "wb") as f:
                    f.write(content)

                print(f"{out_filename!r} extracted")
                self.post_processing(out_filename)

        except BadZipFile as err:
            msg = f"Error extracting archive {self.archive_path!r}: {err}"
            log.error(msg)
            raise BadZipFile(msg)

    def post_processing(self, out_filename):
        hex2bin(
            src=out_filename,
            dst=self.rom_path,
            verbose=False
        )
