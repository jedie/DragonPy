#!/bin/bash

(
    set -x
    cd dragonpy/Dragon32/
    source download_Dragon32_rom.sh
)
echo "========================================================================"
(
    set -x
    cd dragonpy/Dragon64/
    source download_Dragon64_roms.sh
)
echo "========================================================================"
(
    set -x
    cd dragonpy/CoCo/
    source download_CoCo2b_roms.sh
)
echo "========================================================================"





