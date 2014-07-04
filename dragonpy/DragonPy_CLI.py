#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import atexit
import sys

from Dragon32.config import Dragon32Cfg
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.core.DragonPy import Dragon
from dragonpy.core.base_cli import Base_CLI
from dragonpy.core.configs import configs
from dragonpy.sbc09.config import SBC09Cfg


configs.register("Dragon32", Dragon32Cfg, default=True)
configs.register("sbc09", SBC09Cfg)
configs.register("Simple6809", Simple6809Cfg)
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
        self.log.debug("Existing configs: %s" % repr(self.configs))

        default_cfg = self.configs[configs.DEFAULT] # for default values

        self.parser.add_argument("--cfg",
            choices=self.configs.keys(),
            default=configs.DEFAULT,
            help="Used configuration"
        )
        self.parser.add_argument('--display_cycle', action='store_true',
            help="print CPU cycle/sec while running."
        )

        # TODO:
#         self.parser.add_argument('--trace',
#             help="Filename for create a trace file."
#         )

        self.parser.add_argument('--compare_trace',
            type=int, choices=(0, 1, 2, 3, 4, 5), default=0,
            help="Compare with XRoar/v09 trace file? (see README)"
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
            help="ROM file to use (default %s)" % default_cfg.DEFAULT_ROM
        )
        self.parser.add_argument("--max", type=int,
            help="If given: Stop CPU after given cycles else: run forever"
        )
        self.parser.add_argument("--area_debug_active",
            help="Debug in PC area: <level>:<start>-<end> - e.g.: --area_debug_active=10:db79-ffff"
        )
        self.parser.add_argument("--area_debug_cycles", type=int,
            help="activate debug after CPU cycles",
        )

    def setup_cfg(self):
        args = self.parse_args()
        self.setup_logging(args)

        config_name = args.cfg
        config_cls = self.configs[config_name]
        self.cfg = config_cls(args)
        self.cfg.config_name = config_name

    def run(self):
        dragon = Dragon(self.cfg)
        dragon.run()


def get_cli():
    cli = DragonPyCLI(configs)
    cli.setup_cfg()
    return cli

if __name__ == "__main__":
    print "ERROR: Use .../DragonPy/DragonPy_CLI.py instead of this file!"

