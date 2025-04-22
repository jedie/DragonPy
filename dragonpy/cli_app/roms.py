from typing import Annotated

import tyro
from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa

from dragonpy.cli_app import app
from dragonpy.components.rom import ROMFileError
from dragonpy.core.configs import machine_dict


TyroMachineArgType = Annotated[
    str | None,
    tyro.conf.arg(
        default=None,
        help=f'Limits download to one machine, if given. One of: {sorted(machine_dict.keys())}',
    ),
]


@app.command
def download_roms(machine: TyroMachineArgType, verbosity: TyroVerbosityArgType):
    """
    Download/Test only ROM files
    """
    setup_logging(verbosity=verbosity)

    if machine:
        machines = [machine]
    else:
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
