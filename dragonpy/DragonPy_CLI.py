#!/usr/bin/env python2
# coding: utf-8

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import atexit
import locale
import logging
import sys


# https://pypi.python.org/pypi/Click/
import click

from dragonlib.utils.logging_utils import setup_logging, LOG_LEVELS

from basic_editor.editor import run_basic_editor

import dragonpy
from dragonpy.CoCo.config import CoCo2bCfg
from dragonpy.CoCo.machine import run_CoCo2b
from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.machine import run_Dragon32
from dragonpy.Dragon64.config import Dragon64Cfg
from dragonpy.Dragon64.machine import run_Dragon64
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Multicomp6809.machine import run_Multicomp6809
from dragonpy.core import configs
from dragonpy.core.base_cli import Base_CLI
from dragonpy.core.bechmark import run_benchmark
from dragonpy.core.configs import machine_dict
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.machine import run_sbc09
from dragonpy.vectrex.config import VectrexCfg
from dragonpy.vectrex.machine import run_Vectrex


log = logging.getLogger(__name__)


# DEFAULT_LOG_FORMATTER = "%(message)s"
# DEFAULT_LOG_FORMATTER = "%(processName)s/%(threadName)s %(message)s"
# DEFAULT_LOG_FORMATTER = "[%(processName)s %(threadName)s] %(message)s"
# DEFAULT_LOG_FORMATTER = "[%(levelname)s %(asctime)s %(module)s] %(message)s"
# DEFAULT_LOG_FORMATTER = "%(levelname)8s %(created)f %(module)-12s %(message)s"
DEFAULT_LOG_FORMATTER = "%(relativeCreated)-5d %(levelname)8s %(module)13s %(lineno)d %(message)s"


machine_dict.register(configs.DRAGON32, (run_Dragon32, Dragon32Cfg), default=True)
machine_dict.register(configs.DRAGON64, (run_Dragon64, Dragon64Cfg))
machine_dict.register(configs.COCO2B, (run_CoCo2b, CoCo2bCfg))
machine_dict.register(configs.SBC09, (run_sbc09,SBC09Cfg))
# machine_dict.register(configs.SIMPLE6809, Simple6809Cfg)
machine_dict.register(configs.MULTICOMP6809, (run_Multicomp6809, Multicomp6809Cfg))
machine_dict.register(configs.VECTREX, (run_Vectrex, VectrexCfg))


# use user's preferred locale
# e.g.: for formating cycles/sec number
locale.setlocale(locale.LC_ALL, '')


@atexit.register
def goodbye():
    print("\n --- END --- \n")



class CliConfig(object):
    def __init__(self, machine, log, verbosity, log_formatter):
        self.machine = machine
        self.log = log
        self.verbosity=int(verbosity)
        self.log_formatter=log_formatter

        self.setup_logging()

        self.cfg_dict = {
            "verbosity":self.verbosity,
            "trace":None,
        }
        machine_name = self.machine
        self.machine_run_func, self.machine_cfg = machine_dict[machine]

    def setup_logging(self):
        handler = logging.StreamHandler()

        # Setup root logger
        setup_logging(
            level=self.verbosity,
            logger_name=None, # Use root logger
            handler=handler,
            log_formatter=self.log_formatter
        )

        if self.log is None:
            return

        # Setup given loggers
        for logger_cfg in self.log:
            logger_name, level = logger_cfg.rsplit(",", 1)
            level = int(level)

            setup_logging(
                level=level,
                logger_name=logger_name,
                handler=handler,
                log_formatter=self.log_formatter
            )

cli_config = click.make_pass_decorator(CliConfig)


@click.group()
@click.version_option(dragonpy.__version__)
@click.option("--machine",
    type=click.Choice(sorted(machine_dict.keys())),
    default=machine_dict.DEFAULT,
    help="Used machine configuration (Default: %s)" % machine_dict.DEFAULT)
@click.option("--log", default=False, multiple=True,
    help="Setup loggers, e.g.: --log DragonPy.cpu6809,50 --log dragonpy.Dragon32.MC6821_PIA,10")
@click.option("--verbosity",
    type=click.Choice(["%i" % level for level in LOG_LEVELS]),
    default="%i" % logging.CRITICAL,
    help="verbosity level to stdout (lower == more output! default: %s)" % logging.INFO)
@click.option("--log_formatter", default=DEFAULT_LOG_FORMATTER,
    help="see: http://docs.python.org/2/library/logging.html#logrecord-attributes")
@click.pass_context
def cli(ctx, **kwargs):
    log.critical("cli kwargs: %s", repr(kwargs))
    ctx.obj = CliConfig(**kwargs)


@cli.command()
@cli_config
def editor(cli_config):
    log.critical("Use machine cfg: %s", cli_config.machine_cfg.__name__)
    cfg = cli_config.machine_cfg(cli_config.cfg_dict)
    run_basic_editor(cfg)


@cli.command()
@click.option("--trace", default=False,
    help="Create trace lines."
)
@click.option("--ram", default=None, help="RAM file to load (default none)")
@click.option("--rom", default=None, help="ROM file to use (default set by machine configuration)")
@click.option("--max_ops", default=None, type=int,
    help="If given: Stop CPU after given cycles else: run forever")
@cli_config
def run(cli_config, **kwargs):
    log.critical("Use machine func: %s", cli_config.machine_run_func.__name__)
    log.critical("cli run kwargs: %s", repr(kwargs))
    cli_config.cfg_dict.update(kwargs)
    cli_config.machine_run_func(cli_config.cfg_dict)


DEFAULT_LOOPS = 5
@cli.command()
@click.option("--loops", default=DEFAULT_LOOPS,
    help="How many benchmark loops should be run? (default: %i)" % DEFAULT_LOOPS)
@cli_config
def benchmark(cli_config, loops):
    log.critical("Run a benchmark only...")
    run_benchmark(loops)


if __name__ == "__main__":
    cli()



###############################################################################
###############################################################################
###############################################################################
class DragonPyCLI(Base_CLI):
    LOG_NAME = "DragonPy"
    DESCRIPTION = "DragonPy - Dragon 32 emulator in Python"
    VERSION = dragonpy.__version__

    def __init__(self, machine_dict):
        super(DragonPyCLI, self).__init__()
        self.machine_dict = machine_dict
        log.debug("Existing machine_dict: %s" % repr(self.machine_dict))

        self.parser.add_argument("--machine",
            choices=sorted(self.machine_dict.keys()),
            default=machine_dict.DEFAULT,
            help="Used machine configuration (Default: %s)" % machine_dict.DEFAULT
        )

        self.subparsers = self.parser.add_subparsers(title="commands",
            help="Help for commands, e.g.: '%s run --help'" % self.parser.prog
        )

        # The run Emulator command:

        self.parser_run_machine = self.subparsers.add_parser(name="run",
            help="Start the Emulator",
            epilog="e.g.: to run CoCo do: '%s --machine CoCo2b' run" % self.parser.prog
        )
        self.parser_run_machine.set_defaults(func=self.run_machine)

        self.parser_run_machine.add_argument('--trace', action='store_true',
            help="Create trace lines."
        )
#         self.parser_run_machine.add_argument('--dont_open_webbrowser', action='store_true',
#             help="Don't open the Webbrowser on CPU http control Server"
#         )

#         self.parser_run_machine.add_argument("--bus_socket_host",
#             help="Host internal socket bus I/O (do not set manually!)"
#         )
#         self.parser_run_machine.add_argument("--bus_socket_port", type=int,
#             help="Port for internal socket bus I/O (do not set manually!)"
#         )
        self.parser_run_machine.add_argument("--ram",
            help="RAM file to load (default none)"
        )
#         self.parser_run_machine.add_argument("--rom",
#             help="ROM file to use (default set by machine configuration)"
#         )
        self.parser_run_machine.add_argument("--max_ops", type=int,
            help="If given: Stop CPU after given cycles else: run forever"
        )

        # The run BASIC Editor command:

        self.parser_editor = self.subparsers.add_parser(name="editor",
            help="Start only the BASIC Editor",
            epilog="e.g.: CoCo Editor do: '%s --machine CoCo2b' editor" % self.parser.prog
        )
        self.parser_editor.set_defaults(func=self.run_editor)

        # The run only Benchmarks

        self.parser_benchmark = self.subparsers.add_parser(name="benchmark",
            help="Start a benchmark",
        )
        default_loops = 5
        self.parser_benchmark.add_argument("--loops", type=int, default=default_loops,
            help="How many loops should be run? (default: %i)" % default_loops
        )
        self.parser_benchmark.set_defaults(func=self.run_benchmark)

    def setup_cfg(self):
        self.args = self.parse_args()
        self.setup_logging(self.args)

        self.cfg_dict = {
            "verbosity":self.verbosity,
            "trace":None,
        }
        machine_name = self.machine
        self.machine_run_func, self.machine_cfg = self.machine_dict[machine_name]

#     def open_webbrowser(self):
#         url = "http://%s:%s" % (self.cfg.CPU_CONTROL_ADDR, self.cfg.CPU_CONTROL_PORT)
#         webbrowser.open(url)

    def run(self): # Called from ../DragonPy_CLI.py
        log.critical("run func: %s", self.func.__name__)
        self.func()

    def run_machine(self):
#         if not self.dont_open_webbrowser:
#             threading.Timer(interval=1.0, function=self.open_webbrowser).start()

        log.critical("Use machine func: %s", self.machine_run_func.__name__)
        self.cfg_dict.update({
            "trace":self.trace,
#             "bus_socket_host":self.bus_socket_host,
#             "bus_socket_port":self.bus_socket_port,
            "ram":self.ram,
#             "rom":self.rom,
            "max_ops":self.max_ops,
        })
        self.machine_run_func(self.cfg_dict)

    def run_editor(self):
        log.critical("Use machine cfg: %s", self.machine_cfg.__name__)
        cfg = self.machine_cfg(self.cfg_dict)
        run_basic_editor(cfg)

    def run_benchmark(self):
        log.critical("Run a benchmark only...")
        run_benchmark(self.loops)

# def get_cli():
#     cli = DragonPyCLI(machine_dict)
#     cli.setup_cfg()
#     return cli


#------------------------------------------------------------------------------


def test_run():
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#         "-h"
#         "--log_list",
        "--log", "DragonPy.cpu6809,50", "dragonpy.Dragon32.MC6821_PIA,10",

#         "--verbosity", " 1", # hardcode DEBUG ;)
#         "--verbosity", "10", # DEBUG
#         "--verbosity", "20", # INFO
#         "--verbosity", "30", # WARNING
#         "--verbosity", "40", # ERROR
#         "--verbosity", "50", # CRITICAL/FATAL
#         "--verbosity", "99", # nearly all off
        "--machine", "Dragon32", "run",
#        "--machine", "Vectrex", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()


# if __name__ == "__main__":
    # print("ERROR: Use .../DragonPy/DragonPy_CLI.py instead of this file!")
#     test_run() # Should be only enabled for developing!

