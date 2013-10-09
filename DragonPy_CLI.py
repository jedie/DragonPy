#!/usr/bin/env python

"""
    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import atexit
import logging
import inspect
import sys

from DragonPy import Dragon
from base_cli import Base_CLI
import configs


@atexit.register
def goodbye():
    print "-- END --"
    sys.stdout.flush()
    sys.stderr.flush()


def get_configs():
    cfg_classes = {}
    for name, cls in inspect.getmembers(configs, inspect.isclass):
        if not issubclass(cls, configs.BaseConfig):
            continue
        if name == "BaseConfig":
            continue

        cfg_classes[name] = cls
    return cfg_classes


class DragonPyCLI(Base_CLI):
    LOG_NAME = "DragonPy"
    DESCRIPTION = "DragonPy - Dragon 32 emulator in Python"

    def __init__(self):
        super(DragonPyCLI, self).__init__()
        self.configs = get_configs()
        self.log.debug("Existing configs: %s" % repr(self.configs))

        default_cfg = self.configs[configs.DEFAULT_CFG] # for default values

        self.parser.add_argument("--cfg",
            choices=self.configs.keys(),
            default="Dragon32Cfg",
            help="Used configuration"
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
            help="TODO: max. cpu cycles"
        )
        self.parser.add_argument("--area_debug_active",
            help="Debug in PC area: <level>:<start>-<end> - e.g.: --area_debug_active=10:db79-ffff"
        )


    def setup_cfg(self):
        args = self.parse_args()
        self.setup_logging(args)

        config_name = args.cfg
        config_cls = self.configs[config_name]
        self.cfg = config_cls(args)
        self.cfg.config_name = config_name

        if args.area_debug_active:
            # FIXME: How do this in a easier way?
            level, area = args.area_debug_active.split(":")
            level = int(level)
            start, end = area.split("-")
            start = start.strip()
            end = end.strip()
            start = int(start, 16)
            end = int(end, 16)
            self.cfg.area_debug = (level, start, end)
            print "Activate area debug: Set debug level to %i from $%x to $%x" % self.cfg.area_debug
        else:
            self.cfg.area_debug = None

    def run(self):
        self.setup_cfg()

        dragon = Dragon(self.cfg)
        dragon.run()


if __name__ == "__main__":
    cli = DragonPyCLI()
    cli.run()

    print "\n --- END --- \n"
