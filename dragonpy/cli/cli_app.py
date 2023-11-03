"""
    CLI for usage
"""
from __future__ import annotations

import inspect
import locale
import logging
import sys
from pathlib import Path

import rich_click as click
from bx_py_utils.path import assert_is_file
from rich import print  # noqa
from rich_click import RichGroup

import dragonpy
from basic_editor.editor import run_basic_editor
from dragonpy import __version__, constants
from dragonpy.components.rom import ROMFileError
from dragonpy.constants import VERBOSITY_DEFAULT_VALUE, VERBOSITY_DICT
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import gui_mainloop


logger = logging.getLogger(__name__)


# use user's preferred locale
# e.g.: for formatting cycles/sec number
locale.setlocale(locale.LC_ALL, '')


PACKAGE_ROOT = Path(dragonpy.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=False,
        writable=True,
        path_type=Path,
    )
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


OPTION_KWARGS_VERBOSITY = dict(
    type=click.Choice([str(number) for number in sorted(VERBOSITY_DICT.keys())]),
    default=str(VERBOSITY_DEFAULT_VALUE),
    show_default=True,
    help=", ".join(f'{number}:{text}' for number, text in VERBOSITY_DICT.items()),
)
OPTION_KWARGS_MACHINE = dict(
    type=click.Choice(sorted(machine_dict.keys())),
    default=machine_dict.DEFAULT,
    show_default=True,
    help='Used machine configuration',
)


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


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


@click.command()
def gui():
    """Start the DragonPy tkinter starter GUI"""
    gui_mainloop(confirm_exit=False)


cli.add_command(gui)


@click.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSITY)
@click.option('--trace/--no-trace', **OPTION_ARGS_DEFAULT_FALSE, help='Create trace lines')
@click.option(
    '--max-ops',
    type=int,
    default=None,
    show_default=True,
    help='If given: Stop CPU after given cycles else: run forever',
)
@click.option('--machine', **OPTION_KWARGS_MACHINE)
def run(machine: str, trace: bool, max_ops: int | None, verbosity: str):
    """Run a machine emulation"""
    machine_run_func, MachineConfigClass = machine_dict[machine]
    print(f'Use machine func: {machine_run_func.__name__}')
    cfg_dict = {
        'verbosity': int(verbosity),
        'trace': trace,
        'max_ops': max_ops,
    }
    print(cfg_dict)
    machine_run_func(cfg_dict)


cli.add_command(run)


@click.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSITY)
@click.option('--machine', **OPTION_KWARGS_MACHINE)
def editor(machine: str, verbosity: str):
    """
    Run only the BASIC editor
    """
    machine_run_func, MachineConfigClass = machine_dict[machine]
    cfg_dict = {
        'verbosity': int(verbosity),
        'trace': False,
        'max_ops': None,
    }
    machine_cfg = MachineConfigClass(cfg_dict)
    run_basic_editor(machine_cfg)


cli.add_command(editor)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
@click.option(
    '--machines',
    '-m',
    multiple=True,
    type=click.Choice(sorted(machine_dict.keys())),
    default=None,
    help='Download ROM only for given machine(s). Leave empty to download all known ROMs',
)
def download_roms(machines: tuple[str] | None, verbose: bool = True):
    """
    Download/Test only ROM files
    """
    if not machines:
        machines = sorted(machine_dict.keys())
    print(f'Download ROMs for {machines}')
    success = 0
    for machine_name in machines:
        machine_run_func, machine_cfg = machine_dict[machine_name]
        print(f'Download / test ROM for {machine_name}:')

        for rom in machine_cfg.DEFAULT_ROMS:
            print(f"\tROM file: {rom.FILENAME}")
            try:
                content = rom.get_data()
            except ROMFileError as err:
                print(f'[red]{err}')
                continue

            size = len(content)
            print(f"\tfile size is ${size:04x} (dez.: {size:d}) Bytes\n")
            success += 1

    print(f'{success} ROMs succeed.')


cli.add_command(download_roms)


@click.command()
def log_list():
    """
    List all exiting loggers and exit.
    """
    print("A list of all loggers:")
    for log_name in sorted(logging.Logger.manager.loggerDict):
        print(f"\t{log_name}")


cli.add_command(log_list)


def main():
    print(f'[bold][green]dragonpy[/green] v[cyan]{__version__}')
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

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
