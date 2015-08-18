"""
    DragonPy - 6809 emulator in Python
    ==================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

from dragonpy.components.rom import ROMFile, ARCHIVE_EXT_ZIP


class CoCo2b_Basic13_ROM(ROMFile):
    ARCHIVE_EXT = ARCHIVE_EXT_ZIP
    URL = "http://mess.oldos.net/coco2b.zip"
    DOWNLOAD_SHA1 = "059a8461f09f267a3847980c497e61d6c3ce5d9b" # downloaded .zip archive
    FILE_COUNT = 2 # How many files are in the archive?
    SHA1 = "28b92bebe35fa4f026a084416d6ea3b1552b63d3" # extracted ROM
    FILENAME = "bas13.rom"


class CoCo2b_ExtendedBasic11_ROM(CoCo2b_Basic13_ROM):
    SHA1 = "ad927fb4f30746d820cb8b860ebb585e7f095dea" # extracted ROM
    FILENAME = "extbas11.rom"



