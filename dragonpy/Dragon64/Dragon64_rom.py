"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

from dragonpy.components.rom import ROMFile, ARCHIVE_EXT_ZIP


class Dragon64RomIC17(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC17.zip"
    DOWNLOAD_SHA1 = "b3e734af642d9bb6f4338352b4347764dab24383" # downloaded .zip archive
    FILE_COUNT = 1 # How many files are in the archive?
    RENAME_DATA = {"Dragon Data Ltd - Dragon 64 - IC17.ROM": "d64_ic17.rom"}
    SHA1 = "f119506eaa3b4b70b9aa0dd83761e8cbe043d042" # extracted ROM
    FILENAME = "d64_ic17.rom"


class Dragon64RomIC18(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC18.zip"
    DOWNLOAD_SHA1 = "bf86bfa57a4cf2a8bec23457b4b6a41d8cc7d597" # downloaded .zip archive
    RENAME_DATA = {"Dragon Data Ltd - Dragon 64 - IC18.ROM": "d64_ic18.rom"}
    FILE_COUNT = 1 # How many files are in the archive?
    SHA1 = "e3c8986bb1d44269c4587b04f1ca27a70b0aaa2e" # extracted ROM
    FILENAME = "d64_ic18.rom"

