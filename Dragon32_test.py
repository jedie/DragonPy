#!/usr/bin/env python2
# encoding:utf-8

"""
    Dragon 32 console
    ~~~~~~~~~~~~~~~~~

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue

from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.periphery_dragon import Dragon32Periphery
from dragonpy.utils.logging_utils import log
from dragonpy.utils.logging_utils import setup_logging
from dragonpy.Dragon32.machine import Machine
from dragonpy.core.gui import DragonTkinterGUI


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


class Dragon32(object):

    def __init__(self):
        self.cfg = Dragon32Cfg(CFG_DICT)

        key_input_queue = Queue.Queue()
        display_queue = Queue.Queue()

        # machine == CPU+Memory+Periphery
        self.machine = Machine(
            self.cfg, Dragon32Periphery, display_queue, key_input_queue)

        # gui == TkInter GUI
        self.gui = DragonTkinterGUI(
            self.cfg, self.machine, display_queue, key_input_queue)

    def run(self):
        self.gui.mainloop()
        self.machine.quit()


if __name__ == '__main__':
    print "Startup Dragon 32 machine..."

    setup_logging(log,
                  # level=1 # hardcore debug ;)
                  # level=10 # DEBUG
                  # level=20 # INFO
                  # level=30 # WARNING
                  # level=40 # ERROR
                  level=50  # CRITICAL/FATAL
                  )
    c = Dragon32()
    c.run()

    print " --- END --- "
