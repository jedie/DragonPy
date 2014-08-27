#!/usr/bin/env python2
# coding: utf-8

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import atexit
import sys
import webbrowser
import threading

from dragonpy.core.base_cli import Base_CLI
from dragonpy.core.configs import machine_dict
from dragonlib.utils.logging_utils import log, setup_logging
from dragonpy.CoCo.machine import run_CoCo2b
from dragonpy.Dragon64.machine import run_Dragon64
from dragonpy.Dragon32.machine import run_Dragon32


machine_dict.register("Dragon32", run_Dragon32, default=True)
machine_dict.register("Dragon64", run_Dragon64)
machine_dict.register("CoCo2b", run_CoCo2b)
# machine_dict.register("sbc09", SBC09Cfg)
# machine_dict.register("Simple6809", Simple6809Cfg)
# machine_dict.register("Multicomp6809", Multicomp6809Cfg)


@atexit.register
def goodbye():
    print "\n --- END --- \n"
    try:
        # for Eclipse :(
        sys.stdout.flush()
        sys.stderr.flush()
    except:
        pass


class DragonPyCLI(Base_CLI):
    LOG_NAME = "DragonPy"
    DESCRIPTION = "DragonPy - Dragon 32 emulator in Python"

    def __init__(self, machine_dict):
        super(DragonPyCLI, self).__init__()
        self.machine_dict = machine_dict
        log.debug("Existing machine_dict: %s" % repr(self.machine_dict))

        self.parser.add_argument("--machine",
            choices=self.machine_dict.keys(),
            default=machine_dict.DEFAULT,
            help="Used machine configuration"
        )
        self.parser.add_argument('--trace', action='store_true',
            help="Create trace lines."
        )
#         self.parser.add_argument('--dont_open_webbrowser', action='store_true',
#             help="Don't open the Webbrowser on CPU http control Server"
#         )

#         self.parser.add_argument("--bus_socket_host",
#             help="Host internal socket bus I/O (do not set manually!)"
#         )
#         self.parser.add_argument("--bus_socket_port", type=int,
#             help="Port for internal socket bus I/O (do not set manually!)"
#         )
        self.parser.add_argument("--ram",
            help="RAM file to load (default none)"
        )
#         self.parser.add_argument("--rom",
#             help="ROM file to use (default set by machine configuration)"
#         )
        self.parser.add_argument("--max_ops", type=int,
            help="If given: Stop CPU after given cycles else: run forever"
        )

    def setup_cfg(self):
        self.args = self.parse_args()
        self.setup_logging(self.args)

        self.cfg_dict = {
            "verbosity":self.args.verbosity,
            "trace":self.args.trace,
#             "bus_socket_host":self.args.bus_socket_host,
#             "bus_socket_port":self.args.bus_socket_port,
            "ram":self.args.ram,
#             "rom":self.args.rom,
            "max_ops":self.args.max_ops,
        }

#     def open_webbrowser(self):
#         url = "http://%s:%s" % (self.cfg.CPU_CONTROL_ADDR, self.cfg.CPU_CONTROL_PORT)
#         webbrowser.open(url)

    def run(self): # Called from ../DragonPy_CLI.py
#         if not self.args.dont_open_webbrowser:
#             threading.Timer(interval=1.0, function=self.open_webbrowser).start()

        machine_name = self.args.machine
        run_func = self.machine_dict[machine_name]

        run_func(self.cfg_dict)


def get_cli():
    cli = DragonPyCLI(machine_dict)
    cli.setup_cfg()
    return cli

def test_run():
    import os, subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),

#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL

#         "--machine=Simple6809",
#         "--machine=Simple6809",
#         "--machine=sbc09",
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd=".").wait()


if __name__ == "__main__":
    print "ERROR: Use .../DragonPy/DragonPy_CLI.py instead of this file!"
#     test_run() # Should be only enabled for developing!

