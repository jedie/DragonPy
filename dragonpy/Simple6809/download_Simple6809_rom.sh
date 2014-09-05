#!/bin/bash

if [ ! -f ExBasROM.bin ]; then
    (
        set -x
        wget -nv http://searle.hostei.com/grant/6809/ExBasRom.zip
        unzip -o ExBasRom.zip
        rm ExBasRom.zip
        python2 hex2bin.py
    )
fi
(
    set -x
    sha1sum -c ExBasROM.bin.sha1
)

