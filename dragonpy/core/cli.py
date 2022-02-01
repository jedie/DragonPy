#!/usr/bin/env python2

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import atexit
import locale
import logging
import sys

from dragonlib.utils.logging_utils import LOG_LEVELS, setup_logging

import dragonpy
from basic_editor.editor import run_basic_editor
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import StarterGUI


try:
    # https://pypi.python.org/pypi/click/
    import click
except ImportError as err:
    print(f"\nERROR: 'click' can't be imported: {err}")
    print("\tIs the virtual environment activated?!?")
    print("\tIs 'click' installed?!?")
    print("\nOrigin error is:\n")
    raise


log = logging.getLogger(__name__)


# DEFAULT_LOG_FORMATTER = "%(message)s"
# DEFAULT_LOG_FORMATTER = "%(processName)s/%(threadName)s %(message)s"
# DEFAULT_LOG_FORMATTER = "[%(processName)s %(threadName)s] %(message)s"
# DEFAULT_LOG_FORMATTER = "[%(levelname)s %(asctime)s %(module)s] %(message)s"
# DEFAULT_LOG_FORMATTER = "%(levelname)8s %(created)f %(module)-12s %(message)s"
DEFAULT_LOG_FORMATTER = "%(relativeCreated)-5d %(levelname)8s %(module)13s %(lineno)d %(message)s"


# use user's preferred locale
# e.g.: for formating cycles/sec number
locale.setlocale(locale.LC_ALL, '')


@atexit.register
def goodbye():
    print("\n --- END --- \n")


class CliConfig:
    def __init__(self, machine, log, verbosity, log_formatter):
        self.machine = machine
        self.log = log
        self.verbosity = int(verbosity)
        self.log_formatter = log_formatter

        self.setup_logging()

        self.cfg_dict = {
            "verbosity": self.verbosity,
            "trace": None,
        }
        self.machine_run_func, self.machine_cfg = machine_dict[machine]

    def setup_logging(self):
        handler = logging.StreamHandler()

        # Setup root logger
        setup_logging(
            level=self.verbosity,
            logger_name=None,  # Use root logger
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
              help=f"Used machine configuration (Default: {machine_dict.DEFAULT})")
@click.option("--log", default=False, multiple=True,
              help="Setup loggers, e.g.: --log DragonPy.cpu6809,50 --log dragonpy.Dragon32.MC6821_PIA,10")
@click.option("--verbosity",
              type=click.Choice([f"{level:d}" for level in LOG_LEVELS]),
              default=f"{logging.CRITICAL:d}",
              help=f"verbosity level to stdout (lower == more output! default: {logging.INFO})")
@click.option("--log_formatter", default=DEFAULT_LOG_FORMATTER,
              help="see: http://docs.python.org/2/library/logging.html#logrecord-attributes")
@click.pass_context
def cli(ctx, **kwargs):
    """
    DragonPy is a Open source (GPL v3 or later) emulator
    for the 30 years old homecomputer Dragon 32
    and Tandy TRS-80 Color Computer (CoCo)...

    Homepage: https://github.com/jedie/DragonPy
    """
    log.critical("cli kwargs: %s", repr(kwargs))
    ctx.obj = CliConfig(**kwargs)


@cli.command(help="Run only the BASIC editor")
@cli_config
def editor(cli_config):
    log.critical("Use machine cfg: %s", cli_config.machine_cfg.__name__)
    cfg = cli_config.machine_cfg(cli_config.cfg_dict)
    run_basic_editor(cfg)


@cli.command(help="Run a machine emulation")
@click.option("--trace/--no-trace", default=False,
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


@cli.command(help="List all exiting loggers and exit.")
def log_list():
    print("A list of all loggers:")
    for log_name in sorted(logging.Logger.manager.loggerDict):
        print(f"\t{log_name}")


def main(confirm_exit=True):
    if len(sys.argv) == 1:
        if confirm_exit:
            def confirm():
                # don't close the terminal window directly
                # important for windows users ;)
                click.prompt("Please press [ENTER] to exit", default="", show_default=False)
            atexit.register(confirm)

        click.secho("\nrun DragonPy starter GUI...\n", bold=True)
        gui = StarterGUI(machine_dict)
        gui.mainloop()
    else:
        cli()


if __name__ == "__main__":
    main()
