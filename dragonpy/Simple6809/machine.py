#!/usr/bin/env python

"""
    Simple6809
    ~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from dragonpy.core.machine import MachineGUI
from dragonpy.Multicomp6809.gui import MulticompTkinterGUI
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.periphery_simple6809 import Simple6809Periphery


log = logging.getLogger(__name__)


def run_Simple6809(cfg_dict):
    machine = MachineGUI(
        cfg=Simple6809Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=Simple6809Periphery,
        GUI_Class=MulticompTkinterGUI
    )
