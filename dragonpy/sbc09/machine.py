#!/usr/bin/env python

"""
    Multicomp 6809
    ~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from dragonpy.core.machine import MachineGUI
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.gui import SBC09TkinterGUI
from dragonpy.sbc09.periphery import SBC09Periphery


log = logging.getLogger(__name__)


def run_sbc09(cfg_dict):
    machine = MachineGUI(
        cfg=SBC09Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=SBC09Periphery,
        GUI_Class=SBC09TkinterGUI
    )
