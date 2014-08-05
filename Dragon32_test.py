#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon 32 console
    ~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.periphery_dragon import Dragon32PeripheryTkinter
from dragonpy.components.cpu6809 import CPU
from dragonpy.components.memory import Memory
from dragonpy.utils.logging_utils import log
from dragonpy.utils.logging_utils import setup_logging


CFG_DICT = {
    "verbosity":None,
#     "display_cycle":True,
    "display_cycle":False,

    "trace":None,
#    "trace":True,

    "max_ops":None,
#     "max_ops":2000,
#     "max_ops":1800,

    "bus_socket_host":None,
    "bus_socket_port":None,
    "ram":None,
    "rom":None,

    "use_bus":False,
}


class Dragon32(object):
    def __init__(self):
        self.cfg = Dragon32Cfg(CFG_DICT)

        self.periphery = Dragon32PeripheryTkinter(self.cfg)
        self.cfg.periphery = self.periphery

        memory = Memory(self.cfg)
        self.cpu = CPU(memory, self.cfg)
        memory.cpu = self.cpu # FIXME

    def run(self):
        self.cpu.reset()

        self.periphery.mainloop(self.cpu)

        self.cpu.quit()
        self.periphery.exit()


if __name__ == '__main__':
    print "Startup Dragon 32 machine..."

    setup_logging(log,
#        level=1 # hardcore debug ;)
#        level=10 # DEBUG
#        level=20 # INFO
#        level=30 # WARNING
#         level=40 # ERROR
        level=50 # CRITICAL/FATAL
    )
    c = Dragon32()
    c.run()

    print " --- END --- "
