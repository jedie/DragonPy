"""
    CLI for usage
"""

import inspect
import logging
import sys

import rich_click as click
from cli_base.autodiscover import import_all_files
from cli_base.cli_tools.version_info import print_version
from rich import print  # noqa
from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import dragonpy
from dragonpy import constants


logger = logging.getLogger(__name__)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


# Register all click commands, just by import all files in this package:
import_all_files(package=__package__, init_file=__file__)


@cli.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


def main():
    print_version(dragonpy)
    print(
        inspect.cleandoc(
            """
            ********************************************************
            * DragonPy is a Open source (GPL v3 or later) emulator *
            * for the 30 years old homecomputer Dragon 32          *
            * and Tandy TRS-80 Color Computer (CoCo)...            *
            ********************************************************
            * Homepage: https://github.com/jedie/DragonPy          *
            ********************************************************
        """
        )
    )

    console = Console()
    rich_traceback_install(
        width=console.size.width,  # full terminal width
        show_locals=True,
        suppress=[click],
        max_frames=2,
    )

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
