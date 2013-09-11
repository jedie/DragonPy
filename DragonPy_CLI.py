#!/usr/bin/env python

"""
    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

from DragonPy import Display, Dragon
from base_cli import Base_CLI
from configs import Dragon32Cfg


class DragonPyCLI(Base_CLI):
    LOG_NAME = "DragonPy"
    DESCRIPTION = "DragonPy - Dragon 32 emulator in Python"

    def __init__(self):
        super(DragonPyCLI, self).__init__()
        self._cfg = Dragon32Cfg()

        self.parser.add_argument("--bus", type=int,
            help="Initial PC value"
        )
        self.parser.add_argument("--ram",
            help="RAM file to load (default none)"
        )
        self.parser.add_argument("--rom",
            help="ROM file to use (default %s)" % self._cfg.rom
        )
        self.parser.add_argument("--pc",
            help="Initial PC value"
        )

    def get_cfg(self):
        args = self.parse_args()
        self.setup_logging(args)

        self._cfg.bus = args.bus
        if args.ram:
            self._cfg.ram = args.ram
        if args.rom:
            self._cfg.rom = args.rom
        if args.pc:
            self._cfg.pc = args.pc

        self._cfg.verbosity = args.verbosity

        return self._cfg

    def run(self):
        cfg = self.get_cfg()

#         display = Display()
        display = None
        speaker = None
        cassette = None

        dragon = Dragon(cfg, display, speaker, cassette)
        dragon.run()


if __name__ == "__main__":
    cli = DragonPyCLI()
    cli.run()

    print "\n --- END --- \n"
