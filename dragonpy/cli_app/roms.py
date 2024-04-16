from __future__ import annotations

import rich_click as click
from cli_base.click_defaults import OPTION_ARGS_DEFAULT_FALSE
from rich import print  # noqa

from dragonpy.cli_app import cli
from dragonpy.components.rom import ROMFileError
from dragonpy.core.configs import machine_dict


OPTION_KWARGS_MACHINE = dict(
    type=click.Choice(sorted(machine_dict.keys())),
    default=machine_dict.DEFAULT,
    show_default=True,
    help='Used machine configuration',
)


@cli.command()
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
