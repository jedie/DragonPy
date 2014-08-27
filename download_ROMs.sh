#!/bin/bash

if [ ! -f dragonpy/Dragon32/d32.rom ]; then
    (
        set -x
        cd dragonpy/Dragon32/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2032%20-%20IC17.zip -O d32.zip
        unzip -o "d32.zip"
        rm d32.zip
        mv "Dragon Data Ltd - Dragon 32 - IC17.ROM" d32.rom
    )
fi
(
    cd dragonpy/Dragon32/
    set -x
    sha1sum -c d32.rom.sha1
)

echo "========================================================================"

if [ ! -f dragonpy/Dragon64/d64_ic17.rom ]; then
    (
        set -x
        cd dragonpy/Dragon64/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC17.zip -O d64_ic17.zip
        unzip -o "d64_ic17.zip"
        rm "d64_ic17.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC17.ROM" d64_ic17.rom
    )

    echo "========================================================================"

    (
        set -x
        cd dragonpy/Dragon64/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC18.zip -O d64_ic18.zip
        unzip -o "d64_ic18.zip"
        rm "d64_ic18.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC18.ROM" d64_ic18.rom
    )
fi
(
    cd dragonpy/Dragon64/
    set -x
    sha1sum -c d64_ic17.rom.sha1
    sha1sum -c d64_ic18.rom.sha1
)

echo "========================================================================"

if [ ! -f "dragonpy/CoCo/bas13.rom" ]; then
(
    set -x
    cd dragonpy/CoCo/
    wget -nv http://mess.oldos.net/coco2b.zip
    unzip -o "coco2b.zip"
    rm "coco2b.zip"
)
fi
(
    cd dragonpy/CoCo/
    set -x
    sha1sum -c "bas13.rom.sha1"
    sha1sum -c "extbas11.rom.sha1"
)



