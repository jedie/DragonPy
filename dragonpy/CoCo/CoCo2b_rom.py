"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015-2023 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonpy.components.rom import ARCHIVE_EXT_ZIP, ROMFile


class CoCo2b_Basic13_ROM(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "https://raw.githubusercontent.com/Luciano2018/Batocera_V35_Bios/master/bios/coco2b.zip"
    DOWNLOAD_SHA1 = "cc18ec64c5dc181a36c1e333eccb12d6b5441030"  # downloaded .zip archive
    FILE_COUNT = 3  # How many files are in the archive?
    SHA1 = "28b92bebe35fa4f026a084416d6ea3b1552b63d3"  # extracted ROM
    FILENAME = "bas13.rom"


class CoCo2b_ExtendedBasic11_ROM(CoCo2b_Basic13_ROM):
    SHA1 = "ad927fb4f30746d820cb8b860ebb585e7f095dea"  # extracted ROM
    FILENAME = "extbas11.rom"
