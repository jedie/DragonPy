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
import os
import sys

from dragonlib.utils.logging_utils import LOG_LEVELS, setup_logging

import dragonpy
from basic_editor.editor import run_basic_editor
from dragonpy.CoCo.config import CoCo2bCfg
from dragonpy.CoCo.machine import run_CoCo2b
from dragonpy.components.rom import ROMDownloadError
from dragonpy.core import configs
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import StarterGUI
from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.machine import run_Dragon32
from dragonpy.Dragon64.config import Dragon64Cfg
from dragonpy.Dragon64.machine import run_Dragon64
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Multicomp6809.machine import run_Multicomp6809
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.machine import run_sbc09
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.machine import run_Simple6809
from dragonpy.vectrex.config import VectrexCfg
from dragonpy.vectrex.machine import run_Vectrex


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


machine_dict.register(configs.DRAGON32, (run_Dragon32, Dragon32Cfg), default=True)
machine_dict.register(configs.DRAGON64, (run_Dragon64, Dragon64Cfg))
machine_dict.register(configs.COCO2B, (run_CoCo2b, CoCo2bCfg))
machine_dict.register(configs.SBC09, (run_sbc09, SBC09Cfg))
machine_dict.register(configs.SIMPLE6809, (run_Simple6809, Simple6809Cfg))
machine_dict.register(configs.MULTICOMP6809, (run_Multicomp6809, Multicomp6809Cfg))
machine_dict.register(configs.VECTREX, (run_Vectrex, VectrexCfg))


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


@cli.command(help="Download/Test only ROM files")
def download_roms():
    download_error = False
    for machine_name, data in list(machine_dict.items()):
        machine_config = data[1]
        click.secho(
            f"Download / test ROM for {click.style(machine_name, bold=True)}:",
            bg='blue', fg='white'
        )

        for rom in machine_config.DEFAULT_ROMS:
            click.echo(f"\tROM file: {click.style(rom.FILENAME, bold=True)}")
            try:
                content = rom.get_data()
            except ROMDownloadError as err:
                download_error = True
                click.secho(
                    f'Download {err.url!r} -> {err.origin_err}',
                    bg='red', fg='white'
                )
                click.echo('')
                continue

            size = len(content)
            click.echo(f"\tfile size is ${size:04x} (dez.: {size:d}) Bytes\n")

    if download_error:
        sys.exit(1)


@cli.command(help="Run all tests via nose")
@cli_config
def nosetests(cli_config, **kwargs):
    path = os.path.abspath(os.path.dirname(dragonpy.__file__))
    click.secho(f"Run all tests in {path!r}", bold=True)
    #
    # import here, because normal PyPi installation has no nose installed ;)
    try:
        import nose
    except ImportError as err:
        print(f"Can't run test, requirements not installed: {err}")
        sys.exit(-1)

    from nose.config import Config
    config = Config(workingDir=path)
    nose.main(defaultTest=path, argv=[sys.argv[0]], config=config)


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
