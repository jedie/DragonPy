#!/usr/bin/env python
# encoding:utf-8

"""
    Simple6809
    ~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

log = logging.getLogger(__name__)

from dragonpy.Simple6809.periphery_simple6809 import Simple6809Periphery
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Multicomp6809.gui import MulticompTkinterGUI
from dragonpy.core.machine import MachineGUI


def run_Simple6809(cfg_dict):
    machine = MachineGUI(
        cfg=Simple6809Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=Simple6809Periphery,
        GUI_Class=MulticompTkinterGUI
    )


