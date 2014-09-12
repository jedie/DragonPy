#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon 32
    ~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import logging

from dragonlib.utils.logging_utils import setup_logging
from dragonpy.CoCo.config import CoCo2bCfg
from dragonpy.CoCo.periphery_coco import CoCoPeriphery
from dragonpy.core.gui import DragonTkinterGUI
from dragonpy.core.machine import MachineGUI


log = logging.getLogger(__name__)


def run_CoCo2b(cfg_dict):
    machine = MachineGUI(
        cfg=CoCo2bCfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=CoCoPeriphery,
        GUI_Class=DragonTkinterGUI
    )



if __name__ == '__main__':


    setup_logging(log,
#         level=1 # hardcore debug ;)
#         level=10 # DEBUG
#         level=20 # INFO
#         level=30 # WARNING
#         level=40 # ERROR
        level=50  # CRITICAL/FATAL
    )

    CFG_DICT = {
        "verbosity": None,
        #     "display_cycle":True,
        "display_cycle": False,

        "trace": None,
        #     "trace":True,

        "max_ops": None,
        #     "max_ops":2000,
        #     "max_ops":1800,

        "bus_socket_host": None,
        "bus_socket_port": None,
        "ram": None,
        "rom": None,

        "use_bus": False,
    }
    run_CoCo2b(CFG_DICT)


