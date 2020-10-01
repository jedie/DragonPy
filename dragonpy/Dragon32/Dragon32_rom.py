"""
    DragonPy - 6809 emulator in Python
    ==================================

    Dragon ROM Downloads from:
    http://archive.worldofdragon.org/archive/index.php?dir=Software/Dragon/Dragon%20Data%20Ltd/Dragon%20Firmware/

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015-2020 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonpy.components.rom import ARCHIVE_EXT_ZIP, ROMFile


class Dragon32Rom(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = (
        r"http://archive.worldofdragon.org/archive/index.php"
        r"?dir=Software/Dragon/Dragon%20Data%20Ltd/Dragon%20Firmware/"
        r"&file=Dragon%2032%20-%20IC17%26IC18%20%281982%29%28Dragon%20Data%20Ltd%29%5B%21%5D.zip"
    )
    DOWNLOAD_SHA1 = "2cc4cbf81769746d261063eee20719899a001fed"  # downloaded .zip archive
    FILE_COUNT = 1  # How many files are in the archive?
    RENAME_DATA = {"Dragon Data Ltd - Dragon 32 - IC17.ROM": "d32.rom"}
    SHA1 = "f2dab125673e653995a83bf6b793e3390ec7f65a"  # extracted ROM
    FILENAME = "d32.rom"
