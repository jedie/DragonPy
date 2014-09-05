#!/bin/bash

if [ ! -f d64_ic17.rom ]; then
    (
        set -x
        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC17.zip -O d64_ic17.zip
        unzip -o "d64_ic17.zip"
        rm "d64_ic17.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC17.ROM" d64_ic17.rom

        wget -nv http://archive.worldofdragon.org/archive/index.php?dir=Roms/Dragon/\&file=Dragon%20Data%20Ltd%20-%20Dragon%2064%20-%20IC18.zip -O d64_ic18.zip
        unzip -o "d64_ic18.zip"
        rm "d64_ic18.zip"
        mv "Dragon Data Ltd - Dragon 64 - IC18.ROM" d64_ic18.rom
    )
fi
(
    set -x
    sha1sum -c d64_ic17.rom.sha1
    sha1sum -c d64_ic18.rom.sha1
)