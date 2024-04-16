from __future__ import annotations

import locale

import rich_click as click
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE
from cli_base.click_defaults import OPTION_ARGS_DEFAULT_FALSE
from rich import print  # noqa

from basic_editor.editor import run_basic_editor
from dragonpy.cli_app import cli
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import gui_mainloop


# use user's preferred locale
# e.g.: for formatting cycles/sec number
locale.setlocale(locale.LC_ALL, '')


OPTION_KWARGS_MACHINE = dict(
    type=click.Choice(sorted(machine_dict.keys())),
    default=machine_dict.DEFAULT,
    show_default=True,
    help='Used machine configuration',
)


@cli.command()
def gui():
    """<<< **start this** - Start the DragonPy tkinter starter GUI"""
    gui_mainloop(confirm_exit=False)


@cli.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSE)
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


@cli.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSE)
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
