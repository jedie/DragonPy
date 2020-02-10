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
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Multicomp6809.gui import MulticompTkinterGUI
from dragonpy.Multicomp6809.periphery_Multicomp6809 import Multicomp6809Periphery


log = logging.getLogger(__name__)


def run_Multicomp6809(cfg_dict):
    machine = MachineGUI(
        cfg=Multicomp6809Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=Multicomp6809Periphery,
        GUI_Class=MulticompTkinterGUI
    )
