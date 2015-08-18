"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

from dragonpy.components.rom import ROMFile, ARCHIVE_EXT_ZIP


class Dragon32Rom(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2032%20-%20IC17.zip"
    DOWNLOAD_SHA1 = "2cc4cbf81769746d261063eee20719899a001fed" # downloaded .zip archive
    FILE_COUNT = 1 # How many files are in the archive?
    RENAME_DATA = {"Dragon Data Ltd - Dragon 32 - IC17.ROM": "d32.rom"}
    SHA1 = "f2dab125673e653995a83bf6b793e3390ec7f65a" # extracted ROM
    FILENAME = "d32.rom"

