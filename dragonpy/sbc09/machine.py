#!/usr/bin/env python
# encoding:utf-8

"""
    Multicomp 6809
    ~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

log = logging.getLogger(__name__)

from dragonpy.sbc09.periphery import SBC09Periphery
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.gui import SBC09TkinterGUI
from dragonpy.core.machine import MachineGUI


def run_sbc09(cfg_dict):
    machine = MachineGUI(
        cfg=SBC09Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=SBC09Periphery,
        GUI_Class=SBC09TkinterGUI
    )


def test_run():
    import os
    import sys
    import subprocess

    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
        # "-h"
        # "--log_list",
        # "--log", "DragonPy.cpu6809,50", "dragonpy.Dragon32.MC6821_PIA,40",

        # "--verbosity", "0", # hardcode DEBUG ;)
        # "--verbosity", "10", # DEBUG
        # "--verbosity", "20", # INFO
        # "--verbosity", "30", # WARNING
        # "--verbosity", "40", # ERROR
        # "--verbosity", "50", # CRITICAL/FATAL
        "--verbosity", "99", # nearly all off
        # "--verbosity", "100", # complete off

        # "--machine", "Dragon32", "run",
        "--machine", "sbc09", "run",
        # "--max_ops", "1",
        # "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    test_run()
