# encoding:utf8

"""
    DragonPy
    ========

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import logging

from dragonpy.core.machine import MachineGUI
from dragonpy.vectrex.config import VectrexCfg
from dragonpy.vectrex.periphery import VectrexPeriphery
from dragonpy.vectrex.vectrex_gui import VectrexGUI

log = logging.getLogger(__name__)


def run_Vectrex(cfg_dict):
    machine = MachineGUI(
        cfg=VectrexCfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=VectrexPeriphery,
        GUI_Class=VectrexGUI
    )


#------------------------------------------------------------------------------


def test_run():
    import sys
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
        "--verbosity", "5",
        "--machine", "Vectrex", "run",
        "--max_ops", "1",
        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()


