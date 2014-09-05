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
(
    set -x
    cd dragonpy/Multicomp6809/
    source download_Multicomp6809_rom.sh
)
echo "========================================================================"
(
    set -x
    cd dragonpy/Simple6809/
    source download_Simple6809_rom.sh
)
echo "========================================================================"





