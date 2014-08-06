#!/bin/bash

if [ ! -f dragonpy/Dragon32/d32.rom ]; then
    (
        set -x
        cd dragonpy/Dragon32/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2032%20-%20IC17.zip -O d32.zip
        unzip -o "d32.zip"
        rm d32.zip
        mv "Dragon Data Ltd - Dragon 32 - IC17.ROM" d32.rom
        sha1sum -c d32.rom.sha1
    )
fi
(
    cd dragonpy/Dragon32/
    set -x
    sha1sum -c d32.rom.sha1
)

echo "========================================================================"

if [ ! -f dragonpy/Dragon64/d64.rom ]; then
    (
        set -x
        cd dragonpy/Dragon64/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC17.zip -O d64_ic17.zip
        unzip -o "d64_ic17.zip"
        rm "d64_ic17.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC17.ROM" d64_ic17.rom
        sha1sum -c d64_ic17.rom.sha1
    )

    echo "========================================================================"

    (
        set -x
        cd dragonpy/Dragon64/
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC18.zip -O d64_ic18.zip
        unzip -o "d64_ic18.zip"
        rm "d64_ic18.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC18.ROM" d64_ic18.rom
        sha1sum -c d64_ic18.rom.sha1

        python create_d64_rom.py
    )
fi
(
    cd dragonpy/Dragon64/
    set -x
    sha1sum -c d64.rom.sha1
)

echo "========================================================================"

if [ ! -f "dragonpy/CoCo/Color Basic v1.3 (1982)(Tandy).rom" ]; then
(
    set -x
    cd dragonpy/CoCo/
    wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/CoCo/\&file=Color%20Basic%20v1.3%20%281982%29%28Tandy%29.zip -O ColorBasic1.3.zip
    unzip -o "ColorBasic1.3.zip"
    rm "ColorBasic1.3.zip"
)
fi
(
    cd dragonpy/CoCo/
    set -x
    sha1sum -c "Color Basic v1.3 (1982)(Tandy).rom.sha1"
)