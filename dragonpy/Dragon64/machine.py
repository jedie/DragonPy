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

from dragonpy.Dragon32.periphery_dragon import Dragon32Periphery
from dragonpy.Dragon64.config import Dragon64Cfg
from dragonpy.core.gui import DragonTkinterGUI
from dragonpy.core.machine import MachineGUI


log = logging.getLogger(__name__)


def run_Dragon64(cfg_dict):
    machine = MachineGUI(
        cfg=Dragon64Cfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=Dragon32Periphery,
        GUI_Class=DragonTkinterGUI
    )

def test_run():
    import os
    import sys
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#         "-h"
#         "--log_list",
#         "--log", "DragonPy.cpu6809,50", "dragonpy.Dragon32.MC6821_PIA,40",

#         "--verbosity", "0", # hardcode DEBUG ;)
#         "--verbosity", "10", # DEBUG
#         "--verbosity", "20", # INFO
#         "--verbosity", "30", # WARNING
#         "--verbosity", "40", # ERROR
#         "--verbosity", "50", # CRITICAL/FATAL
        "--verbosity", "99", # nearly all off
#         "--verbosity", "100", # complete off

        "--machine", "Dragon64", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()


