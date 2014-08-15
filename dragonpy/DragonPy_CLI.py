#!/usr/bin/env python
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

from Dragon32.config import Dragon32Cfg
from Dragon64.config import Dragon64Cfg
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.core.base_cli import Base_CLI
from dragonpy.core.configs import configs
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.core.process_main import main_process_startup
from dragonlib.utils.logging_utils import log


configs.register("Dragon32", Dragon32Cfg)
configs.register("Dragon64", Dragon64Cfg)
configs.register("sbc09", SBC09Cfg)
configs.register("Simple6809", Simple6809Cfg, default=True)
configs.register("Multicomp6809", Multicomp6809Cfg)


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

    def __init__(self, configs):
        super(DragonPyCLI, self).__init__()
        self.configs = configs
        log.debug("Existing configs: %s" % repr(self.configs))

        default_cfg = self.configs[configs.DEFAULT] # for default values

        self.parser.add_argument("--cfg",
            choices=self.configs.keys(),
            default=configs.DEFAULT,
            help="Used machine configuration"
        )
        self.parser.add_argument('--display_cycle', action='store_true',
            help="print CPU cycle/sec while running."
        )

        self.parser.add_argument('--trace', action='store_true',
            help="Create trace lines."
        )
        self.parser.add_argument('--dont_open_webbrowser', action='store_true',
            help="Don't open the Webbrowser on CPU http control Server"
        )

        self.parser.add_argument("--bus_socket_host",
            help="Host internal socket bus I/O (do not set manually!)"
        )
        self.parser.add_argument("--bus_socket_port", type=int,
            help="Port for internal socket bus I/O (do not set manually!)"
        )
        self.parser.add_argument("--ram",
            help="RAM file to load (default none)"
        )
        self.parser.add_argument("--rom",
            help="ROM file to use (default set by machine configuration)"
        )
        self.parser.add_argument("--max_ops", type=int,
            help="If given: Stop CPU after given cycles else: run forever"
        )

    def setup_cfg(self):
        self.args = self.parse_args()
        self.setup_logging(self.args)

        config_name = self.args.cfg
        config_cls = self.configs[config_name]
        cfg_dict = {
            "verbosity":self.args.verbosity,
            "display_cycle":self.args.display_cycle,
            "trace":self.args.trace,
            "bus_socket_host":self.args.bus_socket_host,
            "bus_socket_port":self.args.bus_socket_port,
            "ram":self.args.ram,
            "rom":self.args.rom,
            "max_ops":self.args.max_ops,
        }
        self.cfg = config_cls(cfg_dict)
        self.cfg.config_name = config_name

    def open_webbrowser(self):
        url = "http://%s:%s" % (self.cfg.CPU_CONTROL_ADDR, self.cfg.CPU_CONTROL_PORT)
        webbrowser.open(url)

    def run(self): # Called from ../DragonPy_CLI.py
        if not self.args.dont_open_webbrowser:
            threading.Timer(interval=1.0, function=self.open_webbrowser).start()

        main_process_startup(self.cfg)


def get_cli():
    cli = DragonPyCLI(configs)
    cli.setup_cfg()
    return cli

if __name__ == "__main__":
    print "ERROR: Use .../DragonPy/DragonPy_CLI.py instead of this file!"

