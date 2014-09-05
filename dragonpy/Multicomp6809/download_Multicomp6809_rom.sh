#!/bin/bash

if [ ! -f EXT_BASIC_NO_USING.bin ]; then
    (
        set -x
        wget -nv http://searle.hostei.com/grant/Multicomp/Multicomp.zip
        unzip -j -o "Multicomp.zip" "ROMS/6809/EXT_BASIC_NO_USING.hex"
        rm Multicomp.zip
        python2 hex2bin.py
    )
fi
(
    set -x
    sha1sum -c EXT_BASIC_NO_USING.bin.sha1
)

