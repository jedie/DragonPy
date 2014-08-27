#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon 32 console
    ~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonlib.utils.logging_utils import log, setup_logging
from dragonpy.CoCo.machine import run_machine


CFG_DICT = {
    "verbosity":None,
#     "display_cycle":True,
    "display_cycle":False,

    "trace":None,
#     "trace":True,

    "max_ops":None,
#     "max_ops":1,
#     "max_ops":1800,

    "bus_socket_host":None,
    "bus_socket_port":None,
    "ram":None,
    "rom":None,

    "use_bus":False,
}


if __name__ == '__main__':
    setup_logging(log,
#         level=1 # hardcore debug ;)
#         level=10 # DEBUG
#         level=20 # INFO
#         level=30 # WARNING
#         level=40 # ERROR
        level=50  # CRITICAL/FATAL
    )

    run_machine(CFG_DICT)
