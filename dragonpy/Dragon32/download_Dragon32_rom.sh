#!/bin/bash

if [ ! -f d32.rom ]; then
    (
        set -x
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2032%20-%20IC17.zip -O d32.zip
        unzip -o "d32.zip"
        rm d32.zip
        mv "Dragon Data Ltd - Dragon 32 - IC17.ROM" d32.rom
    )
fi
(
    set -x
    sha1sum -c d32.rom.sha1
)