# encoding:utf8

"""
    DragonPy
    ========

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonlib.utils.logging_utils import log, setup_logging

from dragonpy.core.machine import ThreadedMachineGUI
from dragonpy.vectrex.vectrex_gui import VectrexGUI
from dragonpy.vectrex.config import VectrexCfg
from dragonpy.vectrex.periphery import VectrexPeriphery


def run_Vectrex(cfg_dict):
    machine = ThreadedMachineGUI(
        cfg=VectrexCfg(cfg_dict)
    )
    machine.run(
        PeripheryClass=VectrexPeriphery,
        GUI_Class=VectrexGUI
    )


if __name__ == '__main__':
    setup_logging(log,
        level=1 # hardcore debug ;)
#         level=10 # DEBUG
#         level=20 # INFO
#         level=30 # WARNING
#         level=40 # ERROR
#         level=50  # CRITICAL/FATAL
    )

    CFG_DICT = {
        "verbosity": None,
        #     "display_cycle":True,
        "display_cycle": False,

#         "trace": None,
        "trace":True,

#         "max_ops": None,
        #     "max_ops":2000,
            "max_ops":1,

        "bus_socket_host": None,
        "bus_socket_port": None,
        "ram": None,
        "rom": None,

        "use_bus": False,
    }
    run_Vectrex(CFG_DICT)


