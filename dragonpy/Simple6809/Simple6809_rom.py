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


class Simple6809Rom(ROMFile):
    """
    Grant Searle's Simple 6809 ROM
    http://searle.x10host.com/
    https://twitter.com/zx80nut
    http://searle.x10host.com/6809/Simple6809.html
    """
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://searle.x10host.com/6809/ExBasRom.zip"
    DOWNLOAD_SHA1 = "435484899156bc93876c9c805d54b4c12dc900c4"  # downloaded .zip archive
    FILE_COUNT = 3  # How many files are in the archive?
    SHA1 = "1e0d5997b1b286aa328bdbff776bcddbb68d1c34"  # extracted ROM
    FILENAME = "ExBasROM.bin"

    ARCHIVE_NAMES = ['ExBasROM.asm', 'ExBasROM.hex', 'ExBasROM.LST']

    def extract_zip(self):
        assert self.FILE_COUNT > 0
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zip:
                namelist = zip.namelist()
                print("namelist():", namelist)
                if namelist != self.ARCHIVE_NAMES:
                    msg = (
                        "Wrong archive content?!?"
                        " namelist should be: %r"
                    ) % self.ARCHIVE_NAMES
                    log.error(msg)
                    raise RuntimeError(msg)

                zip.extractall(path=self.ROM_PATH)

        except BadZipFile as err:
            msg = f"Error extracting archive {self.archive_path!r}: {err}"
            log.error(msg)
            raise BadZipFile(msg)

        hex2bin(
            src=os.path.join(self.ROM_PATH, "ExBasROM.hex"),
            dst=self.rom_path,
            verbose=False
        )
