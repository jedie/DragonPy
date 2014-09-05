#!/bin/bash

if [ ! -f "bas13.rom" ]; then
(
    set -x
    wget -nv http://mess.oldos.net/coco2b.zip
    unzip -o "coco2b.zip"
    rm "coco2b.zip"
)
fi
(
    set -x
    sha1sum -c "bas13.rom.sha1"
    sha1sum -c "extbas11.rom.sha1"
)