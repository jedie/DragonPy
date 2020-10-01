"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015-2020 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonpy.components.rom import ARCHIVE_EXT_ZIP, ROMFile


class CoCo2b_Basic13_ROM(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://www.roust-it.dk/coco/roms/coco2b.zip"
    DOWNLOAD_SHA1 = "8935dcde4ee8d9ced8fc748826870ac0c6cf6c3f"  # downloaded .zip archive
    FILE_COUNT = 2  # How many files are in the archive?
    SHA1 = "28b92bebe35fa4f026a084416d6ea3b1552b63d3"  # extracted ROM
    FILENAME = "bas13.rom"


class CoCo2b_ExtendedBasic11_ROM(CoCo2b_Basic13_ROM):
    SHA1 = "ad927fb4f30746d820cb8b860ebb585e7f095dea"  # extracted ROM
    FILENAME = "extbas11.rom"
